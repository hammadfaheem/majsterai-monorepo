"""phase8_notifications

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notification_type",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("value", sa.String(length=100), nullable=False),
        sa.Column("template", sa.JSON(), nullable=True),
        sa.Column("channels", sa.JSON(), nullable=True),
        sa.Column("schedule", sa.JSON(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "notification_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("target_id", sa.String(length=36), nullable=True),
        sa.Column("sent", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "org_notification_recipient",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("sms", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("sources", sa.JSON(), nullable=True),
        sa.Column("all_tags", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["membership.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "reminder",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("appointment_id", sa.String(length=36), nullable=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("datetime", sa.BigInteger(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("notes_type", sa.String(length=20), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointment.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("reminder")
    op.drop_table("org_notification_recipient")
    op.drop_table("notification_log")
    op.drop_table("notification_type")
