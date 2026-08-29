"""
Repository para equipos biomédicos.

Encapsula el acceso a la tabla biomedical_equipment.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.biomedical_equipment import BiomedicalEquipment


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
        Persiste un nuevo equipo biomédico.
        """

        self.db.add(equipment)
        self.db.commit()
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
        Actualiza un equipo existente.
        """

        self.db.commit()
        self.db.refresh(equipment)

        return equipment

    def delete(
        self,
        equipment: BiomedicalEquipment,
    ) -> None:
        """
        Elimina un equipo.
        """

        self.db.delete(equipment)
        self.db.commit()