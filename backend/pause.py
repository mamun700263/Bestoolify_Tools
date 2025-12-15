import asyncio

from playwright.async_api import async_playwright

from app.core import Logger

logger = Logger.get_logger("pause")


async def consent_pop_up(page):
    """Handle Google consent iframe if present."""
    # Wait a bit for iframe to load
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


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, slow_mo=50, args=["--start-maximized"]
        )
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        await page.goto(
            "https://www.google.com/maps/search/restaurants+near+me?hl=en&gl=us"
        )

        await consent_pop_up(page)

        container_selector = 'div.m6QErb.WNBkOb.XiKgde[role="main"]'
        logger.info("✅ Page loaded. Ready for scroll logic.")

        await page.pause()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
