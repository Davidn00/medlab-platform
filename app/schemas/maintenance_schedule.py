"""
Schemas Pydantic para programación de mantenimiento.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.maintenance import MaintenanceType


class MaintenanceScheduleCreate(BaseModel):

    equipment_id: UUID

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    maintenance_type: MaintenanceType

    frequency_days: int = Field(
        ...,
        ge=1,
    )

    next_due_date: datetime

    description: str | None = None


class MaintenanceScheduleUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    maintenance_type: MaintenanceType | None = None

    frequency_days: int | None = Field(
        default=None,
        ge=1,
    )

    next_due_date: datetime | None = None

    is_active: bool | None = None

    description: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class MaintenanceScheduleResponse(
    BaseModel
):

    id: UUID

    equipment_id: UUID

    name: str

    maintenance_type: MaintenanceType

    frequency_days: int

    next_due_date: datetime

    last_execution_date: datetime | None

    is_active: bool

    description: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )