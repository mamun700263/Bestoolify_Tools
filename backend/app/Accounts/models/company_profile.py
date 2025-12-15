# app/db/models.py
import uuid
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.db import Base


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    company_name = Column(String(255), nullable=False)
    company_logo_url = Column(String(1024), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(30), nullable=True)
    domain = Column(
        String(255), nullable=True
    )  # optional: restrict signups to company domain
    billing_plan = Column(String(100), nullable=True)
    settings = Column(JSON, nullable=True)

    account = relationship("Account", back_populates="company_profile")
