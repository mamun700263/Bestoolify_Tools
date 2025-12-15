import asyncio

from app.core import Logger


async def consent_pop_up(page: str, logger: Logger):
    """Handle Google consent iframe if present."""
    await asyncio.sleep(1)

    consent_frame = page.frame(url=lambda u: "consent.google.com" in u)

    if consent_frame:
        try:
            await consent_frame.get_by_role("button", name="Reject all").click(
                timeout=5000
            )
            logger.info("✅ Rejected cookies")
        except Exception as e:
            logger.info(f"⚠️ Consent frame found but click failed: {e}")
    else:
        logger.info("No consent iframe found")
