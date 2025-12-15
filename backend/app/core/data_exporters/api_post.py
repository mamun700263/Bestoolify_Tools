import time

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from app.core import Logger

logger = Logger.get_logger(__name__, "Data Exporters")


class ApiPoster:
    @staticmethod
    def post_to_api(url: str, items: list) -> bool:
        if not items:
            logger.warning("⚠️ No items to post.")
            return False

        if ApiPoster._post_with_retry(url, items):
            logger.info(f"✅ Successfully posted data to API: {url}")
            return True
        else:
            logger.error(f"❌ Failed to post data to API: {url}")
            return False

    @staticmethod
    def _post_with_retry(url, data, max_retries=3, delay=2, timeout=10, backoff=False):
        for attempt in range(1, max_retries + 1):
            try:
                res = requests.post(url, json=data, timeout=timeout)
                if res.status_code in [200, 201]:
                    logger.info(f"✅ POST success on attempt {attempt}")
                    return True
                else:
                    logger.warning(
                        f"⚠️ Attempt {attempt} failed: {res.status_code} - {res.text}"
                    )
            except (Timeout, ConnectionError, RequestException) as e:
                logger.warning(f"⚠️ Attempt {attempt} error: {e}")
            time.sleep(delay)
            if backoff:
                delay *= 2
        return False
