"""User domain entity."""

from dataclasses import dataclass


@dataclass
class User:
    """User domain entity."""

    id: str
    email: str
    name: str
    password_hash: str
    created_at: int
    updated_at: int
    deleted_at: int | None = None
    phone: str | None = None
    role: str | None = None  # SUPERADMIN, STAFF, CUSTOMER
    email_verified: int | None = None
    phone_verified: int | None = None
