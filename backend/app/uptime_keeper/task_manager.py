import asyncio
from fastapi import FastAPI 
from contextlib import asynccontextmanager
from .scheduler import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(scheduler())
    yield