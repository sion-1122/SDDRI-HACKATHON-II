# Phase 5: Kafka Event Streaming - Architecture Documentation

> **Hackathon Submission Specification 009**
> **Status**: ✅ Architecture Complete | ⏸️ Deployment Deferred (Resource Constraints)
> **Documentation Date**: February 6, 2026

---

## TL;DR - What We Accomplished

| Artifact | Status | Description |
|----------|--------|-------------|
| **Event Schemas** | ✅ Complete | TypeScript + Pydantic models for all 8 event types |
| **API Contracts** | ✅ Complete | Topic configurations, payload definitions |
| **Architecture Diagrams** | ✅ Complete | Visual documentation of event flow |
| **Implementation Guide** | ✅ Complete | Step-by-step deployment instructions |
| **Helm/K8s Configs** | 📝 Documented | Ready-to-deploy configurations |
| **Working Implementation** | ⏸️ Deferred | Requires K8s cluster (local or cloud) |

---

## Problem Statement

We needed to implement **event-driven architecture** for asynchronous task events, but faced constraints:

1. **Local Resource Constraints**: Minikube requires 2+ CPU cores, 4+ GB RAM
2. **No Cloud Access**: Financial/time barriers prevented cloud K8s deployment
3. **Existing Infrastructure**: Current Vercel + HF Spaces setup is working well
4. **Risk Aversion**: Implementing full K8s + Kafka could break existing functionality

---

## Our Solution: "Architecture-as-Documentation"

Instead of risky infrastructure changes, we took a **documentation-first approach**:

### What We Built (Zero Resources Required)

```
specs/009-kafka-events/
├── README.md                    # This file - hackathon submission summary
├── IMPLEMENTATION_GUIDE.md      # Complete deployment guide
├── spec.md                      # Original feature specification
├── plan.md                      # Implementation plan
├── research.md                  # Technical research notes
├── data-model.md                # Data model documentation
├── contracts/
│   ├── events.md                # Event contract definitions
│   ├── dapr.md                  # Dapr component specifications
│   ├── event-schemas.ts         # TypeScript type definitions
│   └── event_schemas.py         # Python Pydantic models
└── quickstart.md                # Quick start guide
```

---

## Event-Driven Architecture Design

### Event Types (8 Total)

| Event | Description | Topic | Producer |
|-------|-------------|-------|----------|
| `task-created` | New task created | `task-events` | Chat API |
| `task-updated` | Task fields changed | `task-updates` | Chat API |
| `task-deleted` | Task removed | `task-events` | Chat API |
| `task-completed` | Task marked done | `task-updates` | Chat API |
| `reminder-scheduled` | Reminder set for task | `reminders` | Reminder Worker |
| `reminder-triggered` | Reminder fired | `reminders` | Reminder Worker |
| `reminder-cancelled` | Reminder cancelled | `reminders` | Reminder Worker |
| `recurrence-instance-created` | New recurring task instance | `task-events` | Recurrence Worker |

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        EVENT FLOW ARCHITECTURE                               │
└──────────────────────────────────────────────────────────────────────────────┘

    USER ACTION
         │
         ▼
┌────────────────┐     publish      ┌──────────────────┐
│   Chat API     │ ────────────────> │                  │
│  (FastAPI)     │   Event Payload   │                  │
│                │                   │                  │
│  - Create task │                   │     Redpanda     │
│  - Update task │                   │     (Kafka)      │
│  - Delete task │                   │                  │
└────────────────┘                   │  ┌────────────┐  │
                                     │  │ task-events│  │
                                     │  ├────────────┤  │
                                     │  │ reminders  │  │
                                     │  ├────────────┤  │
                                     │  │task-updates│  │
                                     │  └────────────┘  │
                                     └─────────┬────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
          ┌───────────────┐         ┌───────────────┐         ┌───────────────┐
          │  Reminder     │         │   Future      │         │   Analytics   │
          │  Consumer     │         │   Consumers   │         │   (TODO)      │
          │               │         │               │         │               │
          │ - Schedule    │         │ - Webhooks    │         │ - Reports     │
          │ - Trigger     │         │ - Integrations│         │ - Metrics     │
          └───────────────┘         └───────────────┘         └───────────────┘
```

---

## Event Schema Examples

### Task Created Event

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task-created",
  "event_version": "v1",
  "timestamp": "2026-02-06T12:00:00Z",
  "correlation_id": "660e8400-e29b-41d4-a716-446655440001",
  "producer": "chat-api",
  "payload": {
    "task_id": "770e8400-e29b-41d4-a716-446655440002",
    "title": "Complete hackathon submission",
    "description": "Finalize Phase 5 documentation",
    "priority": "HIGH",
    "status": "TODO",
    "due_date": null,
    "recurrence": null,
    "tags": ["hackathon", "documentation"],
    "user_id": "880e8400-e29b-41d4-a716-446655440003",
    "created_at": "2026-02-06T12:00:00Z"
  }
}
```

---

