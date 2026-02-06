# Data Model: Kafka Event Streaming

**Feature**: 009-kafka-events | **Date**: 2026-02-06

## Overview

Defines event schemas and topic structures for event-driven task management using Kafka/Redpanda + Dapr.

---

## Event Schema Hierarchy

```
BaseEvent (abstract)
├── TaskCreatedEvent
├── TaskUpdatedEvent
├── TaskDeletedEvent
├── TaskCompletedEvent
└── ReminderDueEvent
```

---

## Base Event Schema

All events share a common base structure:

```python
class BaseEvent(BaseModel):
    """Base event schema for all Kafka events"""
    event_id: str          # UUID v4
    event_type: EventType  # task_created, task_updated, etc.
    event_version: str      # "v1", "v2", etc. for schema evolution
    timestamp: datetime     # ISO-8601 UTC
    correlation_id: str     # UUID for tracing event chains
    producer: str           # "chat-api", "reminder-worker", etc.
    payload: Dict[str, Any] # Event-specific data
```

### Event Types

```python
class EventType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_COMPLETED = "task_completed"
    REMINDER_DUE = "reminder_due"
```

---

## Event Schemas

### TaskCreatedEvent

Published when a user creates a new task via Chat API or UI.

```python
class TaskCreatedEvent(BaseEvent):
    event_type: EventType = EventType.TASK_CREATED
    payload: {
        "task_id": str,           # UUID
        "user_id": str,           # UUID
        "title": str,             # Task title
        "description": str,       # Optional description
        "priority": str,          # "HIGH" | "MEDIUM" | "LOW"
        "status": str,            # "TODO" | "IN_PROGRESS" | "DONE"
        "due_date": str,          # ISO-8601 or null
        "recurrence": dict,       # Recurrence rule or null
        "tags": list[str],        # List of tag strings
        "created_at": str         # ISO-8601 UTC
    }
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task_created",
  "event_version": "v1",
  "timestamp": "2026-02-06T10:00:00Z",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "producer": "chat-api",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "ba5f053e-fd51-4f9f-96a8-c461307ef75e",
    "title": "Complete project proposal",
    "description": "Write and submit the Q1 project proposal",
    "priority": "HIGH",
    "status": "TODO",
    "due_date": "2026-02-10T17:00:00Z",
    "recurrence": null,
    "tags": ["work", "q1"],
    "created_at": "2026-02-06T10:00:00Z"
  }
}
```

### TaskUpdatedEvent

Published when a user modifies an existing task.

```python
class TaskUpdatedEvent(BaseEvent):
    event_type: EventType = EventType.TASK_UPDATED
    payload: {
        "task_id": str,              # UUID
        "user_id": str,              # UUID
        "changed_fields": list[str], # ["status", "due_date"]
        "changes": {
            "field_name": {
                "old": <old value>,
                "new": <new value>
            }
        }
    }
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440002",
  "event_type": "task_updated",
  "event_version": "v1",
  "timestamp": "2026-02-06T11:00:00Z",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "producer": "chat-api",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "ba5f053e-fd51-4f9f-96a8-c461307ef75e",
    "changed_fields": ["status", "due_date"],
    "changes": {
      "status": {"old": "TODO", "new": "IN_PROGRESS"},
      "due_date": {"old": "2026-02-10T17:00:00Z", "new": "2026-02-12T17:00:00Z"}
    }
  }
}
```

### TaskDeletedEvent

Published when a user deletes a task.

```python
class TaskDeletedEvent(BaseEvent):
    event_type: EventType = EventType.TASK_DELETED
    payload: {
        "task_id": str,    # UUID of deleted task
        "user_id": str,    # UUID of user who deleted
        "deleted_at": str  # ISO-8601 UTC
    }
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440003",
  "event_type": "task_deleted",
  "event_version": "v1",
  "timestamp": "2026-02-06T12:00:00Z",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "producer": "chat-api",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "ba5f053e-fd51-4f9f-96a8-c461307ef75e",
    "deleted_at": "2026-02-06T12:00:00Z"
  }
}
```

### TaskCompletedEvent

Published when a user marks a task as complete.

```python
class TaskCompletedEvent(BaseEvent):
    event_type: EventType = EventType.TASK_COMPLETED
    payload: {
        "task_id": str,       # UUID
        "user_id": str,       # UUID
        "completed_at": str,  # ISO-8601 UTC
        "recurrence": dict    # Recurrence rule if recurring task
    }
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440004",
  "event_type": "task_completed",
  "event_version": "v1",
  "timestamp": "2026-02-06T13:00:00Z",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "producer": "chat-api",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "ba5f053e-fd51-4f9f-96a8-c461307ef75e",
    "completed_at": "2026-02-06T13:00:00Z",
    "recurrence": {
      "frequency": "weekly",
      "interval": 1
    }
  }
}
```

### ReminderDueEvent

Published by reminder consumer when a task is due.

```python
class ReminderDueEvent(BaseEvent):
    event_type: EventType = EventType.REMINDER_DUE
    payload: {
        "task_id": str,        # UUID
        "user_id": str,        # UUID
        "title": str,          # Task title
        "due_date": str,       # ISO-8601 UTC
        "priority": str,       # "HIGH" | "MEDIUM" | "LOW"
        "reminder_offset": int # Minutes before due (0 = at due time)
    }
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440005",
  "event_type": "reminder_due",
  "event_version": "v1",
  "timestamp": "2026-02-06T16:45:00Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440001",
  "producer": "reminder-worker",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "ba5f053e-fd51-4f9f-96a8-c461307ef75e",
    "title": "Complete project proposal",
    "due_date": "2026-02-06T17:00:00Z",
    "priority": "HIGH",
    "reminder_offset": 15
  }
}
```

---

## Kafka Topics

### Topic Configuration

| Topic | Partitions | Replication | Retention | Purpose |
|-------|------------|-------------|-----------|---------|
| `task-events` | 1 | 1 | 7 days | Task lifecycle events |
| `task-updates` | 1 | 1 | 7 days | Task change events |
| `reminders` | 1 | 1 | 7 days | Reminder notifications |

**Note**: Single partition due to resource constraints (2 CPU, 4GB RAM).

### Topic: task-events

**Purpose**: Task lifecycle events (created, deleted, completed)

**Event Types**:
- `task_created`
- `task_deleted`
- `task_completed`

**Consumers**: Reminder Worker, Analytics (future)

### Topic: task-updates

**Purpose**: Task modification events

**Event Types**:
- `task_updated`

**Consumers**: Analytics (future), Audit Log (future)

### Topic: reminders

**Purpose**: Scheduled reminder notifications

**Event Types**:
- `reminder_due`

**Consumers**: Notification Service, WebSocket Pusher

---

## Event Flow Diagrams

### Task Creation Flow

```
User → Chat API → Dapr Publish → task-events topic → Reminder Consumer
                                                        ↓
                                                  Schedule reminder
                                                        ↓
                                                  reminders topic → Notification Service
```

### Task Update Flow

```
User → Chat API → Dapr Publish → task-updates topic → Analytics (future)
                              ↓
                        task-events topic → Reminder Consumer
                                                     ↓
                                                   Reschedule reminder
```

---

## Schema Evolution

Events are versioned (`event_version: "v1"`) to support backward compatibility.

**Evolution Rules**:
1. Never remove fields from existing event versions
2. Add optional fields for new data
3. Increment version for breaking changes
4. Consumers must handle multiple versions

**Example v2 Change**:
```python
# v1
class TaskCreatedEvent(BaseEvent):
    payload: {...}  # existing fields

# v2 (new field added)
class TaskCreatedEventV2(BaseEvent):
    event_version: str = "v2"
    payload: {
        ...  # all v1 fields
        "assignee": str,  # NEW: optional assignee
        "project_id": str  # NEW: optional project
    }
```

---

## Data Validation

### Pydantic Models

All event schemas use Pydantic for runtime validation:

```python
# services/event_schemas.py
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum

class EventType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_COMPLETED = "task_completed"
    REMINDER_DUE = "reminder_due"

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    event_type: EventType
    event_version: str = "v1"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    producer: str = Field(default="chat-api")
    payload: Dict[str, Any]

    @validator('timestamp')
    def validate_timestamp(cls, v):
        if v.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware")
        return v
```

### Validation Rules

| Field | Validation |
|-------|------------|
| `event_id` | UUID v4 format (auto-generated) |
| `event_type` | Must be valid EventType enum |
| `timestamp` | ISO-8601 UTC, timezone-aware |
| `task_id` | Valid UUID |
| `user_id` | Valid UUID |
| `priority` | "HIGH", "MEDIUM", or "LOW" |
| `status` | "TODO", "IN_PROGRESS", or "DONE" |

---

## Error Handling

### Publish Failures

- Event publishing is **non-blocking**
- Failures are **logged but don't block API responses**
- Failed events go to a **dead letter queue** for retry

### Consumer Errors

- Consumers **commit offset only after successful processing**
- Processing errors trigger **retry with exponential backoff**
- Max retries exceeded → **dead letter queue**

---

## Python Module Structure

```
backend/
├── services/
│   ├── __init__.py
│   ├── event_schemas.py      # Pydantic event models
│   ├── kafka_service.py       # Dapr Kafka publishing service
│   └── event_publisher.py     # Event publishing hooks
├── consumers/
│   ├── __init__.py
│   ├── base_consumer.py       # Base consumer with retry logic
│   ├── reminder_consumer.py   # Processes task events
│   └── notification_consumer.py  # Sends notifications
└── tests/
    ├── test_event_schemas.py # Schema validation tests
    └── test_kafka_service.py  # Publishing tests
```

---

**Data Model Version**: 1.0
**Last Updated**: 2026-02-06
