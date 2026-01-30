"""Task model and related I/O classes."""
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel, Column
from pydantic import field_validator
from sqlalchemy import ARRAY, String


class PriorityLevel(str, Enum):
    """Task priority levels.

    Defines the three priority levels for tasks:
    - HIGH: Urgent tasks that need immediate attention
    - MEDIUM: Default priority for normal tasks
    - LOW: Optional tasks that can be done whenever
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


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
    priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM,
        max_length=10
    )
    tags: list[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String), nullable=False),  # PostgreSQL TEXT[] type
    )
    due_date: Optional[datetime] = Field(
        default=None,
        index=True
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
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    tags: list[str] = Field(default=[])
    due_date: Optional[datetime] = None
    completed: bool = False

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tags: max 50 characters per tag, remove duplicates."""
        validated = []
        seen = set()
        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag[:20]}...' exceeds maximum length of 50 characters")
            # Normalize tag: lowercase and strip whitespace
            normalized = tag.strip().lower()
            if not normalized:
                continue
            if normalized not in seen:
                seen.add(normalized)
                validated.append(normalized)
        return validated

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate due date is not more than 10 years in the past."""
        if v is not None:
            # Normalize to UTC timezone-aware datetime for comparison
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                # If input is naive, assume it's UTC
                v = v.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC
                v = v.astimezone(timezone.utc)

            # Allow dates up to 10 years in the past (for historical tasks)
            min_date = now.replace(year=now.year - 10)
            if v < min_date:
                raise ValueError("Due date cannot be more than 10 years in the past")
        return v


class TaskUpdate(SQLModel):
    """Request model for updating a task.

    All fields are optional - only provided fields will be updated.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[PriorityLevel] = None
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate tags: max 50 characters per tag, remove duplicates."""
        if v is None:
            return v
        validated = []
        seen = set()
        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag[:20]}...' exceeds maximum length of 50 characters")
            # Normalize tag: lowercase and strip whitespace
            normalized = tag.strip().lower()
            if not normalized:
                continue
            if normalized not in seen:
                seen.add(normalized)
                validated.append(normalized)
        return validated

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate due date is not more than 10 years in the past."""
        if v is not None:
            # Normalize to UTC timezone-aware datetime for comparison
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                # If input is naive, assume it's UTC
                v = v.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC
                v = v.astimezone(timezone.utc)

            # Allow dates up to 10 years in the past (for historical tasks)
            min_date = now.replace(year=now.year - 10)
            if v < min_date:
                raise ValueError("Due date cannot be more than 10 years in the past")
        return v


class TaskRead(SQLModel):
    """Response model for task data.

    Used for serializing task data in API responses.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str] | None
    priority: PriorityLevel
    tags: list[str]
    due_date: Optional[datetime] | None
    completed: bool
    created_at: datetime
    updated_at: datetime
