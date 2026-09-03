"""
Tareas asíncronas relacionadas con calibraciones biomédicas.

Autor: David
Proyecto: MedLab Platform
"""

import logging
from app.workers.celery_app import celery_app

from app.db.session import SessionLocal
from app.repositories.calibration_repository import CalibrationRepository
from app.repositories.biomedical_equipment_repository import BiomedicalEquipmentRepository
from app.services.calibration_service import CalibrationService


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

        calibration_service = CalibrationService(
            calibration_repository=calibration_repository,
            equipment_repository=equipment_repository,
        )

        expired = calibration_service.get_expired_calibrations()
        expiring = calibration_service.get_expiring_calibrations(days=days)

        result = {
            "status": "completed",
            "expired_count": len(expired),
            "expiring_count": len(expiring),
            "expired_calibration_ids": [
                str(calibration.id)
                for calibration in expired
            ],
            "expiring_calibration_ids": [
                str(calibration.id)
                for calibration in expiring
            ],
        }

        logger.info(
            "Calibration status check completed: "
            "expired=%s, expiring=%s",
            result["expired_count"],
            result["expiring_count"],
        )

        return result

    except Exception:
        logger.exception(
            "Error checking biomedical calibration status"
        )
        raise

    finally:
        db.close()