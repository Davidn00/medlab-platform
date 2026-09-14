"""
Servicio para programación de mantenimiento.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import EquipmentNotFoundError
from app.models.maintenance_schedule import (
    MaintenanceSchedule,
)
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.maintenance_schedule_repository import (
    MaintenanceScheduleRepository,
)


class MaintenanceScheduleService:

    def __init__(
        self,
        db: Session,
        repository: MaintenanceScheduleRepository,
        equipment_repository: BiomedicalEquipmentRepository,
    ):
        self.db = db
        self.repository = repository
        self.equipment_repository = equipment_repository

    def create(
        self,
        equipment_id,
        name,
        maintenance_type,
        frequency_days,
        next_due_date,
        description,
    ):

        equipment = (
            self.equipment_repository.get_by_id(
                equipment_id
            )
        )

        if equipment is None:
            raise EquipmentNotFoundError(
                "Equipo biomédico no encontrado."
            )

        try:
            schedule = MaintenanceSchedule(
                equipment_id=equipment_id,
                name=name,
                maintenance_type=maintenance_type,
                frequency_days=frequency_days,
                next_due_date=next_due_date,
                description=description,
            )

            self.repository.create(schedule)

            self.db.commit()
            self.db.refresh(schedule)

            return schedule

        except Exception:
            self.db.rollback()
            raise

    def get_by_equipment_id(
        self,
        equipment_id: UUID,
    ):

        equipment = (
            self.equipment_repository.get_by_id(
                equipment_id
            )
        )

        if equipment is None:
            raise EquipmentNotFoundError(
                "Equipo biomédico no encontrado."
            )

        return self.repository.get_by_equipment_id(
            equipment_id
        )