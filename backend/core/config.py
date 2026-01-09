"""Application configuration and settings.

[Task]: T009
[From]: specs/001-user-auth/plan.md
"""
import os
from pydantic_settings import BaseSettings
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

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False
        # Map environment variable names to field names
        fields = {
            "database_url": {"env": "DATABASE_URL"},
            "jwt_secret": {"env": "JWT_SECRET"},
            "frontend_url": {"env": "FRONTEND_URL"},
            "environment": {"env": "ENVIRONMENT"},
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings

    Raises:
        ValueError: If required environment variables are not set
    """
    return Settings()
