# Implementation Plan: Local Kubernetes Deployment (Phase IV)

**Branch**: `006-k8s-deployment` | **Date**: 2025-01-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-k8s-deployment/spec.md`

## Summary

Containerize the Phase III Todo Chatbot application (FastAPI backend + Next.js frontend) and deploy on Kubernetes using Minikube for local development. Package all manifests as Helm charts for declarative deployment automation. Use AI DevOps tools (kubectl-ai, kagent) to assist operations. Follow cloud-native patterns with health checks, resource limits, and zero-downtime rolling updates.

**Technical Approach**: Multi-stage Docker builds for optimized images, Kubernetes Deployments with health probes for self-healing, Helm chart for environment-specific configuration management, and Minikube for local Kubernetes development parity.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**: Docker Desktop, Minikube, Helm 3+, kubectl-ai (optional), kagent (optional)
**Storage**: Neon Serverless PostgreSQL (external, cloud-hosted)
**Testing**: Docker container testing, Kubernetes deployment testing, Helm chart testing
**Target Platform**: Minikube (local Kubernetes cluster)
**Project Type**: web (backend + frontend containerization and orchestration)
**Performance Goals**: Container startup <10s, image build <5min, deployment <2min, zero-downtime rolling updates
**Constraints**: Frontend image <200MB, backend image <150MB, cloud-native patterns (health checks, resource limits, graceful shutdown), stateless application design
**Scale/Scope**: 2 services (frontend, backend), 2+ replicas per service in production, local development deployment on Minikube

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase IV Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **XI. Containerization with Docker** | ✅ PASS | Multi-stage Dockerfiles planned, version tagging, non-root user, size constraints |
| **XII. Kubernetes Orchestration** | ✅ PASS | Minikube deployment, Deployments with replicas, ClusterIP Services, ConfigMaps, Secrets |
| **XIII. Helm Chart Packaging** | ✅ PASS | Helm chart with Chart.yaml, values files, templates for all resources |
| **XIV. AI-Assisted DevOps** | ✅ PASS | kubectl-ai/kagent integration planned, fallback to manual operations |
| **XV. Cloud-Native Deployment Patterns** | ✅ PASS | Health probes, resource limits, graceful shutdown, rolling updates, structured logging |
| **XVI. AIOps and Blueprints** | ✅ PASS | Reusable deployment patterns, MCP server for K8s operations (future) |

### Phase II/III Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **VI. Monorepo Structure Standard** | ✅ PASS | k8s/ directory at root, Dockerfiles in frontend/backend, specs/006-k8s-deployment/ |
| **VII. Authentication & JWT Security** | ✅ PASS | Existing JWT auth preserved, Secrets for sensitive data |
| **VIII. Frontend Architecture (Next.js)** | ✅ PASS | Existing Next.js App Router containerized, no changes to app architecture |
| **IX. Data Ownership & Isolation** | ✅ PASS | Existing user scoping preserved, database connectivity via ConfigMaps/Secrets |

### Gate Evaluation

**Result**: ✅ ALL GATES PASSED - No violations identified. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/006-k8s-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── docker-images.yaml     # Container image specifications
│   ├── k8s-resources.yaml     # Kubernetes resource definitions
│   └── helm-chart.yaml        # Helm chart structure and values
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Full monorepo (All phases: cli + backend + frontend + k8s)
cli/
├── models/
├── services/
├── ui/
└── tests/

backend/
├── CLAUDE.md
├── Dockerfile                # NEW: Phase IV container image
├── .dockerignore             # NEW: Exclude files from build context
├── ai_agent/
├── mcp_server/
├── models/
├── services/
├── api/
├── ws_manager/
└── core/

frontend/
├── CLAUDE.md
├── Dockerfile                # NEW: Phase IV container image
├── .dockerignore             # NEW: Exclude files from build context
├── components.json
├── app/
├── components/
├── lib/
└── public/

k8s/                          # NEW: Phase IV Helm chart (Principle VI)
└── todo-list-hackathon/
    ├── Chart.yaml            # Helm chart metadata
    ├── values.yaml           # Default values
    ├── values-local.yaml     # Minikube-specific overrides
    ├── values-production.yaml # Production overrides (Phase V)
    └── templates/
        ├── NOTES.txt         # Post-install instructions
        ├── deployment.yaml   # Deployment template (frontend + backend)
        ├── service.yaml      # Service template (ClusterIP)
        ├── configmap.yaml    # ConfigMap template
        ├── secret.yaml       # Secret template
        ├── ingress.yaml      # Ingress template (Phase V)
        └── tests/
            ├── test-connection.yaml # Helm test for connectivity
```

**Structure Decision**: Per Principle VI (Monorepo Structure Standard), the project follows the full monorepo layout with cli/, backend/, frontend/, and the new k8s/ directory for Phase IV. Dockerfiles are co-located with application code in backend/ and frontend/ directories. The k8s/ directory at repository root contains the Helm chart, enabling environment-specific deployments. This structure separates concerns (application code vs. deployment manifests) while maintaining monorepo consistency.

