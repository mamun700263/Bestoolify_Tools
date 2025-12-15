import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.Accounts.models import Account, RoleEnum, AccountStatus

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_create_account(db_session):
    acc = Account(email="test@example.com", role=RoleEnum.USER)
    db_session.add(acc)
    db_session.commit()

    fetched = db_session.query(Account).filter_by(email="test@example.com").first()
    assert fetched is not None
    assert fetched.status == AccountStatus.PENDING
    assert fetched.is_verified is False
    assert fetched.created_at is not None
    assert fetched.updated_at is not None

def test_update_account_status(db_session):
    acc = Account(email="update@example.com", role=RoleEnum.USER)
    db_session.add(acc)
    db_session.commit()

    acc.status = AccountStatus.ACTIVE
    db_session.commit()

    fetched = db_session.query(Account).filter_by(email="update@example.com").first()
    assert fetched.status == AccountStatus.ACTIVE
