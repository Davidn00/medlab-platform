"""
Endpoints relacionados con tareas asíncronas.

Autor: David
Proyecto: MedLab Platform
"""

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status
from app.schemas.task import TaskRequest, TaskResponse, TaskStatusResponse
from app.tasks.laboratory_tasks import test_task
from app.workers.celery_app import celery_app


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post(
    "/test",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_test_task(payload: TaskRequest) -> TaskResponse:
    """
    Envía una tarea de prueba a Celery.

    La tarea se ejecutará de forma asíncrona
    mediante Celery Worker.
    """

    task = test_task.delay(payload.name)

    return TaskResponse(
        task_id=task.id,
        status=task.status,
    )


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
)
def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Consulta el estado de una tarea Celery.
    """

    task = AsyncResult(
        task_id,
        app=celery_app,
    )

    response = TaskStatusResponse(
        task_id=task_id,
        status=task.status,
    )

    if task.successful():
        response.result = str(task.result)

    elif task.failed():
        response.error = str(task.result)

    return response