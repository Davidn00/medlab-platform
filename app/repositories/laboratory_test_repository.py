"""
Repositorio de pruebas de laboratorio.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.laboratory_test import LaboratoryTest


class LaboratoryTestRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        test: LaboratoryTest,
    ) -> LaboratoryTest:

        self.db.add(test)

        self.db.commit()

        self.db.refresh(test)

        return test

    def get_by_id(
        self,
        test_id: UUID,
    ) -> LaboratoryTest | None:

        statement = select(LaboratoryTest).where(
            LaboratoryTest.id == test_id
        )

        return self.db.scalar(statement)

    def get_by_sample(
        self,
        sample_id: UUID,
    ) -> list[LaboratoryTest]:

        statement = (
            select(LaboratoryTest)
            .where(LaboratoryTest.sample_id == sample_id)
            .order_by(LaboratoryTest.created_at.asc())
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        test: LaboratoryTest,
    ) -> LaboratoryTest:

        self.db.commit()

        self.db.refresh(test)

        return test

    def delete(
        self,
        test: LaboratoryTest,
    ) -> None:

        self.db.delete(test)

        self.db.commit()