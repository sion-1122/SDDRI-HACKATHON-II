# Data Model: Kubernetes Deployment

**Feature**: 006-k8s-deployment
**Date**: 2025-01-27
**Status**: Complete

## Overview

This document defines the key entities for Kubernetes deployment, including container images, Kubernetes resources, and Helm chart configuration. These entities represent the deployment infrastructure rather than application data.

## Entities

### 1. Container Image

Immutable artifact containing application code, dependencies, and runtime configuration.

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Image name (e.g., `todo-list-frontend`) |
| tag | string | Semantic version (e.g., `v1.0.0`) |
| registry | string | Registry location (local for Minikube) |
| size | number | Compressed image size in bytes |
| digest | string | SHA256 digest for content addressing |
| created_at | timestamp | Build timestamp |

**Frontend Image**:
- Name: `todo-list-frontend`
- Base: `nginx:alpine`
- Port: 80
- Size limit: <200MB compressed
- Tag format: `v{major}.{minor}.{patch}`

**Backend Image**:
- Name: `todo-list-backend`
- Base: `python:3.13-slim`
- Port: 8000
- Size limit: <150MB compressed
- Tag format: `v{major}.{minor}.{patch}`

---

### 2. Kubernetes Deployment

Declarative resource managing pod replicas, update strategy, and health checks.

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Deployment name (e.g., `todo-list-frontend`) |
| replicas | number | Desired pod count (1 for local, 2+ for production) |
| strategy | string | Update strategy (`RollingUpdate`) |
| maxSurge | number | Maximum pods added during update (1) |
| maxUnavailable | number | Maximum pods unavailable during update (0) |
| selector | map | Label selector for pods (`app: frontend`) |

**Frontend Deployment**:
- Replicas: 1 (local), 2 (production)
- Strategy: RollingUpdate
- maxSurge: 1, maxUnavailable: 0 (zero downtime)
- Template: nginx container with port 80

**Backend Deployment**:
- Replicas: 1 (local), 2 (production)
- Strategy: RollingUpdate
- maxSurge: 1, maxUnavailable: 0 (zero downtime)
- Template: FastAPI container with port 8000

**Pod Template**:
- Containers: 1 per pod
- Restart policy: Always
- Termination grace period: 30 seconds
- DNS policy: ClusterFirst

---

### 3. Kubernetes Service

Network abstraction providing stable endpoint for pod access. ClusterIP type enables internal communication.

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Service name (e.g., `todo-list-frontend`) |
| type | string | Service type (`ClusterIP`) |
| clusterIP | string | Cluster IP address (auto-assigned) |
| selector | map | Label selector for pods (`app: frontend`) |
| ports | list | Port mappings |

**Frontend Service**:
- Type: ClusterIP (internal only)
- Port: 80 → targetPort 80
- Protocol: TCP
- Selector: `app: frontend`

**Backend Service**:
- Type: ClusterIP (internal only)
- Port: 8000 → targetPort 8000
- Protocol: TCP
- Selector: `app: backend`

**Service Discovery**:
- Frontend connects to backend via DNS: `http://backend:8000`
- Services resolve to stable IP addresses within cluster
- Load balancing: Round-robin across ready pods

---

### 4. ConfigMap

Kubernetes resource storing non-sensitive configuration data as key-value pairs. Mounted as environment variables or files.

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | ConfigMap name (e.g., `todo-list-frontend-config`) |
| data | map | Key-value pairs (configuration values) |

**Frontend ConfigMap**:
- `API_URL`: Backend API endpoint (`http://backend:8000`)
- `APP_ENV`: Environment (`development`, `production`)
- `FEATURE_FLAGS`: JSON object with feature toggles

**Backend ConfigMap**:
- `DATABASE_HOST`: Neon PostgreSQL host
- `DATABASE_PORT`: Database port (5432)
- `DATABASE_NAME`: Database name
- `OPENAI_MODEL`: OpenAI model name
- `LOG_LEVEL`: Logging level (`INFO`, `DEBUG`)

**Mounting**:
- Injected as environment variables
- Reference in pod spec: `envFrom: configMapRef`
- Hot reload: Not supported (requires pod restart on change)

---

### 5. Secret

Kubernetes resource storing sensitive data (credentials, API keys) in encoded form. Mounted as environment variables or files.

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Secret name (e.g., `todo-list-backend-secret`) |
| type | string | Secret type (`Opaque`) |
| data | map | Base64-encoded key-value pairs |

**Backend Secret**:
- `DATABASE_URL`: Full database connection string (base64 encoded)
- `JWT_SECRET`: JWT signing secret (base64 encoded)
- `OPENAI_API_KEY`: OpenAI API key (base64 encoded)

**Security**:
- Data is base64-encoded (not encrypted by default)
- Minikube: Stored in plain text on disk
- Production: Use Kubernetes Secrets encryption at rest
- RBAC: Restrict access to secrets via service accounts

**Mounting**:
- Injected as environment variables
- Reference in pod spec: `envFrom: secretRef`
- Never logged or printed

---

### 6. Health Probe

Kubernetes mechanism checking container health. Liveness (restart if failed), readiness (stop traffic if not ready), startup (delay liveness until app starts).

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| type | enum | Probe type (`liveness`, `readiness`, `startup`) |
| path | string | HTTP path to check (`/health`) |
| port | number | Container port |
| initialDelaySeconds | number | Delay before first check (0 for startup, configurable for others) |
| periodSeconds | number | Check interval (5-10s) |
| timeoutSeconds | number | Check timeout (3-5s) |
| failureThreshold | number | Failures before action (2-3) |

