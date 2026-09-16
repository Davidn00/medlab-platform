"""
Modelo LaboratoryTest.

Representa una prueba realizada sobre una muestra.

Autor: David
Proyecto: MedLab Platform
"""

import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.biomedical_equipment import BiomedicalEquipment
from app.models.sample import Sample


def utc_now() -> datetime:
    return datetime.now(UTC)


class LabTestStatus(str, Enum):
    """
    Estado de una prueba de laboratorio.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    CANCELLED = "cancelled"


class LaboratoryTest(Base):
    """
    Prueba de laboratorio.
    """

    __tablename__ = "laboratory_tests"

    # ------------------------------------------------------
    # Identificación
    # ------------------------------------------------------

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    sample_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("samples.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ------------------------------------------------------
    # Equipo biomédico utilizado
    # ------------------------------------------------------

    equipment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "biomedical_equipment.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------
    # Información de la prueba
    # ------------------------------------------------------

    test_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    result_value: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    reference_range: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[LabTestStatus] = mapped_column(
        SQLEnum(
            LabTestStatus,
            name="test_status",
        ),
        default=LabTestStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # ------------------------------------------------------
    # Relaciones
    # ------------------------------------------------------

    sample: Mapped["Sample"] = relationship(
        "Sample",
        back_populates="laboratory_tests",
    )

    equipment: Mapped["BiomedicalEquipment | None"] = relationship(
        "BiomedicalEquipment",
        back_populates="laboratory_tests",
    )
