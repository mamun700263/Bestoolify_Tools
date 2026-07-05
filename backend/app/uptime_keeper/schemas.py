import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl

from typing import Optional
from pydantic import BaseModel


class MonitorLiveStatus(BaseModel):
    is_up: bool
    response_time_ms: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    checked_at: str



# ------------------------
# Uptime Monitor Schemas
# ------------------------

class UptimeMonitorBase(BaseModel):
    name: str
    url: HttpUrl
    interval_minutes: int = 5
    is_active: bool = True


class UptimeMonitorCreate(UptimeMonitorBase):
    # account_id: uuid.UUID
    pass


class UptimeMonitorUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    interval_minutes: int | None = None
    is_active: bool | None = None


class UptimeMonitorOut(UptimeMonitorBase):
    id: uuid.UUID
    account_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
class UptimeMonitorWithStatus(UptimeMonitorOut):
    live: Optional[MonitorLiveStatus] = None

# ------------------------
# Uptime Ping Schemas
# ------------------------

class UptimePingBase(BaseModel):
    is_up: bool
    status_code: int | None = None
    response_time_ms: int | None = None
    error_message: str | None = None


class UptimePingCreate(UptimePingBase):
    monitor_id: uuid.UUID


class UptimePingOut(UptimePingBase):
    id: uuid.UUID
    monitor_id: uuid.UUID
    checked_at: datetime

    class Config:
        from_attributes = True