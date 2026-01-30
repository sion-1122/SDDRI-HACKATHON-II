# Feature Specification: Dapr Integration

**Feature Branch**: `010-dapr-integration`
**Created**: 2026-01-30
**Status**: Draft
**Input**: Integrate Dapr (Distributed Application Runtime) to abstract infrastructure complexity. Use Dapr sidecars for pub/sub over Kafka, state management for conversations, and bindings for cron-based reminders.

## User Scenarios & Testing

### User Story 1 - Dapr Sidecar Deployment (Priority: P1) MVP

As a developer, I want to deploy Dapr sidecars alongside application containers so that services can use Dapr building blocks without code changes.

**Why this priority**: Dapr sidecars enable all other Dapr features. Without them, Dapr doesn't work.

**Acceptance Scenarios**:
1. Given I apply Dapr annotations to deployments, When I deploy to Kubernetes, Then Dapr sidecar pods start alongside app pods
2. Given sidecars are running, When I check pod status, Then both app and daprd containers are Ready
3. Given sidecars exist, When I describe pods, Then they have proper sidecar configuration

### User Story 2 - Pub/Sub over Kafka (Priority: P1)

As a developer, I want to use Dapr pub/sub building block so that I don't need to write Kafka client code.

**Why this priority**: This abstracts Kafka complexity and makes the app more portable.

**Acceptance Scenarios**:
1. Given I configure Dapr pub/sub component for Kafka, When I publish via Dapr HTTP API, Then message appears in Kafka topic
2. Given a Dapr subscription exists, When messages arrive in Kafka, Then Dapr delivers them to my service via HTTP
3. Given pub/sub is working, When I check backend logs, Then no Kafka client code exists (pure Dapr)

### User Story 3 - State Management for Conversations (Priority: P2)

As a user, I want my chat conversations to persist across sessions so that I can resume conversations later.

**Why this priority**: Persistent conversation state improves chatbot UX.

**Acceptance Scenarios**:
1. Given I chat with the AI, When I close and reopen the chat, Then conversation history is preserved
2. Given I send multiple messages, When I view history, Then all messages appear in order
3. Given state is stored, When I check Redis, Then conversation data is present

### User Story 4 - Cron Bindings for Reminders (Priority: P2)

As a system, I want Dapr to trigger reminder checks on a schedule so that the backend doesn't need a scheduler.

**Why this priority**: Cron bindings externalize scheduling logic.

**Acceptance Scenarios**:
1. Given I configure a cron binding, When the cron schedule triggers, Then Dapr calls my reminder endpoint
2. Given reminder endpoint is called, When I process it, Then due notifications are sent
3. Given cron triggers, When I check Dapr logs, Then binding invocations are logged

### User Story 5 - Secrets Management (Priority: P3)

As a developer, I want to use Dapr secrets store so that sensitive data isn't in plain text.

**Why this priority**: Security best practice for production deployments.

**Acceptance Scenarios**:
1. Given I configure a secret store, When my app requests a secret via Dapr, Then Dapr retrieves it
2. Given secret is retrieved, When I inspect logs, Then secret value is not logged
3. Given secret changes, When I request it again, Then new value is returned

## Requirements

### Functional Requirements

**Dapr Sidecar (FR-001 to FR-008)**:
- FR-001: System MUST deploy Dapr to Minikube via Dapr CLI
- FR-002: System MUST enable Dapr on backend and reminder-worker deployments
- FR-003: Dapr sidecars MUST use unique app IDs per service
- FR-004: Sidecars MUST expose HTTP endpoint on port 3500
- FR-005: Sidecars MUST be configured with proper placement service address
- FR-006: System MUST use Dapr service mesh for service-to-service communication
- FR-007: Sidecar containers MUST have appropriate resource limits
- FR-008: Dapr configuration MUST enable observability (tracing, metrics)

**Pub/Sub Building Block (FR-009 to FR-016)**:
- FR-009: System MUST configure Kafka as pub/sub component in Dapr
- FR-010: System MUST subscribe to topics via Dapr subscription manifests
- FR-011: Chat API MUST publish events via Dapr HTTP API (not direct Kafka)
- FR-012: Reminder consumer MUST receive events via Dapr endpoint (not Kafka consumer)
- FR-013: System MUST remove all aiokafka client code from backend
- FR-014: Dapr MUST handle message serialization/deserialization
- FR-015: Dapr MUST handle message acknowledgment and retries
- FR-016: System MUST use CloudEvents format for all messages

**State Management (FR-017 to FR-023)**:
- FR-017: System MUST configure Redis as state store component
- FR-018: Chat API MUST save conversation state via Dapr state API
- FR-019: System MUST store conversation history keyed by user_id
- FR-020: System MUST support TTL for conversation state (7 days)
- FR-021: System MUST support state queries for conversation retrieval
- FR-022: System MUST handle state store unavailability gracefully
- FR-023: State operations MUST be consistent (strong consistency)

**Input Bindings (FR-024 to FR-029)**:
- FR-024: System MUST configure cron binding for reminder checks
- FR-025: Cron MUST trigger every 5 minutes
- FR-026: Trigger MUST POST to /api/bindings/reminders endpoint
- FR-027: Endpoint MUST process due tasks and send notifications
- FR-028: System MUST handle concurrent cron invocations
- FR-029: Cron schedule MUST be configurable

**Secrets Management (FR-030 to FR-034)**:
- FR-030: System MUST configure Kubernetes secret store
- FR-031: Application MUST retrieve DATABASE_URL via Dapr secrets API
- FR-032: Application MUST retrieve OPENAI_API_KEY via Dapr secrets API
- FR-033: Application MUST NOT read secrets directly from environment variables
- FR-034: Secret access MUST be logged for audit

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Kubernetes Pod                          │
│  ┌─────────────┐         ┌─────────────┐                       │
│  │    App      │ <─────> │   Dapr      │                       │
│  │  Container  │ HTTP    │  Sidecar    │                       │
│  └─────────────┘         └─────────────┘                       │
│                                  │                              │
│                                  │ Dapr API                     │
│                                  ▼                              │
└─────────────────────────────────────────────────────────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
         ┌──────────┐       ┌──────────┐       ┌──────────┐
         │   Pub/   │       │  State   │       │ Secrets  │
         │   Sub    │       │  Store   │       │  Store   │
         │ (Kafka)  │       │ (Redis)  │       │  (K8s)   │
         └──────────┘       └──────────┘       └──────────┘
```

### Component Configuration

**Pub/Sub Component (Kafka)**:
```yaml
apiVersion: dapr.io/v1alpha1
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
      value: "todo-group"
    - name: authRequired
      value: "false"
```

**State Store (Redis)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: conversation-state
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
    - name: keyPrefix
      value: "conversation"
```

**Cron Binding**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/5 * * * *"
```

## Success Criteria

- SC-001: Dapr deploys to Minikube in under 2 minutes
- SC-002: All application pods have Dapr sidecars running
- SC-003: Pub/sub publishes messages to Kafka via Dapr
- SC-004: Conversation state persists across restarts
- SC-005: Cron binding triggers every 5 minutes
- SC-006: No direct Kafka client code remains in backend

## Dependencies

1. **009-kafka-events** - Kafka cluster must exist
2. **Dapr CLI** - Required for Dapr installation
3. **Redis** - For state store (can deploy via Helm)

## Out of Scope

1. Dapr Actors - Virtual actor pattern
2. Workflow - Dapr workflow engine
3. Resiliency policies - Retry, timeout, circuit breaker policies
4. Link - Service-to-service link configuration
5. Lock - Distributed lock management
