from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import asyncio

from .uptime_keeper.scheduler import scheduler
from app.uptime_keeper.caching.db_to_redis import sync_all_monitors, set_monitor_count
from app.accounts.caching.cache import set_account_count
from sqlalchemy.orm import Session

from app.db import get_db

from app.db.engine import SessionLocal

def sync_db_to_redis():
    db = SessionLocal()

    try:
        sync_all_monitors()
        set_account_count(db)
        set_monitor_count(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):

    # -------------------
    # STARTUP
    # -------------------

    sync_db_to_redis()
    # sync_all_monitors()
    # sync_db_to_redis()
    task = asyncio.create_task(scheduler())
    app.state.scheduler_task = task

    try:
        yield

    finally:
        # -------------------
        # SHUTDOWN
        # -------------------
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            print("[uptime] scheduler stopped")