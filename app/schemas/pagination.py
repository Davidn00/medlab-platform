"""
Schemas reutilizables para paginación.

Autor: David
Proyecto: MedLab Platform
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Parámetros normalizados de paginación.
    """

    page: int = Field(
        default=1,
        ge=1,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    @property
    def offset(self) -> int:
        """
        Calcula el offset SQL correspondiente.
        """

        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta genérica paginada.
    """

    items: list[T]

    page: int

    limit: int

    total: int

    pages: int