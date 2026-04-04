"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file (apps/api/src/config.py → apps/api/.env)
_ENV_FILE = Path(__file__).parent.parent / ".env"

_INSECURE_JWT_SECRET = "change-this-secret-in-production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    environment: str = "development"
    # Defaults to False — must be explicitly set True for local dev
    debug: bool = False

    # Database
    database_url: str = "postgresql://majsterai:majsterai_dev@localhost:5432/majsterai"

    # Auth — no default; app refuses to start if this is missing or insecure
    jwt_secret: str
    jwt_expiration_hours: int = 24

    # LiveKit
    livekit_url: str = "wss://your-project.livekit.cloud"
    livekit_api_key: str = ""
    livekit_api_secret: str = ""

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

    # LiveKit SIP
    livekit_sip_domain: str = "sip.livekit.cloud"

    # Public base URL (used for Twilio webhook URLs)
    base_url: str = "https://your-api.example.com"

    # CORS – add production origins via CORS_ORIGINS env var (comma-separated)
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    # Platform admin: set this email to grant SUPERADMIN role on startup
    superadmin_email: str | None = None

    # Google Calendar OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_must_be_secure(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("JWT_SECRET must be set")
        if v.strip() == _INSECURE_JWT_SECRET:
            raise ValueError(
                "JWT_SECRET is still set to the placeholder value. "
                "Generate a secure random secret (e.g. openssl rand -hex 32) "
                "and set it in your .env file."
            )
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    @model_validator(mode="after")
    def production_requires_explicit_config(self) -> "Settings":
        if self.environment == "production":
            if self.debug:
                raise ValueError("DEBUG must be False in production")
            if self.base_url == "https://your-api.example.com":
                raise ValueError("BASE_URL must be set to the real API URL in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
