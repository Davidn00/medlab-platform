"""
Endpoints de exportación de información.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.export import (
    ExportFormat,
    ExportResource,
)
from app.services.export_service import ExportService

router = APIRouter(
    prefix="/exports",
    tags=["Exports"],
)


EXPORT_ROLES = [
    UserRole.ADMIN,
    UserRole.TECHNICIAN,
    UserRole.DOCTOR,
]


@router.get(
    "/{resource}",
    dependencies=[Depends(require_roles(EXPORT_ROLES))],
)
def export_resource(
    resource: ExportResource,
    format: ExportFormat = Query(default=ExportFormat.JSON),
    ids: list[UUID] | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Exporta información seleccionada
    en CSV, Excel, PDF o JSON.
    """

    service = ExportService(db)

    try:
        records = service.get_records(
            resource.value,
            ids,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if format == ExportFormat.JSON:
        content = service.to_json(records)

        return Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition": (f'attachment; filename="{resource.value}.json"')
            },
        )

    if format == ExportFormat.CSV:
        content = service.to_csv(records)

        return Response(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition": (f'attachment; filename="{resource.value}.csv"')
            },
        )

    if format == ExportFormat.XLSX:
        content = service.to_xlsx(records)

        return Response(
            content=content,
            media_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (f'attachment; filename="{resource.value}.xlsx"')
            },
        )

    if format == ExportFormat.PDF:
        content = service.to_pdf(records)

        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (f'attachment; filename="{resource.value}.pdf"')
            },
        )

    raise HTTPException(
        status_code=400,
        detail="Formato de exportación no soportado.",
    )
