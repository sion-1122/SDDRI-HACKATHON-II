"""Task model and related I/O classes."""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Database table model for Task entity."""

    __tablename__ = "tasks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        index=True
    )
    title: str = Field(max_length=255)
    description: Optional[str] = Field(
        default=None,
        max_length=2000
    )
    due_date: Optional[datetime] = Field(
        default=None,
        index=True
    )
    priority: str = Field(
        default="medium",
        max_length=10
    )
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class TaskCreate(SQLModel):
    """Request model for creating a task.

    Validates input data when creating a new task.
    """
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[datetime] = None
    priority: str = Field(default="medium", max_length=10)
    completed: bool = False


class TaskUpdate(SQLModel):
    """Request model for updating a task.

    All fields are optional - only provided fields will be updated.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[datetime] = None
    priority: Optional[str] = Field(default=None, max_length=10)
    completed: Optional[bool] = None


class TaskRead(SQLModel):
    """Response model for task data.

    Used for serializing task data in API responses.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str] | None
    due_date: Optional[datetime] | None
    priority: str
    completed: bool
    created_at: datetime
    updated_at: datetime
