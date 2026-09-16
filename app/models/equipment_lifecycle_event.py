"""
Modelo de eventos del ciclo de vida de equipos biomédicos.

Autor: David
Proyecto: MedLab Platform
"""

import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EquipmentEventType(str, Enum):
    """
    Tipos de eventos del ciclo de vida.
    """

    EQUIPMENT = "EQUIPMENT"
    MAINTENANCE = "MAINTENANCE"
    CALIBRATION = "CALIBRATION"
    VALIDATION = "VALIDATION"


class EquipmentLifecycleEvent(Base):
    """
    Historial de eventos relacionados con un equipo.
    """

    __tablename__ = "equipment_lifecycle_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "biomedical_equipment.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    event_type: Mapped[EquipmentEventType] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    performed_by: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    new_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    equipment = relationship(
        "BiomedicalEquipment",
        back_populates="lifecycle_events",
    )
