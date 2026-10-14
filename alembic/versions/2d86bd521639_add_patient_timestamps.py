"""add patient timestamps

Revision ID: 2d86bd521639
Revises: 1a7cced02d26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "2d86bd521639"
down_revision: Union[str, Sequence[str], None] = "1a7cced02d26"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "phone",
        existing_type=mysql.VARCHAR(length=10),
        type_=sa.String(length=15),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "phone",
        existing_type=sa.String(length=15),
        type_=mysql.VARCHAR(length=10),
        existing_nullable=False,
    )

    op.alter_column(
        "patients",
        "phone",
        existing_type=sa.String(length=15),
        type_=mysql.VARCHAR(length=10),
        existing_nullable=False,
    )