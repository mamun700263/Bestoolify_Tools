import json
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List
from celery.result import AsyncResult
from app.core.celery import celery_app
from app.tasks.google_map_scraper import run_scraper
from fastapi.responses import StreamingResponse
router = APIRouter()
from app.core.data_exporters.file_saver import FileSaver

@router.post(
        "/run",
        summary="scrapes google map search results",
        description="similer to google map",
    
        )
def google_map_scrapper_view(
    target: str= Query(
        ...,
        description="Query to search anything.",
        example="cafes in london",
        ),

    ):
    # schedule task in background
    task = run_scraper.delay(target)
    # return immediately
    return {"task_id": task.id, "status": "started"}


@router.get(
        "/status",
        summary="status checker",
        description="Checks if the task has started, pending , or done."
        )
def task_status(
    task_id: str = Query(
        ...,
        description="Enter the task id you got ealier.",
        example="ca3d1cd1-48ae-4bde-b56f-7694c9ff46f6",
    )
    ):
    from celery.result import AsyncResult

    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        return {"status": "done","count":len(task_result.result), "result": task_result.result}
    else:
        return {"status": "pending"}
    
@router.get('/bulk')
def google_map_scraper_bulk(
    topic:str = Query(
        ...,
        description="What are you looking for?",
        example="Cafes",
    
    ),
    places:str= Query(
        ...,
        description="where are you looking for? enter the city names comma separated",
        example="london manchester dhaka tokeyo",
    
    ),
    target:str= Query(
        ...,
        description="What are you looking for?",
        example="Cafes",
    
    ),):
    import time
    
    places = places.split(',')
    data = []
    print(target    )
    for place in places:
        task = run_scraper.delay(f'{topic} in {place}',f'{place}.csv')

        # time.sleep(2)
        k = {
            'place':place,
            'task_id':task.id
        }
        print(k)
        data.append(k)
    FileSaver.save(data,'data_test2/bulk.json')

    return data



class TaskItem(BaseModel):
    place: str
    task_id: str

@router.post("/download_bulk/")
async def task_status(list_of_dict: List[TaskItem]):
    results = []
    for item in list_of_dict:
        try:
            task_result = AsyncResult(item.task_id, app=celery_app)
            if task_result.ready():
                FileSaver.save(task_result.result, f'data_test2/{item.place}.csv')
                results.append({"place": item.place, "status": "done", "count": len(task_result.result)})
            else:
                results.append({"place": item.place, "status": "pending"})
        except Exception as e:
            results.append({"place": item.place, "status": "error", "error": str(e)})

    return {"results": results}