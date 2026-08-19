"""
Schemas Pydantic relacionados con pacientes.

Los schemas se encargan de validar los datos que entran
y salen de nuestra API.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientBase(BaseModel):
    """
    Campos comunes de un paciente.
    """

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    birth_date: date = Field(
        ...,
        description="Fecha de nacimiento del paciente.",
    )

    gender: str = Field(
        ...,
        min_length=1,
        max_length=20,
    )

    medical_record: str = Field(
        ...,
        min_length=3,
        max_length=50,
    )

    email: EmailStr | None = None


class PatientCreate(PatientBase):
    """
    Datos necesarios para crear un paciente.
    """

    pass


class PatientUpdate(BaseModel):
    """
    Datos permitidos para actualizar un paciente.

    Todos los campos son opcionales porque el cliente
    puede modificar solamente una propiedad.
    """

    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    birth_date: date | None = None

    gender: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    email: EmailStr | None = None


class PatientResponse(PatientBase):
    """
    Datos que devolverá la API.
    """

    id: UUID

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )