"""
Servicio de auditoría.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction, AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:

    def __init__(self, db: Session):
        self.repository = AuditRepository(db)

    def log(
        self,
        user_id: UUID | None,
        entity_name: str,
        entity_id: str,
        action: AuditAction,
        description: str | None = None,
    ) -> AuditLog:
        """
        Registra un evento de auditoría.
        """

        log = AuditLog(
            user_id=user_id,
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            description=description,
        )

        return self.repository.create(log)

    def get_recent_logs(
        self,
        limit: int = 100,
    ) -> list[AuditLog]:

        return self.repository.get_recent(limit=limit)