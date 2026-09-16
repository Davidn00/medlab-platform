"""
Repositorio de pruebas de laboratorio.
"""

from uuid import UUID

from sqlalchemy import (
    func,
    or_,
    select,
)
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

        statement = select(LaboratoryTest).where(LaboratoryTest.id == test_id)

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

    def search_paginated(
        self,
        *,
        page: int,
        limit: int,
        search: str | None = None,
        sample_id: UUID | None = None,
        status=None,
        created_from=None,
        created_to=None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[LaboratoryTest], int]:
        """
        Busca pruebas de laboratorio con filtros,
        búsqueda, sorting y paginación.
        """

        filters = []

        if search:
            pattern = f"%{search.strip()}%"

            filters.append(
                or_(
                    LaboratoryTest.test_name.ilike(pattern),
                    LaboratoryTest.result_value.ilike(pattern),
                )
            )

        if sample_id:
            filters.append(LaboratoryTest.sample_id == sample_id)

        if status:
            filters.append(LaboratoryTest.status == status)

        if created_from:
            filters.append(LaboratoryTest.created_at >= created_from)

        if created_to:
            filters.append(LaboratoryTest.created_at <= created_to)

        columns = {
            "created_at": LaboratoryTest.created_at,
            "updated_at": LaboratoryTest.updated_at,
            "test_name": LaboratoryTest.test_name,
            "status": LaboratoryTest.status,
        }

        column = columns[sort_by]

        ordering = column.asc() if sort_order == "asc" else column.desc()

        total = int(
            self.db.scalar(
                select(func.count()).select_from(LaboratoryTest).where(*filters)
            )
            or 0
        )

        items = list(
            self.db.scalars(
                select(LaboratoryTest)
                .where(*filters)
                .order_by(
                    ordering,
                    LaboratoryTest.id,
                )
                .offset((page - 1) * limit)
                .limit(limit)
            ).all()
        )

        return items, total
