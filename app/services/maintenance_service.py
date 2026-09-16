"""
Servicio de mantenimiento de equipos biomédicos.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import EquipmentNotFoundError
from app.models.audit_log import AuditAction
from app.models.biomedical_equipment import (
    EquipmentStatus,
)
from app.models.equipment_lifecycle_event import (
    EquipmentEventType,
    EquipmentLifecycleEvent,
)
from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)
from app.models.maintenance_record import MaintenanceRecord
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.equipment_lifecycle_repository import (
    EquipmentLifecycleRepository,
)
from app.repositories.maintenance_record_repository import (
    MaintenanceRecordRepository,
)
from app.repositories.maintenance_repository import (
    MaintenanceRepository,
)
from app.services.audit_service import AuditService


class MaintenanceService:
    def __init__(
        self,
        db: Session,
        maintenance_repository: MaintenanceRepository,
        record_repository: MaintenanceRecordRepository,
        equipment_repository: BiomedicalEquipmentRepository,
        lifecycle_repository: EquipmentLifecycleRepository,
    ):
        self.db = db
        self.maintenance_repository = maintenance_repository
        self.record_repository = record_repository
        self.equipment_repository = equipment_repository
        self.lifecycle_repository = lifecycle_repository
        self.audit_service = AuditService(db)

    def create(
        self,
        equipment_id: UUID,
        title: str,
        maintenance_type,
        status,
        scheduled_date,
        description,
        assigned_to,
        user_id: UUID | None,
    ) -> Maintenance:

        equipment = self.equipment_repository.get_by_id(equipment_id)

        if equipment is None:
            raise EquipmentNotFoundError("Equipo biomédico no encontrado.")

        try:
            maintenance = Maintenance(
                equipment_id=equipment_id,
                title=title,
                maintenance_type=maintenance_type,
                status=status,
                scheduled_date=scheduled_date,
                description=description,
                assigned_to=assigned_to,
                created_by=user_id,
            )

            self.maintenance_repository.create(maintenance)

            if status == MaintenanceStatus.IN_PROGRESS:
                previous_status = equipment.status

                equipment.status = EquipmentStatus.MAINTENANCE

                equipment_event = EquipmentLifecycleEvent(
                    equipment_id=equipment_id,
                    event_type=(EquipmentEventType.MAINTENANCE),
                    description=("Equipo puesto en mantenimiento."),
                    performed_by=assigned_to,
                    reference_id=maintenance.id,
                    previous_status=(previous_status.value),
                    new_status=(EquipmentStatus.MAINTENANCE.value),
                )

                self.lifecycle_repository.create(equipment_event)

            self.audit_service.log(
                user_id=user_id,
                entity_name="Maintenance",
                entity_id=str(maintenance.id),
                action=AuditAction.CREATE,
                description=(f"Mantenimiento creado: {title}."),
            )

            self.db.commit()
            self.db.refresh(maintenance)

            return maintenance

        except Exception:
            self.db.rollback()
            raise

    def get_by_id(
        self,
        maintenance_id: UUID,
    ) -> Maintenance | None:

        return self.maintenance_repository.get_by_id(maintenance_id)

    def get_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> list[Maintenance]:

        equipment = self.equipment_repository.get_by_id(equipment_id)

        if equipment is None:
            raise EquipmentNotFoundError("Equipo biomédico no encontrado.")

        return self.maintenance_repository.get_by_equipment_id(equipment_id)

    def get_all(self) -> list[Maintenance]:

        return self.maintenance_repository.get_all()

    def update_status(
        self,
        maintenance_id: UUID,
        new_status: MaintenanceStatus,
        user_id: UUID | None,
    ) -> Maintenance | None:

        maintenance = self.maintenance_repository.get_by_id(maintenance_id)

        if maintenance is None:
            return None

        equipment = self.equipment_repository.get_by_id(maintenance.equipment_id)

        if equipment is None:
            raise EquipmentNotFoundError("Equipo biomédico no encontrado.")

        old_status = MaintenanceStatus(maintenance.status)

        try:
            maintenance.status = new_status

            now = datetime.now(UTC)

            if new_status == MaintenanceStatus.IN_PROGRESS:
                maintenance.started_at = now
                equipment.status = EquipmentStatus.MAINTENANCE

            elif new_status == MaintenanceStatus.COMPLETED:
                maintenance.completed_at = now

                equipment.status = EquipmentStatus.ACTIVE

            self.maintenance_repository.update(maintenance)

            self.audit_service.log(
                user_id=user_id,
                entity_name="Maintenance",
                entity_id=str(maintenance.id),
                action=AuditAction.STATUS_CHANGED,
                description=(
                    f"Estado cambiado de {old_status.value} a {new_status.value}."
                ),
            )

            self.db.commit()
            self.db.refresh(maintenance)

            return maintenance

        except Exception:
            self.db.rollback()
            raise

    def create_record(
        self,
        maintenance_id: UUID,
        equipment_id: UUID,
        performed_at,
        performed_by,
        action,
        findings,
        parts_replaced,
        notes,
        user_id: UUID | None,
    ) -> MaintenanceRecord:

        maintenance = self.maintenance_repository.get_by_id(maintenance_id)

        if maintenance is None:
            raise ValueError("Mantenimiento no encontrado.")

        if maintenance.equipment_id != equipment_id:
            raise ValueError("El mantenimiento no pertenece al equipo indicado.")

        try:
            record = MaintenanceRecord(
                maintenance_id=maintenance_id,
                equipment_id=equipment_id,
                performed_at=performed_at,
                performed_by=performed_by,
                action=action,
                findings=findings,
                parts_replaced=parts_replaced,
                notes=notes,
            )

            self.record_repository.create(record)

            self.audit_service.log(
                user_id=user_id,
                entity_name="MaintenanceRecord",
                entity_id=str(record.id),
                action=AuditAction.CREATE,
                description=("Registro de mantenimiento creado."),
            )

            self.db.commit()
            self.db.refresh(record)

            return record

        except Exception:
            self.db.rollback()
            raise
