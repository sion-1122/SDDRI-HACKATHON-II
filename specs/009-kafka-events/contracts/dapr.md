# Dapr Component Contracts

**Feature**: 009-kafka-events | **Date**: 2026-02-06

## Overview

Defines Dapr component configurations for Kafka pub/sub with Redpanda on Kubernetes.

---

## Dapr Pub/Sub Component Specification

### Component: kafka-pubsub

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  # Required: Kafka broker addresses
  - name: brokers
    value: "redpanda.redpanda:9092"

  # Required: Consumer group for this application
  - name: consumerGroup
    value: "todo-consumers"

  # Optional: Specific topics (if not specified, all topics available)
  # If omitted, consumer can subscribe to any topic
  - name: authRequired
    value: "false"

  # Optional: Transport protocol
  - name: clientTransport
    value: "tcp://redpanda.redpanda:9092"

  # Optional: Disable topic creation (auto-create by default)
  # - name: disableTopicCreation
  #   value: "false"
```

### Metadata Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `brokers` | string | Yes | - | Comma-separated Kafka broker addresses |
| `consumerGroup` | string | Yes | - | Consumer group ID for offset management |
| `authRequired` | boolean | No | false | Enable SASL authentication |
| `clientTransport` | string | No | tcp | Transport protocol (tcp, ssl, tls) |
| `disableTopicCreation` | boolean | No | false | Disable automatic topic creation |

---

## Redpanda Service Specification

### Service: redpanda

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redpanda
  namespace: redpanda
spec:
  ports:
  - port: 9092
    name: kafka
    protocol: TCP
    targetPort: 9092
  selector:
    app: redpanda
  clusterIP: None  # Headless service for StatefulSet
```

### Pod Selector Labels

```yaml
# Redpanda pods must have these labels
metadata:
  labels:
    app: redpanda
    component: broker
```

---

## Dapr Sidecar Configuration

### Deployment Annotation (Chat API)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-api
  namespace: default
spec:
  template:
    metadata:
      annotations:
        # Dapr application ID
        dapr.io/app-id: "chat-api"

        # Dapr listening port (matches FastAPI port)
        dapr.io/app-port: "8000"

        # Enable Dapr metrics
        dapr.io/enable-metrics: "true"

        # Dapr configuration (optional)
        dapr.io/config: "tracing"

        # Log level
        dapr.io/log-level: "info"
```

### Deployment Annotation (Reminder Consumer)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reminder-consumer
  namespace: default
spec:
  template:
    metadata:
      annotations:
        dapr.io/app-id: "reminder-worker"
        dapr.io/app-port: "8001"  # Different port
        dapr.io/enable-metrics: "true"
        dapr.io/log-level: "info"
```

### Annotation Reference

| Annotation | Value | Description |
|------------|-------|-------------|
| `dapr.io/app-id` | string | Unique application identifier |
| `dapr.io/app-port` | number | Container port for Dapr to call |
| `dapr.io/enable-metrics` | "true"/"false" | Enable Prometheus metrics |
| `dapr.io/log-level` | debug/info/warn/error | Dapr sidecar log level |
| `dapr.io/config` | string | Dapr configuration profile name |
| `dapr.io/sidecar-listen-addresses` | string | Custom listen addresses |

---

## Secret Specifications (Future)

### Basic Auth Secret (if authRequired: true)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kafka-secret
  namespace: default
type: Opaque
stringData:
  saslUsername: "admin"
  saslPassword: "password123"
```

### Dapr Secret Reference

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  metadata:
  - name: brokers
    value: "redpanda.redpanda:9092"
  - name: saslUsername
    secretKeyRef:
      name: kafka-secret
      key: saslUsername
  - name: saslPassword
    secretKeyRef:
      name: kafka-secret
      key: saslPassword
```

---

## Subscription Specifications

### Python/FastAPI Subscription

```python
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr = DaprApp(app)

# Automatic subscription via decorator
@dapr.subscribe(
    pubsub="kafka-pubsub",
    topic="task-events",
    route="/api/events/task-events"
)
async def handle_task_event(event_data: dict) -> dict:
    """Handle task events from Kafka"""
    event_type = event_data.get("event_type")
    payload = event_data.get("payload")

    if event_type == "task_created":
        # Handle task creation
        pass
    elif event_type == "task_deleted":
        # Handle task deletion
        pass

    return {"status": "processed"}
```

### Subscription Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `pubsub` | "kafka-pubsub" | Dapr component name |
| `topic` | "task-events" | Kafka topic to subscribe to |
| `route` | "/api/events/task-events" | HTTP route to receive events |
| `consumerGroup` | (optional) | Override default consumer group |

---

## Helm Chart Values

### Dapr Helm Values

```yaml
# dapr/values-dev.yaml
global:
  ha:
    enabled: false  # Disable HA for development

dapr:
  logLevel: info
  metrics:
    enabled: true
  tracing:
    samplingRate: "1"  # 100% sampling for development

  # Sidecar resources
  resources:
    limits:
      cpu: "500m"
      memory: "256Mi"
    requests:
      cpu: "100m"
      memory: "128Mi"
```

### Redpanda Helm Values

```yaml
# redpanda/values-minimal.yaml
replicas: 1

resources:
  requests:
    cpu: "1"
    memory: "2Gi"
  limits:
    cpu: "2"
    memory: "3Gi"

statefulset:
  replicas: 1

# Disable unnecessary features for development
console:
  enabled: false

# Storage
storage:
  persistence:
    size: 1Gi
    storageClass: standard

# Networking
external:
  enabled:
    type: NodePort
```

---

## Configuration Modes

### Development Mode

```yaml
# Low resource usage, no HA, all logs visible
dapr.io/log-level: "debug"
dapr.io/enable-metrics: "false"
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
```

### Production Mode (Future)

```yaml
# Higher resource usage, HA enabled, metrics on
dapr.io/log-level: "info"
dapr.io/enable-metrics: "true"
dapr.io/config: "production"
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "1000m"
    memory: "512Mi"
```

---

## Deployment Workflows

### 1. Install Dapr Cluster

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --values dapr/values-dev.yaml
```

### 2. Deploy Redpanda

```bash
kubectl create namespace redpanda
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --values redpanda/values-minimal.yaml
```

### 3. Apply Dapr Components

```bash
kubectl apply -f k8s/dapr/components/kafka-pubsub.yaml
```

### 4. Verify Installation

```bash
# Check Dapr pods
kubectl get pods -n dapr-system

# Check Redpanda pods
kubectl get pods -n redpanda

# Verify Dapr components
kubectl get components

# Test Kafka connection (from pod)
kubectl exec -it -n redpanda redpanda-0 -- \
  rpk cluster info
```

---

## Health Check Endpoints

### Dapr Health

```bash
# Check Dapr sidecar health
curl http://localhost:3500/v1.0/healthz

# Check Dapr metrics
curl http://localhost:3500/metrics
```

### Redpanda Health

```bash
# Port-forward to Redpanda
kubectl port-forward -n redpanda redpanda-0 9092:9092

# Check cluster info
rpk cluster info --brokers localhost:9092
```

---

**Dapr Contract Version**: 1.0
**Last Updated**: 2026-02-06