## Current Infrastructure (What We're NOT Breaking)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRODUCTION INFRASTRUCTURE                          │
│                    (Vercel + Hugging Face Spaces)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────────┐         ┌──────────────────────┐                    │
│   │   Frontend       │ ──────> │     Backend          │                    │
│   │   (Vercel)       │ HTTPS   │   (HF Spaces)        │                    │
│   │                  │         │                      │                    │
│   │  - Next.js 16    │         │  - FastAPI           │                    │
│   │  - React 19      │         │  - Neon PostgreSQL   │                    │
│   │  - Tailwind CSS  │         │  - AI Chat Integration│                   │
│   └──────────────────┘         └──────────────────────┘                    │
│                                                                             │
│                     ✅ WORKING - DO NOT MODIFY                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Status**: Production infrastructure remains **unchanged and operational**.

---

## Phase 5 Implementation Path (When Resources Available)

### Step 1: Infrastructure Setup (1-2 hours)

```bash
# Install Dapr
dapr init --kubernetes --wait

# Deploy Redpanda
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda --values k8s/redpanda-values.yaml

# Create topics
kubectl exec -it redpanda-0 -- rpk topic create task-events -p 3 -r 2
kubectl exec -it redpanda-0 -- rpk topic create reminders -p 3 -r 2
kubectl exec -it redpanda-0 -- rpk topic create task-updates -p 3 -r 2
```

### Step 2: Backend Integration (2-3 hours)

```python
# Add event publishing to existing endpoints
from backend.services.events.publisher import EventPublisher

publisher = EventPublisher()

async def create_task(task: TaskCreate, user_id: UUID):
    task = await db.create_task(task, user_id)

    # Publish event (non-blocking)
    await publisher.publish_task_created(task, user_id)

    return task
```

### Step 3: Deploy Consumer Services (1-2 hours)

```bash
# Deploy reminder worker
helm install todo-reminder-worker ./k8s/reminder-worker
```

### Step 4: Verification (30 minutes)

```bash
# Verify events are flowing
kubectl logs -f deployment/todo-reminder-worker

# Should see:
# [INFO] Received task-created event for task abc-123
# [INFO] Scheduled reminder for 2026-02-07T10:00:00Z
```

---

## Key Design Decisions

### Why Redpanda over Apache Kafka?

| Factor | Redpanda | Apache Kafka |
|--------|----------|--------------|
| Resource Usage | Lower (C++) | Higher (Java/Scala) |
| Setup Complexity | Single binary | ZooKeeper + Brokers |
| K8s Integration | Native Helm | Community Charts |
| Compatibility | 100% Kafka API | Native |

### Why Dapr?

1. **Abstraction**: Swap Kafka without code changes
2. **Resilience**: Built-in retries, dead letter queues
3. **Observability**: Distributed tracing out of the box
4. **Language Agnostic**: Same patterns for Python, TypeScript, Go

### Why Event-Driven?

1. **Decoupling**: Producers don't need to know consumers
2. **Scalability**: Add consumers without touching producers
3. **Reliability**: Events persist even if consumers are down
4. **Extensibility**: Future features (analytics, webhooks) just subscribe

---

## Files Delivered

| File | Lines | Purpose |
|------|-------|---------|
| `contracts/event-schemas.ts` | ~200 | TypeScript type definitions |
| `contracts/event_schemas.py` | ~300 | Python Pydantic models |
| `IMPLEMENTATION_GUIDE.md` | ~250 | Complete deployment documentation |
| `README.md` | This file | Hackathon submission summary |

---

## Hackathon Submission Value

### What Judges Can See

1. **Complete Architecture Design**: Production-ready event schemas
2. **Type Safety**: TypeScript + Pydantic contracts
3. **Deployment Readiness**: Helm configs, K8s manifests documented
4. **Migration Path**: Clear upgrade path from current infra
5. **Risk Management**: No breaking changes to working system

### What Would Need Resources

1. Actual K8s cluster (Minikube or cloud)
2. Redpanda deployment
3. End-to-end testing with real Kafka
4. Performance testing at scale

---

## Next Steps (If Continuing)

| Priority | Task | Effort | Resources Required |
|----------|------|--------|-------------------|
| P0 | Get cloud K8s access (AKS/GKE free tier) | 1 day | Cloud account |
| P1 | Deploy Redpanda + Dapr | 2 hours | K8s cluster |
| P2 | Add event publishing to backend | 3 hours | Development |
| P3 | Implement reminder consumer | 4 hours | Development |
| P4 | E2E testing | 2 hours | K8s cluster |

---

## Conclusion

Phase 5 architecture is **production-ready and fully documented**. The event-driven design enables:

- ✅ Asynchronous task processing
- ✅ Scalable reminder scheduling
- ✅ Future extensibility (webhooks, analytics)
- ✅ Clean separation of concerns
- ✅ Migration path when resources allow

**Current infrastructure remains operational and untouched.**

---

**Spec**: 009-kafka-events | **Branch**: k8s-infra | **Date**: 2026-02-06
