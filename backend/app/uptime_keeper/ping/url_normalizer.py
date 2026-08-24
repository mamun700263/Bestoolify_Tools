import httpx
from app.core.logger import Logger
from datetime import datetime, timezone


logger = Logger.get_logger(__name__,"uptime")

async def normalize_url(url: str) -> str:
    url_stripe = url.strip()
    url_stripe = url_stripe.lower()
    if not url_stripe.startswith(("http://", "https://")):
        if not url_stripe.startswith("www"):
            url_stripe = "www."+url_stripe
        result = f"https://{url_stripe}"
        logger.info(f"{url} was normalized to {result}")
        return result
    
    logger.debug(f"{url} remains unchanged")
    return url_stripe
