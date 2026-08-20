
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from app.accounts.router import router as account_router
from app.core.data_exporters.export_routers import router as export_routers
from app.uptime_keeper.routers import router as uptime_keeper
from app.task_manager import lifespan


app = FastAPI(
    title="Tav Tools",
    version="1.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan
)
from fastapi.middleware.cors import CORSMiddleware

# add this after app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://bestoolify-tools.onrender.com",
        "https://monitor.tavdev.com",
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(export_routers, prefix="/export", tags=["export"])
app.include_router(uptime_keeper, prefix="/uptime", tags=["uptime"])
app.include_router(account_router, prefix="/accounts", tags=["Accounts"])


@app.get("/", include_in_schema=False)
async def swagger_ui():
    return get_swagger_ui_html(openapi_url=app.openapi_url, title="Tav Devs API Docs")
