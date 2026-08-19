"""
Modelo de usuario de MedLab Platform.

Este módulo contiene la representación SQLAlchemy de la tabla
'users' de PostgreSQL.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

from datetime import datetime, timezone



def utc_now() -> datetime:
    """
    Devuelve la fecha y hora actual en UTC.
    """
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    """
    Roles disponibles dentro de MedLab Platform.
    """

    ADMIN = "admin"
    TECHNICIAN = "technician"
    DOCTOR = "doctor"


class User(Base):
    """
    Modelo SQLAlchemy correspondiente a la tabla 'users'.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.TECHNICIAN,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

