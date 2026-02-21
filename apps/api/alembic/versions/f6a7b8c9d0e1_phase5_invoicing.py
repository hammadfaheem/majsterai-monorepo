"""phase5_invoicing

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invoice",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("index", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("date", sa.BigInteger(), nullable=True),
        sa.Column("due_date", sa.BigInteger(), nullable=True),
        sa.Column("tax_type", sa.String(length=20), nullable=True),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("accept_credit_card", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("reminder_sent", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("approved_at", sa.BigInteger(), nullable=True),
        sa.Column("sent_at", sa.BigInteger(), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.BigInteger(), nullable=True),
        sa.Column("is_sync_failed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "invoice_item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoice.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "invoice_payment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("date", sa.BigInteger(), nullable=True),
        sa.Column("method", sa.String(length=50), nullable=True),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("account", sa.String(length=255), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoice.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "invoice_settings",
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("tax_rate", sa.Float(), nullable=True),
        sa.Column("index_prefix", sa.String(length=20), nullable=True),
        sa.Column("payment_terms", sa.String(length=100), nullable=True),
        sa.Column("show_logo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("accent_color", sa.String(length=20), nullable=True),
        sa.Column("footer", sa.Text(), nullable=True),
        sa.Column("enable_voice", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sync_to_xero", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sync_from_xero", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reminder_timing", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("org_id"),
    )
    op.create_table(
        "invoice_note",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("file", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoice.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "invoice_activity_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("event", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoice.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("invoice_activity_log")
    op.drop_table("invoice_note")
    op.drop_table("invoice_settings")
    op.drop_table("invoice_payment")
    op.drop_table("invoice_item")
    op.drop_table("invoice")
