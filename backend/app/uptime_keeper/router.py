from .ping import ping
from fastapi import APIRouter
router = APIRouter()


@router.get("/test-ping")
async def test_ping():
    result = await ping("https://google.com")
    return result
