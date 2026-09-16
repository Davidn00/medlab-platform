"""
Endpoints v2 de muestras.

Incluye filtros y paginación.
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
from app.models.sample import (
    SampleStatus,
    SampleType,
)
from app.models.user import User, UserRole
from app.repositories.pagination import (
    pagination_metadata,
)
from app.repositories.sample_repository import (
    SampleRepository,
)
from app.schemas.pagination import (
    PaginatedResponse,
)
from app.schemas.sample import SampleResponse

router = APIRouter(
    prefix="/samples",
    tags=["Samples v2"],
)


@router.get(
    "",
    response_model=PaginatedResponse[SampleResponse],
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
def list_samples_v2(
    page: int = Query(1, ge=1),
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        None,
        min_length=1,
        max_length=100,
    ),
    patient_id: UUID | None = None,
    status: SampleStatus | None = None,
    sample_type: SampleType | None = None,
    collected_from: datetime | None = None,
    collected_to: datetime | None = None,
    sort_by: Literal[
        "collected_at",
        "sample_code",
        "status",
    ] = "collected_at",
    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repository = SampleRepository(db)

    items, total = repository.search_paginated(
        page=page,
        limit=limit,
        search=search,
        patient_id=patient_id,
        status=status,
        sample_type=sample_type,
        collected_from=collected_from,
        collected_to=collected_to,
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
