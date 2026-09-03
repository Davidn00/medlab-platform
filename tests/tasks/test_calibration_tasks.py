from unittest.mock import MagicMock, patch

from app.tasks.calibration_tasks import check_calibration_status


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
            "app.tasks.calibration_tasks.CalibrationRepository"
        ) as calibration_repository:

            with patch(
                "app.tasks.calibration_tasks.BiomedicalEquipmentRepository"
            ) as equipment_repository:

                with patch(
                    "app.tasks.calibration_tasks.CalibrationService"
                ) as service_class:

                    service = service_class.return_value

                    service.get_expired_calibrations.return_value = expired
                    service.get_expiring_calibrations.return_value = expiring

                    result = check_calibration_status.run(days=30)

    assert result["status"] == "completed"
    assert result["expired_count"] == 1
    assert result["expiring_count"] == 1
    assert result["expired_calibration_ids"] == ["expired-1"]
    assert result["expiring_calibration_ids"] == ["expiring-1"]