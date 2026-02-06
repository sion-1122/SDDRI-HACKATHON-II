# Implementation Plan: Kafka Event Streaming with Dapr

**Branch**: `k8s-infra` | **Date**: 2026-02-06 | **Spec**: [specs/009-kafka-events/spec.md](../../specs/009-kafka-events/spec.md)
**Input**: Implement event-driven architecture using Redpanda Kafka + Dapr for async task events, reminder scheduling, and task updates on Minikube.

## Summary

Implement event-driven architecture for the Todo Chatbot using Redpanda (Kafka-compatible) as the event broker and Dapr as the abstraction layer. The Chat API will publish task lifecycle events (created/updated/deleted) to Kafka topics via Dapr, and consumer services will process these events asynchronously for reminder scheduling.

**Key Decision**: Using Dapr instead of direct Kafka (aiokafka) provides:
- Broker abstraction (easier to switch to Redis/Azure Service Bus later)
- Built-in retries and dead-letter queues
- Simplified configuration
- Service invocation patterns

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**: Redpanda (Kafka), Dapr, dapr-ext-fastapi, Pydantic
**Storage**: Neon PostgreSQL (existing), Redpanda topics (event streaming)
**Testing**: pytest (backend), event streaming tests
**Target Platform**: Minikube (local development), AKS/GKE/OKE (production)
**Project Type**: Distributed event-driven microservices
**Performance Goals**: Event publishing <100ms, event consumption <500ms
**Constraints**: 2 CPUs, ~4GB RAM (Minikube), single-node Redpanda
**Scale/Scope**: Development/testing (not production scale)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Checks

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Persistent Storage** | ✅ PASS | Events persisted in Redpanda topics, state in Neon PostgreSQL |
| **II. RESTful API** | ✅ PASS | Existing FastAPI endpoints remain RESTful; events are async side-effect |
| **III. Responsive Web UI** | ✅ PASS | Frontend unchanged; events are backend concern |
| **IV. Multi-User Architecture** | ✅ PASS | Events include user_id for scoping; Kafka ACLs not required (trusted environment) |
| **VI. Monorepo Structure** | ✅ PASS | New services follow existing backend/ structure |
| **XI. Containerization with Docker** | ✅ PASS | Services containerized with Docker |
| **XII. Kubernetes Orchestration** | ✅ PASS | Deployed to Minikube via Helm |
| **XIII. Helm Chart Packaging** | ✅ PASS | Redpanda and Dapr installed via Helm |
| **XIV. AI-Assisted DevOps** | ✅ PASS | Use kubectl-ai for manifest generation |

### Phase IV Constraints

**Containerization Requirements**:
- Backend: Multi-stage Dockerfile with Python slim base
- Dapr sidecar injected via annotations (not in Docker image)
- Images testable locally via `docker run`

**Kubernetes Deployment Requirements**:
- Minikube deployment for local development
- Redpanda: 1 replica (resource-constrained)
- Dapr: Installed via Helm to `dapr-system` namespace
- Services: ClusterIP for internal communication
- ConfigMaps: Dapr component configuration
- Health probes: Liveness/readiness for all pods

**Cloud-Native Requirements**:
- Stateless application design
- Health probes configured
- Resource limits: CPU/memory requests/limits
- Graceful shutdown handling

## Project Structure

### Documentation (this feature)

```text
specs/009-kafka-events/
├── plan.md              # This file
├── research.md          # Phase 0 output (Redpanda + Dapr research)
├── data-model.md        # Phase 1 output (event schemas)
├── quickstart.md        # Phase 1 output (local development guide)
├── contracts/           # Phase 1 output (event schemas OpenAPI)
│   ├── events.md        # Event API contracts
│   └── dapr.md          # Dapr component schemas
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── models/              # Existing SQLModel models
├── services/
│   ├── kafka_service.py     # NEW: Kafka event publishing service
│   └── event_schemas.py     # NEW: Pydantic event models
├── api/
│   └── tasks.py              # EXISTING: Add event publishing hooks
├── consumers/           # NEW: Event consumers
│   ├── __init__.py
│   ├── reminder_consumer.py  # Processes task events for reminders
│   └── base_consumer.py      # Base consumer with retry logic
├── dapr/                # NEW: Dapr configuration
│   ├── components/            # Dapr component YAMLs
│   │   ├── kafka-pubsub.yaml  # Pub/sub component for Redpanda
│   │   └── secret.yaml        # Dapr secrets (if needed)
│   └── config.yaml            # Dapr configuration
├── tests/
│   ├── test_event_schemas.py      # NEW: Event validation tests
│   ├── test_kafka_service.py     # NEW: Kafka publishing tests
│   └── test_consumers.py         # NEW: Consumer tests
├── Dockerfile           # EXISTING (may need Dapr annotations)
└── k8s/                 # NEW: Kubernetes manifests
    ├── redpanda/                  # Redpanda Helm values
    │   └── values-minimal.yaml
    ├── dapr/                      # Dapr Helm values
    │   └── values-dev.yaml
    └── backend/                   # Backend deployment
        ├── deployment.yaml
        └── service.yaml
```

