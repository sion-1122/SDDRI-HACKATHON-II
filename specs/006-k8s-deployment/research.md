# Phase 0 Research: Kubernetes Deployment

**Feature**: 006-k8s-deployment
**Date**: 2025-01-27
**Status**: Complete

## Overview

Research findings for containerizing and deploying the Todo Chatbot application on Kubernetes using Minikube. This document resolves all technical unknowns and establishes best practices for Phase IV implementation.

## Research Areas & Decisions

### 1. Docker Multi-Stage Builds

**Decision**: Use multi-stage builds for both frontend and backend to minimize image sizes and improve security.

**Frontend (Next.js)**:
- **Stage 1 - Build**: `node:20-alpine` as base, run `pnpm install --frozen-lockfile` and `pnpm build`
- **Stage 2 - Serve**: `nginx:alpine` as base, copy built artifacts from stage 1, configure nginx for SPA routing
- **Optimization**: Use build cache for `node_modules`, copy `package.json` first before source code
- **Security**: Run nginx as non-root user (built-in nginx user)
- **Size Target**: <200MB compressed

**Backend (FastAPI)**:
- **Stage 1 - Dependencies**: `python:3.13-slim` as base, install `uv`, copy `pyproject.toml`, run `uv sync --frozen`
- **Stage 2 - Runtime**: `python:3.13-slim` as base, copy `.venv` from stage 1, copy application code
- **Optimization**: Cache virtual environment in separate layer, use `.dockerignore` to exclude `__pycache__`, `.pytest_cache`, `.ruff_cache`
- **Security**: Create non-root user `appuser` with UID 1000, run as that user
- **Size Target**: <150MB compressed

**Alternatives Considered**:
- Single-stage builds: Rejected due to larger image sizes (includes build tools)
- Distroless images: Considered but slim images preferred for easier debugging
- BuildKit caching: Recommended but not required (Docker Desktop includes BuildKit)

**References**:
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Next.js Deployment with Docker](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)

---

### 2. Minikube Development Setup

**Decision**: Use Minikube with Docker driver for local Kubernetes development. Pre-load images using `minikube image load` to avoid registry setup.

**Setup Commands**:
```bash
# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=8192

# Build images locally
docker build -t todo-list-frontend:v1.0.0 ./frontend
docker build -t todo-list-backend:v1.0.0 ./backend

# Load images into Minikube
minikube image load todo-list-frontend:v1.0.0
minikube image load todo-list-backend:v1.0.0

# Verify images
minikube image ls
```

**Configuration**:
- Driver: Docker (most stable for local development)
- Resources: 4 CPUs, 8GB RAM (sufficient for frontend + backend)
- Kubernetes Version: Latest stable (Minikube default)
- Container Runtime: Docker (matches local environment)

**Alternatives Considered**:
- Podman: Rejected due to team familiarity with Docker
- Kind: Considered but Minikube has better GUI support and ecosystem
- Local registry: Rejected as unnecessary complexity for development

