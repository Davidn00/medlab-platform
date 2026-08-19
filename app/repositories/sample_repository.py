"""
Repositorio de muestras.
"""

from uuid import UUID

from sqlalchemy import select
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

        statement = select(Sample).where(
            Sample.id == sample_id
        )

        return self.db.scalar(statement)

    def get_by_code(
        self,
        sample_code: str,
    ) -> Sample | None:

        statement = select(Sample).where(
            Sample.sample_code == sample_code
        )

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