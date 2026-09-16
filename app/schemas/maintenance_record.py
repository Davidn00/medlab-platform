"""
Schemas Pydantic para registros de mantenimiento.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceRecordCreate(BaseModel):
    maintenance_id: UUID

    equipment_id: UUID

    performed_at: datetime

    performed_by: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )

    action: str = Field(
        ...,
        min_length=1,
    )

    findings: str | None = None

    parts_replaced: str | None = None

    notes: str | None = None


class MaintenanceRecordResponse(MaintenanceRecordCreate):
    id: UUID

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
