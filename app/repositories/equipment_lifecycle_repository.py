"""
Repository para eventos del ciclo de vida de equipos.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.equipment_lifecycle_event import (
    EquipmentLifecycleEvent,
)


class EquipmentLifecycleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        event: EquipmentLifecycleEvent,
    ) -> EquipmentLifecycleEvent:

        self.db.add(event)
        self.db.flush()
        self.db.refresh(event)

        return event

    def get_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> list[EquipmentLifecycleEvent]:

        return (
            self.db.query(EquipmentLifecycleEvent)
            .filter(EquipmentLifecycleEvent.equipment_id == equipment_id)
            .order_by(EquipmentLifecycleEvent.event_date.desc())
            .all()
        )
