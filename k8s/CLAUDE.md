# Kubernetes Deployment Instructions for Claude Code

This file provides context for Claude Code when working on the Kubernetes deployment (Phase IV: 006-k8s-deployment).

## Project Context

This is a full-stack Todo Chatbot application deployed on Kubernetes using Minikube for local development and Helm for deployment automation.

**Stack:**
- Frontend: Next.js 16, React 19, Tailwind CSS 4
- Backend: FastAPI, Python 3.13, MCP Tools
- Database: Neon Serverless PostgreSQL (external)
- Container: Docker, Multi-stage builds
- Orchestration: Kubernetes (Minikube)
- Package Manager: Helm 3

## Directory Structure (Per Principle VI - Monorepo)

```
k8s/                                   # Kubernetes deployment (Phase IV)
└── todo-list-hackathon/               # Helm chart
    ├── Chart.yaml                     # Helm metadata
    ├── values.yaml                    # Default values
    ├── values-local.yaml              # Minikube overrides
    ├── values-production.yaml         # Production overrides
    ├── templates/                     # K8s manifest templates
    │   ├── deployment.yaml            # Frontend + Backend Deployments
    │   ├── service.yaml               # ClusterIP Services
    │   ├── ingress.yaml               # Ingress for external access
    │   ├── tests/test-connection.yaml # Helm test
    │   └── NOTES.txt                  # Post-install instructions
    └── README.md                      # Helm chart usage

frontend/                              # Next.js frontend
├── Dockerfile                         # Multi-stage container build
├── .dockerignore                      # Build context exclusions
└── app/                               # Next.js App Router

backend/                               # FastAPI backend
├── Dockerfile                         # Multi-stage container build
├── .dockerignore                      # Build context exclusions
├── api/                               # API endpoints
├── mcp_server/                        # MCP tools
└── core/                              # Configuration, logging

scripts/                               # Automation scripts
├── build-and-load-all.sh              # Build + load images to Minikube
├── deploy-all.sh                      # Helm install
├── cleanup.sh                         # Helm uninstall + Minikube stop
└── scan-images.sh                     # Container security scanning

tests/
├── container/                         # Container tests
│   ├── test-frontend-container.sh
│   └── test-backend-container.sh
└── helm/                              # Helm chart tests
    └── test-helm-chart.sh

specs/006-k8s-deployment/              # Feature specifications
├── spec.md                            # Feature specification
├── plan.md                            # Implementation plan
├── tasks.md                           # Task breakdown
├── quickstart.md                      # 15-minute deployment guide
├── ai-devops.md                       # AI DevOps tools guide
└── TROUBLESHOOTING.md                 # Common issues & solutions
```

## K8s-Specific Commands

### Local Development

```bash
# Start Minikube
minikube start --driver=docker --cpus=4 --memory=3072

# Build and load images
./scripts/build-and-load-all.sh

# Deploy with Helm
./scripts/deploy-all.sh

# Check status
kubectl get pods
kubectl get svc

# Access application
minikube tunnel  # Run in separate terminal
minikube service frontend --url

# Run tests
./tests/helm/test-helm-chart.sh

# Cleanup
./scripts/cleanup.sh
```

### Container Operations

```bash
# Build frontend
docker build -t todo-list-frontend:v1.0.0 ./frontend

# Build backend
docker build -t todo-list-backend:v1.0.0 ./backend

# Verify image sizes
docker images | grep todo-list

# Load into Minikube
minikube image load todo-list-frontend:v1.0.0
minikube image load todo-list-backend:v1.0.0

# Scan for vulnerabilities
./scripts/scan-images.sh
```

### Helm Operations

```bash
# Lint chart
helm lint ./k8s/todo-list-hackathon

# Install
helm install todo-list ./k8s/todo-list-hackathon -f k8s/todo-list-hackathon/values-local.yaml

# Upgrade
helm upgrade todo-list ./k8s/todo-list-hackathon -f k8s/todo-list-hackathon/values-local.yaml

# Rollback
helm rollback todo-list

# Test
helm test todo-list --logs

# Uninstall
helm uninstall todo-list
```

### Troubleshooting

