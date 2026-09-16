"""
Repository para registros de mantenimiento.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.maintenance_record import (
    MaintenanceRecord,
)


class MaintenanceRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        record: MaintenanceRecord,
    ) -> MaintenanceRecord:

        self.db.add(record)
        self.db.flush()
        self.db.refresh(record)

        return record

    def get_by_maintenance_id(
        self,
        maintenance_id: UUID,
    ) -> list[MaintenanceRecord]:

        return (
            self.db.query(MaintenanceRecord)
            .filter(MaintenanceRecord.maintenance_id == maintenance_id)
            .order_by(MaintenanceRecord.performed_at.desc())
            .all()
        )

    def get_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> list[MaintenanceRecord]:

        return (
            self.db.query(MaintenanceRecord)
            .filter(MaintenanceRecord.equipment_id == equipment_id)
            .order_by(MaintenanceRecord.performed_at.desc())
            .all()
        )
