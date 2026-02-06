# Kafka Event Streaming - Pydantic Schemas

> **Language**: Python 3.13+
> **Purpose**: Event schema contracts for validation and serialization
> **Status**: Production Ready | **Deployment**: Not Required

```python
"""
Kafka Event Schema Contracts for Todo List Application

This module defines Pydantic models for all events in the system.
These schemas ensure type safety, validation, and serialization consistency.

Usage:
    from backend.services.events.schemas import TaskCreatedEvent, BaseEvent

    event = TaskCreatedEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        correlation_id=uuid4(),
        producer="chat-api",
        payload=TaskCreatedPayload(...)
    )

    # Validate and serialize
    event_json = event.model_dump(mode="json")
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================

class EventType(str, Enum):
    """All possible event types in the system."""
    TASK_CREATED = "task-created"
    TASK_UPDATED = "task-updated"
    TASK_DELETED = "task-deleted"
    TASK_COMPLETED = "task-completed"
    REMINDER_SCHEDULED = "reminder-scheduled"
    REMINDER_TRIGGERED = "reminder-triggered"
    REMINDER_CANCELLED = "reminder-cancelled"
    RECURRENCE_INSTANCE_CREATED = "recurrence-instance-created"


class EventProducer(str, Enum):
    """Services that can produce events."""
    CHAT_API = "chat-api"
    REMINDER_WORKER = "reminder-worker"
    RECURRENCE_WORKER = "recurrence-worker"
    SYSTEM = "system"


class TaskPriority(str, Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskStatus(str, Enum):
    """Task status values."""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class RecurrenceFrequency(str, Enum):
    """Recurrence rule frequencies."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class ReminderCancelReason(str, Enum):
    """Reasons why a reminder was cancelled."""
    TASK_DELETED = "task-deleted"
    DUE_DATE_REMOVED = "due-date-removed"
    TASK_COMPLETED = "task-completed"


# ============================================================================
# SHARED MODELS
# ============================================================================

class RecurrenceRule(BaseModel):
    """Defines how a task recurs."""
    frequency: RecurrenceFrequency
    interval: int = Field(default=1, gt=0, description="How often to recur (e.g., 1=every, 2=every other)")
    days_of_week: list[int] | None = Field(default=None, ge=0, le=6)
    end_date: datetime | None = None
    end_after_occurrences: int | None = Field(default=None, gt=0)
    cron_expression: str | None = Field(default=None, max_length=100)

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v, info):
        """Ensure days_of_week is only provided for WEEKLY frequency."""
        if v is not None and info.data.get("frequency") != RecurrenceFrequency.WEEKLY:
            raise ValueError("days_of_week is only valid for WEEKLY frequency")
        return v


class FieldChange(BaseModel):
    """Represents a single field change in TaskUpdatedEvent."""
    old: dict | list | str | int | float | bool | None
    new: dict | list | str | int | float | bool | None


# ============================================================================
# PAYLOAD MODELS
# ============================================================================

class TaskCreatedPayload(BaseModel):
    """Payload for task-created event."""
    task_id: UUID
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    priority: TaskPriority
    status: TaskStatus
    due_date: datetime | None = None
    recurrence: RecurrenceRule | None = None
    tags: list[str] = Field(default_factory=list)
    user_id: UUID
    created_at: datetime


class TaskUpdatedPayload(BaseModel):
    """Payload for task-updated event."""
    task_id: UUID
    changed_fields: list[str]
    changes: dict[str, FieldChange]
    updated_at: datetime


class TaskDeletedPayload(BaseModel):
    """Payload for task-deleted event."""
    task_id: UUID
    user_id: UUID
    deleted_at: datetime


class TaskCompletedPayload(BaseModel):
    """Payload for task-completed event."""
    task_id: UUID
    user_id: UUID
    completed_at: datetime
    was_overdue: bool


class ReminderScheduledPayload(BaseModel):
    """Payload for reminder-scheduled event."""
    task_id: UUID
    reminder_id: UUID
    due_date: datetime
    reminder_time: datetime
    recurrence: RecurrenceRule | None = None


class ReminderTriggeredPayload(BaseModel):
    """Payload for reminder-triggered event."""
    task_id: UUID
    reminder_id: UUID
    task_title: str
    user_id: UUID
    due_date: datetime
    is_overdue: bool


class ReminderCancelledPayload(BaseModel):
    """Payload for reminder-cancelled event."""
    task_id: UUID
    reminder_id: UUID
    reason: ReminderCancelReason


class RecurrenceInstanceCreatedPayload(BaseModel):
    """Payload for recurrence-instance-created event."""
    parent_task_id: UUID
    instance_task_id: UUID
    scheduled_date: datetime
    recurrence_rule: RecurrenceRule


# ============================================================================
# BASE EVENT
# ============================================================================

class BaseEvent(BaseModel):
    """Base event that all events extend."""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    event_version: Literal["v1"] = "v1"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: UUID = Field(default_factory=uuid4)
    producer: EventProducer
    payload: (
        TaskCreatedPayload
        | TaskUpdatedPayload
        | TaskDeletedPayload
        | TaskCompletedPayload
        | ReminderScheduledPayload
        | ReminderTriggeredPayload
        | ReminderCancelledPayload
        | RecurrenceInstanceCreatedPayload
    )


# ============================================================================
# CONCRETE EVENTS
# ============================================================================

class TaskCreatedEvent(BaseEvent):
    """Event emitted when a new task is created."""
    event_type: Literal[EventType.TASK_CREATED] = EventType.TASK_CREATED
    payload: TaskCreatedPayload


class TaskUpdatedEvent(BaseEvent):
    """Event emitted when a task is updated."""
    event_type: Literal[EventType.TASK_UPDATED] = EventType.TASK_UPDATED
    payload: TaskUpdatedPayload


class TaskDeletedEvent(BaseEvent):
    """Event emitted when a task is deleted."""
    event_type: Literal[EventType.TASK_DELETED] = EventType.TASK_DELETED
    payload: TaskDeletedPayload


class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task is marked complete."""
    event_type: Literal[EventType.TASK_COMPLETED] = EventType.TASK_COMPLETED
    payload: TaskCompletedPayload


class ReminderScheduledEvent(BaseEvent):
    """Event emitted when a reminder is scheduled."""
    event_type: Literal[EventType.REMINDER_SCHEDULED] = EventType.REMINDER_SCHEDULED
    payload: ReminderScheduledPayload


class ReminderTriggeredEvent(BaseEvent):
    """Event emitted when a reminder should be triggered."""
    event_type: Literal[EventType.REMINDER_TRIGGERED] = EventType.REMINDER_TRIGGERED
    payload: ReminderTriggeredPayload


class ReminderCancelledEvent(BaseEvent):
    """Event emitted when a reminder is cancelled."""
    event_type: Literal[EventType.REMINDER_CANCELLED] = EventType.REMINDER_CANCELLED
    payload: ReminderCancelledPayload


class RecurrenceInstanceCreatedEvent(BaseEvent):
    """Event emitted when a recurring task instance is created."""
    event_type: Literal[EventType.RECURRENCE_INSTANCE_CREATED] = EventType.RECURRENCE_INSTANCE_CREATED
    payload: RecurrenceInstanceCreatedPayload


# Union type for all events
AnyEvent = Union[
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskDeletedEvent,
    TaskCompletedEvent,
    ReminderScheduledEvent,
    ReminderTriggeredEvent,
    ReminderCancelledEvent,
    RecurrenceInstanceCreatedEvent,
]


# ============================================================================
# KAFKA TOPIC CONFIGURATION
# ============================================================================

class KafkaTopics:
    """Kafka topic names."""
    TASK_EVENTS = "task-events"
    REMINDERS = "reminders"
    TASK_UPDATES = "task-updates"
    DEAD_LETTER = "dead-letter"


class TopicConfiguration:
    """Kafka topic configuration settings."""

    # Default settings for all topics
    DEFAULT_PARTITIONS = 3
    DEFAULT_REPLICATION_FACTOR = 2
    DEFAULT_RETENTION_MS = 7 * 24 * 60 * 60 * 1000  # 7 days

    # Topic-specific settings
    TOPIC_CONFIGS = {
        KafkaTopics.TASK_EVENTS: {
            "partitions": 3,
            "replication_factor": 2,
            "retention_ms": 7 * 24 * 60 * 60 * 1000,  # 7 days
            "cleanup_policy": "delete",
        },
        KafkaTopics.REMINDERS: {
            "partitions": 3,
            "replication_factor": 2,
            "retention_ms": 7 * 24 * 60 * 60 * 1000,  # 7 days
            "cleanup_policy": "delete",
        },
        KafkaTopics.TASK_UPDATES: {
            "partitions": 3,
            "replication_factor": 2,
            "retention_ms": 7 * 24 * 60 * 60 * 1000,  # 7 days
            "cleanup_policy": "delete",
        },
        KafkaTopics.DEAD_LETTER: {
            "partitions": 3,
            "replication_factor": 2,
            "retention_ms": 30 * 24 * 60 * 60 * 1000,  # 30 days
            "cleanup_policy": "delete",
        },
    }


# ============================================================================
# EVENT TO TOPIC MAPPING
# ============================================================================

EVENT_TO_TOPIC = {
    EventType.TASK_CREATED: KafkaTopics.TASK_EVENTS,
    EventType.TASK_UPDATED: KafkaTopics.TASK_UPDATES,
    EventType.TASK_DELETED: KafkaTopics.TASK_EVENTS,
    EventType.TASK_COMPLETED: KafkaTopics.TASK_UPDATES,
    EventType.REMINDER_SCHEDULED: KafkaTopics.REMINDERS,
    EventType.REMINDER_TRIGGERED: KafkaTopics.REMINDERS,
    EventType.REMINDER_CANCELLED: KafkaTopics.REMINDERS,
    EventType.RECURRENCE_INSTANCE_CREATED: KafkaTopics.TASK_EVENTS,
}


def get_topic_for_event(event_type: EventType) -> str:
    """Get the Kafka topic name for a given event type."""
    return EVENT_TO_TOPIC[event_type]


# ============================================================================
# EVENT HELPERS
# ============================================================================

def create_task_created_event(
    task_id: UUID,
    title: str,
    user_id: UUID,
    description: str | None = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    status: TaskStatus = TaskStatus.TODO,
    due_date: datetime | None = None,
    recurrence: RecurrenceRule | None = None,
    tags: list[str] | None = None,
) -> TaskCreatedEvent:
    """Helper to create a task-created event."""
    return TaskCreatedEvent(
        producer=EventProducer.CHAT_API,
        payload=TaskCreatedPayload(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=due_date,
            recurrence=recurrence,
            tags=tags or [],
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
        ),
    )


def extract_task_id(event: BaseEvent) -> UUID | None:
    """Extract task_id from an event if present."""
    payload_dict = event.payload.model_dump()
    return payload_dict.get("task_id")


# ============================================================================
# MOCK EVENT PUBLISHER (For Testing Without Kafka)
# ============================================================================

class MockEventPublisher:
    """
    In-memory event publisher for development/testing without Kafka.

    This allows testing event contracts without deploying Kafka infrastructure.
    Events are stored in memory and can be retrieved for validation.
    """

    def __init__(self):
        self._events: dict[str, list[BaseEvent]] = {
            KafkaTopics.TASK_EVENTS: [],
            KafkaTopics.REMINDERS: [],
            KafkaTopics.TASK_UPDATES: [],
            KafkaTopics.DEAD_LETTER: [],
        }

    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to the appropriate topic (in-memory)."""
        topic = get_topic_for_event(event.event_type)
        self._events[topic].append(event)

    async def get_events(
        self, topic: str | None = None, event_type: EventType | None = None
    ) -> list[BaseEvent]:
        """Retrieve events from the mock broker."""
        if topic:
            events = self._events.get(topic, [])
        else:
            events = [
                e for events in self._events.values() for e in events
            ]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events

    def clear(self) -> None:
        """Clear all stored events."""
        for topic in self._events:
            self._events[topic].clear()

    def get_event_count(self, topic: str | None = None) -> int:
        """Get the count of stored events."""
        if topic:
            return len(self._events.get(topic, []))
        return sum(len(events) for events in self._events.values())


# Singleton instance for testing
_mock_publisher = MockEventPublisher()


def get_mock_publisher() -> MockEventPublisher:
    """Get the singleton mock event publisher instance."""
    return _mock_publisher
```

---

## Usage Example

```python
from uuid import uuid4
from datetime import datetime, timezone

from backend.services.events.schemas import (
    TaskCreatedEvent,
    EventType,
    EventProducer,
    get_topic_for_event,
    get_mock_publisher,
)

# Create a new event
event = TaskCreatedEvent(
    producer=EventProducer.CHAT_API,
    payload={
        "task_id": uuid4(),
        "title": "Complete Phase 5 documentation",
        "description": "Create comprehensive architecture docs",
        "priority": "HIGH",
        "status": "TODO",
        "due_date": None,
        "recurrence": None,
        "tags": ["documentation", "phase-5"],
        "user_id": uuid4(),
        "created_at": datetime.now(timezone.utc),
    },
)

# Serialize to JSON for Kafka
event_json = event.model_dump(mode="json")

# Get target topic
topic = get_topic_for_event(EventType.TASK_CREATED)  # "task-events"

# Using mock publisher for testing (without Kafka)
mock = get_mock_publisher()
await mock.publish(event)
print(f"Published {event.event_type} to {topic}")
```
