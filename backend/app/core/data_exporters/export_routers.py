from celery.result import AsyncResult
from fastapi import APIRouter

from app.core.celery import celery_app
from app.core.data_exporters import FileSaver

router = APIRouter()

import io

import pandas as pd
from fastapi.responses import StreamingResponse
from app.core.data_exporters.download_able import export_to_download

@router.get("/save_as/{task_id}")
def download_result(task_id: str, format: str = "csv"):
    task_result = AsyncResult(task_id, app=celery_app)
    if not task_result.ready():
        return {"status": "pending"}

    # Convert Celery result (list of dicts) to DataFrame
    data = task_result.result
    return export_to_download(data,format)

# @router.get("/csv/{task_id}")
# def download_csv(task_id: str,name_of_file):
#     task_result = AsyncResult(task_id, app=celery_app)
#     if task_result.ready():
#         return {"status": "done", "result": task_result.result}
#     else:
#         return {"status": "pending"}

# @router.get("/json/{task_id}")
# def download_json(task_id: str):
#     task_result = AsyncResult(task_id, app=celery_app)
#     if task_result.ready():
#         return {"status": "done", "result": task_result.result}
#     else:
#         return {"status": "pending"}


# @router.get("/xlsx/{task_id}")
# def download_xlsx(task_id: str):
#     task_result = AsyncResult(task_id, app=celery_app)
#     if task_result.ready():
#         return {"status": "done", "result": task_result.result}
#     else:
#         return {"status": "pending"}


# @router.get("/api/{task_id}")
# def download_api(task_id: str):
#     pass


# @router.get("/db/{task_id}")
# def download_db(task_id: str):
#     pass


# @router.get("/sheet/{task_id}")
# def download_sheet(task_id: str):
#     pass
