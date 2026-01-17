# Data Model: Todo AI Chatbot

**Feature**: 004-ai-chatbot
**Date**: 2025-01-15
**Status**: Complete

## Overview

This document defines the database schema extensions for Phase III AI Chatbot. Two new entities are introduced: `Conversation` and `Message`. Existing entities (`User`, `Task`) remain unchanged but are referenced by foreign keys.

---

## Entity-Relationship Diagram

```text
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   User      │────────<│ Conversation │>────────│  Message    │
│ (existing)  │    1:N  │    (new)     │   1:N   │   (new)     │
└─────────────┘         └──────────────┘         └─────────────┘
                                                          │
                                                          │ references
                                                          ▼
                                                   ┌─────────────┐
                                                   │   Task      │
                                                   │ (existing)  │
                                                   └─────────────┘
```

**Relationships**:
- One User has many Conversations
- One Conversation has many Messages
- Each Message belongs to one User and one Conversation
- Messages reference Tasks only through content (not FK relationship)
- MCP tools create/update/delete Tasks independently

---

## Entity Definitions

### 1. Conversation

**Purpose**: Represents a chat session between a user and the AI assistant.

**Table Name**: `conversation`

**Primary Key**: `id` (auto-increment integer)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PRIMARY KEY, AUTO_INCREMENT | Unique conversation identifier |
| `user_id` | int | FOREIGN KEY → user.id, NOT NULL, INDEX | Owner of the conversation |
| `created_at` | datetime | DEFAULT NOW(), NOT NULL | Timestamp when conversation was created |
| `updated_at` | datetime | DEFAULT NOW(), ON UPDATE NOW(), NOT NULL | Timestamp of last message |

**SQLModel Definition**:
```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from models.user import User

class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")
```

**Validation Rules**:
- `user_id` must reference existing User (FK constraint)
- `created_at` must be <= `updated_at` (application logic)
- `updated_at` automatically updated on any message addition

**Indexes**:
```sql
-- Primary index on user_id for efficient user conversation lookup
CREATE INDEX idx_conversation_user ON conversation(user_id);

-- Composite index for user's conversations ordered by recent activity
CREATE INDEX idx_conversation_user_updated
  ON conversation(user_id, updated_at DESC);
```

---

### 2. Message

**Purpose**: Represents a single message (from user or AI assistant) within a conversation.

**Table Name**: `message`

**Primary Key**: `id` (auto-increment integer)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PRIMARY KEY, AUTO_INCREMENT | Unique message identifier |
| `conversation_id` | int | FOREIGN KEY → conversation.id, NOT NULL, INDEX | Conversation this message belongs to |
| `user_id` | int | FOREIGN KEY → user.id, NOT NULL, INDEX | User who owns the conversation |
| `role` | enum | NOT NULL, VALUES ('user', 'assistant') | Who sent the message |
| `content` | text | NOT NULL, MAX_LENGTH=10000 | Message text content |
| `created_at` | datetime | DEFAULT NOW(), NOT NULL, INDEX | Timestamp when message was created |

**SQLModel Definition**:
```python
from typing import Optional, Literal
from sqlmodel import Field, SQLModel, Relationship, Column, Text
from sqlalchemy import Enum
import sqlalchemy as sa

class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: Literal["user", "assistant"] = Field(sa_column=Column(Enum("user", "assistant", name="message_role_enum")))
    content: str = Field(sa_column=Column(Text), max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: User = Relationship(back_populates="messages")
```

**Validation Rules** (from functional requirements):
- `conversation_id` must reference existing Conversation (FK constraint)
- `user_id` must reference existing User (FK constraint)
- `role` must be either "user" or "assistant" (enum constraint)
- `content` must be non-empty and <= 10,000 characters (application validation)
- `created_at` must be >= parent conversation's `created_at` (application logic)
- `created_at` must be <= parent conversation's `updated_at` (application logic)

**Indexes**:
```sql
-- Composite index for efficient conversation history loading
CREATE INDEX idx_message_conversation_created
  ON message(conversation_id, created_at ASC);

-- Index for temporal queries
CREATE INDEX idx_message_created_at
  ON message(created_at DESC);
```

**State Transitions**:
- Messages are **immutable** once created (no updates or deletes)
- Only operation allowed: INSERT new messages
- Conversation deletion cascades to messages (CASCADE DELETE)

---

### 3. User (Existing - No Changes)

**Table Name**: `user`

