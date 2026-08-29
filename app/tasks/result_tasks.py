"""
Tareas Celery para procesamiento de resultados
de laboratorio.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from app.workers.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="medlab.tasks.process_laboratory_result",
)
def process_laboratory_result(
    self,
    test_id: str,
) -> dict:
    """
    Procesa de forma asíncrona el resultado
    de una prueba de laboratorio.
    """

    from app.db.session import SessionLocal
    from app.services.laboratory_result_service import (
        LaboratoryResultService,
    )

    db = SessionLocal()

    try:
        test_uuid = UUID(test_id)

        service = LaboratoryResultService(db)

        test = service.process_result(test_uuid)

        return {
            "test_id": str(test.id),
            "sample_id": str(test.sample_id),
            "status": test.status,
            "result_value": test.result_value,
        }

    finally:
        db.close()