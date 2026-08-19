"""
Endpoints simulados del laboratorio.

Se utilizan para demostrar el sistema RBAC.
"""

from fastapi import APIRouter, Depends

from app.core.permissions import require_roles
from app.models.user import User, UserRole


router = APIRouter(
    prefix="/laboratory",
    tags=["Laboratory"],
)


@router.post("/samples")
def register_sample(
    current_user: User = Depends(
        require_roles([
            UserRole.ADMIN,
            UserRole.TECHNICIAN,
        ])
    ),
):
    """
    Registrar una muestra de laboratorio.
    """

    return {
        "message": "Muestra registrada correctamente",
        "registered_by": current_user.full_name,
    }


@router.get("/results")
def get_results(
    current_user: User = Depends(
        require_roles([
            UserRole.ADMIN,
            UserRole.DOCTOR,
        ])
    ),
):
    """
    Consultar resultados de laboratorio.
    """

    return {
        "message": "Resultados disponibles",
        "requested_by": current_user.full_name,
    }