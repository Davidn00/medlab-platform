"""
Schemas para historial y métricas de calibración.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    field_serializer,
)

from app.schemas.calibration import CalibrationResponse


class CalibrationHistoryMetrics(BaseModel):
    """
    Métricas calculadas del historial de calibraciones.
    """

    equipment_id: UUID
    total_calibrations: int
    last_calibration: datetime | None
    next_calibration: datetime | None
    days_overdue: int
    calibration_frequency_days: float | None

    @field_serializer(
        "last_calibration",
        "next_calibration",
    )
    def serialize_datetime(
        self,
        value: datetime | None,
    ) -> str | None:
        """
        Serializa las fechas de las métricas utilizando
        ISO-8601 con offset explícito.
        """

        if value is None:
            return None

        return value.isoformat()


class CalibrationHistoryResponse(BaseModel):
    """
    Respuesta del historial de calibraciones.
    """

    equipment_id: UUID
    calibrations: list[CalibrationResponse]
    metrics: CalibrationHistoryMetrics

    model_config = ConfigDict(
        from_attributes=True,
    )