"""Trade / business service ORM models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utc_now_ms


class TradeCategory(Base):
    """Category of trade (e.g. plumbing, electrical)."""

    __tablename__ = "trade_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))  # service, product
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class TradeService(Base):
    """Service offered (e.g. drain cleaning)."""

    __tablename__ = "trade_service"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    duration: Mapped[int | None] = mapped_column(Integer)  # minutes
    duration_unit: Mapped[str | None] = mapped_column(String(20))
    followup_questions: Mapped[list[Any] | None] = mapped_column(JSON)
    pricing_mode: Mapped[str | None] = mapped_column(String(20))  # fixed, hourly, quote
    fixed_price: Mapped[int | None] = mapped_column(Integer)  # cents
    hourly_rate: Mapped[int | None] = mapped_column(Integer)
    min_price: Mapped[int | None] = mapped_column(Integer)
    max_price: Mapped[int | None] = mapped_column(Integer)
    call_out_fee: Mapped[int | None] = mapped_column(Integer)
    plus_gst: Mapped[bool] = mapped_column(Boolean, default=False)
    plus_materials: Mapped[bool] = mapped_column(Boolean, default=False)
    is_disclose_price: Mapped[bool] = mapped_column(Boolean, default=True)
    custom_price_response: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trade_category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("trade_category.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class TradeProduct(Base):
    """Product offered."""

    __tablename__ = "trade_product"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[int | None] = mapped_column(Integer)  # cents
    max_price: Mapped[int | None] = mapped_column(Integer)
    pricing_type: Mapped[str | None] = mapped_column(String(20))
    faqs: Mapped[list[Any] | None] = mapped_column(JSON)
    is_disclose_price: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trade_category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("trade_category.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class TradePricing(Base):
    """Pricing configuration per trade category."""

    __tablename__ = "trade_pricing"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    trade_category_id: Mapped[int] = mapped_column(ForeignKey("trade_category.id"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    call_out_fee: Mapped[int | None] = mapped_column(Integer)
    hour_rate: Mapped[int | None] = mapped_column(Integer)
    tax_rate: Mapped[float | None] = mapped_column(Float)
    after_hours: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class TradeModality(Base):
    """Service area / modality (e.g. mobile, location-based)."""

    __tablename__ = "trade_modality"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))
    address_id: Mapped[int | None] = mapped_column(Integer)
    origin_suburb: Mapped[str | None] = mapped_column(String(255))
    travel_distance_km: Mapped[int | None] = mapped_column(Integer)
    service_area: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    postcode_list: Mapped[list[Any] | None] = mapped_column(JSON)
    exception_postcode_list: Mapped[list[Any] | None] = mapped_column(JSON)
    landmark: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
