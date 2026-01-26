"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://majsterai:majsterai_dev@localhost:5432/majsterai"

    # LiveKit
    livekit_url: str = "wss://your-project.livekit.cloud"
    livekit_api_key: str = ""
    livekit_api_secret: str = ""

    # Twilio (optional for now)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
