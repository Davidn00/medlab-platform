"""
Repositorio de auditoría.
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

        self.db.add(log)

        self.db.commit()

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