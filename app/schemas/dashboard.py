"""
Schemas del dashboard.

Autor: David
Proyecto: MedLab Platform
"""

from pydantic import (
    BaseModel,
    Field,
)


class DashboardStatisticsResponse(
    BaseModel
):
    """
    Estadísticas principales del laboratorio.
    """

    patients: int = Field(
        ge=0
    )

    samples: int = Field(
        ge=0
    )

    tests: int = Field(
        ge=0
    )

    equipment: int = Field(
        ge=0
    )

    calibrations: int = Field(
        ge=0
    )

    expired_calibrations: int = Field(
        ge=0
    )

    pending_tests: int = Field(
        ge=0
    )