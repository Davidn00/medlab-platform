from unittest.mock import MagicMock, patch

from app.services.audit_service import AuditService
from app.tasks.calibration_tasks import check_calibration_status

from app.models.audit_log import AuditAction
from app.models.calibration import CalibrationStatus
from app.services.calibration_service import CalibrationService

def test_check_calibration_status():

    expired = [
        MagicMock(id="expired-1"),
    ]

    expiring = [
        MagicMock(id="expiring-1"),
    ]

    with patch(
        "app.tasks.calibration_tasks.SessionLocal"
    ) as session_local:

        db = session_local.return_value

        with patch(
            "app.tasks.calibration_tasks.CalibrationService"
        ) as service_class:

            service = service_class.return_value

            service.get_expired_calibrations.return_value = expired
            service.get_expiring_calibrations.return_value = expiring

            # El task intenta expirar cada calibración.
            service.expire_calibration.return_value = True

            result = check_calibration_status.run(days=30)

    assert result["status"] == "completed"
    assert result["newly_expired_count"] == 1
    assert result["already_expired_count"] == 0
    assert result["expiring_count"] == 1
    assert result["expired_calibration_ids"] == ["expired-1"]
    assert result["expiring_calibration_ids"] == ["expiring-1"]

def test_expire_calibration_is_idempotent():
    calibration = MagicMock()
    calibration.id = "calibration-1"
    calibration.status = CalibrationStatus.VALID

    calibration_repository = MagicMock()
    equipment_repository = MagicMock()
    db = MagicMock()
    audit_service = MagicMock()

    service = CalibrationService(
        calibration_repository=calibration_repository,
        equipment_repository=equipment_repository,
        db=db,
        audit_service=audit_service,
    )

    first_result = service.expire_calibration(
        calibration,
    )

    calibration.status = CalibrationStatus.EXPIRED

    second_result = service.expire_calibration(
        calibration,
    )

    assert first_result is True
    assert second_result is False

    calibration_repository.update_status.assert_called_once()

    audit_service.log.assert_called_once_with(
        user_id=None,
        entity_name="Calibration",
        entity_id="calibration-1",
        action=AuditAction.STATUS_CHANGED,
        description=(
            "Estado de calibración cambiado de "
            "'valid' a 'expired'."
        ),
    )

    db.commit.assert_called_once()