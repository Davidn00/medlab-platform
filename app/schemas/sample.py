"""
Schemas relacionados con muestras de laboratorio.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.sample import SampleStatus, SampleType


class SampleBase(BaseModel):
    """
    Campos comunes de una muestra.
    """

    patient_id: UUID

    sample_type: SampleType

    sample_code: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )


class SampleCreate(SampleBase):
    """
    Datos necesarios para registrar una muestra.
    """

    pass


class SampleUpdate(BaseModel):
    """
    Actualización parcial de una muestra.
    """

    status: SampleStatus | None = None

    received_at: datetime | None = None


class SampleResponse(SampleBase):
    """
    Datos que devuelve la API.
    """

    id: UUID

    status: SampleStatus

    collected_at: datetime

    received_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )