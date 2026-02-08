# Data Model: ChatKit Migration

**Feature**: 010-chatkit-migration
**Date**: 2026-02-06

## Overview

This document describes the data entities for the ChatKit-based chat system. The migration preserves the existing conversation and message storage model while adapting to ChatKit's thread-based architecture.

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     User        │───────│    Thread       │───────│     Message     │
│  (existing)     │ 1    N │   (new/added)   │ 1    N │  (existing)     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (UUID)       │       │ id (UUID)       │       │ id (UUID)       │
│ email           │       │ user_id (FK)    │       │ thread_id (FK)  │
│ password_hash   │       │ title (opt)     │       │ role            │
│ created_at      │       │ metadata (JSON) │       │ content         │
│ updated_at      │       │ created_at      │       │ created_at      │
└─────────────────┘       │ updated_at      │       │ tool_calls (JS) │
                          └─────────────────┘       └─────────────────┘
```

## Entities

### User (Existing - No Changes)

The existing user model from authentication. No modifications required for ChatKit migration.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | string | User email (unique) |
| password_hash | string | Hashed password |
| created_at | timestamp | Account creation time |
| updated_at | timestamp | Last update time |

**Relationships:**
- One-to-many with Thread (user has many threads/conversations)

### Thread (New - ChatKit Required)

ChatKit uses a "thread" abstraction to group messages into conversations. This replaces the previous `conversation_id` string approach.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Auto-generated |
| user_id | UUID | Foreign key to User | NOT NULL, indexed |
| title | string | Optional thread title | Nullable, max 255 chars |
| metadata | JSONB | Thread metadata (tags, etc.) | Nullable |
| created_at | timestamp | Thread creation time | DEFAULT now() |
| updated_at | timestamp | Last message time | Auto-updated |

**Relationships:**
- Many-to-one with User (thread belongs to user)
- One-to-many with Message (thread has many messages)

**Indexes:**
- `idx_thread_user_id` on `(user_id)` for user queries
- `idx_thread_updated_at` on `(user_id, updated_at DESC)` for sorting

### Message (Existing - Schema Extended)

The existing message model from conversations. Extends to support ChatKit's item types.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Auto-generated |
| thread_id | UUID | Foreign key to Thread | NOT NULL, indexed |
| role | enum | Message role | 'user', 'assistant', 'system' |
| content | text | Message content | NOT NULL |
| tool_calls | JSONB | Tool call metadata | Nullable, OpenAI format |
| created_at | timestamp | Message creation time | DEFAULT now() |

**Relationships:**
- Many-to-one with Thread (message belongs to thread)

**Indexes:**
- `idx_message_thread_id` on `(thread_id, created_at ASC)` for message retrieval

**Tool Calls Format (OpenAI-compatible):**
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "create_task",
    "arguments": "{\"title\":\"Buy groceries\"}"
  }
}
```

### ToolCall (New - Optional for Tracking)

Optional entity for tracking tool executions separately. Can be derived from `tool_calls` JSONB in Message table.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| message_id | UUID | Foreign key to Message |
| tool_name | string | Tool/function name |
| parameters | JSONB | Tool parameters |
| result | JSONB | Tool execution result |
| status | enum | 'pending', 'running', 'completed', 'failed' |
| started_at | timestamp | Tool start time |
| completed_at | timestamp | Tool completion time |

**Note**: This entity is optional for basic ChatKit functionality. Can be added later for enhanced analytics.

## State Transitions

### Thread Lifecycle

```
┌──────────┐  message sent  ┌──────────┐  first message  ┌──────────┐
│ Created  │───────────────>│ Active   │─────────────────>│ Updated  │
└──────────┘                └──────────┘                  └──────────┘
```

### Message Tool Call States

```
┌─────────┐  invoked  ┌─────────┐  success  ┌───────────┐
│ Pending │──────────>│ Running │──────────>│ Completed │
└─────────┘           └─────────┘            └───────────┘
                           │
                           │ failure
                           v
                      ┌─────────┐
                      │ Failed  │
                      └─────────┘
```

## ChatKit SDK Interface Requirements

### Store Interface (Backend Implementation)

ChatKit Python SDK requires implementing a `Store` interface for thread/message persistence:

