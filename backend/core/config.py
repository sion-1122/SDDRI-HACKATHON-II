"""Application configuration and settings.

[Task]: T009
[From]: specs/001-user-auth/plan.md

[Task]: T003
[From]: specs/004-ai-chatbot/plan.md
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

    # Gemini API (Phase III: AI Chatbot)
    gemini_api_key: str | None = None  # Optional for migration/setup
    gemini_model: str = "gemini-2.0-flash-exp"

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
