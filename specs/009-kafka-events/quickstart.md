# Quick Start: Kafka Event Streaming with Dapr

**Feature**: 009-kafka-events | **Branch**: `k8s-infra` | **Date**: 2026-02-06

## Prerequisites

- **Minikube** v1.30+ installed
- **Helm** v3+ installed
- **kubectl** installed and configured
- **Python** 3.13+ with `uv`
- **System Resources**: 2 CPUs, 4GB RAM minimum

---

## Quick Start (15 minutes)

### Step 1: Start Minikube (2 min)

```bash
# Start Minikube with resource constraints
minikube start \
  --driver=docker \
  --cpus=2 \
  --memory=4096 \
  --disk-size=30gb

# Verify
minikube status
kubectl get nodes
```

### Step 2: Install Dapr (3 min)

```bash
# Add Dapr Helm repository
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr to dapr-system namespace
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=false \
  --wait

# Verify installation
kubectl get pods -n dapr-system
```

Expected output:
```
NAME                       READY   STATUS    RESTARTS   AGE
dapr-dashboard-xxxxx      1/1     Running   0          30s
dapr-operator-xxxxx       1/1     Running   0          30s
dapr-placement-xxxxx      1/1     Running   0          30s
dapr-sentry-xxxxx         1/1     Running   0          30s
dapr-sidecar-injector-xxx  1/1     Running   0          30s
```

### Step 3: Install Redpanda (5 min)

```bash
# Create namespace
kubectl create namespace redpanda

# Add Redpanda Helm repository
helm repo add redpanda https://charts.redpanda.com/

# Create minimal values file
cat > /tmp/redpanda-values.yaml << 'EOF'
replicas: 1
resources:
  requests:
    cpu: "1"
    memory: "2Gi"
  limits:
    cpu: "2"
    memory: "3Gi"
storage:
  persistent:
    size: 1Gi
console:
  enabled: false
EOF

# Install Redpanda
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --values /tmp/redpanda-values.yaml \
  --wait \
  --timeout 10m

# Verify
kubectl get pods -n redpanda
kubectl get svc -n redpanda
```

### Step 4: Create Dapr Kafka Component (2 min)

```bash
# Create Dapr component for Kafka pub/sub
cat > k8s/dapr/components/kafka-pubsub.yaml << 'EOF'
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
EOF

# Apply component
kubectl apply -f k8s/dapr/components/kafka-pubsub.yaml

# Verify
kubectl get components
```

Expected output:
```
NAME           NAMESPACE   TYPE        VERSION
kafka-pubsub   default     pubsub.kafka  v1
```

### Step 5: Create Topics (3 min)

```bash
# Port-forward to Redpanda
kubectl port-forward -n redpanda svc/redpanda 9092:9092 &
PF_PID=$!

# Wait for connection
sleep 5

# Install rpk (Redpanda CLI)
# Download from https://github.com/redpanda-data/redpanda/releases
# Or use docker:
docker run --rm -it --network host redpandadata/redpanda \
  rpk cluster info --brokers localhost:9092

# Create topics
docker run --rm -it --network host redpandadata/redpanda \
  rpk topic create task-events -r 1 -p 1 --brokers localhost:9092

docker run --rm -it --network host redpandadata/redpanda \
  rpk topic create task-updates -r 1 -p 1 --brokers localhost:9092

docker run --rm -it --network host redpandadata/redpanda \
  rpk topic create reminders -r 1 -p 1 --brokers localhost:9092

# Verify topics
docker run --rm -it --network host redpandadata/redpanda \
  rpk topic list --brokers localhost:9092

# Kill port-forward
kill $PF_PID
```

Expected output:
```
NAME            PARTITIONS  REPLICAS
task-events     1           1
task-updates    1           1
reminders        1           1
```

---

## Backend Integration

### Install Dependencies

```bash
cd backend
uv add "dapr-ext-fastapi[dapr]"
uv add dapr
```

### Add Kafka Publishing Service

```python
# services/kafka_service.py
from dapr.clients import DaprClient
import json
from typing import Optional

class KafkaService:
    def __init__(self):
        self.client = DaprClient()

    async def publish_task_created(self, task_data: dict) -> bool:
        """Publish task-created event to Kafka"""
        event = {
            "event_id": uuid.uuid4().hex,
            "event_type": "task_created",
            "event_version": "v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": str(uuid.uuid4()),
            "producer": "chat-api",
            "payload": task_data
        }

        try:
            self.client.publish_event(
                pubsub_name="kafka-pubsub",
                topic="task-events",
                data=json.dumps(event),
                data_content_type="application/json"
            )
            return True
        except Exception as e:
            # Log but don't block API response
            print(f"Failed to publish event: {e}")
            return False
```

