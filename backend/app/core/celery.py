# app/core/celery.py
import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Read from environment
BROKER_URL = os.getenv("CELERY_BROKER_URL")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "playwrite_tasks", broker=BROKER_URL, backend=RESULT_BACKEND, include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Autodiscover tasks in app/tasks
celery_app.autodiscover_tasks(["app.tasks"])
