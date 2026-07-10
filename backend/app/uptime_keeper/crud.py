# app/uptime_keeper/crud.py

from sqlalchemy import update
from sqlalchemy.orm import Session
from app.uptime_keeper import models, schemas
from app.accounts.models import Account
from app.uptime_keeper.caching.db_to_redis import update_monitor as redis_monitor_update


class MonitorLimitExceeded(Exception):
    """Raised when an account has no free monitor slots left."""
    pass

MAX_MONITORS=10
# ------------------------
# Slot enforcement (SubscriptionStatus)
# ------------------------
from sqlalchemy.exc import IntegrityError

def _get_or_create_subscription_status(db: Session, account_id):
    """
    Returns the account's SubscriptionStatus row, creating it if it
    doesn't exist yet. Backfills monitor_count from any monitors the
    account already has, so accounts created before this logic existed
    (or before the migration ran) don't get a false-zero count.
    """
    status = db.query(models.SubscriptionStatus).filter(
        models.SubscriptionStatus.account_id == account_id
    ).first()

    if status:
        return status

    existing_monitor_count = db.query(models.UptimeMonitor).filter(
        models.UptimeMonitor.account_id == account_id
    ).count()

    status = models.SubscriptionStatus(
        account_id=account_id,
        monitor_count=existing_monitor_count,
        monitor_slots=MAX_MONITORS,
    )
    db.add(status)
    try:
        db.commit()
    except IntegrityError:
        # another request created it first (race) — just re-fetch
        db.rollback()
        status = db.query(models.SubscriptionStatus).filter(
            models.SubscriptionStatus.account_id == account_id
        ).first()
    return status


def _claim_monitor_slot(db: Session, account_id) -> bool:
    """
    Atomically increments monitor_count on SubscriptionStatus if the
    account has room. Creates the SubscriptionStatus row first if it
    doesn't exist. Returns True if a slot was claimed, False if the
    account is at its cap.
    """
    _get_or_create_subscription_status(db, account_id)

    result = db.execute(
        update(models.SubscriptionStatus)
        .where(
            models.SubscriptionStatus.account_id == account_id,
            models.SubscriptionStatus.monitor_count < models.SubscriptionStatus.monitor_slots,
        )
        .values(monitor_count=models.SubscriptionStatus.monitor_count + 1)
    )
    db.commit()
    return result.rowcount == 1


def _release_monitor_slot(db: Session, account_id) -> None:
    """Frees up a slot. Call whenever a monitor is deleted."""
    db.execute(
        update(models.SubscriptionStatus)
        .where(
            models.SubscriptionStatus.account_id == account_id,
            models.SubscriptionStatus.monitor_count > 0,
        )
        .values(monitor_count=models.SubscriptionStatus.monitor_count - 1)
    )
    db.commit()
# ------------------------
# Uptime Monitor CRUD
# ------------------------

def create_monitor(db: Session, data: schemas.UptimeMonitorCreate, account: Account):
    # Claim the slot BEFORE inserting — this is the atomic gate.
    if not _claim_monitor_slot(db, account.id):
        raise MonitorLimitExceeded(
            f"Account {account.id} has reached its monitor limit."
        )

    payload = data.model_dump()
    payload["url"] = str(payload["url"])
    payload["account_id"] = account.id

    obj = models.UptimeMonitor(**payload)

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
    except Exception:
        db.rollback()
        _release_monitor_slot(db, account.id)  # give the slot back, insert failed
        raise

    # --------------------
    # Redis sync (event)
    # --------------------
    from app.uptime_keeper.caching.db_to_redis import sync_monitor_to_redis
    sync_monitor_to_redis(obj)

    return obj


def update_monitor(db: Session, monitor_id, data: schemas.UptimeMonitorUpdate):
    obj = get_monitor(db, monitor_id)
    if not obj:
        return None

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)

    # --------------------
    # Redis sync (event)
    # --------------------
    from app.uptime_keeper.caching.db_to_redis import sync_monitor_to_redis
    sync_monitor_to_redis(obj)

    return obj


def delete_monitor(db: Session, monitor_id):
    obj = get_monitor(db, monitor_id)
    if not obj:
        return None

    account_id = obj.account_id  # grab before delete, obj is gone after commit

    db.delete(obj)
    db.commit()

    # Free the slot now that the monitor is actually gone
    _release_monitor_slot(db, account_id)

    # --------------------
    # Redis cleanup (event)
    # --------------------
    from app.uptime_keeper.caching.db_to_redis import delete_cache_monitor
    delete_cache_monitor(monitor_id)
    # (removed the stray sync_monitor_to_redis(obj) call here — obj no
    # longer exists in the DB at this point, so re-syncing it was pushing
    # a deleted row back into the cache right after clearing it)

    return obj


def count_monitors(db: Session):
    return db.query(models.UptimeMonitor).count()


def get_monitor(db: Session, monitor_id):
    return db.query(models.UptimeMonitor).filter(
        models.UptimeMonitor.id == monitor_id
    ).first()


def get_monitors_by_account(db: Session, account_id):
    return db.query(models.UptimeMonitor).filter(
        models.UptimeMonitor.account_id == account_id
    ).all()


# ------------------------
# Uptime Ping CRUD
# ------------------------

def create_ping(db: Session, data: schemas.UptimePingCreate):
    obj = models.UptimePing(**data.model_dump())

    db.add(obj)
    db.commit()
    db.refresh(obj)

    # --------------------
    # Redis runtime update
    # --------------------
    redis_monitor_update(obj.monitor_id)
    return obj


def get_pings_by_monitor(db: Session, monitor_id):
    return db.query(models.UptimePing).filter(
        models.UptimePing.monitor_id == monitor_id
    ).order_by(models.UptimePing.checked_at.desc()).all()