"""phase2_agent_schema_extensions

Revision ID: c8d9e0f1a2b3
Revises: b7b7548ea359
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, Sequence[str], None] = "b7b7548ea359"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agent: add variables (JSON)
    op.add_column("agent", sa.Column("variables", sa.JSON(), nullable=True))

    # CallHistory: add new columns
    op.add_column("call_history", sa.Column("twilio_call_sid", sa.String(length=255), nullable=True))
    op.add_column("call_history", sa.Column("function_calls", sa.JSON(), nullable=True))
    op.add_column("call_history", sa.Column("cost", sa.JSON(), nullable=True))
    op.add_column("call_history", sa.Column("total_metrics", sa.JSON(), nullable=True))
    op.add_column("call_history", sa.Column("variables", sa.JSON(), nullable=True))

    # scenario (depends on organization)
    op.create_table(
        "scenario",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("response", sa.Text(), nullable=True),
        sa.Column("trigger_type", sa.String(length=20), nullable=True),
        sa.Column("trigger_value", sa.String(length=255), nullable=True),
        sa.Column("questions", sa.JSON(), nullable=True),
        sa.Column("outcome", sa.JSON(), nullable=True),
        sa.Column("trade_service_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # scenario_outcome_template (depends on scenario)
    op.create_table(
        "scenario_outcome_template",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenario.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # transfer (depends on organization, scenario)
    op.create_table(
        "transfer",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.Column("destination_type", sa.String(length=50), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("conditions", sa.JSON(), nullable=True),
        sa.Column("summary_format", sa.Text(), nullable=True),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("scenario_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenario.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # agent_extra_prompt_version (depends on agent, user)
    op.create_table(
        "agent_extra_prompt_version",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agent.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # agent_active_session (no FK to our schema)
    op.create_table(
        "agent_active_session",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("room_name", sa.String(length=255), nullable=False),
        sa.Column("call_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("from_number", sa.String(length=20), nullable=True),
        sa.Column("to_number", sa.String(length=20), nullable=True),
        sa.Column("type", sa.String(length=20), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_name", name="uq_agent_active_session_room_name"),
    )

    # room (depends on user)
    op.create_table(
        "room",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("last_active_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("room")
    op.drop_table("agent_active_session")
    op.drop_table("agent_extra_prompt_version")
    op.drop_table("transfer")
    op.drop_table("scenario_outcome_template")
    op.drop_table("scenario")
    op.drop_column("call_history", "variables")
    op.drop_column("call_history", "total_metrics")
    op.drop_column("call_history", "cost")
    op.drop_column("call_history", "function_calls")
    op.drop_column("call_history", "twilio_call_sid")
    op.drop_column("agent", "variables")
