"""
Servicio de estadísticas del dashboard.

Autor: David
Proyecto: MedLab Platform
"""

from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import (
    DashboardRepository,
)


class DashboardService:
    """
    Lógica de negocio del dashboard.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            DashboardRepository(db)
        )

    def get_statistics(
        self,
    ) -> dict[str, int]:
        """
        Obtiene las estadísticas generales.
        """

        return (
            self.repository
            .get_statistics()
        )