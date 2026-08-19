"""
Endpoints de auditoría.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import UserRole
from app.services.audit_service import AuditService


router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


@router.get(
    "/logs",
    dependencies=[
        Depends(
            require_roles(
                [
                    UserRole.ADMIN,
                ]
            )
        )
    ],
)
def get_audit_logs(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    """
    Obtiene los registros de auditoría.
    """

    service = AuditService(db)

    logs = service.get_recent_logs(limit=limit)

    return [
        {
            "id": str(log.id),
            "user_id": (
                str(log.user_id)
                if log.user_id
                else None
            ),
            "entity_name": log.entity_name,
            "entity_id": log.entity_id,
            "action": log.action.value,
            "description": log.description,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]