**Structure Decision**: This is a **Phase IV** feature extending the existing Phase III Todo Chatbot. The backend directory structure is maintained, with new additions for Dapr integration, Kafka services, and event consumers. The k8s/ directory is added per Principle VI for Kubernetes manifests.

## Architecture

### Event Flow with Dapr

```
┌─────────────┐          ┌──────────────┐          ┌─────────────┐
│  Chat API   │          │    Dapr      │          │  Redpanda   │
│  (FastAPI)  │ ───────> │   Sidecar    │ ───────> │   (Kafka)   │
│             │ Publish  │              │ Publish  │             │
└─────────────┘          └──────────────┘          └─────────────┘
       │                        │                         │
       │                        │ Subscribes             │
       ▼                        ▼                         ▼
┌─────────────┐          ┌──────────────┐          ┌─────────────┐
│   Task      │          │    Dapr      │          │   Reminder   │
│   Database  │          │   Sidecar    │ <────────── │   Consumer   │
│  (Neon SQL) │          │              │  Consume   │  (Service)   │
└─────────────┘          └──────────────┘          └─────────────┘
```

### Dapr Component Configuration

```yaml
# k8s/dapr/components/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  metadata:
  - name: brokers
    value: "redpanda.redpanda:9092"
  - name: consumerGroup
    value: "todo-consumers"
  - name: authRequired
    value: "false"
  - name: clientTransport
    value: "tcp://redpanda.redpanda:9092"
```

### Event Topics

| Topic | Partitions | Purpose | Producer | Consumer |
|-------|------------|---------|----------|----------|
| `task-events` | 3 | Task lifecycle events | Chat API | Reminder Consumer |
| `task-updates` | 3 | Task change events | Chat API | Analytics (future) |
| `reminders` | 3 | Reminder notifications | Reminder Consumer | Notification Service |

## Implementation Phases

### Phase 0: Research (COMPLETED)

**Research.md Generated**: Yes

Key findings:
- Redpanda single-node viable for 2CPU/4GB Minikube
- Dapr simplifies Kafka integration significantly
- dapr-ext-fastapi provides clean FastAPI integration
- Resource constraints require minimal Redpanda configuration

### Phase 1: Design & Contracts

**Deliverables**:
1. `data-model.md` - Event schemas, topic definitions
2. `contracts/events.md` - OpenAPI specs for events
3. `contracts/dapr.md` - Dapr component specifications
4. `quickstart.md` - Local development setup guide

**Event Schemas**:
- Base event: `event_id`, `event_type`, `timestamp`, `correlation_id`, `producer`
- TaskCreatedEvent: Full task details
- TaskUpdatedEvent: Changed fields only
- TaskDeletedEvent: Task ID only
- ReminderDueEvent: Task ID and due date

### Phase 2: Tasks (via /sp.tasks)

**Task Areas**:
1. Infrastructure: Install Dapr, deploy Redpanda
2. Backend: Add Kafka publishing service, event hooks
3. Consumers: Create reminder consumer service
4. Testing: Event validation, integration tests

## Dependencies

### Internal
- **004-ai-chatbot** - Chat API (event producer)
- **008-advanced-features** - Due dates and reminders (event triggers)
- **006-k8s-deployment** - Minikube cluster setup

### External
- **Dapr 1.12+** - Distributed application runtime
- **Redpanda 23.3+** - Kafka-compatible event streaming
- **Helm 3+** - Package manager for Kubernetes
- **Minikube 1.30+** - Local Kubernetes cluster
- **dapr-ext-fastapi** - Dapr FastAPI extension
- **Pydantic** - Event schema validation

## Success Criteria

- SC-001: Dapr installs to Minikube successfully
- SC-002: Redpanda deploys with single-node configuration
- SC-003: Chat API publishes events to Kafka via Dapr
- SC-004: Reminder consumer processes events and schedules reminders
- SC-005: Event schemas validate correctly with Pydantic

## Resource Requirements (Minikube)

```yaml
# Minikube startup
minikube start \
  --cpus=2 \
  --memory=4096 \
  --disk-size=30gb \
  --driver=docker
```

## Known Limitations

1. **Resource Constrained**: 2CPU/4GB is minimum for Redpanda; not production-ready
2. **Single Node**: No fault tolerance; Redpanda has no HA
3. **No Kafka ACLs**: Trusted environment; no authentication
4. **Development Only**: Not suitable for production workloads

## Rollout Plan

1. **Install Dapr** to Minikube via Helm
2. **Deploy Redpanda** with minimal configuration
3. **Create Dapr components** for Kafka pub/sub
4. **Add event publishing** to Chat API
5. **Create reminder consumer** service
6. **Deploy consumers** to Kubernetes
7. **End-to-end testing**

## Testing Strategy

1. **Unit Tests**: Event schema validation with Pydantic
2. **Integration Tests**: Dapr pub/sub with local Redpanda
3. **E2E Tests**: Chat API → Kafka → Consumer flow
4. **Resource Tests**: Verify Minikube can handle load

---

**Plan Version**: 1.0
**Last Updated**: 2026-02-06
**Status**: Ready for Phase 1 (Design & Contracts)
