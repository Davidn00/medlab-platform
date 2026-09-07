"""
Tareas asíncronas de notificaciones.

Autor: David
Proyecto: MedLab Platform
"""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.db.session import SessionLocal
from app.models.calibration import Calibration
from app.repositories.calibration_repository import CalibrationRepository
from app.services.notification_service import NotificationService
from app.workers.celery_app import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(
    name="medlab.tasks.notify_calibration_expired",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def notify_calibration_expired(
    calibration_id: str,
) -> dict:
    """Genera notificaciones para una calibración vencida."""

    db = SessionLocal()

    try:
        repository = CalibrationRepository(db)

        calibration = repository.get_by_id(
            UUID(calibration_id)
        )

        if calibration is None:
            logger.warning(
                "Calibration %s not found for expired notification",
                calibration_id,
            )
            return {
                "status": "skipped",
                "reason": "calibration_not_found",
                "calibration_id": calibration_id,
            }

        now = datetime.now(timezone.utc)

        if (
            calibration.status.value != "expired"
            or calibration.next_calibration_date >= now
        ):
            return {
                "status": "skipped",
                "reason": "calibration_not_expired",
                "calibration_id": calibration_id,
            }

        service = NotificationService(db)

        created_count = service.notify_calibration_expired(
            calibration
        )

        db.commit()

        result = {
            "status": "completed",
            "notification_type": "calibration_expired",
            "calibration_id": calibration_id,
            "created_count": created_count,
        }

        logger.info(
            "Expired calibration notifications processed: %s",
            result,
        )

        return result

    except Exception:
        db.rollback()
        logger.exception(
            "Error creating expired calibration notifications"
        )
        raise

    finally:
        db.close()


@celery_app.task(
    name="medlab.tasks.notify_calibration_expiring",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def notify_calibration_expiring(
    calibration_id: str,
    days: int = 30,
) -> dict:
    """Genera notificaciones para una calibración próxima a vencer."""

    db = SessionLocal()

    try:
        repository = CalibrationRepository(db)

        calibration = repository.get_by_id(
            UUID(calibration_id)
        )

        if calibration is None:
            logger.warning(
                "Calibration %s not found for expiring notification",
                calibration_id,
            )
            return {
                "status": "skipped",
                "reason": "calibration_not_found",
                "calibration_id": calibration_id,
            }

        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=days)

        if (
            calibration.status.value != "valid"
            or calibration.next_calibration_date < now
            or calibration.next_calibration_date > end_date
        ):
            return {
                "status": "skipped",
                "reason": "calibration_not_expiring",
                "calibration_id": calibration_id,
            }

        service = NotificationService(db)

        created_count = service.notify_calibration_expiring(
            calibration,
            days=days,
        )

        db.commit()

        result = {
            "status": "completed",
            "notification_type": "calibration_expiring",
            "calibration_id": calibration_id,
            "created_count": created_count,
        }

        logger.info(
            "Expiring calibration notifications processed: %s",
            result,
        )

        return result

    except Exception:
        db.rollback()
        logger.exception(
            "Error creating expiring calibration notifications"
        )
        raise

    finally:
        db.close()
