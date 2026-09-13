"""
Utilidades comunes para consultas paginadas con SQLAlchemy.

Autor: David
Proyecto: MedLab Platform
"""

from math import ceil


def pagination_metadata(
    total: int,
    page: int,
    limit: int,
) -> dict[str, int]:
    """
    Calcula los metadatos de una respuesta paginada.
    """

    pages = ceil(total / limit) if total else 0

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }