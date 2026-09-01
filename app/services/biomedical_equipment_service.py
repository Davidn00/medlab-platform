"""
Service para equipos biomédicos.

Contiene la lógica de negocio relacionada con
BiomedicalEquipment.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

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
from app.core.exceptions import (
    EquipmentAlreadyExistsError,
    EquipmentHasCalibrationsError,
    EquipmentNotFoundError,
)


class BiomedicalEquipmentService:
    """
    Lógica de negocio de equipos biomédicos.

    El Service es responsable de controlar las
    transacciones de las operaciones de negocio.
    """

    def __init__(
        self,
        equipment_repository: BiomedicalEquipmentRepository,
        calibration_repository: CalibrationRepository,
    ):
        self.equipment_repository = equipment_repository
        self.calibration_repository = calibration_repository

    @property
    def db(self):
        """
        Devuelve la sesión SQLAlchemy utilizada por
        el repository de equipos.

        El Service controla la transacción, mientras
        que el Repository se limita a las operaciones
        de persistencia.
        """

        return self.equipment_repository.db

    def create(
        self,
        data: BiomedicalEquipmentCreate,
    ) -> BiomedicalEquipment:
        """
        Crea un nuevo equipo biomédico.

        La transacción es controlada por el Service.
        """

        try:
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

            equipment = self.equipment_repository.create(
                equipment
            )

            self.db.commit()
            self.db.refresh(equipment)

            return equipment

        except EquipmentAlreadyExistsError:
            self.db.rollback()
            raise

        except IntegrityError as exc:
            self.db.rollback()

            raise EquipmentAlreadyExistsError(
                "Ya existe un equipo con ese número de serie."
            ) from exc

        except Exception:
            self.db.rollback()
            raise

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

        La transacción es controlada por el Service.
        """

        try:
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
                    self.equipment_repository
                    .get_by_serial_number(
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

            equipment = self.equipment_repository.update(
                equipment
            )

            self.db.commit()
            self.db.refresh(equipment)

            return equipment

        except EquipmentNotFoundError:
            self.db.rollback()
            raise

        except EquipmentAlreadyExistsError:
            self.db.rollback()
            raise

        except IntegrityError as exc:
            self.db.rollback()

            raise EquipmentAlreadyExistsError(
                "Ya existe otro equipo con ese número de serie."
            ) from exc

        except Exception:
            self.db.rollback()
            raise

    def delete(
        self,
        equipment_id: UUID,
    ) -> bool:
        """
        Elimina un equipo.

        No permite eliminar un equipo que tenga
        calibraciones asociadas.

        La transacción es controlada por el Service.
        """

        try:
            equipment = self.equipment_repository.get_by_id(
                equipment_id
            )

            if equipment is None:
                raise EquipmentNotFoundError(
                    "Equipo biomédico no encontrado."
                )

            calibrations = (
                self.calibration_repository
                .get_by_equipment_id(equipment_id)
            )

            if calibrations:
                raise EquipmentHasCalibrationsError(
                    "No se puede eliminar un equipo que tiene "
                    "calibraciones registradas."
                )

            self.equipment_repository.delete(
                equipment
            )

            self.db.commit()

            return True

        except EquipmentNotFoundError:
            self.db.rollback()
            raise

        except EquipmentHasCalibrationsError:
            self.db.rollback()
            raise

        except Exception:
            self.db.rollback()
            raise

