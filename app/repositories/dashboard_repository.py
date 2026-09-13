"""
Repositorio de estadísticas del dashboard.

Las métricas se calculan mediante agregaciones
directamente en PostgreSQL.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime, timezone

from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.models.biomedical_equipment import (
    BiomedicalEquipment,
)

from app.models.calibration import (
    Calibration,
)

from app.models.laboratory_test import (
    LaboratoryTest,
    LabTestStatus,
)

from app.models.patient import Patient

from app.models.sample import Sample


class DashboardRepository:
    """
    Acceso a métricas agregadas del laboratorio.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def _count(
        self,
        model,
        *filters,
    ) -> int:
        """
        Ejecuta COUNT(*) sobre un modelo.
        """

        statement = (
            select(func.count())
            .select_from(model)
        )

        if filters:
            statement = statement.where(
                *filters
            )

        return int(
            self.db.scalar(statement)
            or 0
        )

    def get_statistics(
        self,
    ) -> dict[str, int]:
        """
        Obtiene las estadísticas principales.
        """

        now = datetime.now(
            timezone.utc
        )

        return {
            "patients": self._count(
                Patient
            ),

            "samples": self._count(
                Sample
            ),

            "tests": self._count(
                LaboratoryTest
            ),

            "equipment": self._count(
                BiomedicalEquipment
            ),

            "calibrations": self._count(
                Calibration
            ),

            "expired_calibrations": self._count(
                Calibration,
                Calibration.next_calibration_date
                < now,
            ),

            "pending_tests": self._count(
                LaboratoryTest,
                LaboratoryTest.status
                == LabTestStatus.PENDING,
            ),
        }