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
            self.db.query(Calibration).filter(Calibration.id == calibration_id).first()
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

    def search_paginated(
        self,
        *,
        page: int,
        limit: int,
        status=None,
        equipment_id: UUID | None = None,
        search: str | None = None,
        calibration_from=None,
        calibration_to=None,
        next_calibration_from=None,
        next_calibration_to=None,
        sort_by: str = "calibration_date",
        sort_order: str = "desc",
    ) -> tuple[list[Calibration], int]:
        """
        Busca calibraciones aplicando filtros,
        rangos de fechas, sorting y paginación.
        """

        query = self.db.query(Calibration)

        if status:
            query = query.filter(Calibration.status == status)

        if equipment_id:
            query = query.filter(Calibration.equipment_id == equipment_id)

        if search:
            query = query.filter(Calibration.performed_by.ilike(f"%{search.strip()}%"))

        if calibration_from:
            query = query.filter(Calibration.calibration_date >= calibration_from)

        if calibration_to:
            query = query.filter(Calibration.calibration_date <= calibration_to)

        if next_calibration_from:
            query = query.filter(
                Calibration.next_calibration_date >= next_calibration_from
            )

        if next_calibration_to:
            query = query.filter(
                Calibration.next_calibration_date <= next_calibration_to
            )

        columns = {
            "calibration_date": Calibration.calibration_date,
            "next_calibration_date": Calibration.next_calibration_date,
            "created_at": Calibration.created_at,
            "status": Calibration.status,
        }

        column = columns[sort_by]

        ordering = column.asc() if sort_order == "asc" else column.desc()

        total = query.count()

        items = (
            query.order_by(
                ordering,
                Calibration.id,
            )
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return items, total

    def get_last_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> Calibration | None:

        return (
            self.db.query(Calibration)
            .filter(Calibration.equipment_id == equipment_id)
            .order_by(Calibration.calibration_date.desc())
            .first()
        )

    def get_next_by_equipment_id(
        self,
        equipment_id: UUID,
    ) -> Calibration | None:

        return (
            self.db.query(Calibration)
            .filter(Calibration.equipment_id == equipment_id)
            .order_by(Calibration.next_calibration_date.asc())
            .first()
        )
