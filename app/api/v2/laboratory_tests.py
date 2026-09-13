"""
Endpoints v2 para pruebas de laboratorio.

Incluye:
- paginación
- búsqueda
- filtros
- rangos de fecha
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
from app.models.laboratory_test import LabTestStatus
from app.models.user import User, UserRole
from app.repositories.laboratory_test_repository import (
    LaboratoryTestRepository,
)
from app.repositories.pagination import (
    pagination_metadata,
)
from app.schemas.laboratory_test import (
    LaboratoryTestResponse,
)
from app.schemas.pagination import (
    PaginatedResponse,
)


router = APIRouter(
    prefix="/laboratory-tests",
    tags=["Laboratory Tests v2"],
)


@router.get(
    "",
    response_model=PaginatedResponse[
        LaboratoryTestResponse
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
def list_laboratory_tests_v2(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    sample_id: UUID | None = None,
    status: LabTestStatus | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort_by: Literal[
        "created_at",
        "updated_at",
        "test_name",
        "status",
    ] = "created_at",
    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Lista pruebas de laboratorio utilizando
    paginación, búsqueda, filtros y sorting.
    """

    repository = LaboratoryTestRepository(db)

    items, total = repository.search_paginated(
        page=page,
        limit=limit,
        search=search,
        sample_id=sample_id,
        status=status,
        created_from=created_from,
        created_to=created_to,
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