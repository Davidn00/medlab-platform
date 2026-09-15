"""
Endpoints de analytics del laboratorio.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import date, timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import (
    AnalyticsService,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


ANALYTICS_ROLES = [
    UserRole.ADMIN,
    UserRole.TECHNICIAN,
    UserRole.DOCTOR,
]


@router.get(
    "",
    response_model=AnalyticsResponse,
    dependencies=[
        Depends(
            require_roles(
                ANALYTICS_ROLES
            )
        )
    ],
)
def get_analytics(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Obtiene métricas analíticas del laboratorio.

    Si no se especifica un periodo,
    se utiliza la última semana.
    """

    today = date.today()

    if end_date is None:
        end_date = today

    if start_date is None:
        start_date = (
            end_date
            - timedelta(days=6)
        )

    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail=(
                "start_date no puede ser "
                "posterior a end_date."
            ),
        )

    if (
        end_date - start_date
    ).days > 366:
        raise HTTPException(
            status_code=400,
            detail=(
                "El periodo máximo permitido "
                "es de 366 días."
            ),
        )

    service = AnalyticsService(db)

    return service.get_analytics(
        start_date,
        end_date,
    )