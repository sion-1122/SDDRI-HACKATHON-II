# Event API Contracts

**Feature**: 009-kafka-events | **Date**: 2026-02-06

## Overview

Defines the event schema contracts for Kafka-based event streaming in the Todo application.

---

## Base Event Schema

All events follow this base structure:

```yaml
BaseEvent:
  type: object
  properties:
    event_id:
      type: string
      format: uuid
      description: Unique event identifier
    event_type:
      type: string
      enum: [task_created, task_updated, task_deleted, task_completed, reminder_due]
      description: Type of event
    event_version:
      type: string
      pattern: "^v[0-9]+$"
      description: Schema version for evolution
    timestamp:
      type: string
      format: date-time
      description: Event timestamp (ISO-8601 UTC)
    correlation_id:
      type: string
      format: uuid
      description: Correlation ID for event tracing
    producer:
      type: string
      description: Service that produced the event
    payload:
      type: object
      description: Event-specific data
  required:
    - event_id
    - event_type
    - event_version
    - timestamp
    - producer
    - payload
```

---

## Event Type: task_created

**Topic**: `task-events`

**Description**: Published when a new task is created

```yaml
TaskCreatedEvent:
  allOf:
    - $ref: '#/components/schemas/BaseEvent'
  - type: object
  properties:
    event_type:
      enum: [task_created]
    payload:
      type: object
      properties:
        task_id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        title:
          type: string
          minLength: 1
          maxLength: 255
        description:
          type: string
          maxLength: 2000
          nullable: true
        priority:
          type: string
          enum: [HIGH, MEDIUM, LOW]
        status:
          type: string
          enum: [TODO, IN_PROGRESS, DONE]
        due_date:
          type: string
          format: date-time
          nullable: true
        recurrence:
          type: object
          nullable: true
          properties:
            frequency:
              type: string
              enum: [daily, weekly, monthly, cron]
            interval:
              type: integer
              minimum: 1
              maximum: 365
            count:
              type: integer
              minimum: 1
              maximum: 100
              nullable: true
            end_date:
              type: string
              format: date-time
              nullable: true
            cron_expression:
              type: string
              nullable: true
        tags:
          type: array
          items:
            type: string
        created_at:
          type: string
          format: date-time
      required:
        - task_id
        - user_id
        - title
        - priority
        - status
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

---

## Event Type: task_updated

**Topic**: `task-updates`

**Description**: Published when a task is modified

```yaml
TaskUpdatedEvent:
  allOf:
    - $ref: '#/components/schemas/BaseEvent'
  - type: object
  properties:
    event_type:
      enum: [task_updated]
    payload:
      type: object
      properties:
        task_id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        changed_fields:
          type: array
          items:
            type: string
          description: List of field names that changed
        changes:
          type: object
          additionalProperties:
            type: object
            properties:
              old:
                description: Previous value
              new:
                description: New value
      required:
        - task_id
        - user_id
        - changed_fields
        - changes
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

---

## Event Type: task_deleted

**Topic**: `task-events`

**Description**: Published when a task is deleted

```yaml
TaskDeletedEvent:
  allOf:
    - $ref: '#/components/schemas/BaseEvent'
  - type: object
  properties:
    event_type:
      enum: [task_deleted]
    payload:
      type: object
      properties:
        task_id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        deleted_at:
          type: string
          format: date-time
      required:
        - task_id
        - user_id
        - deleted_at
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

---

## Event Type: task_completed

**Topic**: `task-events`

**Description**: Published when a task is marked as complete

```yaml
TaskCompletedEvent:
  allOf:
    - $ref: '#/components/schemas/BaseEvent'
  - type: object
  properties:
    event_type:
      enum: [task_completed]
    payload:
      type: object
      properties:
        task_id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        completed_at:
          type: string
          format: date-time
        recurrence:
          type: object
          nullable: true
          description: Recurrence rule if task is recurring
      required:
        - task_id
        - user_id
        - completed_at
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

---

## Event Type: reminder_due

**Topic**: `reminders`

**Description**: Published by reminder consumer when a task is due

```yaml
ReminderDueEvent:
  allOf:
    - $ref: '#/components/schemas/BaseEvent'
  - type: object
  properties:
    event_type:
      enum: [reminder_due]
    producer:
      type: string
      enum: [reminder-worker]
    payload:
      type: object
      properties:
        task_id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        title:
          type: string
        due_date:
          type: string
          format: date-time
        priority:
          type: string
          enum: [HIGH, MEDIUM, LOW]
        reminder_offset:
          type: integer
          minimum: 0
          description: Minutes before due time (0 = at due time)
      required:
        - task_id
        - user_id
        - title
        - due_date
        - priority
        - reminder_offset
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

## Topic Specifications

| Topic | Partitions | Replication | Retention | Events |
|-------|------------|-------------|-----------|--------|
| `task-events` | 1 | 1 | 7 days | task_created, task_deleted, task_completed |
| `task-updates` | 1 | 1 | 7 days | task_updated |
| `reminders` | 1 | 1 | 7 days | reminder_due |

---

## OpenAPI 3.0 Specification

```yaml
openapi: 3.0.0
info:
  title: Todo Event API
  version: 1.0.0
  description: Kafka event streaming contracts for Todo application

