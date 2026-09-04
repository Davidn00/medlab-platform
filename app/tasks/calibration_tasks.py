"""
Tareas asíncronas relacionadas con calibraciones biomédicas.

Autor: David
Proyecto: MedLab Platform
"""

import logging

from app.db.session import SessionLocal
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.calibration_repository import (
    CalibrationRepository,
)
from app.services.audit_service import AuditService
from app.services.calibration_service import CalibrationService
from app.workers.celery_app import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(
    name="medlab.tasks.check_calibration_status"
)
def check_calibration_status(days: int = 30) -> dict:
    """
    Revisa el estado de las calibraciones de los equipos biomédicos.

    Detecta:
    - calibraciones vencidas;
    - calibraciones próximas a vencer.

    Args:
        days: Número de días utilizados para detectar
              calibraciones próximas a vencer.

    Returns:
        Diccionario serializable con el resultado de la revisión.
    """

    db = SessionLocal()

    try:
        calibration_repository = CalibrationRepository(db)
        equipment_repository = BiomedicalEquipmentRepository(db)
        audit_service = AuditService(db)

        calibration_service = CalibrationService(
            calibration_repository=calibration_repository,
            equipment_repository=equipment_repository,
            db=db,
            audit_service=audit_service,
        )

        expired = (
            calibration_service.get_expired_calibrations()
        )

        expired_count = 0
        already_expired_count = 0
        expired_ids = []

        for calibration in expired:

            changed = calibration_service.expire_calibration(
                calibration,
            )

            if changed:
                expired_count += 1
                expired_ids.append(str(calibration.id))
            else:
                already_expired_count += 1

        expiring = (
            calibration_service.get_expiring_calibrations(
                days=days
            )
        )

        result = {
            "status": "completed",
            "newly_expired_count": expired_count,
            "already_expired_count": already_expired_count,
            "expiring_count": len(expiring),
            "expired_calibration_ids": expired_ids,
            "expiring_calibration_ids": [
                str(calibration.id)
                for calibration in expiring
            ],
        }

        logger.info(
            "Biomedical calibration check completed: %s",
            result,
        )

        return result

    except Exception:
        db.rollback()

        logger.exception(
            "Error processing biomedical calibrations"
        )

        raise

    finally:
        db.close()