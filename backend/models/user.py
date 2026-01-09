"""User model and authentication schemas for FastAPI backend.

[Task]: T016
[From]: specs/001-user-auth/data-model.md
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base User model with common fields."""
    email: str = Field(unique=True, index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase, table=True):
    """Full User model with database table.

    FastAPI backend handles ALL authentication logic:
    - Password hashing (bcrypt)
    - JWT token generation/verification
    - User creation and validation
    """
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(max_length=255)  # bcrypt hash, not plaintext


class UserCreate(SQLModel):
    """Schema for user registration.

    Frontend sends plaintext password, backend hashes it before storage.
    """
    email: str
    password: str  # Plaintext password, will be hashed before storage


class UserRead(SQLModel):
    """Schema for returning user data (excludes password)."""
    id: uuid.UUID
    email: str
    created_at: datetime
    updated_at: datetime


class UserLogin(SQLModel):
    """Schema for user login."""
    email: str
    password: str
