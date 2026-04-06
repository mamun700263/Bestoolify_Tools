import asyncio
from app.core import Logger
from app.core.celery import celery_app
from app.core.data_exporters import FileSaver

logger = Logger.get_logger(__name__, "google_map")

@celery_app.task(
    bind=True,
    name="map_scraper"
)
def run_scraper(self, query: str):
    from app.scrapers import google_map_scraper as scraper
    
    logger.info(f"started search for: {query}")
    try:
        logger.info(f"Starting scrape for: {query}")
        data = scraper(query)
        return data
    except Exception as e:
        logger.error(f"Error scraping {query}: {e}")
        raise self.retry(exc=e, countdown=5, max_retries=1)