```bash
# Check pod status
kubectl get pods -o wide

# Describe pod
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name> --tail=50 -f

# Exec into pod
kubectl exec -it <pod-name> -- /bin/bash

# Port forward
kubectl port-forward svc/frontend 8080:80

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

## Constitution Principles (XI-XVI)

### XI. Containerization with Docker

- Multi-stage Dockerfiles for optimized image sizes
- Non-root user execution (frontend: 1001, backend: 1000)
- Image size constraints: frontend <200MB, backend <150MB
- Health checks in Dockerfile (HEALTHCHECK instruction)
- .dockerignore to exclude unnecessary files

### XII. Kubernetes Orchestration

- Minikube for local Kubernetes development
- Deployments with replicas (1 local, 2+ production)
- ClusterIP Services for internal communication
- Rolling update strategy: maxSurge=1, maxUnavailable=0 (zero downtime)
- Resource requests and limits for all containers

### XIII. Helm Chart Packaging

- Chart.yaml with metadata and version
- values.yaml for default configuration
- values-local.yaml for Minikube overrides
- values-production.yaml for production overrides
- Template files for all K8s resources
- Helm test for connectivity validation

### XIV. AI-Assisted DevOps

- kubectl-ai for manifest generation and issue diagnosis
- kagent for cluster monitoring and optimization
- Documentation in k8s/ai-devops.md
- Fallback to manual operations if AI tools unavailable

### XV. Cloud-Native Deployment Patterns

- Health probes: liveness, readiness, startup
- Graceful shutdown: SIGTERM handling, 30s termination grace period
- Structured JSON logging with correlation IDs
- Resource limits: CPU 100m-500m, Memory 128Mi-512Mi
- Security contexts: runAsNonRoot, drop all capabilities

### XVI. AIOps and Blueprints

- Reusable deployment patterns in k8s-minikube-dev skill
- Helm chart templates can be reused for other projects
- Automation scripts for build, deploy, cleanup
- Troubleshooting guide for common issues

## Common Patterns

### Multi-Stage Docker Build

```dockerfile
# Frontend (Next.js)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN pnpm install
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/.next /app/.next
COPY --from=builder /app/public /app/public
COPY nginx.conf /etc/nginx/nginx.conf
HEALTHCHECK --interval=30s CMD curl -f http://localhost/ || exit 1
```

### Health Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2

startupProbe:
  httpGet:
    path: /health
    port: 8000
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 12
```

### Resource Limits

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Security Context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

## When to Use This Context

Use this file when:
- Working on K8s deployment (k8s/ directory)
- Modifying Helm chart templates
- Debugging deployment issues
- Adding new containerized services
- Implementing CI/CD for K8s

## Key Files to Reference

- `specs/006-k8s-deployment/spec.md` - Feature requirements
- `specs/006-k8s-deployment/plan.md` - Architecture and design
- `specs/006-k8s-deployment/tasks.md` - Implementation tasks
- `specs/006-k8s-deployment/quickstart.md` - 15-minute deployment guide
- `k8s/ai-devops.md` - AI DevOps tools usage
- `k8s/TROUBLESHOOTING.md` - Common issues and solutions

## Testing Commands

```bash
# Container tests
./tests/container/test-frontend-container.sh
./tests/container/test-backend-container.sh

# Helm chart tests
./tests/helm/test-helm-chart.sh

# Manual connectivity test
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://backend:8000/health
```

## Next Steps for Phase V

For cloud K8s deployment (Phase V):
1. Choose cloud provider (AKS, GKE, EKS, OKE)
2. Set up managed Kubernetes cluster
3. Configure container registry (ACR, GCR, ECR)
4. Push images to registry
5. Update values-production.yaml with registry URLs
6. Deploy with Helm using production values
7. Set up Ingress controller and TLS certificates
8. Configure monitoring and logging
9. Implement CI/CD pipeline
10. Add Dapr for event-driven architecture
11. Deploy Kafka for pub/sub messaging


<claude-mem-context>
# Recent Activity

<!-- This section is auto-generated by claude-mem. Edit content outside the tags. -->

### Jan 28, 2026

| ID | Time | T | Title | Read |
|----|------|---|-------|------|
| #537 | 12:20 PM | 🟣 | Kubernetes-Specific CLAUDE.md Documentation Created | ~486 |
</claude-mem-context>