components:
  schemas:
    BaseEvent:
      type: object
      properties:
        event_id:
          type: string
          format: uuid
        event_type:
          type: string
          enum: [task_created, task_updated, task_deleted, task_completed, reminder_due]
        event_version:
          type: string
        timestamp:
          type: string
          format: date-time
        correlation_id:
          type: string
          format: uuid
        producer:
          type: string
        payload:
          type: object
      required:
        - event_id
        - event_type
        - event_version
        - timestamp
        - producer
        - payload

    TaskCreatedEvent:
      allOf:
        - $ref: '#/components/schemas/BaseEvent'
      type: object
      properties:
        event_type:
          enum: [task_created]
        payload:
          type: object
          properties:
            task_id:
              type: string
              format: uuid
            user_id:
              type: string
              format: uuid
            title:
              type: string
            priority:
              type: string
              enum: [HIGH, MEDIUM, LOW]
            status:
              type: string
              enum: [TODO, IN_PROGRESS, DONE]

    TaskUpdatedEvent:
      allOf:
        - $ref: '#/components/schemas/BaseEvent'
      type: object
      properties:
        event_type:
          enum: [task_updated]
        payload:
          type: object
          properties:
            task_id:
              type: string
              format: uuid
            changed_fields:
              type: array
              items:
                type: string
            changes:
              type: object

    TaskDeletedEvent:
      allOf:
        - $ref: '#/components/schemas/BaseEvent'
      type: object
      properties:
        event_type:
          enum: [task_deleted]
        payload:
          type: object
          properties:
            task_id:
              type: string
              format: uuid
            user_id:
              type: string
              format: uuid
            deleted_at:
              type: string
              format: date-time

    TaskCompletedEvent:
      allOf:
        - $ref: '#/components/schemas/BaseEvent'
      type: object
      properties:
        event_type:
          enum: [task_completed]
        payload:
          type: object
          properties:
            task_id:
              type: string
              format: uuid
            user_id:
              type: string
              format: uuid
            completed_at:
              type: string
              format: date-time
            recurrence:
              type: object

    ReminderDueEvent:
      allOf:
        - $ref: '#/components/schemas/BaseEvent'
      type: object
      properties:
        event_type:
          enum: [reminder_due]
        producer:
          type: string
          enum: [reminder-worker]
        payload:
          type: object
          properties:
            task_id:
              type: string
              format: uuid
            user_id:
              type: string
              format: uuid
            title:
              type: string
            due_date:
              type: string
              format: date-time
            priority:
              type: string
              enum: [HIGH, MEDIUM, LOW]
            reminder_offset:
              type: integer
```

---

## Validation Rules

### Common Validation

| Field | Rule |
|-------|------|
| `event_id` | Must be valid UUID v4 |
| `timestamp` | Must be ISO-8601 format, timezone-aware (UTC) |
| `correlation_id` | Must be valid UUID v4 |
| `task_id` | Must be valid UUID v4 |
| `user_id` | Must be valid UUID v4 |

### Task-Specific Validation

| Event | Field | Rule |
|-------|-------|------|
| task_created | `priority` | Must be HIGH, MEDIUM, or LOW |
| task_created | `status` | Must be TODO, IN_PROGRESS, or DONE |
| task_created | `due_date` | Must be ISO-8601 if present |
| task_created | `recurrence.frequency` | Must be daily, weekly, monthly, or cron |
| task_updated | `changed_fields` | Must be non-empty array |
| task_updated | `changes` | Must contain old/new values for each changed field |
| reminder_due | `reminder_offset` | Must be >= 0 |

---

## Error Response Schemas

### Validation Error

```json
{
  "error": "validation_error",
  "message": "Event schema validation failed",
  "details": [
    {
      "field": "payload.task_id",
      "error": "Invalid UUID format"
    }
  ]
}
```

### Publishing Error

```json
{
  "error": "publish_failed",
  "message": "Failed to publish event to Kafka",
  "details": {
    "topic": "task-events",
    "retryable": true,
    "original_error": "Connection refused"
  }
}
```

---

**Events Contract Version**: 1.0
**Last Updated**: 2026-02-06
