import asyncio

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://quotes.toscrape.com/scroll")
        await page.wait_for_timeout(2000)

        last_height = await page.evaluate("() => document.body.scrollHeight")

        for i in range(20):
            await page.evaluate(
                """
                () => {
                    window.scrollTo(0, document.body.scrollHeight);
                    window.dispatchEvent(new Event('scroll'));
                }
            """
            )
            await page.wait_for_timeout(1500)

            new_height = await page.evaluate("() => document.body.scrollHeight")
            print(f"[Scroll {i+1}] Height: {new_height}")

            if new_height == last_height:
                print("🛑 No new content. Stopping scroll.")
                break

            last_height = new_height

        await browser.close()


asyncio.run(main())