## Complexity Tracking

> No constitution violations - this section not required for Phase IV.

## Phase 0: Research & Technology Decisions

### Research Goals

Resolve all technical unknowns for containerization, Kubernetes deployment, and Helm packaging. Establish best practices for multi-stage builds, health probes, resource limits, and Minikube development.

### Research Areas

1. **Docker Multi-Stage Builds**: Optimize frontend (Next.js) and backend (FastAPI) image sizes, layer caching, non-root user configuration
2. **Minikube Development Setup**: Local cluster configuration, image loading (minikube image load), registry setup
3. **Helm Chart Patterns**: Template structure, value overrides, environment-specific configurations, testing strategies
4. **Health Probe Configuration**: Liveness, readiness, startup probe best practices for FastAPI and Next.js
5. **Resource Limits**: CPU/memory requests and limits for local development vs. production
6. **kubectl-ai/kagent Integration**: AI-assisted manifest generation, cluster monitoring (optional)
7. **Cloud-Native Patterns**: Graceful shutdown (SIGTERM handling), structured JSON logging, rolling update strategies

### Research Agents Dispatched

See [research.md](research.md) for detailed findings and decisions.

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](data-model.md) for entity definitions:
- Container Image (metadata, layers, tags)
- Kubernetes Deployment (replicas, strategy, probes)
- Kubernetes Service (ClusterIP, ports)
- ConfigMap (application configuration)
- Secret (sensitive data)

### API Contracts

See [contracts/](contracts/) directory for:
- [docker-images.yaml](contracts/docker-images.yaml) - Container image specifications
- [k8s-resources.yaml](contracts/k8s-resources.yaml) - Kubernetes resource schemas
- [helm-chart.yaml](contracts/helm-chart.yaml) - Helm chart structure and values

### Quickstart Guide

See [quickstart.md](quickstart.md) for:
- Prerequisites installation (Docker Desktop, Minikube, Helm)
- Local development setup
- Container build commands
- Minikube deployment workflow
- Troubleshooting common issues

## Phase 2: Component Breakdown

### Components by User Story

#### User Story 1: Containerize Applications (P1)

| Component | Path | Description |
|-----------|------|-------------|
| Frontend Dockerfile | `frontend/Dockerfile` | Multi-stage build: Node.js build → nginx serve |
| Backend Dockerfile | `backend/Dockerfile` | Multi-stage build: Python dependencies → runtime |
| Frontend .dockerignore | `frontend/.dockerignore` | Exclude node_modules, .next, .git |
| Backend .dockerignore | `backend/.dockerignore` | Exclude __pycache__, .venv, .pytest_cache |
| Build Scripts | `Makefile` or scripts | `docker-build-frontend`, `docker-build-backend` |
| Container Tests | `backend/tests/container/`, `frontend/tests/container/` | Container startup tests, health check tests |

#### User Story 2: Deploy to Minikube (P2)

| Component | Path | Description |
|-----------|------|-------------|
| Frontend Deployment | `k8s/todo-list-hackathon/templates/deployment.yaml` | Frontend Deployment with replicas, probes, resource limits |
| Backend Deployment | `k8s/todo-list-hackathon/templates/deployment.yaml` | Backend Deployment with replicas, probes, resource limits |
| Frontend Service | `k8s/todo-list-hackathon/templates/service.yaml` | ClusterIP Service for frontend |
| Backend Service | `k8s/todo-list-hackathon/templates/service.yaml` | ClusterIP Service for backend |
| Frontend ConfigMap | `k8s/todo-list-hackathon/templates/configmap.yaml` | API URL, feature flags |
| Backend ConfigMap | `k8s/todo-list-hackathon/templates/configmap.yaml` | Database URL, OpenAI API config |
| Application Secret | `k8s/todo-list-hackathon/templates/secret.yaml` | DATABASE_URL, JWT_SECRET, OPENAI_API_KEY |
| Minikube Setup Script | `scripts/setup-minikube.sh` | Minikube start, image load, cluster verify |
| K8s Tests | `k8s/todo-list-hackathon/templates/tests/` | Helm tests for deployment health |

#### User Story 3: Package as Helm Chart (P3)

| Component | Path | Description |
|-----------|------|-------------|
| Chart Metadata | `k8s/todo-list-hackathon/Chart.yaml` | Chart name, version, description |
| Default Values | `k8s/todo-list-hackathon/values.yaml` | Default configuration for all settings |
| Local Values | `k8s/todo-list-hackathon/values-local.yaml` | Minikube-specific overrides (replicas=1, resource limits) |
| Production Values | `k8s/todo-list-hackathon/values-production.yaml` | Production overrides (replicas=2+, strict resource limits) |
| Deployment Template | `k8s/todo-list-hackathon/templates/deployment.yaml` | Unified template for frontend and backend Deployments |
| Service Template | `k8s/todo-list-hackathon/templates/service.yaml` | Unified template for Services |
| ConfigMap Template | `k8s/todo-list-hackathon/templates/configmap.yaml` | Unified template for ConfigMaps |
| Secret Template | `k8s/todo-list-hackathon/templates/secret.yaml` | Unified template for Secrets |
| Ingress Template | `k8s/todo-list-hackathon/templates/ingress.yaml` | Ingress for external access (Phase V) |
| NOTES.txt | `k8s/todo-list-hackathon/templates/NOTES.txt` | Post-install instructions |
| Helm Tests | `k8s/todo-list-hackathon/templates/tests/` | Test pod for deployment verification |
| Helm Deployment Docs | `k8s/todo-list-hackathon/README.md` | Helm chart usage, install/upgrade/rollback |

