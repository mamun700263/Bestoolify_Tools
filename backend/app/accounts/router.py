# app/accounts/router.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import app.accounts.crud as crud
from app.accounts.auth import create_access_token, create_refresh_token, decode_token
from app.accounts.dependencies import get_current_account, get_current_admin
from app.accounts.models import Account
from app.accounts.models.account import AccountStatus
from app.accounts.schemas import (
    AccountCreate,
    AccountLogin,
    AccountResponse,
    AccountStatusUpdate,
    TokenRefresh,
)
from app.accounts.schemas.account import PasswordResetRequest
from app.db import get_db

router = APIRouter()


# ── AUTH ──────────────────────────────────────────────────


@router.post("/register", response_model=AccountResponse)
async def register(data: AccountCreate, db: Session = Depends(get_db)):
    account = crud.create_account(db, data)
    try:
        await crud.send_email_verification(db, account)
    except Exception as e:
        print(f"################\n{e}")
    return account


@router.post("/login")
def login(data: AccountLogin, request: Request, db: Session = Depends(get_db)):
    account = crud.login_account(db, data.email, data.password, request.client.host)
    return {
        "access_token": create_access_token(account.id, account.role),
        "refresh_token": create_refresh_token(account.id),
        "token_type": "bearer",
        "account": {
            "id": account.id,
            "email": account.email,
            "role": account.role,
            "status": account.status,
        },
    }

@router.post("/refresh")
def refresh(data: TokenRefresh, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)

    if payload.get("type") != "refresh":
        print("Refresh")
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    account_id = payload.get("sub")
    if not account_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=401, detail="Account not found")
    print("Account Found")
    if account.status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=403, detail=f"Account is {account.status}")

    return {
        "access_token": create_access_token(account.id, account.role),
        "token_type": "bearer",
        "account": {
            "id": account.id,
            "email": account.email,
            "role": account.role,
            "status": account.status,
        },
    }
## +++++ GOOGLE AUTH ++++++++++++++++++++
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import os
import secrets
from urllib.parse import urlencode



GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

@router.get("/auth/google/login")
def google_login():
    state = secrets.token_urlsafe(32)

    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }

    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    response = RedirectResponse(url)

    # TODO: store state (Redis/DB)
    response.set_cookie(key="oauth_state", value=state, httponly=True)

    return response


import os
import requests

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app.db import get_db
from app.accounts.models import Account



GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/auth/google/callback")
def google_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    

    stored_state = request.cookies.get("oauth_state")

    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    token_data = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
    }

    token_res = requests.post(GOOGLE_TOKEN_URL, data=token_data)

    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get Google token")

    token_json = token_res.json()
    access_token = token_json["access_token"]

    userinfo_res = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if userinfo_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    google_user = userinfo_res.json()

    email = google_user["email"]
    google_sub = google_user["sub"]
    email_verified = google_user.get("email_verified", False)

    account = db.query(Account).filter(Account.email == email).first()
    if account:
        # mismatch protection
        if account.google_sub and account.google_sub != google_sub:
            raise HTTPException(status_code=403, detail="OAuth identity mismatch")

        if not account.google_sub:
            account.google_sub = google_sub
            account.auth_provider = "google"

        account.is_verified = True

    else:
        account = Account(
            email=email,
            google_sub=google_sub,
            auth_provider="google",
            is_verified=True,
            status="active",
        )
        db.add(account)

    db.commit()
    db.refresh(account)

    access_token = create_access_token(account.id, account.role)
    refresh_token = create_refresh_token(account.id)
    from urllib.parse import urlencode

    params = urlencode({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })

    return RedirectResponse(
        url=f"{os.getenv('FRONTEND_URL_REDIRECT_URL')}?{params}"
    )
    # response = RedirectResponse(url=os.getenv("FRONTEND_URL_REDIRECT_URL"),)

    # response.set_cookie(
    #     key="access_token",
    #     value=access_token,
    #     httponly=True,
    #     secure=False,  # True in production (HTTPS)
    #     samesite="lax",
    # )

    # response.set_cookie(
    #     key="refresh_token",
    #     value=refresh_token,
    #     httponly=True,
    #     secure=False,
    #     samesite="lax",
    # )

    # return response
# ── EMAIL VERIFICATION ────────────────────────────────────


@router.post("/verify/send")
async def send_verification(
    data: PasswordResetRequest,  # reusing this schema — it only needs email
    db: Session = Depends(get_db),
):
    account = crud.get_account_by_email(db, data.email)

    if account.is_verified:
        raise HTTPException(status_code=400, detail="Account already verified")

    await crud.send_email_verification(db, account)
    return {"message": "Verification email sent"}


@router.get("/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    account = crud.verify_email_token(db, token)
    return {"message": "Email verified successfully", "email": account.email}


# ── ACCOUNT — ME (must be before /{account_id}) ──────────


@router.get("/me", response_model=AccountResponse)
def get_me(current_account: Account = Depends(get_current_account)):
    return current_account


@router.patch("/me/status", response_model=AccountResponse)
def update_my_status(
    data: AccountStatusUpdate,
    current_account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
):
    return crud.update_account_status(db, current_account.id, data.status)


# ── ACCOUNT — ADMIN OPERATIONS ────────────────────────────


@router.get("/", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db),current_account: Account = Depends(get_current_account)):
    return crud.get_all_accounts(db)

@router.get("/all_account_count", response_model=int)
def count_accounts():
    from app.accounts.caching.cache import get_account_count
    return get_account_count()



@router.get("/{account_id:uuid}", response_model=AccountResponse)
def get_account(account_id: UUID, db: Session = Depends(get_db)):
    return crud.get_account_by_id(db, account_id)


@router.patch("/{account_id}/status", response_model=AccountResponse)
def update_status(
    account_id: UUID,
    data: AccountStatusUpdate,
    db: Session = Depends(get_db),
):
    return crud.update_account_status(db, account_id, data.status)


@router.delete("/delete_account")
def delete_account(db: Session = Depends(get_db),current_account: Account = Depends(get_current_account)):
    return crud.delete_account(db, current_account)

@router.delete("/admin/{account_id}")
def delete_admin_account(account_id: UUID, db: Session = Depends(get_db),current_account: Account = Depends(get_current_admin)):
    return crud.delete_account(db, account_id)


