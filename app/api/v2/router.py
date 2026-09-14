"""
Router principal de la API v2.
"""

from fastapi import APIRouter
from app.api.v2 import (
    calibrations,
    equipment,
    laboratory_tests,
    lifecycle,
    maintenance,
    notifications,
    patients,
    samples,
)


router = APIRouter(
    prefix="/api/v2",
)


router.include_router(
    patients.router,
)

router.include_router(
    samples.router,
)

router.include_router(
    laboratory_tests.router,
)

router.include_router(
    equipment.router,
)

router.include_router(
    calibrations.router,
)

router.include_router(
    notifications.router,
)
router.include_router(
    lifecycle.router,
)
router.include_router(
    maintenance.router,
)

@router.get(
    "/version",
    tags=["API"],
)
def api_version():
    return {
        "api_version": "v2",
        "status": "available",
    }

