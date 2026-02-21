"""phase6_lead_extensions

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lead", sa.Column("suburb", sa.String(length=255), nullable=True))
    op.add_column("lead", sa.Column("business_name", sa.String(length=255), nullable=True))
    op.add_column("lead", sa.Column("socials", sa.JSON(), nullable=True))
    op.add_column("lead", sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("lead", sa.Column("is_phone_valid", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("lead", sa.Column("default_lead_address_id", sa.Integer(), nullable=True))
    op.add_column("lead", sa.Column("last_inquiry_id", sa.String(length=36), nullable=True))
    op.add_column("lead", sa.Column("auto_reply_sms", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("lead", sa.Column("has_flagged_inquiry", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("lead", sa.Column("batch_id", sa.String(length=36), nullable=True))
    op.add_column("lead", sa.Column("is_sample", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("inquiry", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("inquiry", sa.Column("source", sa.String(length=50), nullable=True))
    op.add_column("inquiry", sa.Column("is_first_inquiry", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("inquiry", sa.Column("appointment_id", sa.String(length=36), nullable=True))
    op.add_column("inquiry", sa.Column("lead_address_id", sa.Integer(), nullable=True))
    op.add_column("inquiry", sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("inquiry", sa.Column("tag", sa.String(length=50), nullable=True))
    op.add_column("inquiry", sa.Column("flag_reason", sa.String(length=255), nullable=True))
    op.add_column("inquiry", sa.Column("flagged_at", sa.BigInteger(), nullable=True))
    op.add_column("inquiry", sa.Column("flag_issues", sa.JSON(), nullable=True))
    op.add_column("inquiry", sa.Column("outcome_actions", sa.JSON(), nullable=True))
    op.add_column("inquiry", sa.Column("assigned_member_id", sa.String(length=36), nullable=True))
    op.add_column("inquiry", sa.Column("is_manually_reassigned", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_foreign_key("fk_inquiry_appointment", "inquiry", "appointment", ["appointment_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_inquiry_assigned_member", "inquiry", "membership", ["assigned_member_id"], ["id"], ondelete="SET NULL")

    op.add_column("activity", sa.Column("reference_id", sa.String(length=36), nullable=True))
    op.add_column("activity", sa.Column("json_data", sa.JSON(), nullable=True))

    op.add_column("note", sa.Column("appointment_id", sa.String(length=36), nullable=True))
    op.create_foreign_key("fk_note_appointment", "note", "appointment", ["appointment_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "tag_base",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("value", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("external_type", sa.String(length=50), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tag_base_id", sa.String(length=36), nullable=False),
        sa.Column("inquiry_id", sa.String(length=36), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("org_notification_recipient_id", sa.String(length=36), nullable=True),
        sa.Column("member_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["inquiry_id"], ["inquiry.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["membership.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tag_base_id"], ["tag_base.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "task",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("inquiry_id", sa.String(length=36), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("assigned_member_id", sa.String(length=36), nullable=True),
        sa.Column("is_created_by_sophiie", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["assigned_member_id"], ["membership.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["inquiry_id"], ["inquiry.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lead_address",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("address_id", sa.String(length=36), nullable=False),
        sa.Column("lead_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lead_crm_identifiers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("lead_id", sa.String(length=36), nullable=False),
        sa.Column("crm_source", sa.String(length=50), nullable=False),
        sa.Column("identifier_type", sa.String(length=50), nullable=False),
        sa.Column("crm_identifier", sa.String(length=255), nullable=False),
        sa.Column("last_sync_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("lead_crm_identifiers")
    op.drop_table("lead_address")
    op.drop_table("task")
    op.drop_table("tag")
    op.drop_table("tag_base")
    op.drop_constraint("fk_note_appointment", "note", type_="foreignkey")
    op.drop_column("note", "appointment_id")
    op.drop_column("activity", "json_data")
    op.drop_column("activity", "reference_id")
    op.drop_constraint("fk_inquiry_assigned_member", "inquiry", type_="foreignkey")
    op.drop_constraint("fk_inquiry_appointment", "inquiry", type_="foreignkey")
    op.drop_column("inquiry", "is_manually_reassigned")
    op.drop_column("inquiry", "assigned_member_id")
    op.drop_column("inquiry", "outcome_actions")
    op.drop_column("inquiry", "flag_issues")
    op.drop_column("inquiry", "flagged_at")
    op.drop_column("inquiry", "flag_reason")
    op.drop_column("inquiry", "tag")
    op.drop_column("inquiry", "is_read")
    op.drop_column("inquiry", "lead_address_id")
    op.drop_column("inquiry", "appointment_id")
    op.drop_column("inquiry", "is_first_inquiry")
    op.drop_column("inquiry", "source")
    op.drop_column("inquiry", "summary")
    op.drop_column("lead", "is_sample")
    op.drop_column("lead", "batch_id")
    op.drop_column("lead", "has_flagged_inquiry")
    op.drop_column("lead", "auto_reply_sms")
    op.drop_column("lead", "last_inquiry_id")
    op.drop_column("lead", "default_lead_address_id")
    op.drop_column("lead", "is_phone_valid")
    op.drop_column("lead", "read")
    op.drop_column("lead", "socials")
    op.drop_column("lead", "business_name")
    op.drop_column("lead", "suburb")
