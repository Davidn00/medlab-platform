"""
Schemas Pydantic para mantenimiento.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.maintenance import (
    MaintenanceStatus,
    MaintenanceType,
)


class MaintenanceBase(BaseModel):

    equipment_id: UUID

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    maintenance_type: MaintenanceType

    status: MaintenanceStatus = (
        MaintenanceStatus.SCHEDULED
    )

    scheduled_date: datetime | None = None

    description: str | None = None

    assigned_to: str | None = Field(
        default=None,
        max_length=150,
    )


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    maintenance_type: MaintenanceType | None = None

    status: MaintenanceStatus | None = None

    scheduled_date: datetime | None = None

    description: str | None = None

    assigned_to: str | None = Field(
        default=None,
        max_length=150,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )


class MaintenanceResponse(MaintenanceBase):

    id: UUID

    started_at: datetime | None

    completed_at: datetime | None

    created_by: UUID | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )