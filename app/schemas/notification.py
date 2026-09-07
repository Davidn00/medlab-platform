"""
Schemas Pydantic para notificaciones.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    """Representación pública de una notificación."""

    id: UUID
    notification_type: NotificationType
    title: str
    message: str
    entity_name: str
    entity_id: str
    is_read: bool
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Respuesta para el listado de notificaciones."""

    items: list[NotificationResponse]
    unread_count: int
