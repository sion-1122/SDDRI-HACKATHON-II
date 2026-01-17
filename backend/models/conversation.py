"""Conversation model for AI chatbot.

[Task]: T005
[From]: specs/004-ai-chatbot/plan.md
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime


class Conversation(SQLModel, table=True):
    """Conversation model representing a chat session.

    A conversation groups multiple messages between a user and the AI assistant.
    Conversations persist indefinitely (until 90-day auto-deletion).
    """

    __tablename__ = "conversation"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
