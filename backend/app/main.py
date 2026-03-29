from fastapi import FastAPI

from app.scrapers.google_map.router import \
    router as google_map_scrapper_router
# from app.Accounts.router import router as account_router
from app.core.celery import add
from app.core.data_exporters.export_routers import router as export_routers
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(
    title="Mamuns Scrapers",
    version="1.0",
    docs_url=None,
    redoc_url=None
)

app.include_router(
    google_map_scrapper_router, prefix="/google_map_scrapper", tags=["Scraper"]

    # account_router, prefix="/account",
)
app.include_router(
    export_routers,prefix="/export",tags=['export'],
    # account_router, prefix="/account",
)



@app.get("/", include_in_schema=False)
async def swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="My API Docs"
    )