**Phase III Usage**:
- Referenced by `Conversation.user_id` (one-to-many)
- Referenced by `Message.user_id` (one-to-many)
- JWT token contains `user_id` for authentication
- All MCP tools scoped to `user_id`

**No Schema Changes Required**

---

### 4. Task (Existing - No Changes)

**Table Name**: `task`

**Phase III Usage**:
- Referenced in message content (e.g., "Task 123 has been created")
- Created/updated/deleted by MCP tools based on AI agent decisions
- No direct foreign key from Message to Task
- AI agent describes task operations in natural language

**No Schema Changes Required**

---

## Database Migration SQL

### Migration Script: `003_add_conversation_and_message_tables.sql`

```sql
-- Migration: Add conversation and message tables for AI chatbot
-- Date: 2025-01-15
-- Author: Phase III AI Chatbot Implementation

-- Create message role enum
CREATE TYPE message_role_enum AS ENUM ('user', 'assistant');

-- Create conversation table
CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create message table
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    role message_role_enum NOT NULL,
    content TEXT NOT NULL CHECK (LENGTH(content) > 0 AND LENGTH(content) <= 10000),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_conversation_user ON conversation(user_id);
CREATE INDEX idx_conversation_user_updated ON conversation(user_id, updated_at DESC);

CREATE INDEX idx_message_conversation_created
  ON message(conversation_id, created_at ASC);
CREATE INDEX idx_message_created_at ON message(created_at DESC);
CREATE INDEX idx_message_user ON message(user_id);

-- Add trigger to auto-update conversation.updated_at
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON message
FOR EACH ROW
EXECUTE FUNCTION update_conversation_updated_at();

-- Grant permissions (adjust user as needed)
GRANT SELECT, INSERT, UPDATE, DELETE ON conversation, message TO app_user;
GRANT USAGE, SELECT ON SEQUENCE conversation_id_seq TO app_user;
GRANT USAGE, SELECT ON SEQUENCE message_id_seq TO app_user;
```

### Rollback Script

```sql
-- Rollback: Remove conversation and message tables
DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON message;
DROP FUNCTION IF EXISTS update_conversation_updated_at();
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS conversation;
DROP TYPE IF EXISTS message_role_enum;
```

---

## Validation Rules Summary

### Application-Level Validation

**Conversation Creation**:
```python
def validate_conversation_creation(user_id: int) -> None:
    """Validate conversation creation."""
    # User must exist
    user = await get_user(user_id)
    if not user:
        raise ValidationError("User not found")

    # No active conversation limit (optional)
    active_convs = await count_active_conversations(user_id)
    if active_convs > 100:
        raise ValidationError("Too many active conversations")
```

**Message Creation**:
```python
def validate_message_creation(
    conversation_id: int,
    user_id: int,
    role: str,
    content: str
) -> None:
    """Validate message creation."""
    # Conversation must exist and belong to user
    conv = await get_conversation(conversation_id)
    if not conv or conv.user_id != user_id:
        raise ValidationError("Conversation not found")

    # Role must be valid
    if role not in ["user", "assistant"]:
        raise ValidationError("Invalid message role")

    # Content must be non-empty and within limits
    if not content or len(content.strip()) == 0:
        raise ValidationError("Message content cannot be empty")
    if len(content) > 10000:
        raise ValidationError("Message content too long (max 10,000 characters)")

    # User must match conversation owner
    if conv.user_id != user_id:
        raise ValidationError("User does not own this conversation")
```

---

## Query Patterns

### Common Queries

**Load Conversation History**:
```python
async def load_conversation_history(
    conversation_id: int,
    user_id: int,
    limit: int = 100
) -> list[Message]:
    """Load conversation history for AI agent."""
    # Verify ownership
    conv = await session.get(Conversation, conversation_id)
    if not conv or conv.user_id != user_id:
        return []

    # Load messages chronologically
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(limit)
    )
    results = await session.exec(statement)
    return results.all()
```

**Get User's Active Conversations**:
```python
async def get_user_conversations(
    user_id: int,
    limit: int = 20
) -> list[Conversation]:
    """Get user's conversations ordered by recent activity."""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    results = await session.exec(statement)
    return results.all()
```

**Create New Conversation**:
```python
async def create_conversation(user_id: int) -> Conversation:
    """Create a new conversation for user."""
    conv = Conversation(user_id=user_id)
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return conv
```

