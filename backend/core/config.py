"""Application configuration and settings.

[Task]: T009
[From]: specs/001-user-auth/plan.md

[Task]: T003
[From]: specs/004-ai-chatbot/plan.md

Extended for ChatKit migration with Gemini OpenAI-compatible endpoint.
[From]: specs/010-chatkit-migration/tasks.md - T008
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
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"  # ChatKit migration

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


def get_gemini_client():
    """Create and return an AsyncOpenAI client configured for Gemini.

    [From]: specs/010-chatkit-migration/research.md - Section 2
    [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts

    This client uses Gemini's OpenAI-compatible endpoint, allowing us to use
    the OpenAI SDK and Agents SDK with Gemini as the LLM provider.

    Returns:
        AsyncOpenAI: OpenAI client configured for Gemini

    Example:
        from openai import AsyncOpenAI
        from agents import set_default_openai_client

        client = get_gemini_client()
        set_default_openai_client(client)
    """
    from openai import AsyncOpenAI

    settings = get_settings()

    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please set it in your environment or .env file. "
            "Get your API key from https://aistudio.google.com"
        )

    return AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
    )
