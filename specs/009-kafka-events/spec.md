# Feature Specification: Kafka Event Streaming

**Feature Branch**: `009-kafka-events`
**Created**: 2026-01-30
**Status**: Draft
**Input**: Implement event-driven architecture using Apache Kafka (via Redpanda) for async task events, reminder scheduling, and task updates. Deploy to Minikube and integrate with existing Chat API.

## User Scenarios & Testing

### User Story 1 - Kafka Cluster Deployment (Priority: P1) MVP

As a developer, I want to deploy a Kafka cluster to Minikube so that the application can publish and consume events asynchronously.

**Why this priority**: Without Kafka, no event-driven features work. This is infrastructure for all subsequent features.

**Acceptance Scenarios**:
1. Given Minikube is running, When I deploy Redpanda via Helm, Then the cluster starts with 3 pods
2. Given the cluster is running, When I check pod status, Then all pods are Ready
3. Given Redpanda is running, When I port-forward to 9092, Then I can connect via Kafka client

### User Story 2 - Event Topics Creation (Priority: P1)

As a developer, I want to create Kafka topics for different event types so that events are properly categorized.

**Why this priority**: Topics are the fundamental organizing unit in Kafka.

**Acceptance Scenarios**:
1. Given the cluster is running, When I create topics, Then task-events, reminders, task-updates exist
2. Given topics exist, When I list topics, Then they show correct partition counts (3) and replication factor (2)
3. Given topics exist, When I describe them, Then they have appropriate retention settings

### User Story 3 - Event Publishing from Chat API (Priority: P1)

As a user, when I interact with the AI chatbot, I want task events to be published to Kafka so that other services can react.

**Why this priority**: This connects user actions to the event bus.

**Acceptance Scenarios**:
1. Given I create a task via chat, When the task is saved, Then a task-created event is published
2. Given I update a task via chat, When the task is updated, Then a task-updated event is published
3. Given I delete a task via chat, When the task is deleted, Then a task-deleted event is published

### User Story 4 - Event Consumers (Priority: P2)

As a developer, I want to create consumer services that process events so that reminders and notifications work.

**Why this priority**: Consumers enable async processing of events.

**Acceptance Scenarios**:
1. Given a task-created event is published, When the consumer reads it, Then it schedules a reminder if due_date exists
2. Given a task-updated event is published, When the consumer reads it, Then it reschedules reminders
3. Given a task-deleted event is published, When the consumer reads it, Then it cancels pending reminders

### User Story 5 - Event Schemas (Priority: P2)

As a developer, I want well-defined event schemas so that events are consistent and type-safe.

**Why this priority**: Schemas prevent breaking changes and ensure compatibility.

**Acceptance Scenarios**:
1. Given an event is published, When I inspect the payload, Then it matches the defined schema
2. Given a consumer reads an event, When it validates the schema, Then validation passes
3. Given schema evolution is needed, When I update a schema, Then backward compatibility is maintained

## Requirements

### Functional Requirements

**Kafka Infrastructure (FR-001 to FR-008)**:
- FR-001: System MUST deploy Redpanda Kafka cluster to Minikube via Helm
- FR-002: Kafka cluster MUST have 3 brokers for high availability
- FR-003: Kafka cluster MUST configure persistence with PVCs
- FR-004: System MUST create topic: task-events (partitions: 3, replication: 2)
- FR-005: System MUST create topic: reminders (partitions: 3, replication: 2)
- FR-006: System MUST create topic: task-updates (partitions: 3, replication: 2)
- FR-007: Topics MUST have 7-day retention period
- FR-008: Kafka MUST be accessible from backend services via ClusterIP service

**Event Publishing (FR-009 to FR-015)**:
- FR-009: Chat API MUST publish task-created event to task-events topic
- FR-010: Chat API MUST publish task-updated event to task-updates topic
- FR-011: Chat API MUST publish task-deleted event to task-events topic
- FR-012: Events MUST include event_type, timestamp, task_id, and payload
- FR-013: Events MUST be published asynchronously (non-blocking)
- FR-014: Event publishing failures MUST be logged but not block API response
- FR-015: Events MUST include correlation_id for tracing

**Event Consumption (FR-016 to FR-022)**:
- FR-016: System MUST run reminder consumer service
- FR-017: Consumer MUST subscribe to task-events and task-updates topics
- FR-018: Consumer MUST process events in order per partition
- FR-019: Consumer MUST commit offsets after successful processing
- FR-020: Consumer MUST handle processing errors with retry and dead letter queue
- FR-021: Reminder consumer MUST schedule notifications for tasks with due_dates
- FR-022: Consumer MUST be deployable as Kubernetes Deployment

**Event Schemas (FR-023 to FR-028)**:
- FR-023: All events MUST follow common base schema (id, type, timestamp, correlation_id)
- FR-024: task-created event MUST include full task details
- FR-025: task-updated event MUST include changed fields only
- FR-026: task-deleted event MUST include task_id only
- FR-027: reminder-due event MUST include task_id and due_date
- FR-028: Schemas MUST be versioned (v1, v2, etc)

### Data Model

**Event Base Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "task-created | task-updated | task-deleted | reminder-due",
  "event_version": "v1",
  "timestamp": "ISO-8601 UTC",
  "correlation_id": "uuid",
  "producer": "chat-api | reminder-worker",
  "payload": { /* event-specific data */ }
}
```

**Task Created Event**:
```json
{
  "payload": {
    "task_id": "uuid",
    "title": "string",
    "description": "string | null",
    "priority": "HIGH | MEDIUM | LOW",
    "status": "TODO | IN_PROGRESS | DONE",
    "due_date": "ISO-8601 | null",
    "recurrence": { /* recurrence rule */ },
    "tags": ["string"],
    "user_id": "uuid"
  }
}
```

**Task Updated Event**:
```json
{
  "payload": {
    "task_id": "uuid",
    "changed_fields": ["status", "due_date"],
    "changes": {
      "status": { "old": "TODO", "new": "IN_PROGRESS" },
      "due_date": { "old": null, "new": "2026-01-31T10:00:00Z" }
    }
  }
}
```

### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Chat API   │ ──────> │   Kafka      │ <────── │  Reminder   │
│  (FastAPI)  │ Publish │   (Redpanda) │ Consume │  Consumer   │
└─────────────┘         └──────────────┘         └─────────────┘
                               ▲
                               │ task-events
                               │ reminders
                               │ task-updates
                               ▼
                        ┌──────────────┐
                        │ Future: More │
                        │ Consumers    │
                        └──────────────┘
```

## Success Criteria

- SC-001: Redpanda cluster deploys to Minikube in under 3 minutes
- SC-002: All topics created and verified within 30 seconds
- SC-003: Event published from Chat API appears in topic within 1 second
- SC-004: Consumer processes event and schedules reminder within 2 seconds
- SC-005: All events pass schema validation

## Dependencies

1. **006-k8s-deployment** - Minikube cluster available
2. **Helm 3+** - Required for Redpanda deployment
3. **aiokafka** - Python async Kafka client library

## Out of Scope

1. Kafka Connect - External system integrations
2. KSQL - Stream processing
3. Kafka MirrorMaker - Cross-cluster replication
4. Schema Registry - Formal schema registry (Confluent)
5. Multiple consumer groups - Single consumer only
