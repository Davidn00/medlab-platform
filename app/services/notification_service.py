"""
Service de notificaciones.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.calibration import Calibration
from app.models.notification import Notification, NotificationType
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    """Lógica de negocio de notificaciones."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationRepository(db)

    def notify_calibration_expired(
        self,
        calibration: Calibration,
    ) -> int:
        """
        Genera una notificación para cada administrador activo.

        La operación es idempotente por usuario y calibración.
        """

        admins = self.repository.get_active_admins()
        created = 0

        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                notification_type=NotificationType.CALIBRATION_EXPIRED,
                title="Calibración vencida",
                message=(
                    "La calibración "
                    f"{calibration.id} del equipo "
                    f"{calibration.equipment_id} está vencida."
                ),
                entity_name="Calibration",
                entity_id=str(calibration.id),
                deduplication_key=(f"calibration:{calibration.id}:expired:{admin.id}"),
            )

            result = self.repository.create_if_not_exists(notification)

            if result is not None:
                created += 1

        return created

    def notify_calibration_expiring(
        self,
        calibration: Calibration,
        days: int,
    ) -> int:
        """
        Genera una alerta de próxima calibración.

        La fecha de próxima calibración forma parte de la clave
        de deduplicación para permitir una nueva alerta si la
        calibración es posteriormente reprogramada.
        """

        admins = self.repository.get_active_admins()
        created = 0

        next_date = calibration.next_calibration_date.isoformat()

        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                notification_type=NotificationType.CALIBRATION_EXPIRING,
                title="Calibración próxima a vencer",
                message=(
                    "La calibración "
                    f"{calibration.id} del equipo "
                    f"{calibration.equipment_id} vencerá el "
                    f"{next_date} (dentro de {days} días o menos)."
                ),
                entity_name="Calibration",
                entity_id=str(calibration.id),
                deduplication_key=(
                    f"calibration:{calibration.id}:expiring:{next_date}:{admin.id}"
                ),
            )

            result = self.repository.create_if_not_exists(notification)

            if result is not None:
                created += 1

        return created

    def get_for_user(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 100,
    ) -> list[Notification]:
        return self.repository.get_for_user(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
        )

    def get_unread_count(self, user_id: UUID) -> int:
        return self.repository.count_unread(user_id)

    def mark_as_read(
        self,
        notification_id: UUID,
        user_id: UUID,
    ) -> Notification | None:
        notification = self.repository.get_by_id(notification_id)

        if notification is None:
            return None

        if notification.user_id != user_id:
            return None

        if notification.is_read:
            return notification

        self.repository.mark_as_read(
            notification,
            datetime.now(UTC),
        )

        self.db.commit()
        self.db.refresh(notification)

        return notification
