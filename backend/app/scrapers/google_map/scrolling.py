import random

from app.core import Logger

from .card_management import get_cards


async def scrolling_map_search(page: str, logger: Logger):
    last_count = 0
    for scroll_count in range(40):
        cards = await get_cards(page, logger)
        count = len(cards)
        print(f"[Scroll {scroll_count}] Found {count} cards so far...")

        if count == last_count:
            print("🛑 No new cards after scrolling. Exiting.")
            break
        last_count = count

        # 👇 this triggers loading
        if cards:
            await cards[-1].scroll_into_view_if_needed()
        random_wait_time = random.uniform(3, 5)
        logger.info(f"wating for {random_wait_time} seconds")

        await page.wait_for_timeout(random_wait_time * 1000)
