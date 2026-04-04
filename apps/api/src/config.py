"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file (apps/api/src/config.py → apps/api/.env)
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://majsterai:majsterai_dev@localhost:5432/majsterai"

    # Auth
    jwt_secret: str = "change-this-secret-in-production"
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


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
