"""
Repository para notificaciones.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User, UserRole


class NotificationRepository:
    """Acceso a datos de notificaciones."""

    def __init__(self, db: Session):
        self.db = db

    def create_if_not_exists(
        self,
        notification: Notification,
    ) -> Notification | None:
        """
        Crea una notificación de forma idempotente.

        PostgreSQL garantiza la unicidad mediante
        deduplication_key. Si la notificación ya existe,
        no se inserta una segunda fila.
        """

        statement = (
            insert(Notification)
            .values(
                user_id=notification.user_id,
                notification_type=notification.notification_type,
                title=notification.title,
                message=notification.message,
                entity_name=notification.entity_name,
                entity_id=notification.entity_id,
                deduplication_key=notification.deduplication_key,
                is_read=(
                    notification.is_read
                    if notification.is_read is not None
                    else False
                ),
                created_at=(
                    notification.created_at
                    or datetime.now(timezone.utc)
                ),
                read_at=notification.read_at,
            )
            .on_conflict_do_nothing(
                index_elements=[Notification.deduplication_key]
            )
            .returning(Notification.id)
        )

        notification_id = self.db.execute(statement).scalar_one_or_none()

        if notification_id is None:
            return None

        return self.db.get(Notification, notification_id)

    def get_by_id(
        self,
        notification_id: UUID,
    ) -> Notification | None:
        return self.db.get(Notification, notification_id)

    def get_for_user(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 100,
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )

        if unread_only:
            statement = statement.where(
                Notification.is_read.is_(False)
            )

        return list(self.db.scalars(statement).all())

    def get_active_admins(self) -> list[User]:
        statement = (
            select(User)
            .where(
                User.role == UserRole.ADMIN,
                User.is_active.is_(True),
            )
            .order_by(User.id)
        )

        return list(self.db.scalars(statement).all())

    def count_unread(self, user_id: UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )

        return int(self.db.scalar(statement) or 0)

    def mark_as_read(
        self,
        notification: Notification,
        read_at: datetime,
    ) -> Notification:
        notification.is_read = True
        notification.read_at = read_at

        self.db.flush()
        self.db.refresh(notification)

        return notification

    def search_paginated(
        self,
        *,
        user_id: UUID,
        page: int,
        limit: int,
        unread_only: bool = False,
        created_from=None,
        created_to=None,
        sort_order: str = "desc",
    ) -> tuple[list[Notification], int]:
        """
        Obtiene las notificaciones del usuario
        aplicando paginación y filtros.
        """

        filters = [
            Notification.user_id == user_id
        ]

        if unread_only:
            filters.append(
                Notification.is_read.is_(False)
            )

        if created_from:
            filters.append(
                Notification.created_at
                >= created_from
            )

        if created_to:
            filters.append(
                Notification.created_at
                <= created_to
            )

        count_statement = (
            select(func.count())
            .select_from(Notification)
            .where(*filters)
        )

        total = int(
            self.db.scalar(
                count_statement
            )
            or 0
        )

        ordering = (
            Notification.created_at.asc()
            if sort_order == "asc"
            else Notification.created_at.desc()
        )

        items = list(
            self.db.scalars(
                select(Notification)
                .where(*filters)
                .order_by(
                    ordering,
                    Notification.id,
                )
                .offset(
                    (page - 1) * limit
                )
                .limit(limit)
            ).all()
        )

        return items, total
