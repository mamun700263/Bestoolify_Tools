import uuid

from sqlalchemy import JSON, Boolean, Column
from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from .account import Account
from app.db import Base


class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    is_super_admin = Column(Boolean, default=False, nullable=False)
    permissions = Column(JSON, nullable=True)  # e.g. {"users.manage": true}

    account = relationship("Account", back_populates="admin_profile")


# Indexes for performance; already created via Column(index=True) mostly, but adding composite if needed
Index("ix_accounts_email_role", Account.email, Account.role)
