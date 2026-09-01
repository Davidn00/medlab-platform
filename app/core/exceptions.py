"""
Excepciones de dominio de MedLab Platform.
"""


class EquipmentNotFoundError(Exception):
    """
    Se produce cuando se intenta operar con un
    equipo biomédico que no existe.
    """

    pass