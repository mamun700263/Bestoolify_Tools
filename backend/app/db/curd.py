from sqlalchemy.orm import Session
from app.Accounts.models import Account, RoleEnum

def create_account(db:Session, email:str, hashed_password:str=None):
    db_account = Account(email=email, hashed_password=hashed_password)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db:Session):
    return db.query.all()