"""
Schemas para analytics del laboratorio.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import date

from pydantic import BaseModel, Field


class DailyMetric(BaseModel):
    date: date
    count: int = Field(ge=0)


class EquipmentUtilization(BaseModel):
    total_equipment: int = Field(ge=0)
    utilized_equipment: int = Field(ge=0)
    utilization_rate: float = Field(
        ge=0,
        le=100,
    )


class CalibrationCompliance(BaseModel):
    total_equipment: int = Field(ge=0)
    calibrated_equipment: int = Field(ge=0)
    compliant_equipment: int = Field(ge=0)
    compliance_rate: float = Field(
        ge=0,
        le=100,
    )


class AnalyticsResponse(BaseModel):
    period_start: date
    period_end: date

    tests_per_day: list[DailyMetric]

    samples_per_day: list[DailyMetric]

    equipment_utilization: EquipmentUtilization

    calibration_compliance: CalibrationCompliance

    failed_tests: int = Field(
        ge=0
    )