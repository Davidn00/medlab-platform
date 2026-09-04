
"""
Schemas Pydantic para calibraciones.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.calibration import CalibrationStatus


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

    status: CalibrationStatus = Field(
        default=CalibrationStatus.VALID,
        description="Estado actual de la calibración.",
    )

    notes: str | None = Field(
        default=None,
        description="Observaciones relacionadas con la calibración.",
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        """
        Permite recibir tanto el nombre del enum
        como su valor.

        Ejemplos válidos:
            VALID
            valid
            EXPIRED
            expired
        """

        if isinstance(value, CalibrationStatus):
            return value

        if isinstance(value, str):
            normalized = value.strip().upper()

            try:
                return CalibrationStatus[normalized]
            except KeyError:
                pass

        return value


class CalibrationCreate(CalibrationBase):
    """
    Datos necesarios para crear una calibración.
    """

    pass


class CalibrationUpdate(BaseModel):
    """
    Datos permitidos para actualizar una calibración.
    """

    equipment_id: UUID | None = None

    calibration_date: datetime | None = None

    next_calibration_date: datetime | None = None

    performed_by: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    certificate_number: str | None = Field(
        default=None,
        max_length=100,
    )

    status: CalibrationStatus | None = None

    notes: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        """
        Permite recibir tanto el nombre del enum
        como su valor.
        """

        if value is None:
            return None

        if isinstance(value, CalibrationStatus):
            return value

        if isinstance(value, str):
            normalized = value.strip().upper()

            try:
                return CalibrationStatus[normalized]
            except KeyError:
                pass

        return value


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

