"""phase4_trade_services

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trade_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "trade_service",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("duration_unit", sa.String(length=20), nullable=True),
        sa.Column("followup_questions", sa.JSON(), nullable=True),
        sa.Column("pricing_mode", sa.String(length=20), nullable=True),
        sa.Column("fixed_price", sa.Integer(), nullable=True),
        sa.Column("hourly_rate", sa.Integer(), nullable=True),
        sa.Column("min_price", sa.Integer(), nullable=True),
        sa.Column("max_price", sa.Integer(), nullable=True),
        sa.Column("call_out_fee", sa.Integer(), nullable=True),
        sa.Column("plus_gst", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("plus_materials", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_disclose_price", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("custom_price_response", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("trade_category_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trade_category_id"], ["trade_category.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "trade_product",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("max_price", sa.Integer(), nullable=True),
        sa.Column("pricing_type", sa.String(length=20), nullable=True),
        sa.Column("faqs", sa.JSON(), nullable=True),
        sa.Column("is_disclose_price", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("trade_category_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trade_category_id"], ["trade_category.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "trade_pricing",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("trade_category_id", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("call_out_fee", sa.Integer(), nullable=True),
        sa.Column("hour_rate", sa.Integer(), nullable=True),
        sa.Column("tax_rate", sa.Float(), nullable=True),
        sa.Column("after_hours", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["trade_category_id"], ["trade_category.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "trade_modality",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("address_id", sa.Integer(), nullable=True),
        sa.Column("origin_suburb", sa.String(length=255), nullable=True),
        sa.Column("travel_distance_km", sa.Integer(), nullable=True),
        sa.Column("service_area", sa.JSON(), nullable=True),
        sa.Column("postcode_list", sa.JSON(), nullable=True),
        sa.Column("exception_postcode_list", sa.JSON(), nullable=True),
        sa.Column("landmark", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("organization", sa.Column("main_trade_category_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_organization_main_trade_category",
        "organization",
        "trade_category",
        ["main_trade_category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_organization_main_trade_category", "organization", type_="foreignkey")
    op.drop_column("organization", "main_trade_category_id")
    op.drop_table("trade_modality")
    op.drop_table("trade_pricing")
    op.drop_table("trade_product")
    op.drop_table("trade_service")
    op.drop_table("trade_category")
