"""
Pruebas unitarias del repository de notificaciones.

Se mockea la sesión SQLAlchemy para validar la construcción de consultas
y el contrato del repository sin requerir una base de datos real.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.notification import Notification
from app.repositories.notification_repository import (
    NotificationRepository,
)


def test_notification_repository_create_if_not_exists_inserted():
    db = MagicMock()

    db.execute.return_value.scalar_one_or_none.return_value = (
        "n1"
    )

    db.get.return_value = SimpleNamespace(
        id="n1"
    )

    repository = NotificationRepository(db)

    notification = SimpleNamespace(
        user_id="u1",
        notification_type="calibration_expired",
        title="Expired",
        message="Expired",
        entity_name="Calibration",
        entity_id="c1",
        deduplication_key="dedup-1",
        is_read=None,
        created_at=None,
        read_at=None,
    )

    result = repository.create_if_not_exists(
        notification
    )

    assert result.id == "n1"

    db.execute.assert_called_once()

    db.get.assert_called_once_with(
        Notification,
        "n1",
    )


def test_notification_repository_create_if_not_exists_duplicate():
    db = MagicMock()

    db.execute.return_value.scalar_one_or_none.return_value = (
        None
    )

    repository = NotificationRepository(db)

    notification = SimpleNamespace(
        user_id="u1",
        notification_type="calibration_expired",
        title="Expired",
        message="Expired",
        entity_name="Calibration",
        entity_id="c1",
        deduplication_key="dedup-1",
        is_read=False,
        created_at=datetime.now(timezone.utc),
        read_at=None,
    )

    assert (
        repository.create_if_not_exists(
            notification
        )
        is None
    )

    db.get.assert_not_called()


def test_notification_repository_queries_and_count():
    db = MagicMock()

    scalar_result = MagicMock()

    scalar_result.all.return_value = [
        "n1",
        "n2",
    ]

    db.scalars.return_value = scalar_result

    db.scalar.return_value = 4

    repository = NotificationRepository(db)

    assert (
        repository.get_by_id("n1")
        is db.get.return_value
    )

    assert (
        repository.get_for_user("u1")
        == ["n1", "n2"]
    )

    assert (
        repository.get_for_user(
            "u1",
            unread_only=True,
            limit=10,
        )
        == ["n1", "n2"]
    )

    assert (
        repository.get_active_admins()
        == ["n1", "n2"]
    )

    assert (
        repository.count_unread("u1")
        == 4
    )

    assert db.scalars.call_count == 3

    assert db.scalar.call_count == 1


def test_notification_repository_count_unread_handles_null():
    db = MagicMock()

    db.scalar.return_value = None

    repository = NotificationRepository(db)

    assert (
        repository.count_unread("u1")
        == 0
    )


def test_notification_repository_mark_as_read():
    db = MagicMock()

    repository = NotificationRepository(db)

    notification = SimpleNamespace(
        is_read=False,
        read_at=None,
    )

    read_at = datetime.now(timezone.utc)

    result = repository.mark_as_read(
        notification,
        read_at,
    )

    assert result is notification

    assert notification.is_read is True

    assert notification.read_at == read_at

    db.flush.assert_called_once()

    db.refresh.assert_called_once_with(
        notification
    )