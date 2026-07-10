# app/uptime_keeper/models.py

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import (
    Column, String, Boolean, Integer, DateTime, ForeignKey, Text,
    CheckConstraint, func
)
from sqlalchemy.orm import relationship
from app.db.base import Base
MAX_MONITORS = 10 

class UptimeMonitor(Base):
    __tablename__ = "uptime_monitors"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
                    PG_UUID(as_uuid=True),
                    ForeignKey("accounts.id", ondelete="CASCADE"),
                    nullable=False,
                    index=True
                )

    name               = Column(String(100), nullable=False)        # "My API", "Production Server"
    url                = Column(String(2048), nullable=False)        # the URL to ping
    interval_minutes   = Column(Integer, default=5, nullable=False)  # how often to ping
    is_active          = Column(Boolean, default=True, nullable=False)
    created_at         = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at         = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # relationships
    account = relationship("Account")
    pings = relationship(
        "UptimePing",
        back_populates="monitor",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<UptimeMonitor {self.name} ({self.url})>"


class UptimePing(Base):
    __tablename__ = "uptime_pings"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitor_id = Column(PG_UUID(as_uuid=True), ForeignKey("uptime_monitors.id", ondelete="CASCADE"), nullable=False, index=True)

    is_up            = Column(Boolean, nullable=False)               # True = up, False = down
    status_code      = Column(Integer, nullable=True)                # 200, 404, 500 etc. None if unreachable
    response_time_ms = Column(Integer, nullable=True)                # how long it took in ms
    error_message    = Column(Text, nullable=True)                   # if it failed, why
    checked_at       = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # relationship
    monitor = relationship("UptimeMonitor", back_populates="pings")

    def __repr__(self):
        status = "UP" if self.is_up else "DOWN"
        return f"<UptimePing {status} {self.response_time_ms}ms>"


class SubscriptionStatus(Base):
    __tablename__ = "subscription_status"

    id            = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id    = Column(
                        PG_UUID(as_uuid=True),
                        ForeignKey("accounts.id", ondelete="CASCADE"),
                        nullable=False,
                        unique=True,
                        index=True
                    )
    monitor_count = Column(Integer, default=0, nullable=False)   # monitors currently in use
    monitor_slots = Column(Integer, default=MAX_MONITORS, nullable=False)  # free-tier default: 10
    description   = Column(Text, default="")

    account = relationship("Account")

    __table_args__ = (
        CheckConstraint("monitor_count <= monitor_slots", name="ck_within_slots"),
        CheckConstraint(f"monitor_slots <= {MAX_MONITORS}", name="ck_hard_cap"),
        CheckConstraint("monitor_count >= 0", name="ck_non_negative"),
    )

    def __repr__(self):
        return f"<SubscriptionStatus account={self.account_id} {self.monitor_count}/{self.monitor_slots}>"


class MonitorPurchase(Base):
    """Audit trail — not wired to payment yet, but keep the shape ready
    for whenever you decide to sell slots above the free cap."""
    __tablename__ = "monitor_purchases"

    id                = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id        = Column(PG_UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity          = Column(Integer, nullable=False, default=1)
    price_paid_cents  = Column(Integer, nullable=False)
    stripe_charge_id  = Column(String, nullable=True)
    purchased_at      = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account")

    def __repr__(self):
        return f"<MonitorPurchase account={self.account_id} qty={self.quantity}>"