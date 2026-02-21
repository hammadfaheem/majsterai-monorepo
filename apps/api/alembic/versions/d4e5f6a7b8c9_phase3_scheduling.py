"""phase3_scheduling

Revision ID: d4e5f6a7b8c9
Revises: c8d9e0f1a2b3
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c8d9e0f1a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schedule",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("time_zone", sa.String(length=50), nullable=False, server_default="UTC"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "department",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_schedule_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("max_concurrent_calls", sa.Integer(), nullable=True),
        sa.Column("escalation_timeout", sa.Integer(), nullable=True),
        sa.Column("escalation_settings", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["default_schedule_id"], ["schedule.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("schedule", sa.Column("department_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_schedule_department", "schedule", "department", ["department_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "availability",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=False),
        sa.Column("days", sa.JSON(), nullable=True),
        sa.Column("start_time", sa.BigInteger(), nullable=True),
        sa.Column("end_time", sa.BigInteger(), nullable=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedule.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "department_assignee",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["department.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["membership.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "selected_calendar",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("credential_id", sa.String(length=255), nullable=True),
        sa.Column("calendar_id", sa.String(length=255), nullable=True),
        sa.Column("calendar_name", sa.String(length=255), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active_for_conflict_check", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("channel_id", sa.String(length=255), nullable=True),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("channel_expiration", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["membership.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "appointment",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("serial_id", sa.Integer(), nullable=True),
        sa.Column("start", sa.BigInteger(), nullable=False),
        sa.Column("end", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="scheduled"),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("inquiry_id", sa.String(length=36), nullable=True),
        sa.Column("trade_service_id", sa.Integer(), nullable=True),
        sa.Column("lead_address_id", sa.Integer(), nullable=True),
        sa.Column("selected_calendar_id", sa.Integer(), nullable=True),
        sa.Column("attendees", sa.JSON(), nullable=True),
        sa.Column("is_rescheduled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_created_by_sophiie", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("customer_notes", sa.Text(), nullable=True),
        sa.Column("customer_cancellation_reason", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("photos", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["inquiry_id"], ["inquiry.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["selected_calendar_id"], ["selected_calendar.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "appointment_assignee",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("appointment_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointment.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "appointment_crm_identifiers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("appointment_id", sa.String(length=36), nullable=False),
        sa.Column("crm_source", sa.String(length=50), nullable=False),
        sa.Column("identifier_type", sa.String(length=50), nullable=False),
        sa.Column("crm_identifier", sa.String(length=255), nullable=False),
        sa.Column("last_sync_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointment.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("appointment_crm_identifiers")
    op.drop_table("appointment_assignee")
    op.drop_table("appointment")
    op.drop_table("selected_calendar")
    op.drop_table("department_assignee")
    op.drop_table("availability")
    op.drop_constraint("fk_schedule_department", "schedule", type_="foreignkey")
    op.drop_column("schedule", "department_id")
    op.drop_table("department")
    op.drop_table("schedule")
