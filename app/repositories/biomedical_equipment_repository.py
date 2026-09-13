"""
Repository para equipos biomédicos.

Encapsula el acceso a la tabla biomedical_equipment.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.biomedical_equipment import BiomedicalEquipment

from sqlalchemy import (
    or_,
)


class BiomedicalEquipmentRepository:
    """
    Acceso a datos de equipos biomédicos.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        equipment: BiomedicalEquipment,
    ) -> BiomedicalEquipment:
        """
        Persiste un nuevo equipo biomédico dentro
        de la transacción actual.
        """

        self.db.add(equipment)
        self.db.flush()
        self.db.refresh(equipment)

        return equipment

    def get_by_id(
        self,
        equipment_id: UUID,
    ) -> BiomedicalEquipment | None:
        """
        Obtiene un equipo por su UUID.
        """

        return (
            self.db.query(BiomedicalEquipment)
            .filter(
                BiomedicalEquipment.id == equipment_id
            )
            .first()
        )

    def get_by_serial_number(
        self,
        serial_number: str,
    ) -> BiomedicalEquipment | None:
        """
        Obtiene un equipo mediante su número de serie.
        """

        return (
            self.db.query(BiomedicalEquipment)
            .filter(
                BiomedicalEquipment.serial_number
                == serial_number
            )
            .first()
        )

    def get_all(
        self,
    ) -> list[BiomedicalEquipment]:
        """
        Obtiene todos los equipos.
        """

        return (
            self.db.query(BiomedicalEquipment)
            .order_by(
                BiomedicalEquipment.name
            )
            .all()
        )

    def update(
        self,
        equipment: BiomedicalEquipment,
    ) -> BiomedicalEquipment:
        """
        Actualiza un equipo existente dentro
        de la transacción actual.
        """

        self.db.flush()
        self.db.refresh(equipment)

        return equipment

    def delete(
        self,
        equipment: BiomedicalEquipment,
    ) -> None:
        """
        Elimina un equipo dentro de la transacción actual.
        """

        self.db.delete(equipment)
        self.db.flush()

    def search_paginated(
        self,
        *,
        page: int,
        limit: int,
        search: str | None = None,
        status: str | None = None,
        created_from=None,
        created_to=None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[
        list[BiomedicalEquipment],
        int,
    ]:
        """
        Busca equipos biomédicos con filtros,
        búsqueda y paginación.
        """

        query = self.db.query(
            BiomedicalEquipment
        )

        if search:
            pattern = (
                f"%{search.strip()}%"
            )

            query = query.filter(
                or_(
                    BiomedicalEquipment.name.ilike(
                        pattern
                    ),
                    BiomedicalEquipment.manufacturer.ilike(
                        pattern
                    ),
                    BiomedicalEquipment.model.ilike(
                        pattern
                    ),
                    BiomedicalEquipment.serial_number.ilike(
                        pattern
                    ),
                    BiomedicalEquipment.location.ilike(
                        pattern
                    ),
                )
            )

        if status:
            query = query.filter(
                BiomedicalEquipment.status
                == status
            )

        if created_from:
            query = query.filter(
                BiomedicalEquipment.created_at
                >= created_from
            )

        if created_to:
            query = query.filter(
                BiomedicalEquipment.created_at
                <= created_to
            )

        columns = {
            "name":
                BiomedicalEquipment.name,
            "manufacturer":
                BiomedicalEquipment.manufacturer,
            "model":
                BiomedicalEquipment.model,
            "serial_number":
                BiomedicalEquipment.serial_number,
            "status":
                BiomedicalEquipment.status,
            "created_at":
                BiomedicalEquipment.created_at,
        }

        column = columns[sort_by]

        ordering = (
            column.asc()
            if sort_order == "asc"
            else column.desc()
        )

        total = query.count()

        items = (
            query
            .order_by(
                ordering,
                BiomedicalEquipment.id,
            )
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
            .all()
        )

        return items, total

