"""
Repository para programación de mantenimiento.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.maintenance_schedule import (
    MaintenanceSchedule,
)


class MaintenanceScheduleRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        schedule: MaintenanceSchedule,
    ) -> MaintenanceSchedule:

        self.db.add(schedule)
        self.db.flush()
        self.db.refresh(schedule)

        return schedule

    def get_by_id(
        self,
        schedule_id: UUID,
    ) -> MaintenanceSchedule | None:

        return (
            self.db.query(MaintenanceSchedule)
            .filter(
                MaintenanceSchedule.id == schedule_id
            )
            .first()
        )

    def get_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> list[MaintenanceSchedule]:

        return (
            self.db.query(MaintenanceSchedule)
            .filter(
                MaintenanceSchedule.equipment_id
                == equipment_id
            )
            .order_by(
                MaintenanceSchedule.next_due_date.asc()
            )
            .all()
        )

    def get_due_schedules(
        self,
        current_date,
    ) -> list[MaintenanceSchedule]:

        return (
            self.db.query(MaintenanceSchedule)
            .filter(
                MaintenanceSchedule.is_active.is_(True),
                MaintenanceSchedule.next_due_date
                <= current_date,
            )
            .order_by(
                MaintenanceSchedule.next_due_date.asc()
            )
            .all()
        )

    def update(
        self,
        schedule: MaintenanceSchedule,
    ) -> MaintenanceSchedule:

        self.db.flush()
        self.db.refresh(schedule)

        return schedule