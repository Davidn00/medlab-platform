
"""
Endpoints v2 para notificaciones.

Incluye:
- paginación
- filtro de no leídas
- rangos de fecha
- sorting

Las notificaciones pertenecen al usuario autenticado.

Los endpoints v1 permanecen sin cambios.
"""

from datetime import datetime
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.notification_repository import (
    NotificationRepository,
)
from app.repositories.pagination import (
    pagination_metadata,
)
from app.schemas.notification import (
    NotificationResponse,
)
from app.schemas.pagination import (
    PaginatedResponse,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications v2"],
)


@router.get(
    "",
    response_model=PaginatedResponse[
        NotificationResponse
    ],
)
def list_notifications_v2(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    unread_only: bool = Query(
        default=False,
    ),
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista las notificaciones del usuario autenticado.

    Incluye paginación, filtro de no leídas,
    rangos de fecha y ordenamiento.
    """

    repository = NotificationRepository(db)

    items, total = repository.search_paginated(
        user_id=current_user.id,
        page=page,
        limit=limit,
        unread_only=unread_only,
        created_from=created_from,
        created_to=created_to,
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

