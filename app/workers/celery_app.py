from celery import Celery

from app.core.config import settings
from celery.schedules import crontab


celery_app = Celery(
    "medlab_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    #timezone="America/Mexico_City",
    result_expires=3600,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


celery_app.autodiscover_tasks(
    [
        "app.tasks",
    ]
)

celery_app.conf.beat_schedule = {
    "scheduled-health-check": {
        "task": "medlab.tasks.scheduled_health_check",
        "schedule": crontab(minute="*/5"),
    },
}

# Importar las tareas para que Celery las registre. 
import app.tasks.laboratory_tasks 
import app.tasks.report_tasks
import app.tasks.result_tasks
import app.tasks.scheduled_tasks