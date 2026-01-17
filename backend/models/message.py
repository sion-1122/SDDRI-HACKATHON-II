"""Message model for AI chatbot.

[Task]: T006
[From]: specs/004-ai-chatbot/plan.md
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, Text, String as SQLString, Index
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message model representing a single message in a conversation.

    Messages can be from the user or the AI assistant.
    All messages are persisted to enable conversation history replay.
    """

    __tablename__ = "message"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    role: MessageRole = Field(default=MessageRole.USER, sa_column=Column(SQLString(10), nullable=False, index=True))
    content: str = Field(
        ...,
        sa_column=Column(Text, nullable=False),
        max_length=10000  # FR-042: Maximum message length
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True)
    )

    # Table indexes for query optimization
    __table_args__ = (
        Index('idx_message_conversation_created', 'conversation_id', 'created_at'),
    )
