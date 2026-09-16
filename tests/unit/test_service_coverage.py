"""
Pruebas unitarias de reglas de negocio con repositorios aislados.

Estas pruebas complementan las pruebas HTTP existentes y cubren
ramas de negocio sin depender de Redis, Celery ni PostgreSQL.
"""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.exceptions import (
    EquipmentNotFoundError,
    InvalidCalibrationDatesError,
)
from app.models.calibration import CalibrationStatus
from app.models.notification import NotificationType
from app.services.calibration_service import CalibrationService
from app.services.notification_service import NotificationService
from app.services.report_service import ReportService


def _calibration():
    return SimpleNamespace(
        id="cal-1",
        equipment_id="eq-1",
        calibration_date=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        next_calibration_date=datetime(
            2026,
            2,
            1,
            tzinfo=UTC,
        ),
        status=CalibrationStatus.VALID,
    )


# ==========================================================
# ReportService
# ==========================================================


def test_report_service_rejects_unknown_sample():
    repository = MagicMock()
    repository.get_by_id.return_value = None

    service = ReportService(MagicMock())
    service.sample_repository = repository

    with pytest.raises(HTTPException) as exc:
        service.generate_sample_report("sample-1")

    assert exc.value.status_code == 404

    repository.get_by_id.assert_called_once_with("sample-1")


def test_report_service_generates_pdf_with_and_without_result_values():
    patient = SimpleNamespace(
        first_name="Ana",
        last_name="García",
        medical_record="MR-001",
        birth_date=datetime(1990, 5, 10).date(),
        gender="F",
        email="ana.garcia@example.com",
    )

    tests = [
        SimpleNamespace(
            id="test-1",
            test_name="Hemoglobina",
            result_value="13.5",
            unit="g/dL",
            reference_range="12-16",
            status=SimpleNamespace(value="completed"),
            equipment=None,
        ),
        SimpleNamespace(
            id="test-2",
            test_name="Observación",
            result_value=None,
            unit=None,
            reference_range=None,
            status=SimpleNamespace(value="pending"),
            equipment=None,
        ),
    ]

    sample = SimpleNamespace(
        id="sample-1",
        patient=patient,
        laboratory_tests=tests,
        sample_code="S-001",
        sample_type=SimpleNamespace(value="blood"),
        status=SimpleNamespace(value="received"),
        collected_at=datetime(
            2026,
            1,
            20,
            12,
            30,
            tzinfo=UTC,
        ),
        received_at=datetime(
            2026,
            1,
            20,
            13,
            0,
            tzinfo=UTC,
        ),
        equipment=None,
    )

    repository = MagicMock()
    repository.get_by_id.return_value = sample

    service = ReportService(MagicMock())
    service.sample_repository = repository

    pdf = service.generate_sample_report("sample-1")

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000

    repository.get_by_id.assert_called_once_with("sample-1")


# ==========================================================
# NotificationService
# ==========================================================


def test_notification_service_creates_only_new_expired_notifications():
    db = MagicMock()
    repository = MagicMock()

    admins = [
        SimpleNamespace(id="admin-1"),
        SimpleNamespace(id="admin-2"),
    ]

    repository.get_active_admins.return_value = admins

    repository.create_if_not_exists.side_effect = [
        MagicMock(),
        None,
    ]

    service = NotificationService(db)
    service.repository = repository

    calibration = _calibration()

    created = service.notify_calibration_expired(calibration)

    assert created == 1

    assert repository.create_if_not_exists.call_count == 2

    first = repository.create_if_not_exists.call_args_list[0].args[0]

    assert first.notification_type == NotificationType.CALIBRATION_EXPIRED

    assert first.user_id == "admin-1"


def test_notification_service_creates_expiring_notifications():
    db = MagicMock()
    repository = MagicMock()

    repository.get_active_admins.return_value = [
        SimpleNamespace(id="admin-1"),
    ]

    repository.create_if_not_exists.return_value = MagicMock()

    service = NotificationService(db)
    service.repository = repository

    calibration = _calibration()

    created = service.notify_calibration_expiring(
        calibration,
        30,
    )

    assert created == 1

    notification = repository.create_if_not_exists.call_args.args[0]

    assert notification.notification_type == NotificationType.CALIBRATION_EXPIRING

    assert "30 días o menos" in notification.message

    assert "expiring:2026-02-01" in notification.deduplication_key


def test_notification_service_delegates_queries():
    db = MagicMock()
    repository = MagicMock()

    service = NotificationService(db)
    service.repository = repository

    repository.get_for_user.return_value = ["n1"]

    repository.count_unread.return_value = 3

    assert service.get_for_user(
        "u1",
        unread_only=True,
        limit=10,
    ) == ["n1"]

    assert service.get_unread_count("u1") == 3

    repository.get_for_user.assert_called_once_with(
        user_id="u1",
        unread_only=True,
        limit=10,
    )

    repository.count_unread.assert_called_once_with("u1")


def test_notification_service_mark_as_read_branches():
    db = MagicMock()
    repository = MagicMock()

    service = NotificationService(db)
    service.repository = repository

    # No existe.
    repository.get_by_id.return_value = None

    assert (
        service.mark_as_read(
            "n1",
            "u1",
        )
        is None
    )

    # Pertenece a otro usuario.
    other = SimpleNamespace(
        user_id="u2",
        is_read=False,
    )

    repository.get_by_id.return_value = other

    assert (
        service.mark_as_read(
            "n1",
            "u1",
        )
        is None
    )

    # Ya estaba leída.
    already = SimpleNamespace(
        user_id="u1",
        is_read=True,
    )

    repository.get_by_id.return_value = already

    assert (
        service.mark_as_read(
            "n1",
            "u1",
        )
        is already
    )

    # Pendiente de lectura.
    unread = SimpleNamespace(
        user_id="u1",
        is_read=False,
    )

    repository.get_by_id.return_value = unread
    repository.mark_as_read.return_value = unread

    assert (
        service.mark_as_read(
            "n1",
            "u1",
        )
        is unread
    )

    repository.mark_as_read.assert_called_once()

    db.refresh.assert_called_once_with(unread)


