import json
import os
import logging
from datetime import datetime, timezone

from app.core.redis import redis_client
from app.db.engine import SessionLocal
from app.uptime_keeper.models import UptimeMonitor
from app.uptime_keeper.constants import SCHEDULE_PREFIX, SCHEDULE_ZSET_KEY
logger = logging.getLogger(__name__)



def _monitor_key(monitor_id: str) -> str:
    return f"{SCHEDULE_PREFIX}{monitor_id}"


# def sync_monitor_to_redis(monitor: UptimeMonitor):
#     key = _monitor_key(str(monitor.id))

#     data = {
#         "id": str(monitor.id),
#         "url": monitor.url,
#         "interval": monitor.interval_minutes,
#         "is_active": monitor.is_active,
#         "last_pinged": None,
#     }

#     now = datetime.now(timezone.utc).timestamp()
#     # Score = next time this monitor is due to run, not "now"
#     next_run = now + (monitor.interval_minutes * 60)

#     try:
#         pipe = redis_client.pipeline()
#         pipe.set(key, json.dumps(data))
#         pipe.zadd(SCHEDULE_ZSET_KEY, {str(monitor.id): next_run})
#         pipe.execute()
#     except Exception:
#         logger.exception("Failed to sync monitor %s to redis", monitor.id)
#         raise

