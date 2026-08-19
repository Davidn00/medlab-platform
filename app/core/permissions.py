"""
Sistema de autorización basado en roles (RBAC).

Este módulo contiene dependencias reutilizables que permiten
proteger endpoints según el rol del usuario autenticado.

Autor: David
Proyecto: MedLab Platform
"""

from collections.abc import Iterable

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User, UserRole


def require_roles(allowed_roles: Iterable[UserRole]):
    """
    Crea una dependencia que verifica si el usuario autenticado
    posee alguno de los roles permitidos.

    Ejemplo:

        @router.post(...)
        def endpoint(
            current_user: User = Depends(
                require_roles([UserRole.ADMIN])
            )
        )

    """

    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )

        return current_user

    return dependency