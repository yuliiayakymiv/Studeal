"""saved events

Revision ID: 7c2d4e9f1a6b
Revises: 5b1c7e9a2d3f
Create Date: 2026-11-19 00:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7c2d4e9f1a6b"
down_revision: str | None = "5b1c7e9a2d3f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "saved_events",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "event_id"),
    )


def downgrade() -> None:
    op.drop_table("saved_events")