```python
class Store(Protocol):
    """ChatKit storage interface for thread/message persistence."""

    async def list_threads(
        self,
        user_id: str,
        limit: int,
        offset: int
    ) -> list[ThreadMetadata]: ...

    async def get_thread(self, thread_id: str) -> Optional[ThreadMetadata]: ...

    async def create_thread(
        self,
        user_id: str,
        title: Optional[str],
        metadata: dict
    ) -> ThreadMetadata: ...

    async def update_thread(
        self,
        thread_id: str,
        title: Optional[str],
        metadata: dict
    ) -> ThreadMetadata: ...

    async def delete_thread(self, thread_id: str) -> None: ...

    async def list_messages(
        self,
        thread_id: str,
        limit: int,
        offset: int
    ) -> list[MessageItem]: ...

    async def get_message(self, message_id: str) -> Optional[MessageItem]: ...

    async def create_message(
        self,
        thread_id: str,
        item: UserMessageItem | ClientToolCallOutputItem
    ) -> MessageItem: ...

    async def update_message(
        self,
        message_id: str,
        item: MessageItem
    ) -> MessageItem: ...

    async def delete_message(self, message_id: str) -> None: ...
```

### Database Schema Migration

```sql
-- Create threads table
CREATE TABLE threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_thread_user_id ON threads(user_id);
CREATE INDEX idx_thread_updated_at ON threads(user_id, updated_at DESC);

-- Modify messages table (if not already using thread_id)
-- If existing messages use conversation_id (string), migrate to thread_id (UUID)
ALTER TABLE messages ADD COLUMN thread_id UUID REFERENCES threads(id) ON DELETE CASCADE;

-- Migrate existing conversation_id to thread_id (if applicable)
-- This is a one-time migration script
UPDATE messages m
SET thread_id = t.id
FROM threads t
WHERE m.conversation_id::text = t.id::text;  -- Adjust based on actual schema

-- Add constraints after migration
ALTER TABLE messages ALTER COLUMN thread_id SET NOT NULL;
CREATE INDEX idx_message_thread_id ON messages(thread_id, created_at ASC);

-- Optionally drop old conversation_id column
-- ALTER TABLE messages DROP COLUMN conversation_id;
```

## Data Access Patterns

### Retrieve User's Conversations

```sql
SELECT t.id, t.title, t.updated_at,
       (SELECT content FROM messages WHERE thread_id = t.id ORDER BY created_at DESC LIMIT 1) as last_message
FROM threads t
WHERE t.user_id = $1
ORDER BY t.updated_at DESC
LIMIT $2 OFFSET $3;
```

### Retrieve Conversation Messages

```sql
SELECT id, role, content, tool_calls, created_at
FROM messages
WHERE thread_id = $1
ORDER BY created_at ASC
LIMIT $2 OFFSET $3;
```

### Create New Thread with Message

```sql
-- Begin transaction
BEGIN;

-- Create thread
INSERT INTO threads (user_id, title)
VALUES ($1, NULL)
RETURNING id;

-- Create initial message
INSERT INTO messages (thread_id, role, content)
VALUES ($2, 'user', $3)
RETURNING id;

-- Commit
COMMIT;
```

## Validation Rules

### Thread Validation

- `user_id` must reference existing user
- `title` max 255 characters if provided
- `metadata` must be valid JSON

### Message Validation

- `thread_id` must reference existing thread
- `role` must be one of: 'user', 'assistant', 'system'
- `content` required, max 100,000 characters
- `tool_calls` must be valid OpenAI format if provided

## Security Considerations

1. **Data Isolation**: All queries scoped to authenticated user's `user_id`
2. **Cascade Delete**: Deleting a user cascades to threads and messages
3. **Input Validation**: All user inputs validated before database insert
4. **SQL Injection**: Use parameterized queries (SQLModel handles this)

## Performance Considerations

1. **Indexing**: Thread lookups by user_id and message lookups by thread_id are indexed
2. **Pagination**: List queries use LIMIT/OFFSET for pagination
3. **JSONB Storage**: Tool calls stored as JSONB for efficient querying
4. **Connection Pooling**: Database connection pooling for concurrent requests