**References**:
- [Minikube Start](https://minikube.sigs.k8s.io/docs/start/)
- [Minikube Image Load](https://minikube.sigs.k8s.io/docs/handbook/pushing/)
- [Minikube Drivers](https://minikube.sigs.k8s.io/docs/drivers/)

---

### 3. Helm Chart Patterns

**Decision**: Use standard Helm chart structure with environment-specific value overrides. Template all Kubernetes resources with Helm template functions.

**Chart Structure**:
```
k8s/todo-list-hackathon/
├── Chart.yaml                    # Chart metadata
├── values.yaml                   # Default values
├── values-local.yaml             # Minikube overrides
├── values-production.yaml        # Production overrides (Phase V)
└── templates/
    ├── NOTES.txt                 # Post-install instructions
    ├── deployment.yaml           # Unified Deployment template
    ├── service.yaml              # Unified Service template
    ├── configmap.yaml            # ConfigMap template
    ├── secret.yaml               # Secret template
    ├── ingress.yaml              # Ingress template (Phase V)
    └── tests/
        └── test-connection.yaml  # Helm test
```

**Template Patterns**:
- Use `{{- if .Values.frontend.enabled }}` for optional frontend component
- Use `{{- if .Values.backend.enabled }}` for optional backend component
- Use `{{ .Release.Name }}` prefix for resource names (e.g., `todo-list-frontend`)
- Use `{{ .Chart.AppVersion }}` for image tags
- Use `{{ .Values.replicaCount }}` for configurable replica counts
- Use `{{ tpl .Values.someConfig $ }}` for complex configuration injection

**Value Override Strategy**:
- `values.yaml`: Sensible defaults (replicas=2, standard resource limits)
- `values-local.yaml`: Minikube overrides (replicas=1, minimal limits, imagePullPolicy=Never)
- `values-production.yaml`: Production overrides (replicas=3+, strict limits, imagePullPolicy=Always)

**Alternatives Considered**:
- Separate charts per component: Rejected due to complexity
- Kustomize: Considered but Helm chosen for better templating and ecosystem
- Plain YAML: Rejected due to lack of environment-specific configuration

**References**:
- [Helm Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Helm Template Guide](https://helm.sh/docs/chart_template_guide/)
- [Helm Values Files](https://helm.sh/docs/howto/charts_tips_and_tricks/)

---

### 4. Health Probe Configuration

**Decision**: Implement liveness, readiness, and startup probes for both frontend and backend. Use HTTP GET requests to `/health` endpoint.

**Backend (FastAPI)**:
- **Liveness Probe**: Check `/health` every 10s, timeout 5s, failureThreshold 3
- **Readiness Probe**: Check `/health` every 5s, timeout 3s, failureThreshold 2
- **Startup Probe**: Check `/health` every 5s, timeout 3s, failureThreshold 12 (60s total)
- **Endpoint**: `GET /health` returns `{"status": "healthy", "timestamp": "..."}`
- **Implementation**: Create `backend/api/health.py` with `/health` endpoint

**Frontend (Next.js + nginx)**:
- **Liveness Probe**: Check `/` every 10s, timeout 5s, failureThreshold 3
- **Readiness Probe**: Check `/` every 5s, timeout 3s, failureThreshold 2
- **Startup Probe**: Check `/` every 5s, timeout 3s, failureThreshold 12 (60s total)
- **Endpoint**: Nginx serves static files, `/` returns index.html
- **Implementation**: No code changes needed, nginx handles HTTP

**Probe Timing Rationale**:
- Startup probe gives 60s for app to start (covers cold starts, dependency connections)
- Readiness probe more aggressive (every 5s) to quickly route traffic away from unready pods
- Liveness probe less aggressive (every 10s) to avoid killing pods for transient issues
- Failure thresholds prevent false positives (2-3 failures before restart)

**Alternatives Considered**:
- TCP socket probes: Rejected (don't verify app is actually working)
- Command probes: Rejected (less portable than HTTP)
- gRPC probes: Rejected (not using gRPC)

**References**:
- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [FastAPI Health Checks](https://fastapi.tiangolo.com/advanced/advanced-user-dependencies/)
- [Nginx Health Checks](https://docs.nginx.com/nginx-ingress-controller/)

---

### 5. Resource Limits

**Decision**: Set resource requests and limits for both frontend and backend pods to prevent resource exhaustion and ensure cluster stability.

**Frontend (Next.js + nginx)**:
- **Requests**: CPU 100m, Memory 128Mi
- **Limits**: CPU 500m, Memory 512Mi
- **Rationale**: Static file serving is lightweight, nginx has small footprint
- **Local**: Limits can be relaxed in Minikube (values-local.yaml)
- **Production**: Strict limits to prevent runaway processes

**Backend (FastAPI)**:
- **Requests**: CPU 100m, Memory 128Mi
- **Limits**: CPU 500m, Memory 512Mi
- **Rationale**: Python app with moderate memory usage, async operations
- **Local**: Limits can be relaxed in Minikube (values-local.yaml)
- **Production**: Strict limits to prevent memory leaks from affecting cluster

**Minikube Overrides**:
- **Requests**: CPU 50m, Memory 64Mi (reduced for local development)
- **Limits**: CPU 1000m, Memory 1Gi (increased to accommodate local builds)

**Resource Limit Rationale**:
- Requests ensure pods get guaranteed resources
- Limits prevent pods from consuming entire cluster
- CPU throttling allows burst capacity without eviction
- Memory limits trigger OOMKilled when exceeded

**Alternatives Considered**:
- No limits: Rejected (single pod can crash cluster)
- Only requests: Rejected (no protection against resource leaks)
- Vertical Pod Autoscaler: Considered but premature for local deployment

**References**:
- [Kubernetes Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Resource Requests vs Limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#resource-requests-and-limits-of-pod-and-container)

---

### 6. kubectl-ai/kagent Integration

**Decision**: Integrate kubectl-ai and kagent as optional AI DevOps tools. Document usage patterns but provide manual fallback procedures.

**kubectl-ai Usage**:
```bash
# Generate Deployment manifest
kubectl-ai "Create a Kubernetes Deployment for FastAPI backend with 2 replicas, health checks, and resource limits"

# Diagnose pod issues
kubectl-ai "Diagnose why my backend-xxx pod is in CrashLoopBackOff state"

# Optimize resources
kubectl-ai "Suggest CPU and memory resource limits for a Next.js frontend pod"
```

**kagent Usage**:
```bash
# Monitor cluster health
kagent monitor --namespace default

# Analyze pod performance
kagent analyze pods --selector app=backend --metrics cpu,memory

# Get scaling recommendations
kagent recommend --resource deployments --app backend
```

**Documentation Strategy**:
- Document AI tool usage in `k8s/README.md`
- Include example commands and expected outputs
- Document manual fallback procedures
- Mark AI operations as "optional" in success criteria

**Alternatives Considered**:
- Mandatory AI usage: Rejected (not available in all regions/tiers)
- No AI integration: Rejected (misses opportunity for bonus points)
- Custom AI agents: Considered but existing tools sufficient

**References**:
- [kubectl-ai GitHub](https://github.com/ebrym1/kubectl-ai)
- [kagent Documentation](https://kagent.ai/docs)
- [AI DevOps Best Practices](https://csrc.nist.gov/projects/aops)

---

### 7. Cloud-Native Patterns

**Decision**: Implement cloud-native patterns including graceful shutdown, structured logging, and rolling updates.

**Graceful Shutdown**:
- **Backend (FastAPI)**: Handle SIGTERM signal, close database connections, complete in-flight requests
- **Implementation**: Use `@app.on_event("shutdown")` in FastAPI, set `uvicorn` timeout to 30s
- **Kubernetes**: `terminationGracePeriodSeconds: 30`

**Structured Logging**:
- **Backend (FastAPI)**: JSON logging with `level`, `timestamp`, `correlation_id`, `message` fields
- **Frontend (Next.js)**: Console logging with structured format (limited by browser)
- **Implementation**: Use Python `structlog` library, configure in `backend/core/logging.py`
- **Output**: stdout/stderr (collected by Minikube logs)

**Rolling Updates**:
- **Strategy**: `RollingUpdate` with `maxSurge: 1`, `maxUnavailable: 0`
- **Result**: Zero-downtime deployments (new pods started before old pods terminated)
- **Helm**: `helm upgrade` automatically performs rolling updates
- **Rollback**: `helm rollback` reverts to previous release

**Stateless Design**:
- **Existing**: Application is already stateless (all state in Neon PostgreSQL)
- **Verification**: No local file storage, no in-memory session state
- **Kubernetes**: Pods can be killed and replaced without data loss

**Alternatives Considered**:
- Sidecar containers: Rejected (unnecessary complexity for stateless app)
- Init containers: Considered for migrations but rejected (use separate job)
- PreStop hooks: Rejected (graceful shutdown handler sufficient)

**References**:
- [Graceful Shutdown in Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
- [Structured Logging Best Practices](https://www.boost.org/doc/libs/release/libs/log/doc/html/html/log.html)
- [Kubernetes Rolling Updates](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)

---

## Technology Decisions Summary

| Area | Decision | Rationale |
|------|----------|-----------|
| **Frontend Base Image** | `nginx:alpine` | Minimal size, static file serving optimized |
| **Backend Base Image** | `python:3.13-slim` | Official Python image, smaller than full image |
| **Minikube Driver** | Docker | Most stable, matches local Docker environment |
| **Package Manager** | Helm 3+ | Industry standard, excellent templating, large ecosystem |
| **Health Check Method** | HTTP GET `/health` | Simple, universal, works with nginx and FastAPI |
| **Resource Requests** | CPU 100m, Memory 128Mi | Sufficient for app, minimal for local development |
| **Resource Limits** | CPU 500m, Memory 512Mi | Prevent resource exhaustion, allow bursts |
| **Probes Timing** | Startup 60s, Readiness 5s, Liveness 10s | Balance between fast detection and false positives |
| **Logging Format** | JSON with structured fields | Enables log aggregation and analysis |
| **AI DevOps** | kubectl-ai, kagent (optional) | Bonus points, manual fallback available |

## Open Questions Resolved

| Question | Answer | Source |
|----------|--------|--------|
| How to load images into Minikube? | Use `minikube image load` command | [Minikube Docs](https://minikube.sigs.k8s.io/docs/handbook/pushing/) |
| How to implement health checks? | HTTP GET `/health` endpoint in FastAPI, `/` for nginx | [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) |
| How to handle graceful shutdown? | SIGTERM handler in FastAPI, terminationGracePeriodSeconds in K8s | [Kubernetes Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination) |
| How to structure Helm chart? | Standard structure with values-local.yaml and values-production.yaml | [Helm Best Practices](https://helm.sh/docs/chart_best_practices/) |
| How to integrate AI DevOps? | Optional kubectl-ai/kagent with manual fallback | Tool documentation |

## Next Steps

1. ✅ Research complete: All technical unknowns resolved
2. 🔄 Phase 1: Generate data-model.md, contracts/, quickstart.md
3. ⏳ Phase 2: Generate tasks.md via `/sp.tasks`
4. ⏳ Implementation: Execute tasks following user story priority (US1 → US2 → US3)
