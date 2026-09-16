"""
Repository para mantenimiento.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.maintenance import Maintenance


class MaintenanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        maintenance: Maintenance,
    ) -> Maintenance:

        self.db.add(maintenance)
        self.db.flush()
        self.db.refresh(maintenance)

        return maintenance

    def get_by_id(
        self,
        maintenance_id: UUID,
    ) -> Maintenance | None:

        return (
            self.db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
        )

    def get_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> list[Maintenance]:

        return (
            self.db.query(Maintenance)
            .filter(Maintenance.equipment_id == equipment_id)
            .order_by(Maintenance.scheduled_date.desc())
            .all()
        )

    def get_all(self) -> list[Maintenance]:

        return self.db.query(Maintenance).order_by(Maintenance.created_at.desc()).all()

    def update(
        self,
        maintenance: Maintenance,
    ) -> Maintenance:

        self.db.flush()
        self.db.refresh(maintenance)

        return maintenance
