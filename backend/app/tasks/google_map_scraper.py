import asyncio

from app.core import Logger
from app.core.celery import celery_app
from app.core.data_exporters import FileSaver
from app.scrapers.google_map import scraper

logger = Logger.get_logger(__file__, "google_map")
logger.info("logger on")


@celery_app.task(bind=True, name="map_scraper")
def run_scraper(self, query: str, file_name: str):
    logger.info(f"started search for: {query}, saving as {file_name}")
    try:
        logger.info(f"Starting scrape for: {query}")
        data = asyncio.run(scraper(query))
        FileSaver.save(data, file_name)
        logger.info(f"[SUCCESS] Saved results to {file_name}")
        return data
    except Exception as e:
        logger.error(f"Error scraping {query}: {e}")
        raise self.retry(exc=e, countdown=5, max_retries=1)
