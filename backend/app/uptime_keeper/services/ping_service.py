from app.core.logger import Logger
from app.uptime_keeper.ping import ping
from app.core.data_exporters import GoogleSheetPusher


class PingService:

    def __init__(self):
        self.logger = Logger.get_logger(__name__,"uptime_services")
        self.sheet = GoogleSheetPusher("Tavdev Monitor")


    async def check_url(self, url: str):

        result = await ping(url)

        await self._export_result(
            url,
            result
        )

        return result


    async def _export_result(self, url, result):

        try:
            row = {
                **result,
                "base_url": url,
                "checked_at": result["checked_at"].isoformat()
            }

            self.sheet.append_row(
                row,
                "passed"
            )

        except Exception as e:
            self.logger.warning(
                f"GoogleSheet export failed for {url}: {e}"
            )