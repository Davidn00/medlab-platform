"""
Modelo Sample.

Representa una muestra biológica tomada a un paciente.

Autor: David
Proyecto: MedLab Platform
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SampleType(str, Enum):
    """
    Tipos de muestras soportadas.
    """

    BLOOD = "blood"
    URINE = "urine"
    SALIVA = "saliva"
    TISSUE = "tissue"
    OTHER = "other"


class SampleStatus(str, Enum):
    """
    Estado de procesamiento de una muestra.
    """

    COLLECTED = "collected"
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Sample(Base):
    """
    Muestra biológica.
    """

    __tablename__ = "samples"

    # ------------------------------------------------------
    # Identificación
    # ------------------------------------------------------

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    sample_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------
    # Relación con paciente
    # ------------------------------------------------------

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ------------------------------------------------------
    # Información de la muestra
    # ------------------------------------------------------

    sample_type: Mapped[SampleType] = mapped_column(
        SQLEnum(SampleType, name="sample_type"),
        nullable=False,
    )

    status: Mapped[SampleStatus] = mapped_column(
        SQLEnum(SampleStatus, name="sample_status"),
        default=SampleStatus.COLLECTED,
        nullable=False,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------
    # Relaciones
    # ------------------------------------------------------

    patient: Mapped["Patient"] = relationship(
        back_populates="samples"
    )

    laboratory_tests: Mapped[list["LaboratoryTest"]] = relationship(
        "LaboratoryTest",
        back_populates="sample",
        cascade="all, delete-orphan"
    )
    