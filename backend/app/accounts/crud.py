from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.accounts.models import (
    Account,
    AdminProfile,
    CompanyProfile,
    RoleEnum,
    UserProfile,
)
from app.accounts.schemas import AccountCreate

from app.accounts.models.account import AccountStatus
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import secrets
from datetime import datetime, timedelta, timezone

from app.core.email.email import send_verification_email
from app.accounts.caching.cache import set_account_count

async def send_email_verification(db: Session, account: Account):
    # 1. generate a secure random token
    token = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    # 2. save token to account
    account.verification_token = token
    account.verification_expires_at = expires_at
    db.commit()

    # 3. send the email
    await send_verification_email(account.email, token)


def verify_email_token(db: Session, token: str) -> Account:
    # 1. find account with this token
    account = db.query(Account).filter(Account.verification_token == token).first()

    if not account:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    # 2. check expiry
    if account.verification_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification token has expired")

    # 3. activate the account
    account.is_verified = True
    account.status = AccountStatus.ACTIVE
    account.verification_token = None
    account.verification_expires_at = None
    db.commit()
    db.refresh(account)
    return account


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── CREATE ────────────────────────────────────────────────


def create_account(db: Session, data: AccountCreate) -> Account:
    # 1. check if email already exists
    existing = db.query(Account).filter(Account.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. create the account
    account = Account(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(account)
    db.flush()  # writes to DB within transaction so account.id exists
    # but not committed yet — still rollbackable

    # 3. create the right profile based on role
    if data.role == RoleEnum.USER:
        db.add(UserProfile(account_id=account.id))

    elif data.role == RoleEnum.COMPANY:
        db.add(
            CompanyProfile(
                account_id=account.id,
                company_name="My Company",  # placeholder — updated later via profile endpoint
            )
        )

    elif data.role == RoleEnum.ADMIN:
        db.add(AdminProfile(account_id=account.id))

    # 4. commit everything together — account + profile in one transaction
    db.commit()
    db.refresh(account)
    set_account_count(db)
    return account


# ── READ ──────────────────────────────────────────────────


def get_account_by_id(db: Session, account_id) -> Account:
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


def get_account_by_email(db: Session, email: str) -> Account:
    account = db.query(Account).filter(Account.email == email).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


def get_all_accounts(db: Session) -> list[Account]:
    return db.query(Account).all()

def get_all_account_count(db: Session) -> int:
    return db.query(Account).count()

# ── UPDATE ────────────────────────────────────────────────


def update_account_status(db: Session, account_id, status) -> Account:
    account = get_account_by_id(db, account_id)
    account.status = status
    db.commit()
    db.refresh(account)
    set_account_count(db)
    return account


# ── DELETE ────────────────────────────────────────────────

#for admin
def delete_account(db: Session, account_id) -> dict:
    account = get_account_by_id(db, account_id)
    db.delete(account)
    db.commit()
    set_account_count(db)
    return {"message": f"Account {account_id} deleted"}

#for users
def delete_account_self(db: Session, account) -> dict:
    db.delete(account)
    db.commit()
    set_account_count(db)
    return {"message": f"Account {account.id} deleted"}



MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15


def login_account(db: Session, email: str, password: str, ip: str = None) -> Account:
    # 1. find account
    account = db.query(Account).filter(Account.email == email).first()
    if not account:
        # don't reveal whether email exists
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. check status
    if account.status == AccountStatus.DISABLED:
        raise HTTPException(status_code=403, detail="Account is disabled")
    if account.status == AccountStatus.DELETED:
        raise HTTPException(status_code=403, detail="Account not found")

    # 3. check if locked
    if account.locked_until and account.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=403,
            detail=f"Account locked until {account.locked_until.strftime('%H:%M UTC')}",
        )

    # 4. verify password
    if not verify_password(password, account.hashed_password):
        account.failed_attempts += 1

        if account.failed_attempts >= MAX_FAILED_ATTEMPTS:
            account.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=LOCK_DURATION_MINUTES
            )
            account.status = AccountStatus.LOCKED
            db.commit()
            raise HTTPException(
                status_code=403,
                detail=f"Too many failed attempts. Account locked for {LOCK_DURATION_MINUTES} minutes",
            )

        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 5. successful login — reset security fields
    account.failed_attempts = 0
    account.locked_until = None
    account.status = AccountStatus.ACTIVE
    account.last_login_at = datetime.now(timezone.utc)
    account.last_login_ip = ip
    db.commit()
    db.refresh(account)
    return account
