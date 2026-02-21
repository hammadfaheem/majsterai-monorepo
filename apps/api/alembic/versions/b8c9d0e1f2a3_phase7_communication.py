"""phase7_communication

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "call",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("recording_url", sa.String(length=500), nullable=True),
        sa.Column("transcripts", sa.JSON(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("direction", sa.String(length=20), nullable=True),
        sa.Column("key_points", sa.JSON(), nullable=True),
        sa.Column("recording_url_status", sa.String(length=20), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "message_thread",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("inquiry_id", sa.String(length=36), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["inquiry_id"], ["inquiry.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "message",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("direction", sa.String(length=20), nullable=True),
        sa.Column("sender_type", sa.String(length=20), nullable=True),
        sa.Column("receiver_type", sa.String(length=20), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("sentiment", sa.String(length=20), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_points", sa.JSON(), nullable=True),
        sa.Column("attachments", sa.JSON(), nullable=True),
        sa.Column("message_thread_id", sa.String(length=36), nullable=True),
        sa.Column("replied_by_ai", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("content_storage", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["message_thread_id"], ["message_thread.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chatbot",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chatbot_thread",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("transcripts", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.BigInteger(), nullable=True),
        sa.Column("ended_at", sa.BigInteger(), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "call_now",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("country_restriction_type", sa.String(length=20), nullable=True),
        sa.Column("countries", sa.JSON(), nullable=True),
        sa.Column("dial_code_restriction_type", sa.String(length=20), nullable=True),
        sa.Column("dial_codes", sa.JSON(), nullable=True),
        sa.Column("blocked_phone_numbers", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "webform",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("inputs", sa.JSON(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("subtitle", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "webform_submission",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("webform_id", sa.String(length=36), nullable=False),
        sa.Column("submission_data", sa.JSON(), nullable=True),
        sa.Column("submitted_at", sa.BigInteger(), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["webform_id"], ["webform.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("webform_submission")
    op.drop_table("webform")
    op.drop_table("call_now")
    op.drop_table("chatbot_thread")
    op.drop_table("chatbot")
    op.drop_table("message")
    op.drop_table("message_thread")
    op.drop_table("call")
