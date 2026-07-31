import asyncio
import logging
from datetime import datetime, timezone

from app.core.redis import redis_client
from app.core.logger import Logger
from app.db.engine import SessionLocal
from app.uptime_keeper.models import UptimeMonitor, UptimePing
from app.uptime_keeper.ping import ping, to_uptime_ping
from app.uptime_keeper.constants import SCHEDULE_ZSET_KEY 
from app.uptime_keeper.caching.db_to_redis import get_monitor_cached, store_ping_result, update_monitor
logger = Logger.get_logger(__name__,"uptime")

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
    success = False
    try:
        monitor = await asyncio.to_thread(get_monitor_cached, monitor_id)

        if not monitor or not monitor["is_active"]:
            return

        logger.info("[uptime] pinging %s → %s", monitor_id, monitor["url"])

        result = await ping(monitor["url"])
        result = to_uptime_ping(result)

        checked_at = datetime.now(timezone.utc)

        # store the ping (redis always, postgres only if down)
        await asyncio.to_thread(store_ping_result, monitor_id, result)

        # updates cached last_pinged + reschedules in one redis pipeline
        await asyncio.to_thread(
            update_monitor, monitor_id, checked_at, monitor["interval"]
        )
        success = True

    except Exception as e:
        logger.exception("[uptime] monitor failed %s: %r", monitor_id, e)

    finally:
        if not success:
            try:
                await asyncio.to_thread(_reschedule, monitor_id, FAILURE_RETRY_SECONDS)
            except Exception:
                logger.exception("[uptime] failed to reschedule %s after failure", monitor_id)
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