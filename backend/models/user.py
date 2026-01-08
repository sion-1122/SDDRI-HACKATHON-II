"""User model - minimal entity for task ownership."""
import uuid
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User entity representing a task owner.

    This is a minimal implementation for Phase 1.
    Authentication and authorization will be added in future phases.
    """

    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
