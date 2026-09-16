"""
Pruebas unitarias para tareas de notificación.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

from app.tasks.notification_tasks import (
    notify_calibration_expired,
    notify_calibration_expiring,
)


def test_notify_calibration_expired_creates_notifications():
    calibration = MagicMock()
    calibration.status.value = "expired"
    calibration.next_calibration_date = datetime.now(UTC) - timedelta(days=1)

    with patch("app.tasks.notification_tasks.SessionLocal") as session_local:
        db = session_local.return_value

        with patch(
            "app.tasks.notification_tasks.CalibrationRepository"
        ) as repository_class:
            repository = repository_class.return_value
            repository.get_by_id.return_value = calibration

            with patch(
                "app.tasks.notification_tasks.NotificationService"
            ) as service_class:
                service = service_class.return_value
                service.notify_calibration_expired.return_value = 1

                result = notify_calibration_expired.run(
                    "11111111-1111-1111-1111-111111111111"
                )

    assert result["status"] == "completed"
    assert result["notification_type"] == "calibration_expired"
    assert result["created_count"] == 1
    db.commit.assert_called_once()
    db.close.assert_called_once()


def test_notify_calibration_expiring_creates_notifications():
    calibration = MagicMock()
    calibration.status.value = "valid"
    calibration.next_calibration_date = datetime.now(UTC) + timedelta(days=10)

    with patch("app.tasks.notification_tasks.SessionLocal") as session_local:
        db = session_local.return_value

        with patch(
            "app.tasks.notification_tasks.CalibrationRepository"
        ) as repository_class:
            repository = repository_class.return_value
            repository.get_by_id.return_value = calibration

            with patch(
                "app.tasks.notification_tasks.NotificationService"
            ) as service_class:
                service = service_class.return_value
                service.notify_calibration_expiring.return_value = 1

                result = notify_calibration_expiring.run(
                    "11111111-1111-1111-1111-111111111111",
                    30,
                )

    assert result["status"] == "completed"
    assert result["notification_type"] == "calibration_expiring"
    assert result["created_count"] == 1
    db.commit.assert_called_once()
    db.close.assert_called_once()


def test_notify_calibration_expired_missing_calibration():
    with patch("app.tasks.notification_tasks.SessionLocal") as session_local:
        db = session_local.return_value

        with patch(
            "app.tasks.notification_tasks.CalibrationRepository"
        ) as repository_class:
            repository = repository_class.return_value
            repository.get_by_id.return_value = None

            result = notify_calibration_expired.run(
                "11111111-1111-1111-1111-111111111111"
            )

    assert result["status"] == "skipped"
    assert result["reason"] == "calibration_not_found"
    db.commit.assert_not_called()
    db.close.assert_called_once()
