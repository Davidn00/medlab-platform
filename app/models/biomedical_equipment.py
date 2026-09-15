"""
Modelo de equipos biomédicos.

Autor: David
Proyecto: MedLab Platform
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EquipmentStatus(str, Enum):
    """
    Estados posibles durante el ciclo de vida
    de un equipo biomédico.
    """

    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"
    RETIRED = "RETIRED"


class BiomedicalEquipment(Base):
    __tablename__ = "biomedical_equipment"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    manufacturer: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    serial_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    location: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    status: Mapped[EquipmentStatus] = mapped_column(
        String(30),
        nullable=False,
        default=EquipmentStatus.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    calibrations = relationship(
        "Calibration",
        back_populates="equipment",
        cascade="all, delete-orphan",
    )
    
    laboratory_tests = relationship(
        "LaboratoryTest",
        back_populates="equipment",
    )

    maintenance_records = relationship(
        "MaintenanceRecord",
        back_populates="equipment",
        cascade="all, delete-orphan",
    )

    maintenance_schedules = relationship(
        "MaintenanceSchedule",
        back_populates="equipment",
        cascade="all, delete-orphan",
    )

    lifecycle_events = relationship(
        "EquipmentLifecycleEvent",
        back_populates="equipment",
        cascade="all, delete-orphan",
    )