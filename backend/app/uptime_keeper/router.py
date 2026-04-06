from .ping import ping
from fastapi import Query
from fastapi import APIRouter
router = APIRouter()

@router.get(
    "/test-ping",
    summary="check health of  a URL",
    description="Checks whether a given URL is reachable and returns the response time. Useful for uptime monitoring or pre-scrape health checks.",
    tags=["Utilities"],
)
async def test_ping(
    url: str = Query(
        ...,
        description="The full URL to ping, including scheme.",
        example="https://example.com",
    )
):
    """
    Ping a URL to check its reachability.

    - **url**: Must include `http://` or `https://`
    - Returns response time in milliseconds if reachable
    - Returns `reachable: false` if the host is down or times out
    """
    result = await ping(url)
    return result