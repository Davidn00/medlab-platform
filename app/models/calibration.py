"""
Modelo de calibraciones de equipos biomédicos.

Autor: David
Proyecto: MedLab Platform
"""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CalibrationStatus(str, PyEnum):
    VALID = "valid"
    EXPIRED = "expired"


class Calibration(Base):
    __tablename__ = "calibrations"

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

    calibration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    next_calibration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    performed_by: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    certificate_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[CalibrationStatus] = mapped_column(
        SQLEnum(
            CalibrationStatus,
            name="calibration_status",
        ),
        nullable=False,
        default=CalibrationStatus.VALID,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    equipment = relationship(
        "BiomedicalEquipment",
        back_populates="calibrations",
    )