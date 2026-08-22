import pytest

from app.uptime_keeper.ping import normalize_url


@pytest.mark.asyncio
async def test_normalize_url():
    valid_url = "https://www.google.com"

    result = await normalize_url(valid_url)

    assert result == valid_url
