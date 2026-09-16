"""
Servicio para ciclo de vida de equipos biomédicos.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import (
    EquipmentNotFoundError,
    InvalidEquipmentStatusTransitionError,
)
from app.models.audit_log import AuditAction
from app.models.biomedical_equipment import (
    BiomedicalEquipment,
    EquipmentStatus,
)
from app.models.equipment_lifecycle_event import (
    EquipmentEventType,
    EquipmentLifecycleEvent,
)
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.equipment_lifecycle_repository import (
    EquipmentLifecycleRepository,
)
from app.services.audit_service import AuditService


class EquipmentLifecycleService:
    ALLOWED_TRANSITIONS = {
        EquipmentStatus.ACTIVE: {
            EquipmentStatus.MAINTENANCE,
            EquipmentStatus.OUT_OF_SERVICE,
            EquipmentStatus.RETIRED,
        },
        EquipmentStatus.MAINTENANCE: {
            EquipmentStatus.ACTIVE,
            EquipmentStatus.OUT_OF_SERVICE,
        },
        EquipmentStatus.OUT_OF_SERVICE: {
            EquipmentStatus.ACTIVE,
            EquipmentStatus.RETIRED,
        },
        EquipmentStatus.RETIRED: set(),
    }

    def __init__(
        self,
        db: Session,
        equipment_repository: BiomedicalEquipmentRepository,
        lifecycle_repository: EquipmentLifecycleRepository,
    ):
        self.db = db
        self.equipment_repository = equipment_repository
        self.lifecycle_repository = lifecycle_repository
        self.audit_service = AuditService(db)

    def change_status(
        self,
        equipment_id: UUID,
        new_status: EquipmentStatus,
        user_id: UUID | None = None,
    ) -> BiomedicalEquipment:

        equipment = self.equipment_repository.get_by_id(equipment_id)

        if equipment is None:
            raise EquipmentNotFoundError("Equipo biomédico no encontrado.")

        current_status = EquipmentStatus(equipment.status)

        if current_status == new_status:
            return equipment

        allowed = self.ALLOWED_TRANSITIONS[current_status]

        if new_status not in allowed:
            raise InvalidEquipmentStatusTransitionError(
                f"No se permite cambiar el equipo "
                f"de {current_status.value} a "
                f"{new_status.value}."
            )

        try:
            equipment.status = new_status

            self.db.flush()

            event = EquipmentLifecycleEvent(
                equipment_id=equipment.id,
                event_type=EquipmentEventType.EQUIPMENT,
                event_date=datetime.now(UTC),
                description=(
                    f"Estado cambiado de {current_status.value} a {new_status.value}."
                ),
                performed_by=None,
                previous_status=current_status.value,
                new_status=new_status.value,
            )

            self.lifecycle_repository.create(event)

            self.audit_service.log(
                user_id=user_id,
                entity_name="BiomedicalEquipment",
                entity_id=str(equipment.id),
                action=AuditAction.STATUS_CHANGED,
                description=(
                    f"Estado cambiado de {current_status.value} a {new_status.value}."
                ),
            )

            self.db.commit()
            self.db.refresh(equipment)

            return equipment

        except Exception:
            self.db.rollback()
            raise

    def record_event(
        self,
        equipment_id: UUID,
        event_type: EquipmentEventType,
        description: str,
        performed_by: str | None = None,
        reference_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> EquipmentLifecycleEvent:

        equipment = self.equipment_repository.get_by_id(equipment_id)

        if equipment is None:
            raise EquipmentNotFoundError("Equipo biomédico no encontrado.")

        try:
            event = EquipmentLifecycleEvent(
                equipment_id=equipment_id,
                event_type=event_type,
                description=description,
                performed_by=performed_by,
                reference_id=reference_id,
            )

            self.lifecycle_repository.create(event)

            self.audit_service.log(
                user_id=user_id,
                entity_name="EquipmentLifecycleEvent",
                entity_id=str(event.id),
                action=AuditAction.CREATE,
                description=description,
            )

            self.db.commit()
            self.db.refresh(event)

            return event

        except Exception:
            self.db.rollback()
            raise

    def get_history(
        self,
        equipment_id: UUID,
    ) -> list[EquipmentLifecycleEvent]:

        equipment = self.equipment_repository.get_by_id(equipment_id)

        if equipment is None:
            raise EquipmentNotFoundError("Equipo biomédico no encontrado.")

        return self.lifecycle_repository.get_by_equipment_id(equipment_id)
