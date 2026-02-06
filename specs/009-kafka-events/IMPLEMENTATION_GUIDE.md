# Kafka Event Streaming - Implementation Guide

> **Status**: Architecture Complete | **Deployment**: Deferred (Resource Constraints)
> **Current Infrastructure**: Vercel (Frontend) + Hugging Face Spaces (Backend) | **Phase 5**: Designed, Not Deployed

---

## Executive Summary

This document describes the **event-driven architecture** designed for Phase 5 of the Todo List Hackathon project. The implementation is **deferred** due to resource constraints (local K8s limitations, no cloud access).

The architecture design is **complete and production-ready**. When resources become available, deployment can proceed using the configurations in this document.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CURRENT INFRASTRUCTURE                             │
│                    (Vercel + Hugging Face Spaces)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐         ┌──────────────┐                                │
│   │   Frontend   │ ──────> │    Backend   │                                │
│   │   (Vercel)   │ HTTPS   │   (HF Spaces)│                                │
│   │  Next.js 16  │         │    FastAPI   │                                │
│   └──────────────┘         └──────────────┘                                │
│                                       │                                      │
│                                       ▼                                      │
│                              ┌──────────────┐                               │
│                              │   Neon DB    │                               │
│                              │  PostgreSQL  │                               │
│                              └──────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                  PHASE 5: DESIGNED (NOT DEPLOYED)
                              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 5 TARGET INFRASTRUCTURE                         │
│              (Minikube/AKS/GKE + Redpanda + Dapr)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐         ┌──────────────────────────────────────┐        │
│   │   Frontend   │ ──────> │              Backend                  │        │
│   │  (K8s Pod)   │ HTTPS   │         (K8s Deployment)             │        │
│   └──────────────┘         │  ┌─────────┐  ┌──────────────────┐   │        │
│                            │  │ FastAPI │  │  Dapr Sidecar    │   │        │
│                            │  └────┬────┘  │  (Pub/Sub API)   │   │        │
│                            │       │       └─────────┬──────────┘   │        │
│                            │       │                 │              │        │
│                            └───────┼─────────────────┼──────────────┘        │
│                                    │                 │                      │
│                                    │                 ▼                      │
│                                    │         ┌──────────────┐               │
│                                    │         │   Redpanda   │               │
│                                    │         │  (Kafka)     │               │
│                                    │         └──────┬───────┘               │
│                                    │                │                      │
│                                    │    ┌───────────┴───────────┐          │
│                                    │    │                       │          │
│                                    ▼    ▼                       ▼          │
│                            ┌─────────────┐          ┌─────────────┐        │
│                            │   Reminder  │          │   Future    │        │
│                            │   Consumer  │          │  Consumers  │        │
│                            │  (Worker)   │          │             │        │
│                            └─────────────┘          └─────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Event Schema Contracts

### Base Event Structure

All events follow this base contract:

```typescript
interface BaseEvent {
  event_id: string;           // UUID v4
  event_type: EventType;      // Union of all event types
  event_version: 'v1';        // Schema version
  timestamp: string;          // ISO-8601 UTC
  correlation_id: string;     // UUID for tracing
  producer: 'chat-api' | 'reminder-worker' | 'system';
  payload: unknown;           // Event-specific data
}

type EventType =
  | 'task-created'
  | 'task-updated'
  | 'task-deleted'
  | 'task-completed'
  | 'reminder-scheduled'
  | 'reminder-triggered'
  | 'reminder-cancelled';
```

### Event Payloads

#### Task Created Event

```typescript
interface TaskCreatedPayload {
  task_id: string;
  title: string;
  description: string | null;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'TODO' | 'IN_PROGRESS' | 'DONE';
  due_date: string | null;           // ISO-8601
  recurrence: RecurrenceRule | null;
  tags: string[];
  user_id: string;
  created_at: string;
}
```

#### Task Updated Event

```typescript
interface TaskUpdatedPayload {
  task_id: string;
  changed_fields: string[];
  changes: Record<string, { old: unknown; new: unknown }>;
  updated_at: string;
}
```

#### Reminder Scheduled Event

```typescript
interface ReminderScheduledPayload {
  task_id: string;
  reminder_id: string;
  due_date: string;                  // ISO-8601
  reminder_time: string;             // ISO-8601
  recurrence: RecurrenceRule | null;
}
```

---

## Kafka Topic Configuration

