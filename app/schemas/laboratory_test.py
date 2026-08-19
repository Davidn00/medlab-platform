"""
Schemas relacionados con pruebas de laboratorio.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.laboratory_test import LabTestStatus


class LaboratoryTestBase(BaseModel):
    """
    Campos comunes de una prueba.
    """

    sample_id: UUID

    test_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    unit: str | None = Field(
        default=None,
        max_length=30,
    )

    reference_range: str | None = Field(
        default=None,
        max_length=100,
    )


class LaboratoryTestCreate(LaboratoryTestBase):
    """
    Datos necesarios para crear una prueba.
    """

    pass


class LaboratoryTestUpdate(BaseModel):
    """
    Actualización parcial de una prueba.
    """

    result_value: str | None = None

    comments: str | None = None

    status: LabTestStatus | None = None


class LaboratoryTestResponse(LaboratoryTestBase):
    """
    Datos que devuelve la API.
    """

    id: UUID

    result_value: str | None

    comments: str | None

    status: LabTestStatus

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )