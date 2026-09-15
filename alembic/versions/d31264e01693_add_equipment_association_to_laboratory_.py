"""add equipment association to laboratory tests

Revision ID: d31264e01693
Revises: 7e31cdc60bb0
Create Date: 2026-09-15 17:36:42.732098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d31264e01693"
down_revision: Union[str, Sequence[str], None] = "7e31cdc60bb0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "laboratory_tests",
        sa.Column(
            "equipment_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_laboratory_tests_equipment_id",
        "laboratory_tests",
        ["equipment_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_laboratory_tests_equipment_id",
        "laboratory_tests",
        "biomedical_equipment",
        ["equipment_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_laboratory_tests_equipment_id",
        "laboratory_tests",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_laboratory_tests_equipment_id",
        table_name="laboratory_tests",
    )

    op.drop_column(
        "laboratory_tests",
        "equipment_id",
    )