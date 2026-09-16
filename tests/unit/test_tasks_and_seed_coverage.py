"""
Cobertura de tareas Celery y del script de inicialización.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.models.laboratory_test import (
    LaboratoryTest,
    LabTestStatus,
    utc_now,
)
from app.tasks.result_tasks import (
    process_laboratory_result,
)
from app.tasks.scheduled_tasks import (
    scheduled_health_check,
)

# ==========================================================
# Scheduled tasks
# ==========================================================


def test_scheduled_health_check_returns_utc_timestamp():
    result = scheduled_health_check.run()

    assert result["task"] == "scheduled_health_check"

    assert result["status"] == "OK"

    assert result["timestamp"].endswith("+00:00")


# ==========================================================
# Result task
# ==========================================================


def test_result_task_processes_test_and_closes_session():
    test = MagicMock()

    test.id = "test-1"
    test.sample_id = "sample-1"
    test.status = "completed"
    test.result_value = "12.5"

    db = MagicMock()

    service = MagicMock()

    service.process_result.return_value = test

    with (
        patch(
            "app.db.session.SessionLocal",
            return_value=db,
        ),
        patch(
            "app.services.laboratory_result_service.LaboratoryResultService",
            return_value=service,
        ),
    ):
        result = process_laboratory_result.run("11111111-1111-1111-1111-111111111111")

    assert result == {
        "test_id": "test-1",
        "sample_id": "sample-1",
        "status": "completed",
        "result_value": "12.5",
    }

    service.process_result.assert_called_once()

    db.close.assert_called_once()


def test_result_task_closes_session_on_invalid_uuid():
    db = MagicMock()

    with patch(
        "app.db.session.SessionLocal",
        return_value=db,
    ):
        with pytest.raises(ValueError):
            process_laboratory_result.run("not-a-uuid")

    db.close.assert_called_once()


# ==========================================================
# LaboratoryTest model
# ==========================================================


def test_laboratory_test_model_and_clock():
    now = utc_now()

    assert now.tzinfo is not None

    assert LabTestStatus.PENDING.value == "pending"

    test = LaboratoryTest(
        sample_id=("11111111-1111-1111-1111-111111111111"),
        test_name="Hemoglobina",
    )

    assert test.status is None
    status_column = LaboratoryTest.__table__.c.status

    assert status_column.default.arg == LabTestStatus.PENDING


# ==========================================================
# Seed
# ==========================================================


def test_seed_admin_existing_user():
    from app import seed

    db = MagicMock()

    existing = MagicMock()

    (db.query.return_value.filter.return_value.first.return_value) = existing

    with (
        patch.object(
            seed,
            "SessionLocal",
            return_value=db,
        ),
        patch.object(
            seed.settings,
            "ADMIN_EMAIL",
            "admin@test.local",
        ),
    ):
        seed.seed_admin()

    db.commit.assert_not_called()

    db.close.assert_called_once()


def test_seed_admin_creates_user():
    from app import seed

    db = MagicMock()

    (db.query.return_value.filter.return_value.first.return_value) = None

    with (
        patch.object(
            seed,
            "SessionLocal",
            return_value=db,
        ),
        patch.object(
            seed.settings,
            "ADMIN_EMAIL",
            "admin@test.local",
        ),
        patch.object(
            seed.settings,
            "ADMIN_FULL_NAME",
            "Admin Test",
        ),
        patch.object(
            seed.settings,
            "ADMIN_PASSWORD",
            "Admin123!SecurePassword",
        ),
    ):
        seed.seed_admin()

    db.add.assert_called_once()

    created = db.add.call_args.args[0]

    assert created.email == "admin@test.local"

    assert created.full_name == "Admin Test"

    assert created.is_active is True

    db.commit.assert_called_once()

    db.refresh.assert_called_once_with(created)

    db.close.assert_called_once()


def test_seed_admin_rolls_back_and_closes_on_failure():
    from app import seed

    db = MagicMock()

    db.query.side_effect = RuntimeError("database unavailable")

    with patch.object(
        seed,
        "SessionLocal",
        return_value=db,
    ):
        with pytest.raises(RuntimeError):
            seed.seed_admin()

    db.rollback.assert_called_once()

    db.close.assert_called_once()
