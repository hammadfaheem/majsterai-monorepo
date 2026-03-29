"""phase10 calendar extensions

Adds columns missing from initial create_all schema:
- schedule.org_id, schedule.created_at, schedule.updated_at
- appointment.reference_id, appointment.deleted_at
- selected_calendar.org_id, selected_calendar.integration, selected_calendar.next_async_token

Revision ID: h2i3j4k5l6m7
Revises: (none — first alembic migration on this DB)
Create Date: 2026-03-28
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "h2i3j4k5l6m7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # schedule — add org_id, created_at, updated_at (present in model but missing from DB)
    op.add_column("schedule", sa.Column("org_id", sa.String(36), nullable=True))
    op.add_column("schedule", sa.Column("created_at", sa.BigInteger(), nullable=True))
    op.add_column("schedule", sa.Column("updated_at", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fk_schedule_org_id", "schedule", "organization", ["org_id"], ["id"]
    )

    # appointment — add reference_id and deleted_at
    op.add_column("appointment", sa.Column("reference_id", sa.String(255), nullable=True))
    op.add_column("appointment", sa.Column("deleted_at", sa.BigInteger(), nullable=True))

    # selected_calendar — add org_id, integration, next_async_token
    op.add_column("selected_calendar", sa.Column("org_id", sa.String(36), nullable=True))
    op.add_column("selected_calendar", sa.Column("integration", sa.String(20), nullable=True))
    op.add_column("selected_calendar", sa.Column("next_async_token", sa.String(500), nullable=True))
    op.create_foreign_key(
        "fk_selected_calendar_org_id", "selected_calendar", "organization", ["org_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_selected_calendar_org_id", "selected_calendar", type_="foreignkey")
    op.drop_column("selected_calendar", "next_async_token")
    op.drop_column("selected_calendar", "integration")
    op.drop_column("selected_calendar", "org_id")

    op.drop_column("appointment", "deleted_at")
    op.drop_column("appointment", "reference_id")

    op.drop_constraint("fk_schedule_org_id", "schedule", type_="foreignkey")
    op.drop_column("schedule", "updated_at")
    op.drop_column("schedule", "created_at")
    op.drop_column("schedule", "org_id")
