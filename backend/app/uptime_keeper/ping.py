import httpx
from app.core.logger import Logger
from datetime import datetime, timezone


logger = Logger.get_logger(__name__,"uptime")

async def normalize_url(url: str) -> str:
    url_stripe = url.strip()
    if not url.startswith(("http://", "https://")):
        result = f"https://{url_stripe}"
        logger.info(f"{url} was normalized to {result}")
        return result
    logger.debug(f"{url} remains unchanged")
    return url_stripe

async def ping(url: str) -> dict:
    checked_at = datetime.now(timezone.utc)
    url = await normalize_url(url)

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            start = datetime.now(timezone.utc)

            r = await client.get(url)

            elapsed_ms = int(
                (datetime.now(timezone.utc) - start).total_seconds() * 1000
            )

            redirect_count = len(r.history)
            st = {
                # LAYER A: availability
                "is_up": True,
                "status_code": r.status_code,
                "reason": r.reason_phrase,

                # LAYER B: performance
                "response_time_ms": elapsed_ms,

                # LAYER C: routing
                "final_url": str(r.url),
                "redirect_count": redirect_count,
                "http_version": r.http_version,

                # LAYER D: metadata
                "content_type": r.headers.get("content-type"),
                "content_length": len(r.content) if r.content else 0,

                # meta
                "checked_at": checked_at,
                "error_message": None,
            }
            logger.debug(f"ping successfull {url} {elapsed_ms}")
            return st

    except httpx.TimeoutException as e:
        error_type = "timeout"
        logger.error(
        f"Ping failed | url={url} | type={error_type} | error={e}"
    )
    except httpx.ConnectError as e:
        error_type = "connection_refused"
        logger.error(
        f"Ping failed | url={url} | type={error_type} | error={e}"
    )
    except Exception as e:
        error_type = "http_error"
        logger.error(
        f"Ping failed | url={url} | type={error_type} | error={e}"
    )
    logger.error(f"{url} failed {error_type}")
    return {
        "is_up": False,
        "status_code": None,
        "response_time_ms": None,
        "error_type": error_type or None,
        "checked_at": checked_at,
    }

def to_uptime_ping(result: dict) -> dict:
    """
    Maps full ping telemetry → DB persistence schema.
    No mutation of input. No side effects.
    """

    return {
        "is_up": result["is_up"],
        "status_code": result.get("status_code"),
        "response_time_ms": result.get("response_time_ms"),
        "error_message": result.get("error_message"),
        "checked_at": result.get("checked_at"),
    }