"""
Service para equipos biomédicos.

Contiene la lógica de negocio relacionada con
BiomedicalEquipment.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from app.core.exceptions import (
    EquipmentAlreadyExistsError,
    EquipmentHasCalibrationsError,
    EquipmentNotFoundError,
)
from app.models.biomedical_equipment import BiomedicalEquipment
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.calibration_repository import (
    CalibrationRepository,
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
        equipment_repository: BiomedicalEquipmentRepository,
        calibration_repository: CalibrationRepository,
    ):
        self.equipment_repository = equipment_repository
        self.calibration_repository = calibration_repository

    def create(
        self,
        data: BiomedicalEquipmentCreate,
    ) -> BiomedicalEquipment:
        """
        Crea un nuevo equipo biomédico.
        """

        existing_equipment = (
            self.equipment_repository.get_by_serial_number(
                data.serial_number
            )
        )

        if existing_equipment:
            raise EquipmentAlreadyExistsError(
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

        return self.equipment_repository.create(equipment)

    def get_by_id(
        self,
        equipment_id: UUID,
    ) -> BiomedicalEquipment | None:
        """
        Obtiene un equipo por su UUID.
        """

        return self.equipment_repository.get_by_id(
            equipment_id
        )

    def get_all(
        self,
    ) -> list[BiomedicalEquipment]:
        """
        Obtiene todos los equipos.
        """

        return self.equipment_repository.get_all()

    def update(
        self,
        equipment_id: UUID,
        data: BiomedicalEquipmentUpdate,
    ) -> BiomedicalEquipment:
        """
        Actualiza un equipo existente.
        """

        equipment = self.equipment_repository.get_by_id(
            equipment_id
        )

        if equipment is None:
            raise EquipmentNotFoundError(
                "Equipo biomédico no encontrado."
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "serial_number" in update_data:
            existing_equipment = (
                self.equipment_repository.get_by_serial_number(
                    update_data["serial_number"]
                )
            )

            if (
                existing_equipment
                and existing_equipment.id != equipment.id
            ):
                raise EquipmentAlreadyExistsError(
                    "Ya existe otro equipo con ese número de serie."
                )

        for field, value in update_data.items():
            setattr(equipment, field, value)

        return self.equipment_repository.update(
            equipment
        )

    def delete(
        self,
        equipment_id: UUID,
    ) -> bool:
        """
        Elimina un equipo.

        Un equipo que tenga calibraciones asociadas
        no puede ser eliminado.

        Devuelve True si fue eliminado.
        """

        equipment = self.equipment_repository.get_by_id(
            equipment_id
        )

        if equipment is None:
            raise EquipmentNotFoundError(
                "Equipo biomédico no encontrado."
            )

        calibrations = (
            self.calibration_repository.get_by_equipment_id(
                equipment_id
            )
        )

        if calibrations:
            raise EquipmentHasCalibrationsError(
                "No se puede eliminar el equipo biomédico "
                "porque tiene calibraciones asociadas."
            )

        self.equipment_repository.delete(equipment)

        return True