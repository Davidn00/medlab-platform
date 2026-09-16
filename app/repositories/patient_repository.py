"""
Repositorio de pacientes.

Esta capa contiene exclusivamente operaciones relacionadas
con la persistencia de pacientes en PostgreSQL.
"""

from uuid import UUID

from sqlalchemy import (
    func,
    or_,
    select,
)
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

        statement = select(Patient).where(Patient.id == patient_id)

        return self.db.scalar(statement)

    def get_by_medical_record(
        self,
        medical_record: str,
    ) -> Patient | None:
        """
        Busca un paciente mediante su expediente médico.
        """

        statement = select(Patient).where(Patient.medical_record == medical_record)

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

    def search_paginated(
        self,
        *,
        page: int,
        limit: int,
        search: str | None = None,
        gender: str | None = None,
        birth_date_from=None,
        birth_date_to=None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Patient], int]:
        """
        Busca pacientes aplicando filtros,
        búsqueda, ordenamiento y paginación.
        """

        filters = []

        if search:
            pattern = f"%{search.strip()}%"

            filters.append(
                or_(
                    Patient.first_name.ilike(pattern),
                    Patient.last_name.ilike(pattern),
                    Patient.medical_record.ilike(pattern),
                    Patient.email.ilike(pattern),
                )
            )

        if gender:
            filters.append(Patient.gender == gender)

        if birth_date_from:
            filters.append(Patient.birth_date >= birth_date_from)

        if birth_date_to:
            filters.append(Patient.birth_date <= birth_date_to)

        columns = {
            "created_at": Patient.created_at,
            "updated_at": Patient.updated_at,
            "first_name": Patient.first_name,
            "last_name": Patient.last_name,
            "birth_date": Patient.birth_date,
        }

        column = columns[sort_by]

        ordering = column.asc() if sort_order == "asc" else column.desc()

        base = select(Patient).where(*filters)

        count_statement = select(func.count()).select_from(Patient).where(*filters)

        total = int(self.db.scalar(count_statement) or 0)

        items = list(
            self.db.scalars(
                base.order_by(
                    ordering,
                    Patient.id,
                )
                .offset((page - 1) * limit)
                .limit(limit)
            ).all()
        )

        return items, total
