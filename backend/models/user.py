"""User model for BetterAuth integration.

[Task]: T024
[From]: specs/001-user-auth/data-model.md
"""
import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User account entity managed by BetterAuth.

    BetterAuth handles user creation, email/password storage,
    and JWT token generation. This model defines the database schema.

    Note: BetterAuth creates and manages this table automatically.
    The model is defined here for SQLModel metadata and type safety.
    """

    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255
    )
    password_hash: str = Field(
        max_length=255
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )
