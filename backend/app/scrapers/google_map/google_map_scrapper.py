from fastapi import APIRouter

from app.core.celery import celery_app
from app.tasks.google_map_scraper import run_scraper

router = APIRouter()


@router.post("/run")
def google_map_scrapper_view(target: str, file_type: str):
    # schedule task in background
    task = run_scraper.delay(target, file_type)
    # return immediately
    return {"task_id": task.id, "status": "started"}


@router.get("/status/{task_id}")
def task_status(task_id: str):
    from celery.result import AsyncResult

    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        return {"status": "done", "result": task_result.result}
    else:
        return {"status": "pending"}