| Topic | Partitions | Replication Factor | Retention | Purpose |
|-------|------------|-------------------|-----------|---------|
| `task-events` | 3 | 2 | 7 days | Task lifecycle events (created, updated, deleted) |
| `reminders` | 3 | 2 | 7 days | Reminder scheduling and triggering |
| `task-updates` | 3 | 2 | 7 days | Task state change events |
| `dead-letter` | 3 | 2 | 30 days | Failed events for analysis |

---

## Dapr Component Configuration

```yaml
# dapr/components/pubsub.yaml
apiVersion: dapr.io/v1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda.redpanda.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-app-consumers"
    - name: authRequired
      value: "false"
    - name: allowedTopics
      value: "task-events,reminders,task-updates"
```

---

## Implementation Checklist (When Resources Available)

### Pre-Deployment

- [ ] Verify Minikube/Cloud K8s cluster access
- [ ] Verify Helm 3+ installed
- [ ] Verify kubectl configured
- [ ] Review resource requirements (CPU: 2 cores, RAM: 4GB minimum)

### Deployment Steps

1. **Install Dapr to K8s Cluster**
   ```bash
   dapr init --kubernetes --wait
   ```

2. **Deploy Redpanda via Helm**
   ```bash
   helm repo add redpanda https://charts.redpanda.com
   helm install redpanda redpanda/redpanda --values k8s/helm/redpanda-values.yaml
   ```

3. **Create Kafka Topics**
   ```bash
   kubectl exec -it redpanda-0 -- rpk topic create task-events -p 3 -r 2
   kubectl exec -it redpanda-0 -- rpk topic create reminders -p 3 -r 2
   kubectl exec -it redpanda-0 -- rpk topic create task-updates -p 3 -r 2
   ```

4. **Deploy Backend with Dapr Sidecar**
   ```bash
   helm install todo-backend ./k8s/helm/todo-backend --values k8s/helm/values-local.yaml
   ```

5. **Deploy Reminder Consumer**
   ```bash
   helm install todo-reminder-worker ./k8s/helm/todo-reminder-worker
   ```

---

## Migration Path: Current → Phase 5

### Phase 1: Add Event Publishing (Non-Breaking)

Add event publishing to existing HF Spaces backend without requiring Kafka:

```python
# backend/services/event_publisher.py
class EventPublisher:
    async def publish_task_created(self, task: Task):
        """In Phase 5: Publishes to Kafka. Currently: No-op."""
        # TODO: Implement Kafka publishing when Phase 5 is deployed
        logger.info(f"[EVENT] Task created: {task.id}")
        # When Phase 5 is ready:
        # await dapr.publish_event(
        #     pubsub_name="kafka-pubsub",
        #     topic_name="task-events",
        #     data=event_data
        # )
```

### Phase 2: Deploy K8s Infrastructure

When resources available, deploy K8s + Kafka without touching current infra.

### Phase 3: Migrate Backend to K8s

Migrate HF Spaces → K8s Deployment (Blue-Green deployment, zero downtime).

---

## Configuration Files (Reference)

All configuration files are located in:
- `specs/009-kafka-events/contracts/` - Schema definitions
- `k8s/helm/` - Helm charts (created when deployment ready)
- `k8s/manifests/` - Raw K8s manifests (created when deployment ready)

---

## Testing Strategy (Without Deployment)

### Mock Event Bus for Testing

```python
# backend/services/mock_event_bus.py
class MockEventBus:
    """In-memory event bus for testing Phase 5 event contracts."""

    def __init__(self):
        self.events: List[BaseEvent] = []

    async def publish(self, event: BaseEvent) -> None:
        """Store event in memory for validation."""
        self.events.append(event)
        logger.info(f"[MOCK EVENT] {event.event_type}: {event.event_id}")

    async def get_events(self, event_type: str) -> List[BaseEvent]:
        """Retrieve events by type for testing."""
        return [e for e in self.events if e.event_type == event_type]
```

---

## Success Metrics (For Deployment Readiness)

| Metric | Target | Status |
|--------|--------|--------|
| Event schemas defined | 100% | ✅ Complete |
| API contracts documented | 100% | ✅ Complete |
| Helm charts created | 0% | ⏳ Deferred |
| K8s manifests created | 0% | ⏳ Deferred |
| Integration tests written | 0% | ⏳ Deferred |

---

## Resources Required for Deployment

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 20 GB | 50 GB |
| Network | 100 Mbps | 1 Gbps |

---

## Contact & Support

For questions about this architecture or deployment:
- Review: `specs/009-kafka-events/` directory
- Issues: Create GitHub issue with tag `phase-5`
- Documentation: This file + `contracts/` directory
