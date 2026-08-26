from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "medlab_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Mexico_City",
    enable_utc=True,
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


# Importar las tareas para que Celery las registre.
import app.tasks.laboratory_tasks