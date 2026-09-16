"""
Repositorio de analytics.

Calcula métricas agregadas directamente
sobre PostgreSQL.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import UTC, date, datetime, time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.biomedical_equipment import (
    BiomedicalEquipment,
    EquipmentStatus,
)
from app.models.calibration import Calibration
from app.models.laboratory_test import (
    LaboratoryTest,
    LabTestStatus,
)
from app.models.sample import Sample


class AnalyticsRepository:
    """
    Acceso a métricas analíticas.
    """

    def __init__(self, db: Session):
        self.db = db

    # ======================================================
    # Rango temporal
    # ======================================================

    @staticmethod
    def _datetime_range(
        start_date: date,
        end_date: date,
    ):
        start = datetime.combine(
            start_date,
            time.min,
            tzinfo=UTC,
        )

        end = datetime.combine(
            end_date,
            time.max,
            tzinfo=UTC,
        )

        return start, end

    # ======================================================
    # Tests / day
    # ======================================================

    def tests_per_day(
        self,
        start_date: date,
        end_date: date,
    ) -> dict[date, int]:

        start, end = self._datetime_range(
            start_date,
            end_date,
        )

        statement = (
            select(
                func.date(LaboratoryTest.created_at),
                func.count(),
            )
            .where(
                LaboratoryTest.created_at >= start,
                LaboratoryTest.created_at <= end,
            )
            .group_by(func.date(LaboratoryTest.created_at))
            .order_by(func.date(LaboratoryTest.created_at))
        )

        return {row[0]: int(row[1]) for row in self.db.execute(statement).all()}

    # ======================================================
    # Samples / day
    # ======================================================

    def samples_per_day(
        self,
        start_date: date,
        end_date: date,
    ) -> dict[date, int]:

        start, end = self._datetime_range(
            start_date,
            end_date,
        )

        statement = (
            select(
                func.date(Sample.collected_at),
                func.count(),
            )
            .where(
                Sample.collected_at >= start,
                Sample.collected_at <= end,
            )
            .group_by(func.date(Sample.collected_at))
            .order_by(func.date(Sample.collected_at))
        )

        return {row[0]: int(row[1]) for row in self.db.execute(statement).all()}

    # ======================================================
    # Equipment utilization
    # ======================================================

    def equipment_utilization(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:

        start, end = self._datetime_range(
            start_date,
            end_date,
        )

        total_statement = (
            select(func.count())
            .select_from(BiomedicalEquipment)
            .where(BiomedicalEquipment.status != EquipmentStatus.RETIRED)
        )

        total = int(self.db.scalar(total_statement) or 0)

        utilized_statement = select(
            func.count(func.distinct(LaboratoryTest.equipment_id))
        ).where(
            LaboratoryTest.equipment_id.is_not(None),
            LaboratoryTest.created_at >= start,
            LaboratoryTest.created_at <= end,
        )

        utilized = int(self.db.scalar(utilized_statement) or 0)

        rate = (utilized / total) * 100 if total else 0.0

        return {
            "total_equipment": total,
            "utilized_equipment": utilized,
            "utilization_rate": round(
                rate,
                2,
            ),
        }

    # ======================================================
    # Calibration compliance
    # ======================================================

    def calibration_compliance(self) -> dict:

        now = datetime.now(UTC)

        equipment_statement = select(BiomedicalEquipment.id).where(
            BiomedicalEquipment.status != EquipmentStatus.RETIRED
        )

        equipment_ids = list(self.db.scalars(equipment_statement).all())

        total_equipment = len(equipment_ids)

        calibrated = 0
        compliant = 0

        for equipment_id in equipment_ids:
            calibration = (
                self.db.query(Calibration)
                .filter(Calibration.equipment_id == equipment_id)
                .order_by(Calibration.next_calibration_date.desc())
                .first()
            )

            if calibration is None:
                continue

            calibrated += 1

            if calibration.next_calibration_date >= now:
                compliant += 1

        rate = (compliant / calibrated) * 100 if calibrated else 0.0

        return {
            "total_equipment": total_equipment,
            "calibrated_equipment": calibrated,
            "compliant_equipment": compliant,
            "compliance_rate": round(
                rate,
                2,
            ),
        }

    # ======================================================
    # Failed tests
    # ======================================================

    def failed_tests(
        self,
        start_date: date,
        end_date: date,
    ) -> int:

        start, end = self._datetime_range(
            start_date,
            end_date,
        )

        statement = (
            select(func.count())
            .select_from(LaboratoryTest)
            .where(
                LaboratoryTest.status == LabTestStatus.CANCELLED,
                LaboratoryTest.created_at >= start,
                LaboratoryTest.created_at <= end,
            )
        )

        return int(self.db.scalar(statement) or 0)
