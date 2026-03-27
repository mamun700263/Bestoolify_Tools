from fastapi import FastAPI

from app.scrapers.google_map.router import \
    router as google_map_scrapper_router
# from app.Accounts.router import router as account_router
from app.core.celery import add
from app.core.data_exporters.export_routers import router as export_routers

app = FastAPI(
    title="playwright google scrapper",
    version="1.0",
)

app.include_router(
    google_map_scrapper_router, prefix="/google_map_scrapper", tags=["Scraper"]

    # account_router, prefix="/account",
)
app.include_router(
    export_routers,prefix="/export",tags=['export'],
    # account_router, prefix="/account",
)



@app.get("/")
def fast_api():
    return {'mamun': 'i am alive'}

# from fastapi import FastAPI
import redis
import os

# app = FastAPI()

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(redis_url)

@app.get("/redis-test")
def test_redis():
    r.set("ping", "pong")
    return {"ping": r.get("ping").decode()}

@app.get("/celery-test")
def celery_test():
    task = add.delay(3, 7)
    return {"task_id": task.id, "status": task.status}