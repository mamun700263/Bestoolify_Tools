from fastapi import FastAPI

from app.scrapers.google_map.router import \
    router as google_map_scrapper_router
# from app.Accounts.router import router as account_router
from app.uptime_keeper.router import router as uptime_keeper
from app.core.data_exporters.export_routers import router as export_routers
from fastapi.openapi.docs import get_swagger_ui_html

from app.uptime_keeper.task_manager import lifespan

app = FastAPI(
    title="Mamuns Scrapers",
    version="1.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan
)

app.include_router(
    google_map_scrapper_router, prefix="/google_map_scrapper", tags=["Scraper"]

    # account_router, prefix="/account",
)
app.include_router(
    export_routers,prefix="/export",tags=['export']
    
)

app.include_router(
    uptime_keeper, prefix="/uptime",tags=['uptime'],

)


@app.get("/", include_in_schema=False)
async def swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="My API Docs"
    )

