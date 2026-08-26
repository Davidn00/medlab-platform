"""
Tareas asíncronas de MedLab Platform.

Contiene las tareas que serán ejecutadas por Celery Worker.

Autor: David
Proyecto: MedLab Platform
"""

from app.workers.celery_app import celery_app


@celery_app.task(
    name="medlab.tasks.test_task",
)
def test_task(name: str) -> str:
    """
    Tarea de prueba para validar la infraestructura
    FastAPI → Redis → Celery Worker.

    Parameters
    ----------
    name:
        Nombre utilizado para la prueba.

    Returns
    -------
    str
        Mensaje generado por el Worker.
    """

    message = f"Hola {name}, Celery está funcionando correctamente."

    return message
