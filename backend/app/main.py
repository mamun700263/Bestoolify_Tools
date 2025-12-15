from fastapi import FastAPI

from app.scrapers.google_map.google_map_scrapper import \
    router as google_map_scrapper_router
from app.Accounts.router import router as account_router
app = FastAPI(
    title="playwright google scrapper",
    version="1.0",
)

app.include_router(
    # google_map_scrapper_router, prefix="/google_map_scrapper", tags=["Scraper"]
    account_router, prefix="/account",
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Playwrite API online"}
