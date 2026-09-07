"""
Repositorio de auditoría.

Autor: David
Proyecto: MedLab Platform
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        log: AuditLog,
    ) -> AuditLog:
        """
        Persiste un registro de auditoría sin confirmar
        la transacción.

        El commit pertenece al Service que controla la
        operación de negocio.
        """

        self.db.add(log)
        self.db.flush()
        self.db.refresh(log)

        return log

    def get_recent(
        self,
        limit: int = 100,
    ) -> list[AuditLog]:

        statement = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())
