from fastapi import (
    APIRouter,
    Query
    )
from app.core.logger import Logger
from app.uptime_keeper.ping import ping

router = APIRouter()

logger = Logger.get_logger(__name__,"uptime")

@router.get(
    "/test-ping",
    summary="check health of a URL",
    description="Checks whether a given URL is reachable and returns the response time.",
)
async def test_ping(
    url: str = Query(..., description="The full URL to ping, including scheme.", example="https://example.com")
):
    result = await ping(url)

    # Logging side-effect should never break the actual response to the caller.
    try:
        from app.core.data_exporters import GoogleSheetPusher
        sheet = GoogleSheetPusher('Tavdev Monitor')
        row = {**result, "base_url": url, "checked_at": result["checked_at"].isoformat()}
        sheet.append_row(row, "passed")
    except Exception as e:
        logger.warning(f"GoogleSheet export failed for test-ping url {url}: {e}")

    return result


