# Research: Kafka Event Streaming with Dapr Integration

**Feature**: 009-kafka-events | **Date**: 2026-02-06

## Overview

Research findings for implementing event-driven architecture using Redpanda (Kafka-compatible) and Dapr on Minikube with resource constraints (2 CPUs, ~4GB RAM).

---

## Decision: Dapr + Redpanda Architecture

### Chosen Approach

**Use Dapr as abstraction layer over Redpanda Kafka**

**Rationale**:
- Dapr provides broker abstraction (easily switch to Redis/Azure Service Bus later)
- Built-in retries and dead-letter queues
- Simplified configuration vs direct aiokafka
- Service invocation patterns for future microservices
- Better observability with built-in metrics

**Alternatives Considered**:
- **aiokafka (Direct Kafka)**: Rejected due to manual connection management, failure handling complexity
- **Redis Pub/Sub**: Rejected because spec explicitly requires Kafka/Redpanda
- **Confluent Cloud**: Rejected due to cost ($100+/mo for development)

---

## Redpanda on Minikube

### Resource-Constrained Configuration

Given **2 CPUs / 4GB RAM** constraints:

```yaml
# Single-node Redpanda for development
resources:
  requests:
    cpu: "1"
    memory: "2Gi"
  limits:
    cpu: "2"
    memory: "3Gi"

# Redpanda startup args
--overprovisioned
--smp=1
--memory=3G
--reserve-memory=512M
```

**Key Findings**:
- Single node required (resource constraints prevent 3-broker cluster)
- 3GB RAM minimum for Redpanda stability
- Development/testing only - NOT production grade
- Enable `enable_memory_locking: true` for performance

### Helm Installation

```bash
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --create-namespace \
  --set replicas=1 \
  --set resources.requests.cpu=1 \
  --set resources.requests.memory=2Gi \
  --set resources.limits.cpu=2 \
  --set resources.limits.memory=3Gi
```

---

## Dapr Integration

### Installation on Minikube

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=false \
  --wait
```

**Resource Requirements**: Dapr requires <100MB per pod (minimal impact)

### Dapr Component for Kafka Pub/Sub

```yaml
# k8s/dapr/components/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
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

### FastAPI + Dapr SDK Integration

```python
# Install
pip install dapr-ext-fastapi dapr

# main.py
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient
import json

app = FastAPI()
dapr = DaprApp(app)
dapr_client = DaprClient()

# Publish event
@app.post("/api/tasks/{task_id}/events")
async def publish_task_event(task_id: str, event_data: dict):
    dapr_client.publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-events",
        data=json.dumps(event_data),
        data_content_type="application/json"
    )
    return {"status": "published"}

# Subscribe to topic (Dapr handles subscription)
@dapr.subscribe(pubsub="kafka-pubsub", topic="task-events")
async def handle_task_event(event_data: dict):
    print(f"Received event: {event_data}")
    # Process event
    return {"status": "processed"}
```

---

## Event Schema Design

### Pydantic Models for Validation

```python
# services/event_schemas.py
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum

class EventType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_COMPLETED = "task_completed"
    REMINDER_DUE = "reminder_due"

class BaseEvent(BaseModel):
    """Base event schema"""
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    event_type: EventType
    event_version: str = "v1"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    producer: str = "chat-api"

class TaskCreatedEvent(BaseEvent):
    """Event published when a task is created"""
    event_type: EventType = EventType.TASK_CREATED
    payload: Dict[str, Any]

    @validator('payload')
    def validate_payload(cls, v):
        required_fields = ["task_id", "user_id", "title"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field: {field}")
        return v

class TaskUpdatedEvent(BaseEvent):
    """Event published when a task is updated"""
    event_type: EventType = EventType.TASK_UPDATED
    payload: Dict[str, Any]

    @validator('payload')
    def validate_payload(cls, v):
        if "task_id" not in v:
            raise ValueError("Missing task_id")
        if "changed_fields" not in v or "changes" not in v:
            raise ValueError("Missing change details")
        return v

class TaskDeletedEvent(BaseEvent):
    """Event published when a task is deleted"""
    event_type: EventType = EventType.TASK_DELETED
    payload: Dict[str, Any]

    @validator('payload')
    def validate_payload(cls, v):
        if "task_id" not in v:
            raise ValueError("Missing task_id")
        return v
```

---

## Topics Configuration

| Topic | Partitions | Replication | Retention | Purpose |
|-------|------------|-------------|-----------|---------|
| `task-events` | 1 | 1 | 7 days | Task lifecycle (created, deleted) |
| `task-updates` | 1 | 1 | 7 days | Task change events |
| `reminders` | 1 | 1 | 7 days | Scheduled reminders |

**Note**: Original spec called for 3 partitions and 2 replication factor, but resource constraints require single-node configuration with 1 partition.

---

## aiokafka vs Dapr Comparison

| Aspect | aiokafka | Dapr |
|--------|----------|------|
| **Complexity** | High (manual connection mgmt) | Low (abstracted) |
| **Latency** | Lower (~10-20ms) | Higher (~50-100ms) |
| **Portability** | Kafka-only | Any broker (Redis, Azure, etc.) |
| **Retries/DLQ** | Manual implementation | Built-in |
| **Configuration** | Kafka-specific | Broker-agnostic |
| **Learning Curve** | Steep | Gentle |

**Recommendation**: Dapr for development simplicity and future flexibility.

---

## Challenges and Limitations

### Resource Constraints
- **Memory Pressure**: 4GB RAM is tight for Redpanda + Dapr + applications
- **Single Node**: No fault tolerance; cluster failure = total failure
- **CPU Limited**: 2 CPUs may cause contention during high load

### Mitigation Strategies
1. Use minimal Redpanda configuration
2. Monitor resource usage with `kubectl top pods`
3. Consider lightweight alternative (Redis) for development
4. Scale Minikube resources if possible
5. Use Dapr development mode for reduced overhead

### Development vs Production
This setup is **development/testing only**. For production:
- Minimum 3-node Redpanda cluster
- 6GB+ RAM per node
- 4+ CPUs per node
- Proper Kafka ACLs
- External schema registry (Confluent)

---

## Quick Start Commands

```bash
# 1. Start Minikube with resources
minikube start --cpus=2 --memory=4096 --driver=docker

# 2. Install Dapr
helm repo add dapr https://dapr.github.io/helm-charts/
helm install dapr dapr/dapr --namespace dapr-system --create-namespace --wait

# 3. Install Redpanda (minimal)
helm repo add redpanda https://charts.redpanda.com/
kubectl create namespace redpanda
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --set replicas=1 \
  --set resources.requests.memory=2Gi \
  --set resources.limits.memory=3Gi

# 4. Apply Dapr component
kubectl apply -f k8s/dapr/components/kafka-pubsub.yaml

# 5. Verify
kubectl get pods -n dapr-system
kubectl get pods -n redpanda
kubectl get components
```

---

## References

- [Dapr Python SDK with FastAPI](https://docs.dapr.io/developing-applications/sdks/python/python-sdk-extensions/python-fastapi/)
- [Dapr Kafka Pub/Sub](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [Redpanda Kubernetes Requirements](https://docs.redpanda.com/current/deploy/redpanda/kubernetes/k-requirements/)
- [Dapr Helm Installation](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/)

---

**Research Version**: 1.0
**Last Updated**: 2026-02-06
