from typing import Any, Dict, List, Optional, Type

# from app.core .dataExporters.api_post import post_data_to_api
# from app.core .dataExporters.file_saver import save_to_file
# from app.core .dataExporters.google_sheet_pusher import push_to_google_sheet
from app.core.utils import ScraperConfig

from ..scrapers import BaseScraper


class BaseOrchestrator:
    def __init__(
        self,
        scraper_class: Type[BaseScraper],
        config: ScraperConfig,
        exporter: Optional[str] = "file",
        export_config: Optional[Dict[str, Any]] = None,
    ):
        self.scraper = scraper_class(config)
        self.exporter = exporter
        self.export_config = export_config or {}

    def run(self) -> List[Dict[str, Any]]:
        print("🚀 Starting scraping process...")
        data = self.scraper.scrape()

        if not data:
            print("⚠️ No data scraped.")
            return []

        print(f"✅ Scraped {len(data)} items. Exporting via '{self.exporter}'...")
        # self._export(data)
        return data

    # def _export(self, data: List[Dict[str, Any]]) -> None:
    #     if self.exporter == "file":
    #         save_to_file(data, **self.export_config)
    #     elif self.exporter == "api":
    #         post_data_to_api(data, **self.export_config)
    #     elif self.exporter == "google":
    #         push_to_google_sheet(data, **self.export_config)
    #     else:
    #         print(f"❌ Unknown exporter: {self.exporter}")
