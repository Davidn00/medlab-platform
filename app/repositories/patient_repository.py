"""
Repositorio de pacientes.

Esta capa contiene exclusivamente operaciones relacionadas
con la persistencia de pacientes en PostgreSQL.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient


class PatientRepository:
    """
    Encapsula las operaciones de base de datos relacionadas
    con pacientes.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, patient: Patient) -> Patient:
        """
        Guarda un nuevo paciente en PostgreSQL.
        """

        self.db.add(patient)

        self.db.commit()

        self.db.refresh(patient)

        return patient

    def get_by_id(self, patient_id: UUID) -> Patient | None:
        """
        Busca un paciente mediante su UUID.
        """

        statement = select(Patient).where(
            Patient.id == patient_id
        )

        return self.db.scalar(statement)

    def get_by_medical_record(
        self,
        medical_record: str,
    ) -> Patient | None:
        """
        Busca un paciente mediante su expediente médico.
        """

        statement = select(Patient).where(
            Patient.medical_record == medical_record
        )

        return self.db.scalar(statement)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Patient]:
        """
        Obtiene una lista de pacientes.

        skip:
            Número de registros que se deben saltar.

        limit:
            Número máximo de registros.
        """

        statement = (
            select(Patient)
            .offset(skip)
            .limit(limit)
            .order_by(Patient.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update(self, patient: Patient) -> Patient:
        """
        Guarda los cambios realizados sobre un paciente.
        """

        self.db.commit()

        self.db.refresh(patient)

        return patient

    def delete(self, patient: Patient) -> None:
        """
        Elimina un paciente de PostgreSQL.
        """

        self.db.delete(patient)

        self.db.commit()