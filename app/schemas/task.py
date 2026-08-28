
"""
Schemas relacionados con tareas asíncronas.

Autor: David
Proyecto: MedLab Platform
"""

from typing import Any

from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    """
    Datos necesarios para crear una tarea.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre utilizado para la tarea de prueba.",
    )


class TaskResponse(BaseModel):
    """
    Respuesta devuelta al crear una tarea.
    """

    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    """
    Estado de una tarea Celery.
    """

    task_id: str
    status: str
    result: Any | None = None
    error: str | None = None

