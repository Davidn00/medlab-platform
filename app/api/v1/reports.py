"""
Endpoints para generación y consulta de reportes clínicos.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.permissions import require_roles
from app.models.user import UserRole
from app.schemas.task import TaskResponse, TaskStatusResponse
from app.tasks.report_tasks import generate_report
from app.workers.celery_app import celery_app


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


REPORT_ROLES = [
    UserRole.ADMIN,
    UserRole.TECHNICIAN,
    UserRole.DOCTOR,
]


@router.post(
    "/sample/{sample_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(require_roles(REPORT_ROLES))
    ],
)
def create_sample_report(
    sample_id: UUID,
) -> TaskResponse:
    """
    Solicita de forma asíncrona la generación del reporte
    PDF correspondiente a una muestra.
    """

    task = generate_report.delay(str(sample_id))

    return TaskResponse(
        task_id=task.id,
        status=task.status,
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(REPORT_ROLES))
    ],
)
def get_report_task_status(
    task_id: str,
) -> TaskStatusResponse:
    """
    Consulta el estado de una tarea de generación de reportes.
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
        response.result = task.result

    elif task.failed():
        response.error = str(task.result)

    return response

