"""user_columns_if_missing

Add user.phone, role, email_verified, phone_verified if missing (idempotent).
Useful when DB was created without running phase1 or table was created elsewhere.

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op


revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL: ADD COLUMN IF NOT EXISTS (idempotent)
    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS phone VARCHAR(20)')
    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS role VARCHAR(20)')
    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_verified BIGINT')
    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS phone_verified BIGINT')


def downgrade() -> None:
    op.drop_column("user", "phone_verified")
    op.drop_column("user", "email_verified")
    op.drop_column("user", "role")
    op.drop_column("user", "phone")
