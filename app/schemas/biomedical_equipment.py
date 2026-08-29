"""
Schemas Pydantic para equipos biomédicos.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class BiomedicalEquipmentBase(BaseModel):
    """
    Campos comunes de un equipo biomédico.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nombre identificativo del equipo.",
    )

    manufacturer: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Fabricante del equipo.",
    )

    model: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Modelo del equipo.",
    )

    serial_number: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Número de serie único del equipo.",
    )

    location: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Ubicación física del equipo.",
    )

    status: Literal[
        "ACTIVE",
        "INACTIVE",
        "MAINTENANCE",
        "RETIRED",
    ] = "ACTIVE"



class BiomedicalEquipmentCreate(
    BiomedicalEquipmentBase
):
    """
    Datos necesarios para crear un equipo biomédico.
    """

    pass


class BiomedicalEquipmentUpdate(BaseModel):
    """
    Datos permitidos para actualizar un equipo.

    Todos los campos son opcionales para permitir
    actualizaciones parciales.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    manufacturer: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    serial_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    status: Literal[
        "ACTIVE",
        "INACTIVE",
        "MAINTENANCE",
        "RETIRED",
    ] | None = None


class BiomedicalEquipmentResponse(
    BiomedicalEquipmentBase
):
    """
    Representación de un equipo biomédico
    devuelto por la API.
    """

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )