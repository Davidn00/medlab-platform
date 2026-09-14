
"""
Endpoints v2 para calibraciones.

Incluye:
- paginación
- búsqueda
- filtros por estado
- filtro por equipo
- rangos de fechas
- sorting

Los endpoints v1 permanecen sin cambios.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.calibration import CalibrationStatus
from app.models.user import User, UserRole
from app.repositories.calibration_repository import (
    CalibrationRepository,
)
from app.repositories.pagination import (
    pagination_metadata,
)
from app.schemas.calibration import (
    CalibrationResponse,
)
from app.schemas.pagination import (
    PaginatedResponse,
)
from fastapi import HTTPException

from app.core.exceptions import (
    EquipmentNotFoundError,
)

from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)

from app.schemas.calibration_history import (
    CalibrationHistoryResponse,
)

from app.services.calibration_history_service import (
    CalibrationHistoryService,
)

router = APIRouter(
    prefix="/calibrations",
    tags=["Calibrations v2"],
)


@router.get(
    "",
    response_model=PaginatedResponse[
        CalibrationResponse
    ],
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
def list_calibrations_v2(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    status: CalibrationStatus | None = None,
    equipment_id: UUID | None = None,
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    calibration_from: datetime | None = None,
    calibration_to: datetime | None = None,
    next_calibration_from: datetime | None = None,
    next_calibration_to: datetime | None = None,
    sort_by: Literal[
        "calibration_date",
        "next_calibration_date",
        "created_at",
        "status",
    ] = "calibration_date",
    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Lista calibraciones utilizando paginación,
    búsqueda, filtros, rangos de fecha y sorting.
    """

    repository = CalibrationRepository(db)

    items, total = repository.search_paginated(
        page=page,
        limit=limit,
        status=status,
        equipment_id=equipment_id,
        search=search,
        calibration_from=calibration_from,
        calibration_to=calibration_to,
        next_calibration_from=next_calibration_from,
        next_calibration_to=next_calibration_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return {
        "items": items,
        **pagination_metadata(
            total,
            page,
            limit,
        ),
    }

@router.get(
    "/equipment/{equipment_id}/history",
    response_model=CalibrationHistoryResponse,
)
def get_calibration_history(
    equipment_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Obtiene el historial completo de calibraciones
    de un equipo junto con sus métricas.
    """

    equipment_repository = BiomedicalEquipmentRepository(db)

    calibration_repository = CalibrationRepository(db)

    service = CalibrationHistoryService(
        equipment_repository=equipment_repository,
        calibration_repository=calibration_repository,
    )

    try:
        history = service.get_history(
            equipment_id
        )

        return CalibrationHistoryResponse(
            equipment_id=history["equipment_id"],
            calibrations=history["calibrations"],
            metrics=history["metrics"],
        )

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc