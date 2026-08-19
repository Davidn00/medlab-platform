"""
Esquemas Pydantic relacionados con usuarios.

Estos esquemas validan la información recibida por la API
y controlan qué datos se envían como respuesta.

Autor: David
Proyecto: MedLab Platform
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


# ==========================================================
# Esquema base
# ==========================================================

class UserBase(BaseModel):
    """
    Información común de un usuario.
    """

    full_name: str
    email: EmailStr
    role: UserRole = UserRole.TECHNICIAN


# ==========================================================
# Crear usuario
# ==========================================================

class UserCreate(UserBase):
    """
    Datos necesarios para crear un usuario.
    """

    password: str


# ==========================================================
# Actualizar usuario
# ==========================================================

class UserUpdate(BaseModel):
    """
    Campos opcionales para actualizar un usuario.
    """

    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


# ==========================================================
# Respuesta pública
# ==========================================================

class UserResponse(UserBase):
    """
    Información que la API devolverá al cliente.

    Nunca exponemos hashed_password.
    """

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }