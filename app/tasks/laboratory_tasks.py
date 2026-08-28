"""
Tareas asíncronas de MedLab Platform.

Autor: David
Proyecto: MedLab Platform
"""

from app.workers.celery_app import celery_app


@celery_app.task(
    name="medlab.tasks.test_task",
)
def test_task(name: str) -> str:
    """
    Tarea de prueba para validar la comunicación:

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

    if not name or not name.strip():
        raise ValueError("El nombre no puede estar vacío.")

    return f"Hola {name}, Celery está funcionando correctamente."