import logging

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_failure, task_postrun, task_prerun

from app.core.config import settings

logger = logging.getLogger("medlab.celery")


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
    # ------------------------------------------------------
    # Serialización
    # ------------------------------------------------------
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    task_track_started=True,
    # ------------------------------------------------------
    # Entrega segura de tareas
    # ------------------------------------------------------
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # ------------------------------------------------------
    # Tolerancia ante pérdida temporal de Redis
    # ------------------------------------------------------
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_transport_options={
        "retry_policy": {
            "max_retries": 10,
            "interval_start": 0,
            "interval_step": 2,
            "interval_max": 10,
        },
    },
    # ------------------------------------------------------
    # Reintento de publicación desde productores Celery
    # ------------------------------------------------------
    task_publish_retry=True,
    task_publish_retry_policy={
        "max_retries": 5,
        "interval_start": 0,
        "interval_step": 2,
        "interval_max": 10,
    },
    # ------------------------------------------------------
    # Backend de resultados Redis
    # ------------------------------------------------------
    result_backend_transport_options={
        "retry_policy": {
            "max_retries": 10,
            "interval_start": 0,
            "interval_step": 2,
            "interval_max": 10,
        },
    },
    # ------------------------------------------------------
    # Recuperación de workers
    # ------------------------------------------------------
    worker_max_tasks_per_child=100,
    task_time_limit=300,
    task_soft_time_limit=240,
)


# Importación explícita de las tareas del proyecto.
#
# La estructura utiliza módulos *_tasks.py en lugar
# del nombre convencional tasks.py de Celery.

celery_app.autodiscover_tasks(["app.tasks"])


celery_app.conf.beat_schedule = {
    "check-biomedical-calibrations": {
        "task": "medlab.tasks.check_calibration_status",
        "schedule": crontab(minute=0),
        "args": (30,),
    },
}


@task_prerun.connect
def celery_task_started(
    task_id=None,
    task=None,
    **kwargs,
):
    logger.info(
        "Celery task started | task=%s task_id=%s",
        task.name if task else "unknown",
        task_id,
    )


@task_postrun.connect
def celery_task_finished(
    task_id=None,
    task=None,
    retval=None,
    state=None,
    **kwargs,
):
    logger.info(
        "Celery task finished | task=%s task_id=%s state=%s",
        task.name if task else "unknown",
        task_id,
        state,
    )


@task_failure.connect
def celery_task_failed(
    task_id=None,
    exception=None,
    sender=None,
    **kwargs,
):
    logger.error(
        "Celery task failed | task=%s task_id=%s error=%s",
        sender.name if sender else "unknown",
        task_id,
        exception,
    )