def sync_monitor_to_redis(monitor: UptimeMonitor):

    key = _monitor_key(str(monitor.id))

    data = {
        "id": str(monitor.id),
        "account_id": str(monitor.account_id),   # <-- needed for ownership checks
        "url": monitor.url,
        "interval": monitor.interval_minutes,
        "is_active": monitor.is_active,
        "last_pinged": None,
    }

    now = datetime.now(timezone.utc).timestamp()
    next_run = now + (monitor.interval_minutes * 60)

    db = SessionLocal()
    set_monitor_count(db)

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
    set_monitor_count(db)
    try:
        monitors = db.query(UptimeMonitor).all()
        pipe = redis_client.pipeline()
        now = datetime.now(timezone.utc).timestamp()

        for m in monitors:
            key = _monitor_key(str(m.id))
            data = {
                "id": str(m.id),
                "account_id": str(m.account_id),
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


def get_monitor_cached(monitor_id: str) -> dict | None:
    key = _monitor_key(monitor_id)
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception:
        logger.exception("Failed to read monitor %s from redis cache", monitor_id)

    logger.warning("[redis-sync] cache miss for monitor %s, falling back to db", monitor_id)
    db = SessionLocal()
    try:
        monitor = db.query(UptimeMonitor).filter(UptimeMonitor.id == monitor_id).first()
        if not monitor:
            return None
        sync_monitor_to_redis(monitor)
        return {
            "id": str(monitor.id),
            "account_id": str(monitor.account_id),
            "url": monitor.url,
            "interval": monitor.interval_minutes,
            "is_active": monitor.is_active,
            "last_pinged": None,
        }
    finally:
        db.close()


def get_latest_pings_bulk(monitor_ids: list[str]) -> dict[str, dict | None]:
    """
    One MGET for N monitors instead of N separate GETs. Use this whenever
    you're rendering a list of monitors and need each one's live status.
    """
    if not monitor_ids:
        return {}

    keys = [f"{LATEST_PING_PREFIX}{mid}" for mid in monitor_ids]
    print(keys)
    try:
        raw_values = redis_client.mget(keys)
    except Exception:
        logger.exception("Failed to bulk-fetch latest pings")
        return {mid: None for mid in monitor_ids}

    out = {}
    for mid, raw in zip(monitor_ids, raw_values):
        out[mid] = json.loads(raw) if raw else None
    return out

# def sync_all_monitors():
#     db = SessionLocal()
#     try:
#         monitors = db.query(UptimeMonitor).all()

#         pipe = redis_client.pipeline()
#         now = datetime.now(timezone.utc).timestamp()

#         for m in monitors:
#             key = _monitor_key(str(m.id))
#             data = {
#                 "id": str(m.id),
#                 "url": m.url,
#                 "interval": m.interval_minutes,
#                 "is_active": m.is_active,
#                 "last_pinged": None,
#             }
#             next_run = now + (m.interval_minutes * 60)
#             pipe.set(key, json.dumps(data))
#             pipe.zadd(SCHEDULE_ZSET_KEY, {str(m.id): next_run})

#         pipe.execute()
#         logger.info("[redis-sync] synced %d monitors", len(monitors))

#     except Exception:
#         logger.exception("Failed to sync all monitors")
#         raise
#     finally:
#         db.close()


def delete_cache_monitor(monitor_id: str):
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


LATEST_PING_PREFIX = "uptime:latest:"
LATEST_PING_TTL_SECONDS = 60 * 60 * 24  # 1 day — matches "only care about today"


# def get_monitor_cached(monitor_id: str) -> dict | None:
#     """
#     Read monitor config from redis. Falls back to Postgres only on a cache
#     miss (should be rare — cache is populated on create/update via
#     sync_monitor_to_redis). This is what keeps the scheduler off Neon.
#     """
#     key = _monitor_key(monitor_id)
#     try:
#         cached = redis_client.get(key)
#         if cached:
#             return json.loads(cached)
#     except Exception:
#         logger.exception("Failed to read monitor %s from redis cache", monitor_id)

#     logger.warning("[redis-sync] cache miss for monitor %s, falling back to db", monitor_id)
#     db = SessionLocal()
#     try:
#         monitor = db.query(UptimeMonitor).filter(UptimeMonitor.id == monitor_id).first()
#         if not monitor:
#             return None
#         sync_monitor_to_redis(monitor)
#         return {
#             "id": str(monitor.id),
#             "url": monitor.url,
#             "interval": monitor.interval_minutes,
#             "is_active": monitor.is_active,
#             "last_pinged": None,
#         }
#     finally:
#         db.close()


def add_monitor(monitor_id: str):
    """
    Called right after a monitor row is created in Postgres.
    Registers it in the redis cache + schedule so the scheduler
    never has to touch the DB for it during normal ticks.
    """
    db = SessionLocal()
    try:
        monitor = db.query(UptimeMonitor).filter(UptimeMonitor.id == monitor_id).first()
        if not monitor:
            logger.warning("add_monitor: monitor %s not found in db", monitor_id)
            return
        sync_monitor_to_redis(monitor)
        logger.info("[redis-sync] registered new monitor %s", monitor_id)
    finally:
        db.close()


def get_monitors(account_id: str):
    """
    Dashboard list view: monitor config comes from Postgres (rare, cheap —
    one query per page load), but each monitor's live status comes from
    redis, not from any ping table.
    """
    db = SessionLocal()
    try:
        monitors = db.query(UptimeMonitor).filter(UptimeMonitor.account_id == account_id).all()
        out = []
        for m in monitors:
            latest_raw = None
            try:
                latest_raw = redis_client.get(f"{LATEST_PING_PREFIX}{m.id}")
            except Exception:
                logger.exception("Failed to read latest ping for %s", m.id)

            out.append({
                "id": str(m.id),
                "name": m.name,
                "url": m.url,
                "interval_minutes": m.interval_minutes,
                "is_active": m.is_active,
                "latest": json.loads(latest_raw) if latest_raw else None,
            })
        return out
    finally:
        db.close()

import time

HISTORY_PREFIX = "uptime:history:"
HISTORY_WINDOW_SECONDS = 60 * 60 * 24  # 24h


def _history_key(monitor_id: str) -> str:
    return f"{HISTORY_PREFIX}{monitor_id}"


def store_ping_result(monitor_id: str, result: dict):
    """
    Latest snapshot -> redis (for the live badge), always overwritten.
    Rolling history  -> redis sorted set, last 24h of pings, self-trimming.
    Down pings       -> ALSO postgres (permanent incident record beyond 24h).
    """
    checked_at = datetime.now(timezone.utc)
    payload = {**result, "checked_at": checked_at.isoformat()}
    score = checked_at.timestamp()

    # 1. latest snapshot (unchanged from before)
    latest_key = f"{LATEST_PING_PREFIX}{monitor_id}"
    try:
        redis_client.set(latest_key, json.dumps(payload, default=str), ex=LATEST_PING_TTL_SECONDS)
    except Exception:
        logger.exception("Failed to cache latest ping for %s", monitor_id)

    # 2. rolling 24h history
    hist_key = _history_key(monitor_id)
    # include a small unique suffix so two pings in the same second don't collide as members
    member = json.dumps({**payload, "_score": score}, default=str)
    cutoff = score - HISTORY_WINDOW_SECONDS
    try:
        pipe = redis_client.pipeline()
        pipe.zadd(hist_key, {member: score})
        pipe.zremrangebyscore(hist_key, 0, cutoff)  # drop anything older than 24h
        pipe.expire(hist_key, HISTORY_WINDOW_SECONDS)  # safety net if a monitor stops pinging
        pipe.execute()
    except Exception:
        logger.exception("Failed to append ping history for %s", monitor_id)

    # 3. down pings still get a permanent postgres record for /incidents
    is_up = result.get("is_up", True)
    if is_up:
        return

    from app.uptime_keeper.models import UptimePing
    db = SessionLocal()
    try:
        db.add(UptimePing(monitor_id=monitor_id, **result))
        db.commit()
    except Exception:
        logger.exception("Failed to persist down-ping for %s", monitor_id)
        db.rollback()
    finally:
        db.close()


def get_ping_history(monitor_id: str, since_hours: int = 24) -> list[dict]:
    """
    Returns pings from the last `since_hours` (max 24, since that's the window
    we retain), latest first.
    """
    hist_key = _history_key(monitor_id)
    cutoff = time.time() - min(since_hours, 24) * 3600
    try:
        raw = redis_client.zrevrangebyscore(
                hist_key,
                "+inf",
                cutoff,
            )
    except Exception:
        logger.exception("Failed to read ping history for %s", monitor_id)
        return []
    return [json.loads(r) for r in raw]


# def store_ping_result(monitor_id: str, result: dict):
    # """
    # Up  -> redis only, 1-day TTL. This is 95%+ of pings and never touches Postgres.
    # Down -> redis (for the live badge) AND Postgres (this is the only history
    #          that matters — incidents).

    # NOTE: adjust `is_up` below to whatever key `to_uptime_ping` actually returns
    # (e.g. result["status"] == "up" instead of result.get("is_up")).
    # """
    # key = f"{LATEST_PING_PREFIX}{monitor_id}"
    # payload = {**result, "checked_at": datetime.now(timezone.utc).isoformat()}

    # try:
    #     redis_client.set(key, json.dumps(payload, default=str), ex=LATEST_PING_TTL_SECONDS)
    # except Exception:
    #     logger.exception("Failed to cache latest ping for %s", monitor_id)

    # is_up = result.get("is_up", True)
    # if is_up:
    #     return  # up pings never hit postgres

    # from app.uptime_keeper.models import UptimePing  # local import, only needed on the down path
    # db = SessionLocal()
    # try:
    #     db.add(UptimePing(monitor_id=monitor_id, **result))
    #     db.commit()
    # except Exception:
    #     logger.exception("Failed to persist down-ping for %s", monitor_id)
    #     db.rollback()
    # finally:
    #     db.close()


from  app.uptime_keeper import crud


def set_monitor_count(db):
    db_count = crud.count_monitors(db)
    try:
        redis_client.set('monitor_count',db_count)
    except:
        logger.exception("Failed to cache latest monitor count")

def get_monitor_count():
    return redis_client.get('monitor_count')