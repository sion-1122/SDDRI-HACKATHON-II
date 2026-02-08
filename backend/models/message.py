"""Message model for AI chatbot.

[Task]: T006
[From]: specs/004-ai-chatbot/plan.md

Extended for ChatKit integration with thread_id support.
[From]: specs/010-chatkit-migration/tasks.md - T005
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, Text, String as SQLString, Index
from sqlalchemy.dialects.postgresql import JSONB
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum.

    Extended to include 'system' role for ChatKit compatibility.
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"  # Added for ChatKit compatibility


class Message(SQLModel, table=True):
    """Message model representing a single message in a conversation.

    Messages can be from the user, the AI assistant, or system.
    All messages are persisted to enable conversation history replay.

    ChatKit Migration:
    - Added thread_id foreign key to Thread model
    - Added tool_calls JSONB field for function call metadata
    - conversation_id retained for backward compatibility (can be removed after migration)

    [From]: specs/010-chatkit-migration/data-model.md - Message Entity
    """

    __tablename__ = "message"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Legacy conversation_id (retained for backward compatibility during migration)
    conversation_id: Optional[uuid.UUID] = Field(default=None, foreign_key="conversation.id", index=True)

    # New thread_id for ChatKit integration
    thread_id: Optional[uuid.UUID] = Field(default=None, foreign_key="threads.id", index=True)

    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    role: MessageRole = Field(default=MessageRole.USER, sa_column=Column(SQLString(10), nullable=False, index=True))
    content: str = Field(
        ...,
        sa_column=Column(Text, nullable=False),
        max_length=10000  # FR-042: Maximum message length
    )

    # Tool call metadata for ChatKit function calls
    # Stores OpenAI-compatible tool call format
    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True)
    )

    # Table indexes for query optimization
    __table_args__ = (
        Index('idx_message_conversation_created', 'conversation_id', 'created_at'),
        Index('idx_message_thread_created', 'thread_id', 'created_at'),  # Added for ChatKit
    )
