"""
Modelo de registros de mantenimiento ejecutados.

Autor: David
Proyecto: MedLab Platform
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MaintenanceRecord(Base):
    """
    Registro técnico de una actividad de mantenimiento.
    """

    __tablename__ = "maintenance_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    maintenance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "maintenances.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
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

    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    performed_by: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    findings: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parts_replaced: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    maintenance = relationship(
        "Maintenance",
        back_populates="records",
    )

    equipment = relationship(
        "BiomedicalEquipment",
        back_populates="maintenance_records",
    )