**Backend Probes**:
- **Liveness**: `/health`, every 10s, timeout 5s, failureThreshold 3
- **Readiness**: `/health`, every 5s, timeout 3s, failureThreshold 2
- **Startup**: `/health`, every 5s, timeout 3s, failureThreshold 12 (60s total)

**Frontend Probes**:
- **Liveness**: `/`, every 10s, timeout 5s, failureThreshold 3
- **Readiness**: `/`, every 5s, timeout 3s, failureThreshold 2
- **Startup**: `/`, every 5s, timeout 3s, failureThreshold 12 (60s total)

**Probe Behavior**:
- Liveness fails → Pod restarted
- Readiness fails → Pod removed from service endpoints
- Startup fails → Liveness checks delayed
- Startup succeeds → Liveness checks begin

---

### 7. Helm Chart

Collection of pre-configured Kubernetes resources as a package. Contains templates, values, and metadata for deployment automation.

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Chart name (`todo-list-hackathon`) |
| version | string | Chart version (semver) |
| appVersion | string | Application version (matches image tags) |
| description | string | Chart description |
| templates | list | Kubernetes manifest templates |
| values | map | Default configuration values |
| valuesFiles | list | Environment-specific value overrides |

**Chart Structure**:
- `Chart.yaml`: Metadata (name, version, description)
- `values.yaml`: Default values for all settings
- `values-local.yaml`: Minikube overrides
- `values-production.yaml`: Production overrides (Phase V)
- `templates/`: Kubernetes manifest templates

**Value Overrides**:
- `replicaCount`: Number of pod replicas
- `image.tag`: Container image tag
- `image.pullPolicy`: Image pull policy (IfNotPresent, Always, Never)
- `resources.requests.*`: Resource requests (CPU, memory)
- `resources.limits.*`: Resource limits (CPU, memory)
- `autoscaling.enabled`: Enable HPA (Phase V)

**Helm Operations**:
- `helm install`: Install chart for first time
- `helm upgrade`: Upgrade existing release (rolling update)
- `helm rollback`: Rollback to previous release
- `helm test`: Run tests against release
- `helm uninstall`: Remove release

---

### 8. Resource Limits

CPU and memory constraints for containers to prevent resource exhaustion and ensure cluster stability.

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| requests.cpu | string | Guaranteed CPU (e.g., `100m`) |
| requests.memory | string | Guaranteed memory (e.g., `128Mi`) |
| limits.cpu | string | Maximum CPU (e.g., `500m`) |
| limits.memory | string | Maximum memory (e.g., `512Mi`) |

**Frontend Resources**:
- Requests: CPU 100m, Memory 128Mi
- Limits: CPU 500m, Memory 512Mi
- Local override: Requests CPU 50m, Memory 64Mi; Limits CPU 1000m, Memory 1Gi

**Backend Resources**:
- Requests: CPU 100m, Memory 128Mi
- Limits: CPU 500m, Memory 512Mi
- Local override: Requests CPU 50m, Memory 64Mi; Limits CPU 1000m, Memory 1Gi

**Resource Behavior**:
- Requests: Pod gets guaranteed resources, scheduled only if available
- Limits: Pod cannot exceed (CPU throttled, memory OOMKilled)
- No limits: Pod can consume entire node resources (anti-pattern)

---

## Entity Relationships

```
Helm Chart
├── Contains → Container Images (referenced by tag)
├── Templates → Kubernetes Deployments
├── Templates → Kubernetes Services
├── Templates → ConfigMaps
└── Templates → Secrets

Kubernetes Deployment
├── References → Container Image (image:tag)
├── Defines → Health Probes (liveness, readiness, startup)
├── Sets → Resource Limits (requests, limits)
├── Creates → Pods (matching replica count)
└── Depends On → ConfigMap, Secret (environment variables)

Kubernetes Service
└── Selects → Pods (by label selector)

ConfigMap
└── Mounted By → Kubernetes Deployment (environment variables)

Secret
└── Mounted By → Kubernetes Deployment (environment variables)
```

## State Transitions

### Helm Release Lifecycle

```
install → deployed
deployed → upgrade → deployed
deployed → rollback → deployed
deployed → uninstall → uninstalled
```

### Pod Lifecycle

```
Pending → Running → Ready (serving traffic)
Running → Failed → Restarted (back to Pending)
Ready → Terminating → Deleted (graceful shutdown)
```

### Container Health States

```
Startup Probe Failing → (startup probe period)
Startup Probe Passing → Liveness/Readiness Active
Readiness Probe Failing → Not Ready (no traffic)
Readiness Probe Passing → Ready (receiving traffic)
Liveness Probe Failing → Pod Restarted
```

## Validation Rules

| Entity | Rule | Enforcement |
|--------|------|-------------|
| Container Image | Size < 200MB (frontend), < 150MB (backend) | Docker build check |
| Container Image | Tag matches semver format | Helm template validation |
| Kubernetes Deployment | maxUnavailable = 0 (zero downtime) | Helm value validation |
| Kubernetes Deployment | terminationGracePeriodSeconds >= 30 | Helm template default |
| Health Probe | failureThreshold >= 2 (prevent false positives) | Helm template default |
| Resource Limits | limits >= requests (CPU, memory) | Kubernetes admission controller |
| Secret | Data base64-encoded | Kubernetes validation |
| Helm Chart | appVersion matches image tag | Convention (manual) |

## Next Steps

1. ✅ Data model complete: All deployment entities defined
2. 🔄 Phase 1: Generate contracts/ with Kubernetes schemas
3. 🔄 Phase 1: Generate quickstart.md with setup instructions
4. ⏳ Phase 2: Generate tasks.md via `/sp.tasks`
