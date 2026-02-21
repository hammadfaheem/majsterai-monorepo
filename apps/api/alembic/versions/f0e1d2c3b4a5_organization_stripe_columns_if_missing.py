"""organization_stripe_columns_if_missing

Add stripe_plan and stripe_customer_id to organization if missing (e.g. table
was created by create_all before these columns were in the model).

Revision ID: f0e1d2c3b4a5
Revises: d0e1f2a3b4c5
Create Date: 2026-02-13

"""
from typing import Sequence, Union

from alembic import op


revision: str = "f0e1d2c3b4a5"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL: add columns only if they don't exist (idempotent)
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS stripe_plan VARCHAR(50)"
    )
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255)"
    )


def downgrade() -> None:
    op.drop_column("organization", "stripe_customer_id")
    op.drop_column("organization", "stripe_plan")