### Cross-Cutting Components

| Component | Path | Description |
|-----------|------|-------------|
| Health Endpoints | `backend/api/health.py` | /health, /metrics endpoints for probes |
| Graceful Shutdown | `backend/main.py`, `frontend/` | SIGTERM handling, connection cleanup |
| Structured Logging | `backend/core/logging.py`, `frontend/` | JSON logging with correlation ID |
| Environment Config | `backend/core/config.py`, `frontend/` | Environment variable loading |
| Deployment Documentation | `k8s/README.md`, `docs/DEPLOYMENT.md` | Deployment guide, troubleshooting |
| AI DevOps Scripts | `scripts/ai-deploy.sh` | kubectl-ai/kagent integration examples |

## Implementation Notes

### Dockerfile Strategy

**Frontend (Next.js)**:
- Stage 1 (build): `FROM node:20-alpine` - Run `pnpm build` to create static assets
- Stage 2 (serve): `FROM nginx:alpine` - Copy built assets, configure nginx for SPA routing
- Optimization: Use `.dockerignore` to exclude `node_modules`, `.next`, `.git`
- Security: Run as non-root user (nginx user)
- Health: Nginx exposes port 80, liveness probe checks /

**Backend (FastAPI)**:
- Stage 1 (deps): `FROM python:3.13-slim` - Install uv, copy `pyproject.toml`, run `uv sync`
- Stage 2 (runtime): `FROM python:3.13-slim` - Copy installed dependencies, copy application code
- Optimization: Cache dependencies in separate layer, use `.dockerignore`
- Security: Create non-root user, run as that user
- Health: Expose port 8000, `/health` endpoint for probes

### Kubernetes Resource Strategy

**Deployments**:
- Frontend: 1 replica (local), 2+ replicas (production)
- Backend: 1 replica (local), 2+ replicas (production)
- Rolling update: `maxSurge: 1`, `maxUnavailable: 0`
- Resource requests: CPU 100m, Memory 128Mi
- Resource limits: CPU 500m, Memory 512Mi

**Health Probes**:
- Liveness: `GET /health`, every 10s, timeout 5s, failureThreshold 3
- Readiness: `GET /health`, every 5s, timeout 3s, failureThreshold 2
- Startup: `GET /health`, every 5s, timeout 3s, failureThreshold 12 (60s total)

**Services**:
- Frontend Service: ClusterIP, port 80 → targetPort 80
- Backend Service: ClusterIP, port 8000 → targetPort 8000
- Service discovery: Frontend connects to `backend:8000`

### Helm Chart Strategy

**Template Structure**:
- Use `{{- if .Values.frontend.enabled }}` for optional components
- Use `{{ .Release.Name }}` prefix for resource names
- Use `{{ .Chart.AppVersion }}` for image tag
- Use `{{ tpl (toYaml .Values.someConfig) $ }}` for complex config injection

**Value Overrides**:
- `values-local.yaml`: replicas=1, minimal resource limits, imagePullPolicy=Never
- `values-production.yaml`: replicas=2+, strict resource limits, imagePullPolicy=Always

**Testing**:
- Helm test pod runs `curl` against services
- Verify frontend and backend are accessible
- Verify database connectivity

### AI DevOps Integration

**kubectl-ai** (optional):
- Generate manifests: `kubectl-ai "Create a Kubernetes Deployment for FastAPI backend with 2 replicas"`
- Diagnose issues: `kubectl-ai "Why is my pod in CrashLoopBackOff?"`
- Optimize resources: `kubectl-ai "Suggest resource limits for a Next.js frontend pod"`

**kagent** (optional):
- Monitor cluster: `kagent monitor --namespace default`
- Analyze health: `kagent analyze pods --selector app=backend`
- Get recommendations: `kagent recommend --resource deployments`

**Fallback**:
- All AI operations are optional
- Manual manifest generation and kubectl operations work without AI tools
- Documentation includes manual procedures

## Next Steps

1. ✅ Constitution Check: PASSED
2. 🔄 Phase 0: Execute research (see [research.md](research.md))
3. ⏳ Phase 1: Generate data-model.md, contracts/, quickstart.md
4. ⏳ Phase 2: Generate tasks.md via `/sp.tasks`
5. ⏳ Implementation: Execute tasks in priority order (US1 → US2 → US3)