### Add Event Hooks to Chat API

```python
# api/tasks.py (modify existing create_task endpoint)

from services.kafka_service import KafkaService

kafka_service = KafkaService()

@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    task: TaskCreate,
    session: SessionDep,
    user_id: CurrentUserDep
):
    # ... existing task creation logic ...

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish event to Kafka (async, non-blocking)
    asyncio.create_task(
        kafka_service.publish_task_created(db_task.model_dump())
    )

    return db_task
```

---

## Consumer Service Setup

### Create Reminder Consumer

```python
# consumers/reminder_consumer.py
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI

app = FastAPI(__name__="")
dapr = DaprApp(app)

@dapr.subscribe(
    pubsub="kafka-pubsub",
    topic="task-events"
)
async def handle_task_event(event_data: dict) -> dict:
    """Process task events from Kafka"""
    event_type = event_data.get("event_type")
    payload = event_data.get("payload")

    if event_type == "task_created":
        # Schedule reminder if due_date exists
        due_date = payload.get("due_date")
        if due_date:
            await schedule_reminder(payload)
    elif event_type == "task_deleted":
        # Cancel pending reminders
        await cancel_reminders(payload["task_id"])

    return {"status": "processed"}
```

---

## Testing

### Test Event Publishing

```bash
# Run backend with Dapr sidecar
dapr run --app-port 8000 uv run uvicorn main:app
```

### Test Consumer

```bash
# Run consumer with Dapr
dapr run --app-port 8001 uv run uvicorn consumers.reminder_consumer:app
```

### End-to-End Test

```python
# tests/test_kafka_flow.py
import pytest
from dapr.clients import DaprClient

def test_event_flow():
    """Test complete event flow"""
    client = DaprClient()

    # Publish event
    client.publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-events",
        data=json.dumps(test_event)
    )

    # Verify (in consumer logs)
    # Event should be processed
```

---

## Troubleshooting

### Dapr Sidecar Not Starting

```bash
# Check sidecar injector logs
kubectl logs -n dapr-system -l app=dapr-sidecar-injector

# Check pod annotations
kubectl get pod <pod-name> -o yaml | grep dapr.io
```

### Redpanda Not Ready

```bash
# Check Redpanda logs
kubectl logs -n redpanda -l app=redpanda

# Describe pod
kubectl describe pod -n redpanda -l app=redpanda

# Check resources
kubectl top pods -n redpanda
```

### Component Not Found

```bash
# List all components
kubectl get components --all-namespaces

# Describe component
kubectl describe component kafka-pubsub
```

### Connection Refused

```bash
# Verify Redpanda service
kubectl get svc -n redpanda

# Port-forward to test
kubectl port-forward -n redpanda svc/redpanda 9092:9092

# Test connection
telnet localhost 9092
```

---

## Resource Limits

Given **2 CPUs / 4GB RAM**, these are the resource allocations:

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|-----------------|---------------|
| Minikube | - | 2 | - | 4096MB |
| Dapr | 100m | 500m | 128Mi | 256Mi |
| Redpanda | 1 | 2 | 2Gi | 3Gi |
| Chat API | 100m | 500m | 128Mi | 256Mi |
| Consumer | 100m | 500m | 128Mi | 256Mi |
| **Total** | **~1.4** | **~4** | **~2.5GB** | **~4GB** |

**Note**: This is at maximum capacity. Consider stopping unused services when not testing.

---

## Clean Up

```bash
# Stop Minikube (preserves state)
minikube stop

# Delete everything (start fresh)
minikube delete

# Uninstall Dapr
helm uninstall dapr -n dapr-system
kubectl delete namespace dapr-system

# Uninstall Redpanda
helm uninstall redpanda -n redpanda
kubectl delete namespace redpanda
```

---

## Next Steps

1. ✅ Install Dapr and Redpanda
2. ✅ Create Dapr component for Kafka
3. ✅ Create Kafka topics
4. ⬜ Add event publishing to Chat API
5. ⬜ Create reminder consumer service
6. ⬜ Deploy consumers to Kubernetes
7. ⬜ End-to-end testing

---

**Quick Start Version**: 1.0
**Last Updated**: 2026-02-06
