import json
import os
import logging
from datetime import datetime, timezone

from app.core.redis import redis_client
from app.db.engine import SessionLocal
from app.uptime_keeper.models import UptimeMonitor

logger = logging.getLogger(__name__)

# Two distinct keys/prefixes — don't reuse one name for both roles
SCHEDULE_PREFIX = os.getenv("SCHEDULE_PREFIX", "schedule:monitor:")
SCHEDULE_ZSET_KEY = os.getenv("SCHEDULE_ZSET_KEY", "schedule:monitor:zset")


def _monitor_key(monitor_id: str) -> str:
    return f"{SCHEDULE_PREFIX}{monitor_id}"


def sync_monitor_to_redis(monitor: UptimeMonitor):
    key = _monitor_key(str(monitor.id))

    data = {
        "id": str(monitor.id),
        "url": monitor.url,
        "interval": monitor.interval_minutes,
        "is_active": monitor.is_active,
        "last_pinged": None,
    }

    now = datetime.now(timezone.utc).timestamp()
    # Score = next time this monitor is due to run, not "now"
    next_run = now + (monitor.interval_minutes * 60)

    try:
        pipe = redis_client.pipeline()
        pipe.set(key, json.dumps(data))
        pipe.zadd(SCHEDULE_ZSET_KEY, {str(monitor.id): next_run})
        pipe.execute()
    except Exception:
        logger.exception("Failed to sync monitor %s to redis", monitor.id)
        raise


def sync_all_monitors():
    db = SessionLocal()
    try:
        monitors = db.query(UptimeMonitor).all()

        pipe = redis_client.pipeline()
        now = datetime.now(timezone.utc).timestamp()

        for m in monitors:
            key = _monitor_key(str(m.id))
            data = {
                "id": str(m.id),
                "url": m.url,
                "interval": m.interval_minutes,
                "is_active": m.is_active,
                "last_pinged": None,
            }
            next_run = now + (m.interval_minutes * 60)
            pipe.set(key, json.dumps(data))
            pipe.zadd(SCHEDULE_ZSET_KEY, {str(m.id): next_run})

        pipe.execute()
        logger.info("[redis-sync] synced %d monitors", len(monitors))

    except Exception:
        logger.exception("Failed to sync all monitors")
        raise
    finally:
        db.close()


def delete_monitor(monitor_id: str):
    logger.info("Deleting monitor %s from redis", monitor_id)

    key = _monitor_key(monitor_id)

    try:
        pipe = redis_client.pipeline()
        pipe.delete(key)
        pipe.zrem(SCHEDULE_ZSET_KEY, monitor_id)  # remove from schedule too
        pipe.execute()
    except Exception:
        logger.exception("Failed to delete monitor %s from redis", monitor_id)
        raise


def update_monitor(monitor_id: str, checked_at: datetime, reschedule_interval_minutes: int | None = None):
    """
    Update the cached 'last_pinged' timestamp for a monitor after a check runs.

    Pass the monitor_id and checked_at explicitly rather than an ORM object,
    since the caller is typically an UptimeCheck/result, not the UptimeMonitor itself.
    """
    key = _monitor_key(monitor_id)

    try:
        cached = redis_client.get(key)
    except Exception:
        logger.exception("Failed to read monitor %s from redis", monitor_id)
        return

    if not cached:
        logger.warning("Cache miss for monitor %s during update; skipping", monitor_id)
        return

    data = json.loads(cached)
    data["last_pinged"] = checked_at.isoformat()

    try:
        pipe = redis_client.pipeline()
        pipe.set(key, json.dumps(data))

        if reschedule_interval_minutes is not None:
            next_run = checked_at.timestamp() + (reschedule_interval_minutes * 60)
            pipe.zadd(SCHEDULE_ZSET_KEY, {monitor_id: next_run})

        pipe.execute()
    except Exception:
        logger.exception("Failed to update monitor %s in redis", monitor_id)
        raise