"""
Repository para calibraciones.

Encapsula el acceso a la tabla calibrations.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.calibration import Calibration


class CalibrationRepository:
    """Acceso a datos de calibraciones."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        calibration: Calibration,
    ) -> Calibration:
        self.db.add(calibration)
        self.db.flush()
        self.db.refresh(calibration)
        return calibration

    def get_by_id(
        self,
        calibration_id: UUID,
    ) -> Calibration | None:
        return (
            self.db.query(Calibration)
            .filter(Calibration.id == calibration_id)
            .first()
        )

    def get_all(
        self,
    ) -> list[Calibration]:
        return (
            self.db.query(Calibration)
            .order_by(Calibration.calibration_date.desc())
            .all()
        )

    def get_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> list[Calibration]:
        return (
            self.db.query(Calibration)
            .filter(Calibration.equipment_id == equipment_id)
            .order_by(Calibration.calibration_date.desc())
            .all()
        )

    def get_expiring_calibrations(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Calibration]:
        return (
            self.db.query(Calibration)
            .filter(
                Calibration.status == "VALID",
                Calibration.next_calibration_date >= start_date,
                Calibration.next_calibration_date <= end_date,
            )
            .order_by(Calibration.next_calibration_date.asc())
            .all()
        )

    def get_expired_calibrations(
        self,
        current_date: datetime,
    ) -> list[Calibration]:
        return (
            self.db.query(Calibration)
            .filter(
                Calibration.next_calibration_date < current_date,
            )
            .order_by(Calibration.next_calibration_date.asc())
            .all()
        )

    def update(
        self,
        calibration: Calibration,
    ) -> Calibration:
        self.db.flush()
        self.db.refresh(calibration)
        return calibration

    def update_status(
        self,
        calibration: Calibration,
        new_status,
    ) -> Calibration:
        """
        Actualiza únicamente el estado.

        No hace commit y no genera auditoría. La auditoría
        pertenece al Service para que estado + auditoría
        formen una única transacción.
        """

        calibration.status = new_status

        self.db.flush()
        self.db.refresh(calibration)

        return calibration

    def delete(
        self,
        calibration: Calibration,
    ) -> None:
        self.db.delete(calibration)
        self.db.flush()
