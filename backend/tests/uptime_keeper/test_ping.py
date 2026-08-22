import pytest

from app.uptime_keeper.ping import normalize_url
class TestNormalizeUrl:
    valid_url = "https://www.google.com"
    no_http = "www.google.com"
    no_www = "google.com"
    extra_space = "   www.google.com"
    upper_case = "WWW.gooGle.cOm"

    @pytest.mark.asyncio
    async def test_normalize_url(self):
        result = await normalize_url(self.valid_url)
        assert result == self.valid_url

    @pytest.mark.asyncio
    async def test_nohttp(self):
        result = await normalize_url(self.no_http)
        assert result == self.valid_url
    
    @pytest.mark.asyncio
    async def test_no_www(self):
        result = await normalize_url(self.no_www)
        assert result == self.valid_url
    
    @pytest.mark.asyncio
    async def test_extra_space(self):
        result = await normalize_url(self.extra_space)
        assert result == self.valid_url
    
    @pytest.mark.asyncio
    async def test_upper_case(self):
        result = await normalize_url(self.upper_case)
        assert result == self.valid_url