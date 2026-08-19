"""
Base declarativa de SQLAlchemy.

Todos los modelos del proyecto heredarán de esta clase.

Autor: David
Proyecto: MedLab Platform
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos SQLAlchemy.
    """

    pass