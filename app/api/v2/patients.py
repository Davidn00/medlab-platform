"""
Endpoints v2 de pacientes.

Incluye:

- paginación
- búsqueda
- filtros
- sorting
- rangos de fecha
"""

from datetime import date
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.pagination import (
    pagination_metadata,
)
from app.repositories.patient_repository import (
    PatientRepository,
)
from app.schemas.pagination import (
    PaginatedResponse,
)
from app.schemas.patient import PatientResponse


router = APIRouter(
    prefix="/patients",
    tags=["Patients v2"],
)


@router.get(
    "",
    response_model=PaginatedResponse[
        PatientResponse
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
def list_patients_v2(
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
    gender: str | None = Query(
        default=None,
        max_length=20,
    ),
    birth_date_from: date | None = None,
    birth_date_to: date | None = None,
    sort_by: Literal[
        "created_at",
        "updated_at",
        "first_name",
        "last_name",
        "birth_date",
    ] = "created_at",
    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repository = PatientRepository(db)

    items, total = repository.search_paginated(
        page=page,
        limit=limit,
        search=search,
        gender=gender,
        birth_date_from=birth_date_from,
        birth_date_to=birth_date_to,
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