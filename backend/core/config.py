"""Application configuration and settings.

[Task]: T009
[From]: specs/001-user-auth/plan.md
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 7

    # CORS
    frontend_url: str

    # Environment
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        # Support legacy Better Auth environment variables
        env_prefix="",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings

    Raises:
        ValueError: If required environment variables are not set
    """
    return Settings()
