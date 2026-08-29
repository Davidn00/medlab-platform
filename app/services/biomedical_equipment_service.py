"""
Service para equipos biomédicos.

Contiene la lógica de negocio relacionada con
BiomedicalEquipment.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from app.models.biomedical_equipment import BiomedicalEquipment
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.schemas.biomedical_equipment import (
    BiomedicalEquipmentCreate,
    BiomedicalEquipmentUpdate,
)


class BiomedicalEquipmentService:
    """
    Lógica de negocio de equipos biomédicos.
    """

    def __init__(
        self,
        repository: BiomedicalEquipmentRepository,
    ):
        self.repository = repository

    def create(
        self,
        data: BiomedicalEquipmentCreate,
    ) -> BiomedicalEquipment:
        """
        Crea un nuevo equipo biomédico.
        """

        existing_equipment = (
            self.repository.get_by_serial_number(
                data.serial_number
            )
        )

        if existing_equipment:
            raise ValueError(
                "Ya existe un equipo con ese número de serie."
            )

        equipment = BiomedicalEquipment(
            name=data.name,
            manufacturer=data.manufacturer,
            model=data.model,
            serial_number=data.serial_number,
            location=data.location,
            status=data.status,
        )

        return self.repository.create(equipment)

    def get_by_id(
        self,
        equipment_id: UUID,
    ) -> BiomedicalEquipment | None:
        """
        Obtiene un equipo por su UUID.
        """

        return self.repository.get_by_id(equipment_id)

    def get_all(
        self,
    ) -> list[BiomedicalEquipment]:
        """
        Obtiene todos los equipos.
        """

        return self.repository.get_all()

    def update(
        self,
        equipment_id: UUID,
        data: BiomedicalEquipmentUpdate,
    ) -> BiomedicalEquipment | None:
        """
        Actualiza un equipo existente.
        """

        equipment = self.repository.get_by_id(
            equipment_id
        )

        if equipment is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "serial_number" in update_data:
            existing_equipment = (
                self.repository.get_by_serial_number(
                    update_data["serial_number"]
                )
            )

            if (
                existing_equipment
                and existing_equipment.id != equipment.id
            ):
                raise ValueError(
                    "Ya existe otro equipo con ese número de serie."
                )

        for field, value in update_data.items():
            setattr(equipment, field, value)

        return self.repository.update(equipment)

    def delete(
        self,
        equipment_id: UUID,
    ) -> bool:
        """
        Elimina un equipo.

        Devuelve True si fue eliminado y False
        si no existe.
        """

        equipment = self.repository.get_by_id(
            equipment_id
        )

        if equipment is None:
            return False

        self.repository.delete(equipment)

        return True