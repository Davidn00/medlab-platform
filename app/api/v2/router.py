"""
Router principal de la API v2.

La API v2 se introduce de forma independiente
para mantener compatibilidad con la API v1.
"""

from fastapi import APIRouter


router = APIRouter(
    prefix="/api/v2",
)


@router.get(
    "/version",
    tags=["API"],
)
def api_version():
    """
    Devuelve información sobre la versión de la API.
    """

    return {
        "api_version": "v2",
        "status": "available",
    }