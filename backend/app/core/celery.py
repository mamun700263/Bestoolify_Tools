import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

BROKER_URL = os.getenv("CELERY_BROKER_URL")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "playwrite_tasks",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    broker_pool_limit=5,
    redis_max_connections=10,
    broker_connection_timeout=10,

    broker_transport_options={
        "visibility_timeout": 3600,
        "fanout_prefix": True,
        "fanout_patterns": True,
    },

    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
)