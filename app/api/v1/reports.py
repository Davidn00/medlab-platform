"""
Endpoints para generación de reportes clínicos.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import UserRole
from app.services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/sample/{sample_id}",
    dependencies=[
        Depends(
            require_roles(
                [
                    UserRole.ADMIN,
                    UserRole.TECHNICIAN,
                    UserRole.DOCTOR,
                ]
            )
        )
    ],
)
def generate_sample_report(
    sample_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Genera un reporte PDF para una muestra.
    """

    service = ReportService(db)

    pdf = service.generate_sample_report(sample_id)

    return StreamingResponse(
        iter([pdf]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"attachment; filename=sample_{sample_id}.pdf"
            )
        },
    )