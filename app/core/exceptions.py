"""
Excepciones específicas del dominio MedLab.

Autor: David
Proyecto: MedLab Platform
"""


class EquipmentNotFoundError(Exception):
    """
    Se produce cuando se intenta operar con un
    equipo biomédico que no existe.
    """

    pass

class MedLabDomainError(Exception):
    """Excepción base para errores de dominio."""


class EquipmentNotFoundError(MedLabDomainError):
    """El equipo biomédico solicitado no existe."""


class EquipmentAlreadyExistsError(MedLabDomainError):
    """Ya existe un equipo con el mismo identificador único."""
    pass

class EquipmentHasCalibrationsError(MedLabDomainError):
    """No se puede eliminar un equipo con historial de calibraciones."""


class CalibrationNotFoundError(MedLabDomainError):
    """La calibración solicitada no existe."""


class InvalidCalibrationDatesError(MedLabDomainError):
    """Las fechas de calibración no son válidas."""