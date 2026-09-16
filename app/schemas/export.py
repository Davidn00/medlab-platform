"""
Schemas relacionados con exportaciones.

Autor: David
Proyecto: MedLab Platform
"""

from enum import Enum


class ExportFormat(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"
    JSON = "json"


class ExportResource(str, Enum):
    PATIENTS = "patients"
    SAMPLES = "samples"
    LABORATORY_TESTS = "laboratory-tests"
    EQUIPMENT = "equipment"
    CALIBRATIONS = "calibrations"
