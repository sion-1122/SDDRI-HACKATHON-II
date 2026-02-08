"""Thread model for ChatKit integration.

[Task]: T004
[From]: specs/010-chatkit-migration/data-model.md

This model implements ChatKit's thread abstraction for grouping messages
into conversations. It extends the existing Conversation model with
ChatKit-specific fields.

Migration Note: The existing Conversation model serves a similar purpose.
During migration, we can either:
1. Use Thread alongside Conversation (dual model approach)
2. Migrate Conversation to Thread (single model approach)

This implementation uses Thread as the primary model for ChatKit integration.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, JSON as SQLJSON, String as SQLString, Index
from sqlalchemy.dialects.postgresql import JSONB


class Thread(SQLModel, table=True):
    """Thread model representing a ChatKit conversation session.

    ChatKit uses "thread" terminology for conversation grouping.
    A thread contains multiple messages and belongs to a single user.

    [From]: specs/010-chatkit-migration/data-model.md - Thread Entity
    """

    __tablename__ = "threads"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)

    # Optional thread title (ChatKit allows threads to have titles)
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        sa_column=Column(SQLString(255), nullable=True)
    )

    # Thread metadata (tags, settings, etc.) stored as JSONB
    # Note: Using 'thread_metadata' instead of 'metadata' to avoid SQLAlchemy reserved attribute
    thread_metadata: Optional[dict] = Field(
        default=None,
        sa_column=Column("metadata", JSONB, nullable=True),  # Column name in DB is 'metadata'
    )

    # Thread creation timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    # Last message/update timestamp (auto-updated by application logic)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True)
    )

    # Table indexes for query optimization
    __table_args__ = (
        Index('idx_thread_user_id', 'user_id'),
        Index('idx_thread_updated_at', 'user_id', 'updated_at'),  # For sorting conversations by recent activity
    )

    def __repr__(self) -> str:
        return f"<Thread(id={self.id}, user_id={self.user_id}, title={self.title})>"
