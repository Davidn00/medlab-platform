"""
Schemas Pydantic para calibraciones.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class CalibrationBase(BaseModel):
    """
    Campos comunes de una calibración.
    """

    equipment_id: UUID = Field(
        ...,
        description="UUID del equipo biomédico asociado.",
    )

    calibration_date: datetime = Field(
        ...,
        description="Fecha en la que se realizó la calibración.",
    )

    next_calibration_date: datetime = Field(
        ...,
        description="Fecha programada para la próxima calibración.",
    )

    performed_by: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Persona responsable de realizar la calibración.",
    )

    certificate_number: str | None = Field(
        default=None,
        max_length=100,
        description="Número del certificado de calibración.",
    )

    status: Literal[
        "VALID",
        "CANCELLED",
    ] = "VALID"

    notes: str | None = Field(
        default=None,
        description="Observaciones relacionadas con la calibración.",
    )


class CalibrationCreate(CalibrationBase):
    """
    Datos necesarios para crear una calibración.
    """

    pass


class CalibrationUpdate(BaseModel):
    """
    Datos permitidos para actualizar una calibración.
    """

    equipment_id: UUID | None = Field(
        default=None,
    )

    calibration_date: datetime | None = Field(
        default=None,
    )

    next_calibration_date: datetime | None = Field(
        default=None,
    )

    performed_by: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    certificate_number: str | None = Field(
        default=None,
        max_length=100,
    )

    status: Literal[
        "VALID",
        "CANCELLED",
    ] | None = None

    notes: str | None = None


class CalibrationResponse(CalibrationBase):
    """
    Representación de una calibración devuelta
    por la API.
    """

    id: UUID
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )