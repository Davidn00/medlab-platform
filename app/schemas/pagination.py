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
    Respuesta estándar para endpoints paginados.
    """

    items: list[T]

    page: int = Field(
        ge=1,
    )

    limit: int = Field(
        ge=1,
        le=100,
    )

    total: int = Field(
        ge=0,
    )

    pages: int = Field(
        ge=0,
    )
