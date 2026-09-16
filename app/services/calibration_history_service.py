"""
Servicio de historial y métricas de calibración.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import EquipmentNotFoundError
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.calibration_repository import (
    CalibrationRepository,
)


class CalibrationHistoryService:
    def __init__(
        self,
        equipment_repository: BiomedicalEquipmentRepository,
        calibration_repository: CalibrationRepository,
    ):
        self.equipment_repository = equipment_repository
        self.calibration_repository = calibration_repository

    def get_history(
        self,
        equipment_id: UUID,
    ):

        equipment = self.equipment_repository.get_by_id(equipment_id)

        if equipment is None:
            raise EquipmentNotFoundError("Equipo biomédico no encontrado.")

        calibrations = self.calibration_repository.get_by_equipment_id(equipment_id)

        ordered = sorted(
            calibrations,
            key=lambda calibration: calibration.calibration_date,
        )

        total = len(ordered)

        last_calibration = ordered[-1] if ordered else None

        next_calibration = None

        if last_calibration is not None:
            next_calibration = min(
                ordered,
                key=lambda calibration: calibration.next_calibration_date,
            )

        now = datetime.now(UTC)

        days_overdue = 0

        if next_calibration is not None:
            delta = (now - next_calibration.next_calibration_date).days

            if delta > 0:
                days_overdue = delta

        frequency = None

        if len(ordered) >= 2:
            intervals = []

            for previous, current in zip(
                ordered,
                ordered[1:],
                strict=False,
            ):
                interval = (
                    current.calibration_date - previous.calibration_date
                ).total_seconds() / 86400

                intervals.append(interval)

            if intervals:
                frequency = sum(intervals) / len(intervals)

        return {
            "equipment_id": equipment_id,
            "calibrations": ordered,
            "metrics": {
                "equipment_id": equipment_id,
                "total_calibrations": total,
                "last_calibration": (
                    last_calibration.calibration_date if last_calibration else None
                ),
                "next_calibration": (
                    next_calibration.next_calibration_date if next_calibration else None
                ),
                "days_overdue": days_overdue,
                "calibration_frequency_days": frequency,
            },
        }
