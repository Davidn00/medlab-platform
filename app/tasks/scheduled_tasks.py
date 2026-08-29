"""
Tareas programadas de MedLab Platform.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime, timezone

from app.workers.celery_app import celery_app

@celery_app.task(
    name="medlab.tasks.scheduled_health_check",
)
def scheduled_health_check() -> dict:

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    return {
        "task": "scheduled_health_check",
        "status": "OK",
        "timestamp": now.isoformat(),
    }