**Add Message to Conversation**:
```python
async def add_message(
    conversation_id: int,
    user_id: int,
    role: Literal["user", "assistant"],
    content: str
) -> Message:
    """Add a message to conversation."""
    msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg
```

---

## Performance Considerations

### Optimization Strategies

**1. Pagination for Large Conversations**:
```python
# Load messages in batches
async def load_conversation_paginated(
    conversation_id: int,
    page: int = 0,
    page_size: int = 50
) -> list[Message]:
    """Load conversation with pagination."""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(page * page_size)
        .limit(page_size)
    )
    results = await session.exec(statement)
    return results.all()
```

**2. Message Summarization for Long Histories**:
```python
# For conversations > 100 messages, summarize older messages
async def load_conversation_with_summary(
    conversation_id: int,
    user_id: int
) -> tuple[str, list[Message]]:
    """Load conversation with summary for AI context."""
    total = await count_messages(conversation_id)

    if total <= 100:
        # Load all messages
        messages = await load_conversation_history(conversation_id, user_id)
        return "", messages
    else:
        # Generate summary of older messages
        summary = await generate_summary(conversation_id)
        recent = await load_recent_messages(conversation_id, limit=50)
        return summary, recent
```

**3. Connection Pooling**:
```python
# Configure SQLModel connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Max concurrent connections
    max_overflow=20,        # Additional connections under load
    pool_pre_ping=True,     # Verify connections before use
    echo=False              # Disable SQL logging in production
)
```

---

## Security Considerations

### Data Isolation

**User Ownership Verification**:
```python
# Every query must verify user ownership
async def get_conversation(conversation_id: int, user_id: int) -> Conversation | None:
    """Get conversation only if owned by user."""
    statement = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)  # Critical: enforce ownership
    )
    result = await session.exec(statement)
    return result.first()
```

**Cross-User Access Prevention**:
```python
# Never expose other users' conversations
async def get_message(message_id: int, user_id: int) -> Message | None:
    """Get message only if conversation owned by user."""
    statement = (
        select(Message)
        .join(Conversation)
        .where(Message.id == message_id)
        .where(Conversation.user_id == user_id)  # Enforce ownership via conversation
    )
    result = await session.exec(statement)
    return result.first()
```

---

## Data Retention (Optional)

**Conversation Cleanup Policy** (Future Enhancement):
```sql
-- Example: Delete conversations inactive for 1 year
DELETE FROM conversation
WHERE updated_at < NOW() - INTERVAL '1 year';
```

**Message Cleanup**:
- Messages automatically deleted when conversation deleted (CASCADE)
- No separate message cleanup needed

---

## Testing Data Model

### Unit Test Examples

```python
async def test_create_conversation():
    """Test conversation creation."""
    user = await create_test_user()
    conv = await create_conversation(user.id)

    assert conv.id is not None
    assert conv.user_id == user.id
    assert conv.created_at is not None

async def test_add_message_to_conversation():
    """Test adding messages to conversation."""
    user = await create_test_user()
    conv = await create_conversation(user.id)

    msg1 = await add_message(conv.id, user.id, "user", "Hello")
    msg2 = await add_message(conv.id, user.id, "assistant", "Hi there!")

    assert msg1.conversation_id == conv.id
    assert msg2.conversation_id == conv.id

    # Load conversation
    messages = await load_conversation_history(conv.id, user.id)
    assert len(messages) == 2
    assert messages[0].content == "Hello"
    assert messages[1].content == "Hi there!"

async def test_cross_user_isolation():
    """Test users cannot access each other's conversations."""
    user1 = await create_test_user()
    user2 = await create_test_user()

    conv1 = await create_conversation(user1.id)

    # User2 cannot access user1's conversation
    conv = await get_conversation(conv1.id, user2.id)
    assert conv is None
```

---

## Summary

**New Tables**: 2 (`conversation`, `message`)
**Modified Tables**: 0 (existing tables unchanged)
**New Foreign Keys**: 4 (Conversation → User, Message → Conversation, Message → User)
**New Indexes**: 5 (performance optimization)
**New Triggers**: 1 (auto-update conversation.updated_at)

**Validation**: Enforced at database level (FK constraints, checks) and application level (business logic)

**Security**: All queries scoped to authenticated user_id via WHERE clauses

**Performance**: Indexed for efficient conversation loading and user conversation lookup

---

**Data Model Version**: 1.0.0
**Last Updated**: 2025-01-15
**Status**: ✅ Complete - Ready for implementation
