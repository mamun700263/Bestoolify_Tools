import uuid


from sqlalchemy import JSON,Column
from sqlalchemy import ForeignKey,String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db import Base
# -------- role-specific profile tables (thin, extendable) --------


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    first_name = Column(String(120), nullable=True)
    last_name = Column(String(120), nullable=True)
    phone = Column(String(30), nullable=True)
    avatar_url = Column(String(1024), nullable=True)
    timezone = Column(String(64), nullable=True)
    notification_preferences = Column(
        JSON, nullable=True
    )  # {"email": true, "sms": false}

    account = relationship("Account", back_populates="user_profile")

    def display_name(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return None
