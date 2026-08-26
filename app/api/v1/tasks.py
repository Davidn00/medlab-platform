"""
Endpoints para tareas asíncronas.

Autor: David
Proyecto: MedLab Platform
"""

from fastapi import APIRouter

from app.tasks.laboratory_tasks import test_task
from celery.result import AsyncResult
from app.workers.celery_app import celery_app


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post("/test")
def create_test_task(name: str):
    """
    Envía una tarea de prueba a Celery.

    La tarea se ejecutará de forma asíncrona
    mediante Celery Worker.
    """

    task = test_task.delay(name)

    return {
        "task_id": task.id,
        "status": task.status,
    }

@router.get("/{task_id}")
def get_task_status(task_id: str):
    """
    Consulta el estado y resultado de una tarea Celery.
    """

    task = AsyncResult(
        task_id,
        app=celery_app,
    )

    response = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.successful():
        response["result"] = task.result

    if task.failed():
        response["error"] = str(task.result)

    return response