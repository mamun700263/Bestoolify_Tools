from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import engine, Base, get_db, create_account,get_accounts

# Create tables
Base.metadata.create_all(bind=engine)
from fastapi import APIRouter
router = APIRouter()

@router.post("/accounts")
def create_account_(email: str, password: str = None, db: Session = Depends(get_db)):
    return create_account(db, email, password)

@router.get("/accounts")
def list_accounts(db: Session = Depends(get_db)):
    return get_accounts(db)
