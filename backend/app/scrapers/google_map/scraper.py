import asyncio
import random

from playwright.async_api import async_playwright

from app.core import Logger

from .card_management import extract_card, get_cards
from .cookies_concent import consent_pop_up
from .scrolling import scrolling_map_search

logger = Logger.get_logger("map_scrapper")


def search_query(sentence: str, laguage: str = "en"):
    sentence = sentence.strip().replace(" ", "+")
    base_url = "https://www.google.com/maps/search/"
    target_url = f"{base_url}{sentence}"
    # target_url = f"{base_url}{sentence}?hl={laguage}"
    return target_url


async def scraper(search: str):
    logger.info("scraper on ")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, slow_mo=150, args=["--start-maximized"]
        )
        context = await browser.new_context()
        page = await context.new_page()
        target_url = search_query(search)
        logger.info(f"going to {target_url}")
        await page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
        await consent_pop_up(page, logger)
        await page.wait_for_timeout(5000)
        await scrolling_map_search(page, logger)
        cards = await get_cards(page, logger)
        logger.info(f"✅ Final count: {len(cards)} cards")
        data = []
        for card in cards:
            cards_data = await extract_card(card)
            cards_data.query = search
            data.append(cards_data.dict())

        await browser.close()
        return data
