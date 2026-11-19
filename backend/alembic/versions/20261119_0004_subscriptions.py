"""subscriptions, followed venues, deal notifications

Revision ID: 8d3e5f0a2b7c
Revises: 7c2d4e9f1a6b
Create Date: 2026-11-19 14:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "8d3e5f0a2b7c"
down_revision: str | None = "7c2d4e9f1a6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "followed_venues",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_followed_venues_user_name"),
    )
    op.create_index("ix_followed_venues_user_id", "followed_venues", ["user_id"])
    op.create_table(
        "deal_notifications",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("deal_id", sa.Uuid(), nullable=False),
        sa.Column(
            "sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "deal_id"),
    )


def downgrade() -> None:
    op.drop_table("deal_notifications")
    op.drop_index("ix_followed_venues_user_id", table_name="followed_venues")
    op.drop_table("followed_venues")
    op.drop_table("subscriptions")
