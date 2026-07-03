import asyncio
import logging
from datetime import datetime, timezone

from app.core.redis import redis_client
from app.db.engine import SessionLocal
from app.uptime_keeper.models import UptimeMonitor, UptimePing
from app.uptime_keeper.ping import ping, to_uptime_ping
from app.uptime_keeper.constants import SCHEDULE_ZSET_KEY 

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 30
FAILURE_RETRY_SECONDS = 60  # backoff before retrying a failed monitor

# Lua script: atomically read due jobs AND remove them in one round trip.
# Prevents duplicate claims across concurrent scheduler instances.
_CLAIM_DUE_SCRIPT = """
local due = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1])
if #due > 0 then
    redis.call('ZREM', KEYS[1], unpack(due))
end
return due
"""
_claim_due = redis_client.register_script(_CLAIM_DUE_SCRIPT)


def _reschedule(monitor_id: str, seconds_from_now: float):
    next_run = datetime.now(timezone.utc).timestamp() + seconds_from_now
    redis_client.zadd(SCHEDULE_ZSET_KEY, {monitor_id: next_run})


# -------------------------
# SINGLE MONITOR EXECUTION
# -------------------------
async def handle_monitor(monitor_id: str):
    db = SessionLocal()
    success = False
    try:
        monitor = await asyncio.to_thread(
            lambda: db.query(UptimeMonitor).filter(UptimeMonitor.id == monitor_id).first()
        )

        if not monitor or not monitor.is_active:
            # inactive/deleted: intentionally do NOT reschedule.
            # re-syncing (sync_monitor_to_redis) is responsible for re-adding it if reactivated.
            return

        logger.info("[uptime] pinging %s → %s", monitor.name, monitor.url)

        result = await ping(monitor.url)
        result = to_uptime_ping(result)

        def _write():
            db.add(UptimePing(monitor_id=monitor.id, **result))
            db.commit()

        await asyncio.to_thread(_write)

        await asyncio.to_thread(
            _reschedule, str(monitor.id), monitor.interval_minutes * 60
        )
        success = True

    except Exception as e:
        logger.exception("[uptime] monitor failed %s: %r", monitor_id, e)

    finally:
        if not success:
            # Still reschedule on failure, just sooner — prevents the monitor
            # from silently falling out of the schedule forever.
            try:
                await asyncio.to_thread(_reschedule, monitor_id, FAILURE_RETRY_SECONDS)
            except Exception:
                logger.exception("[uptime] failed to reschedule %s after failure", monitor_id)
        db.close()


# -------------------------
# SCHEDULER LOOP
# -------------------------
async def scheduler():
    logger.info("[uptime] redis scheduler started")

    while True:
        try:
            now_ts = datetime.now(timezone.utc).timestamp()

            # Atomic claim: read + remove due monitors in one Lua script call
            due = await asyncio.to_thread(_claim_due, keys=[SCHEDULE_ZSET_KEY], args=[now_ts])

            if not due:
                logger.debug("[uptime] no monitors due")
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
                continue

            monitor_ids = [
                m.decode() if isinstance(m, bytes) else m for m in due
            ]

            logger.info("[uptime] due monitors: %d", len(monitor_ids))

            tasks = [handle_monitor(monitor_id) for monitor_id in monitor_ids]
            await asyncio.gather(*tasks)

        except Exception as e:
            logger.exception("[uptime] scheduler error: %r", e)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)