# ==========================================================
# CalibrationService
# ==========================================================


def test_calibration_service_create_validates_equipment_and_dates():
    repo = MagicMock()
    equipment_repo = MagicMock()
    db = MagicMock()

    # CalibrationService.create() utiliza la sesión del repositorio.
    repo.db = db

    service = CalibrationService(
        repo,
        equipment_repo,
        db=db,
    )

    data = SimpleNamespace(
        equipment_id="eq-1",
        calibration_date=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        next_calibration_date=datetime(
            2026,
            2,
            1,
            tzinfo=UTC,
        ),
        performed_by="Technician",
        certificate_number="CERT-1",
        status=CalibrationStatus.VALID,
        notes="OK",
    )

    equipment_repo.get_by_id.return_value = SimpleNamespace(id="eq-1")

    created = SimpleNamespace(id="cal-1")

    repo.create.return_value = created

    assert service.create(data) is created
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created)


def test_calibration_service_create_rejects_missing_equipment_and_bad_dates():
    repo = MagicMock()
    equipment_repo = MagicMock()
    db = MagicMock()

    # El servicio obtiene la sesión transaccional desde el repositorio.
    repo.db = db

    service = CalibrationService(
        repo,
        equipment_repo,
        db=db,
    )

    data = SimpleNamespace(
        equipment_id="missing",
        calibration_date=datetime(
            2026,
            2,
            1,
            tzinfo=UTC,
        ),
        next_calibration_date=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        performed_by="Technician",
        certificate_number=None,
        status=CalibrationStatus.VALID,
        notes=None,
    )

    equipment_repo.get_by_id.return_value = None

    with pytest.raises(EquipmentNotFoundError):
        service.create(data)

    equipment_repo.get_by_id.assert_called_once_with("missing")

    equipment_repo.get_by_id.return_value = SimpleNamespace(id="eq-1")

    with pytest.raises(InvalidCalibrationDatesError):
        service.create(data)

    assert db.rollback.call_count == 2


def test_calibration_service_queries_and_expiration_window():
    repo = MagicMock()
    equipment_repo = MagicMock()

    service = CalibrationService(
        repo,
        equipment_repo,
        db=MagicMock(),
    )

    calibration = _calibration()

    repo.get_by_id.return_value = calibration
    equipment_repo.get_by_id.return_value = SimpleNamespace(id="eq-1")

    repo.get_all.return_value = [calibration]

    repo.get_by_equipment_id.return_value = [calibration]

    repo.get_expiring_calibrations.return_value = [calibration]

    repo.get_expired_calibrations.return_value = [calibration]

    assert service.get_by_id("c1") is calibration

    assert service.get_all() == [calibration]

    assert service.get_by_equipment_id("eq-1") == [calibration]

    assert service.get_expiring_calibrations(30) == [calibration]

    assert service.get_expired_calibrations() == [calibration]

    with pytest.raises(ValueError):
        service.get_expiring_calibrations(0)

    equipment_repo.get_by_id.return_value = None

    with pytest.raises(EquipmentNotFoundError):
        service.get_by_equipment_id("missing")


def test_calibration_service_update_delete_and_expire():
    repo = MagicMock()
    equipment_repo = MagicMock()
    db = MagicMock()
    audit = MagicMock()

    repo.db = db

    service = CalibrationService(
        repo,
        equipment_repo,
        db=db,
        audit_service=audit,
    )

    # UPDATE: calibración inexistente.
    repo.get_by_id.return_value = None

    assert (
        service.update(
            "missing",
            MagicMock(model_dump=lambda **_: {}),
        )
        is None
    )

    # DELETE: calibración inexistente.
    assert service.delete("missing") is False

    # UPDATE: operación válida.
    calibration = _calibration()

    repo.get_by_id.return_value = calibration

    equipment_repo.get_by_id.return_value = SimpleNamespace(id="eq-2")

    repo.update.return_value = calibration

    update = MagicMock()

    update.model_dump.return_value = {"equipment_id": "eq-2"}

    assert (
        service.update(
            "c1",
            update,
        )
        is calibration
    )
    repo.update.assert_called_once()

    # DELETE: operación válida.
    repo.delete.reset_mock()

    assert service.delete("c1") is True

    repo.delete.assert_called_once_with(calibration)

    # EXPIRACIÓN.
    audit.reset_mock()

    calibration.status = CalibrationStatus.VALID

    def update_status_side_effect(calibration_obj, status):
        calibration_obj.status = status
        return calibration_obj

    repo.update_status.side_effect = update_status_side_effect

    assert (
        service.expire_calibration(
            calibration,
            user_id="u1",
        )
        is True
    )

    audit.log.assert_called_once()

    # Idempotencia.
    assert (
        service.expire_calibration(
            calibration,
            user_id="u1",
        )
        is False
    )
    # Error transaccional.
    db.commit.side_effect = RuntimeError("db failure")

    calibration.status = CalibrationStatus.VALID

    with pytest.raises(RuntimeError):
        service.expire_calibration(calibration)

    db.rollback.assert_called()


def test_calibration_date_validation_is_strict():
    start = datetime.now(UTC)

    with pytest.raises(InvalidCalibrationDatesError):
        CalibrationService._validate_dates(
            start,
            start,
        )

    with pytest.raises(InvalidCalibrationDatesError):
        CalibrationService._validate_dates(
            start,
            start - timedelta(seconds=1),
        )
