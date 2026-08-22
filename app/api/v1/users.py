"""
Endpoints relacionados con usuarios.

Autor: David
Proyecto: MedLab Platform
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

from app.api.deps import get_current_user

from app.core.permissions import require_roles
from app.models.user import User, UserRole


router = APIRouter(prefix="/users", tags=["Users"])

service = UserService()



# ==========================================================
# Crear usuario
# ==========================================================

@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.ADMIN])
    ),
):
    try:
        return service.create_user(db, user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================================
# Listar usuario autenticado
# ==========================================================

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(
        require_roles([
            UserRole.ADMIN,
            UserRole.TECHNICIAN,
            UserRole.DOCTOR,
        ])
    ),
):
    """
    Devuelve la información del usuario autenticado.
    """

    return current_user


# ==========================================================
# Obtener usuario por ID
# ==========================================================

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.ADMIN])
    ),
):
    user = service.get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user


# ==========================================================
# Listar usuarios
# ==========================================================

@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.ADMIN])
    ),
):
    return service.get_users(db)


