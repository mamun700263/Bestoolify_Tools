from .models import GoogleMapSearch


def valid_address(address: str) -> bool:
    """the .  needs to be removed"""
    invalid_words = ["Open", "Closed", ".", "Closes"]
    address.strip()
    return (
        len(address) > 2
        and not any(word in address for word in invalid_words)
        and not address == " · "
    )


def clean_address(address: str):
    return address[3:]


async def extract_address(spans: list, index: int = 0) -> str | None:
    target_indexes = [6, 8, 2]
    if index >= len(target_indexes):
        return None

    address = None
    if spans and target_indexes[index] < len(spans):
        address = await spans[target_indexes[index]].text_content()

    if address and valid_address(address):
        return clean_address(address)

    return await extract_address(spans, index + 1)


async def extract_card(card: str):
    anchor = await card.query_selector("a")
    img_el = await card.query_selector("img")
    rating_el = await card.query_selector("span[class*='MW4etd']")
    reviews_el = await card.query_selector("span[class*='UY7F9']")
    spans = await card.query_selector_all("div.UaQhfb div.W4Efsd div.W4Efsd span")
    type_of_place = await spans[0].text_content()

    if spans:
        address = await extract_address(spans, 0)
    else:
        address = None

    name = await anchor.get_attribute("aria-label") if anchor else None
    href = await anchor.get_attribute("href") if anchor else None
    img = await img_el.get_attribute("src") if img_el else None
    rating = await rating_el.text_content() if rating_el else None
    reviews = await reviews_el.text_content() if reviews_el else None
    price_rage = ""
    status = ""

    return GoogleMapSearch(
        **{
            "name": name,
            "type": type_of_place,
            "address": address,
            "link": href,
            "image": img,
            "rating": rating,
            "reviews": reviews,
            "query": "n/a",
        }
    )


async def get_cards(page, logger):
    selectors = ["div.Nv2PK", "div.CpccDe", "div.THOPZb"]

    for selector in selectors:
        cards = await page.query_selector_all(selector)
        logger.info(f"found {len(cards)} cards with selecor {selector}")
        if cards:
            return cards
    return []
