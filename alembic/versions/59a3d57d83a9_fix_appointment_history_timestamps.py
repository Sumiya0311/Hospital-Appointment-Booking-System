"""fix appointment history timestamps

Revision ID: 59a3d57d83a9
Revises: 2d86bd521639
Create Date: 2026-10-13 11:36:11.864268
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = "59a3d57d83a9"
down_revision: Union[str, Sequence[str], None] = "2d86bd521639"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename changed_at and add updated_at."""

    op.alter_column(
        "appointment_history",
        "changed_at",
        new_column_name="created_at",
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )

    op.add_column(
        "appointment_history",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Reverse the timestamp changes."""

    op.drop_column(
        "appointment_history",
        "updated_at",
    )

    op.alter_column(
        "appointment_history",
        "created_at",
        new_column_name="changed_at",
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )