import asyncio
import os

from app.core.data_exporters import FileSaver
from app.tasks.google_map_scraper import run_scraper

if __name__ == "__main__":
    query = os.getenv("QUERY")
    file_name = os.getenv("FILENAME")

    if not query or not file_name:
        # fallback to interactive mode
        query = input("search -> ").strip()
        file_name = input("what would be the file name? ").strip()
        FileSaver.check_format(file_name)
    # run_scraper.delay(query, file_name)
    result = run_scraper.delay(query, file_name)
    print(result.id)         # Task ID
    print(result.status)     # PENDING, STARTED, SUCCESS
    print(result.get())      # Blocks until finished




# shops that are open
# distance
# python3 runner.py
# burger shops near me
# burger.json
