"""add virtual_assistant_phone table

Revision ID: p11_virtual_assistant_phone
Revises: h2i3j4k5l6m7
Create Date: 2026-04-04
"""

import sqlalchemy as sa
from alembic import op

revision = "p11_virtual_assistant_phone"
down_revision = "h2i3j4k5l6m7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "virtual_assistant_phone",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        # Core Twilio identity
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("twilio_sid", sa.String(34), nullable=False),
        # Org / agent assignment
        sa.Column("org_id", sa.String(191), nullable=False),
        sa.Column("agent_id", sa.BigInteger(), nullable=False),
        sa.Column("assigned_by", sa.String(191), nullable=False),
        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(20), nullable=True, server_default="pending"),
        sa.Column("type", sa.String(255), nullable=True),
        # SMS settings
        sa.Column("is_sms_listening", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("global_sms_auto_reply", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "default_lead_sms_auto_reply", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        # Twilio Elastic SIP Trunk fields
        sa.Column("trunk_sid", sa.String(255), nullable=True),
        sa.Column("sip_domain", sa.String(255), nullable=True),
        sa.Column("sip_username", sa.String(255), nullable=True),
        sa.Column("sip_password", sa.String(255), nullable=True),
        sa.Column("credential_list_sid", sa.String(255), nullable=True),
        sa.Column("trunk_termination_url", sa.String(255), nullable=True),
        # LiveKit SIP fields
        sa.Column("livekit_trunk_id", sa.String(255), nullable=True),
        sa.Column("livekit_inbound_trunk_id", sa.String(255), nullable=True),
        sa.Column("livekit_outbound_trunk_id", sa.String(255), nullable=True),
        sa.Column("livekit_inbound_dispatch_rule_id", sa.String(255), nullable=True),
        # Recording
        sa.Column("recording_enabled", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("recording_public", sa.Boolean(), nullable=True, server_default=sa.false()),
        # Per-org LiveKit overrides
        sa.Column("custom_credentials", sa.JSON(), nullable=True),
        # Soft-delete / timestamps
        sa.Column("schedule_deleted_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.BigInteger(), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number"),
        sa.UniqueConstraint("twilio_sid"),
        sa.UniqueConstraint("org_id"),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], name="fk_vap_org_id"),
        sa.ForeignKeyConstraint(["agent_id"], ["agent.id"], name="fk_vap_agent_id"),
    )


def downgrade() -> None:
    op.drop_table("virtual_assistant_phone")
