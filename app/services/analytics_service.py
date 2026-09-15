"""
Servicio de analytics del laboratorio.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.repositories.analytics_repository import (
    AnalyticsRepository,
)


class AnalyticsService:

    def __init__(self, db: Session):
        self.repository = AnalyticsRepository(db)

    @staticmethod
    def _build_daily_series(
        start_date: date,
        end_date: date,
        values: dict[date, int],
    ) -> list[dict]:

        result = []

        current = start_date

        while current <= end_date:

            result.append(
                {
                    "date": current,
                    "count": values.get(
                        current,
                        0,
                    ),
                }
            )

            current += timedelta(
                days=1
            )

        return result

    def get_analytics(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:

        tests = (
            self.repository
            .tests_per_day(
                start_date,
                end_date,
            )
        )

        samples = (
            self.repository
            .samples_per_day(
                start_date,
                end_date,
            )
        )

        return {
            "period_start": start_date,
            "period_end": end_date,

            "tests_per_day": (
                self._build_daily_series(
                    start_date,
                    end_date,
                    tests,
                )
            ),

            "samples_per_day": (
                self._build_daily_series(
                    start_date,
                    end_date,
                    samples,
                )
            ),

            "equipment_utilization": (
                self.repository
                .equipment_utilization(
                    start_date,
                    end_date,
                )
            ),

            "calibration_compliance": (
                self.repository
                .calibration_compliance()
            ),

            "failed_tests": (
                self.repository
                .failed_tests(
                    start_date,
                    end_date,
                )
            ),
        }