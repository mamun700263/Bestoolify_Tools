from fastapi import APIRouter
from celery.result import AsyncResult
from app.core.celery import celery_app


from app.core.data_exporters import FileSaver
router = APIRouter()

from fastapi.responses import StreamingResponse
import io, pandas as pd

@router.get("/save_as/{task_id}")
def download_result(task_id: str, format: str = "csv"):
    task_result = AsyncResult(task_id, app=celery_app)
    if not task_result.ready():
        return {"status": "pending"}

    # Convert Celery result (list of dicts) to DataFrame
    data = task_result.result
    df = pd.DataFrame(data)

    buffer = io.BytesIO()
    headers = {}

    if format == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="results.csv"'}
        return StreamingResponse(buffer, media_type="text/csv", headers=headers)

    elif format == "json":
        buffer.write(df.to_json(orient="records", indent=4).encode("utf-8"))
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="results.json"'}
        return StreamingResponse(buffer, media_type="application/json", headers=headers)

    elif format == "excel":
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Results")
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="results.xlsx"'}
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )
    

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
    

@router.get("/api/{task_id}")
def download_api(task_id: str):
    pass
@router.get("/db/{task_id}")
def download_db(task_id: str):
    pass

@router.get("/sheet/{task_id}")
def download_sheet(task_id: str):
    pass