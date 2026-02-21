"""organization_remaining_columns_if_missing

Add all remaining organization columns if missing (default_schedule_id,
public_scheduler_configurations, tag, seats, addons, main_trade_category_id).
Idempotent for DBs created without full phase1 schema.

Revision ID: g1f2e3d4c5b6a
Revises: f0e1d2c3b4a5
Create Date: 2026-02-13

"""
from typing import Sequence, Union

from alembic import op


revision: str = "g1f2e3d4c5b6a"
down_revision: Union[str, Sequence[str], None] = "f0e1d2c3b4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL: add columns only if they don't exist (idempotent)
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS default_schedule_id INTEGER"
    )
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS public_scheduler_configurations JSONB"
    )
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS tag VARCHAR(50)"
    )
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS seats INTEGER"
    )
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS addons JSONB"
    )
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS main_trade_category_id INTEGER"
    )


def downgrade() -> None:
    op.drop_column("organization", "main_trade_category_id")
    op.drop_column("organization", "addons")
    op.drop_column("organization", "seats")
    op.drop_column("organization", "tag")
    op.drop_column("organization", "public_scheduler_configurations")
    op.drop_column("organization", "default_schedule_id")
