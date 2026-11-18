"""events: category

Revision ID: 5b1c7e9a2d3f
Revises: d8ede60d8d7c
Create Date: 2026-11-18 00:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "5b1c7e9a2d3f"
down_revision: str | None = "d8ede60d8d7c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("events", sa.Column("category", sa.String(length=50), nullable=True))
    op.create_index(op.f("ix_events_category"), "events", ["category"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_column("events", "category")
