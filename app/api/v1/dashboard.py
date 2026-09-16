"""
Endpoint de estadísticas generales.

Autor: David
Proyecto: MedLab Platform
"""

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
)
from app.core.permissions import (
    require_roles,
)
from app.db.session import (
    get_db,
)
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.dashboard import (
    DashboardStatisticsResponse,
)
from app.services.dashboard_service import (
    DashboardService,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/statistics",
    response_model=DashboardStatisticsResponse,
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
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Devuelve estadísticas agregadas
    del laboratorio.
    """

    service = DashboardService(db)

    return service.get_statistics()
