"""
Service para calibraciones.

Contiene la lógica de negocio relacionada con
Calibration.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime, timezone, timedelta
from uuid import UUID

from app.core.exceptions import (
    CalibrationNotFoundError,
    EquipmentNotFoundError,
    InvalidCalibrationDatesError,
)
from app.models.calibration import Calibration
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.calibration_repository import (
    CalibrationRepository,
)
from app.schemas.calibration import (
    CalibrationCreate,
    CalibrationUpdate,
)


class CalibrationService:
    """
    Lógica de negocio de calibraciones.

    El Service es responsable de controlar las
    transacciones de las operaciones de negocio.
    """

    def __init__(
        self,
        calibration_repository: CalibrationRepository,
        equipment_repository: BiomedicalEquipmentRepository,
    ):
        self.calibration_repository = (
            calibration_repository
        )

        self.equipment_repository = (
            equipment_repository
        )

    def create(
        self,
        data: CalibrationCreate,
    ) -> Calibration:
        """
        Crea una nueva calibración.

        La operación completa se confirma mediante
        commit desde la capa Service.
        """

        db = self.calibration_repository.db

        try:
            equipment = (
                self.equipment_repository.get_by_id(
                    data.equipment_id
                )
            )

            if equipment is None:
                raise EquipmentNotFoundError(
                    "El equipo biomédico indicado no existe."
                )

            self._validate_dates(
                data.calibration_date,
                data.next_calibration_date,
            )

            calibration = Calibration(
                equipment_id=data.equipment_id,
                calibration_date=data.calibration_date,
                next_calibration_date=(
                    data.next_calibration_date
                ),
                performed_by=data.performed_by,
                certificate_number=data.certificate_number,
                status=data.status,
                notes=data.notes,
            )

            calibration = (
                self.calibration_repository.create(
                    calibration
                )
            )

            db.commit()
            db.refresh(calibration)

            return calibration

        except Exception:
            db.rollback()
            raise

    def get_by_id(
        self,
        calibration_id: UUID,
    ) -> Calibration | None:
        """
        Obtiene una calibración por UUID.
        """

        return self.calibration_repository.get_by_id(
            calibration_id
        )

    def get_all(
        self,
    ) -> list[Calibration]:
        """
        Obtiene todas las calibraciones.
        """

        return self.calibration_repository.get_all()

    def get_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> list[Calibration]:
        """
        Obtiene las calibraciones de un equipo.
        """

        equipment = (
            self.equipment_repository.get_by_id(
                equipment_id
            )
        )

        if equipment is None:
            raise EquipmentNotFoundError(
                "El equipo biomédico indicado no existe."
            )

        return (
            self.calibration_repository
            .get_by_equipment_id(equipment_id)
        )

    def get_expiring_calibrations(
        self,
        days: int = 30,
    ) -> list[Calibration]:
        """
        Obtiene calibraciones próximas a vencer.

        Por defecto se consideran los próximos
        30 días.
        """

        if days < 1:
            raise ValueError(
                "El número de días debe ser mayor que cero."
            )

        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=days)

        return (
            self.calibration_repository
            .get_expiring_calibrations(
                start_date=now,
                end_date=end_date,
            )
        )

    def get_expired_calibrations(
        self,
    ) -> list[Calibration]:
        """
        Obtiene calibraciones cuya fecha de próxima
        calibración ya venció.
        """

        now = datetime.now(timezone.utc)

        return (
            self.calibration_repository
            .get_expired_calibrations(
                current_date=now,
            )
        )

    def update(
        self,
        calibration_id: UUID,
        data: CalibrationUpdate,
    ) -> Calibration | None:
        """
        Actualiza una calibración.

        La operación se confirma mediante commit
        desde la capa Service.
        """

        db = self.calibration_repository.db

        try:
            calibration = (
                self.calibration_repository.get_by_id(
                    calibration_id
                )
            )

            if calibration is None:
                return None

            update_data = data.model_dump(
                exclude_unset=True
            )

            equipment_id = update_data.get(
                "equipment_id",
                calibration.equipment_id,
            )

            if "equipment_id" in update_data:

                equipment = (
                    self.equipment_repository.get_by_id(
                        equipment_id
                    )
                )

                if equipment is None:
                    raise EquipmentNotFoundError(
                        "El equipo biomédico indicado "
                        "no existe."
                    )

            calibration_date = update_data.get(
                "calibration_date",
                calibration.calibration_date,
            )

            next_calibration_date = update_data.get(
                "next_calibration_date",
                calibration.next_calibration_date,
            )

            self._validate_dates(
                calibration_date,
                next_calibration_date,
            )

            for field, value in update_data.items():
                setattr(calibration, field, value)

            calibration = (
                self.calibration_repository.update(
                    calibration
                )
            )

            db.commit()
            db.refresh(calibration)

            return calibration

        except Exception:
            db.rollback()
            raise

    def delete(
        self,
        calibration_id: UUID,
    ) -> bool:
        """
        Elimina una calibración.

        La eliminación se confirma mediante commit
        desde la capa Service.
        """

        db = self.calibration_repository.db

        try:
            calibration = (
                self.calibration_repository.get_by_id(
                    calibration_id
                )
            )

            if calibration is None:
                return False

            self.calibration_repository.delete(
                calibration
            )

            db.commit()

            return True

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _validate_dates(
        calibration_date: datetime,
        next_calibration_date: datetime,
    ) -> None:
        """
        Valida la coherencia temporal de una calibración.
        """

        if next_calibration_date <= calibration_date:
            raise InvalidCalibrationDatesError(
                "La próxima fecha de calibración "
                "debe ser posterior a la fecha de "
                "calibración."
            )

