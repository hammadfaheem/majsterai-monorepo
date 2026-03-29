"""phase10 calendar extensions

Adds:
- appointment.reference_id   — external calendar event ID for deduplication
- appointment.deleted_at     — soft delete (Google cancelled events need to find the row)
- selected_calendar.org_id   — org-level ownership
- selected_calendar.integration — provider tag (google, outlook)
- selected_calendar.next_async_token — Google incremental sync token

Revision ID: h2i3j4k5l6m7
Revises: c9d0e1f2a3b4_phase8_notifications
Create Date: 2026-03-28
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "h2i3j4k5l6m7"
down_revision = "c9d0e1f2a3b4_phase8_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # appointment — add reference_id and deleted_at
    with op.batch_alter_table("appointment") as batch_op:
        batch_op.add_column(
            sa.Column("reference_id", sa.String(255), nullable=True),
            insert_after="photos",
        )
        batch_op.add_column(
            sa.Column("deleted_at", sa.BigInteger(), nullable=True),
            insert_after="updated_at",
        )

    # selected_calendar — add org_id, integration, next_async_token
    with op.batch_alter_table("selected_calendar") as batch_op:
        batch_op.add_column(
            sa.Column("org_id", sa.String(36), sa.ForeignKey("organization.id"), nullable=True),
            insert_after="id",
        )
        batch_op.add_column(
            sa.Column("integration", sa.String(20), nullable=True),
            insert_after="calendar_name",
        )
        batch_op.add_column(
            sa.Column("next_async_token", sa.String(500), nullable=True),
            insert_after="last_synced_at",
        )


def downgrade() -> None:
    with op.batch_alter_table("selected_calendar") as batch_op:
        batch_op.drop_column("next_async_token")
        batch_op.drop_column("integration")
        batch_op.drop_column("org_id")

    with op.batch_alter_table("appointment") as batch_op:
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("reference_id")
