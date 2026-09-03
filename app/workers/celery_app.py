from celery import Celery

from app.core.config import settings
from celery.schedules import crontab


celery_app = Celery(
    "medlab",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# celery_app = Celery(
#     "medlab",
#     broker="redis://redis:6379/0",
#     backend="redis://redis:6379/1",
# )

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Importación explícita de las tareas del proyecto.
#
# La estructura utiliza módulos *_tasks.py en lugar
# del nombre convencional tasks.py de Celery.
import app.tasks.calibration_tasks
import app.tasks.laboratory_tasks
import app.tasks.report_tasks

celery_app.autodiscover_tasks(
    ["app.tasks"]
)


celery_app.conf.beat_schedule = {
    "check-biomedical-calibrations": {
        "task": "medlab.tasks.check_calibration_status",
        "schedule": crontab(minute=0),
        "args": (30,),
    },
}