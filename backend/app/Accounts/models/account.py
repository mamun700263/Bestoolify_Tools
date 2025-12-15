import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db import Base


class RoleEnum(str, Enum):
    ADMIN = "admin"
    COMPANY = "company"
    USER = "user"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"
    DELETED = "deleted"
    LOCKED = "locked"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    role = Column(
        SAEnum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.USER
    )
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    status = Column(
        SAEnum(AccountStatus, name="account_status_enum"),
        default=AccountStatus.PENDING,
        nullable=False,
        index=True,
    )

    # tokens and expiries used for email-verify / password reset (one-time tokens)
    verification_token = Column(String(128), nullable=True, index=True)
    verification_expires_at = Column(DateTime(timezone=True), nullable=True)
    reset_token = Column(String(128), nullable=True, index=True)
    reset_expires_at = Column(DateTime(timezone=True), nullable=True)

    # security & throttling
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # telemetry
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    signup_ip = Column(String(45), nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    signup_user_agent = Column(Text, nullable=True)
    last_login_user_agent = Column(Text, nullable=True)

    # multi-tenant (optional)
    # tenant_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)

    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # relationship to profiles
    user_profile = relationship(
        "UserProfile",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
    )
    company_profile = relationship(
        "CompanyProfile",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
    )
    admin_profile = relationship(
        "AdminProfile",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # handy string representation
    def __repr__(self):
        return f"<Account {self.email} ({self.role})>"
