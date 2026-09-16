"""
Repositorio de muestras.
"""

from uuid import UUID

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.sample import Sample


class SampleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, sample: Sample) -> Sample:

        self.db.add(sample)

        self.db.commit()

        self.db.refresh(sample)

        return sample

    def get_by_id(
        self,
        sample_id: UUID,
    ) -> Sample | None:

        statement = select(Sample).where(Sample.id == sample_id)

        return self.db.scalar(statement)

    def get_by_code(
        self,
        sample_code: str,
    ) -> Sample | None:

        statement = select(Sample).where(Sample.sample_code == sample_code)

        return self.db.scalar(statement)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Sample]:

        statement = (
            select(Sample)
            .offset(skip)
            .limit(limit)
            .order_by(Sample.collected_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_patient(
        self,
        patient_id: UUID,
    ) -> list[Sample]:

        statement = (
            select(Sample)
            .where(Sample.patient_id == patient_id)
            .order_by(Sample.collected_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update(self, sample: Sample) -> Sample:

        self.db.commit()

        self.db.refresh(sample)

        return sample

    def delete(self, sample: Sample) -> None:

        self.db.delete(sample)

        self.db.commit()

    def search_paginated(
        self,
        *,
        page: int,
        limit: int,
        search: str | None = None,
        patient_id: UUID | None = None,
        status=None,
        sample_type=None,
        collected_from=None,
        collected_to=None,
        sort_by: str = "collected_at",
        sort_order: str = "desc",
    ) -> tuple[list[Sample], int]:
        """
        Busca muestras con filtros,
        ordenamiento y paginación.
        """

        filters = []

        if search:
            filters.append(Sample.sample_code.ilike(f"%{search.strip()}%"))

        if patient_id:
            filters.append(Sample.patient_id == patient_id)

        if status:
            filters.append(Sample.status == status)

        if sample_type:
            filters.append(Sample.sample_type == sample_type)

        if collected_from:
            filters.append(Sample.collected_at >= collected_from)

        if collected_to:
            filters.append(Sample.collected_at <= collected_to)

        columns = {
            "collected_at": Sample.collected_at,
            "sample_code": Sample.sample_code,
            "status": Sample.status,
        }

        column = columns[sort_by]

        ordering = column.asc() if sort_order == "asc" else column.desc()

        total = int(
            self.db.scalar(select(func.count()).select_from(Sample).where(*filters))
            or 0
        )

        items = list(
            self.db.scalars(
                select(Sample)
                .where(*filters)
                .order_by(
                    ordering,
                    Sample.id,
                )
                .offset((page - 1) * limit)
                .limit(limit)
            ).all()
        )

        return items, total
