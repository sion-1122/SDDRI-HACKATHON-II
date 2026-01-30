# Feature Specification: Cloud Kubernetes Deployment

**Feature Branch**: `011-cloud-k8s-deployment`
**Created**: 2026-01-30
**Status**: Draft
**Input**: Deploy the complete application stack to a managed cloud Kubernetes service (AKS/GKE/OKE). Set up container registry, deploy Kafka and Dapr to cloud, implement CI/CD with GitHub Actions, and add monitoring.

## User Scenarios & Testing

### User Story 1 - Cloud K8s Cluster Setup (Priority: P1) MVP

As a developer, I want to provision a managed Kubernetes cluster so that the application runs in production environment.

**Why this priority**: Cloud cluster is the foundation for production deployment.

**Acceptance Scenarios**:
1. Given I have cloud CLI installed, When I create a cluster, Then it provisions with 3 nodes
2. Given cluster is created, When I get credentials, Then kubectl can access the cluster
3. Given kubectl is configured, When I list nodes, Then all nodes are Ready

### User Story 2 - Container Registry Setup (Priority: P1)

As a developer, I want to push Docker images to a container registry so that cloud clusters can pull them.

**Why this priority**: Registry is required for cloud deployment images.

**Acceptance Scenarios**:
1. Given registry exists, When I build images, Then they are tagged for the registry
2. Given images are tagged, When I push them, Then they upload to registry
3. Given images are in registry, When I deploy to cloud, Then pods pull images successfully

### User Story 3 - Cloud Kafka Deployment (Priority: P1)

As a developer, I want to deploy Kafka to the cloud cluster so that event streaming is production-ready.

**Why this priority**: Cloud deployment requires cloud-native Kafka for reliability.

**Acceptance Scenarios**:
1. Given I deploy Redpanda to cloud, When pods are running, Then they have persistent storage
2. Given Kafka is running, When I produce messages, Then they are persisted across pod restarts
3. Given cluster scales, When I add nodes, Then Kafka rebalances automatically

### User Story 4 - Dapr on Cloud K8s (Priority: P1)

As a developer, I want Dapr running on the cloud cluster so that all Dapr features work in production.

**Why this priority**: Dapr is required for the application to function.

**Acceptance Scenarios**:
1. Given I install Dapr on cloud cluster, When I deploy the app, Then sidecars start properly
2. Given Dapr is running, When I test pub/sub, Then messages flow through Kafka
3. Given Dapr is running, When I test state store, Then Redis connects successfully

### User Story 5 - CI/CD Pipeline (Priority: P2)

As a developer, I want automated deployment so that pushes to main branch deploy automatically.

**Why this priority**: CI/CD enables continuous delivery and reduces manual errors.

**Acceptance Scenarios**:
1. Given I push to main branch, When GitHub Actions triggers, Then it builds images
2. Given images build, When tests pass, Then pipeline pushes images to registry
3. Given images are pushed, When deploy step runs, Then cloud cluster updates

### User Story 6 - Monitoring & Logging (Priority: P2)

As an operator, I want centralized logging and metrics so that I can monitor production health.

**Why this priority**: Production systems require observability.

**Acceptance Scenarios**:
1. Given I deploy monitoring stack, When I access Grafana, Then dashboards load
2. Given application logs, When I query Loki, Then logs appear in search
3. Given metrics are collected, When I view dashboards, Then I see request rates, errors

## Requirements

### Functional Requirements

**Cloud Cluster (FR-001 to FR-006)**:
- FR-001: System MUST provision cluster on AKS/GKE/OKE (provider choice)
- FR-002: Cluster MUST have at least 3 nodes for HA
- FR-003: Nodes MUST have minimum 4 CPU and 16GB RAM
- FR-004: Cluster MUST have ingress controller configured
- FR-005: Cluster MUST enable pod autoscaling
- FR-006: Cluster MUST have network policies configured

**Container Registry (FR-007 to FR-012)**:
- FR-007: System MUST create ACR/GCR/OCR registry
- FR-008: Images MUST be tagged with registry URL
- FR-009: Images MUST use semantic version tags (v1.0.0)
- FR-010: Images MUST use :latest tag for development
- FR-011: Registry MUST integrate with cloud K8s (no auth required)
- FR-012: CI/CD MUST push images on every commit

**Cloud Deployment (FR-013 to FR-020)**:
- FR-013: System MUST deploy all components via Helm
- FR-014: System MUST use values-cloud.yaml for production configuration
- FR-015: Deployments MUST use cloud container registry images
- FR-016: Services MUST use cloud ingress for external access
- FR-017: Secrets MUST use cloud secret management (not plain ConfigMaps)
- FR-018: Database MUST use cloud PostgreSQL or external Neon
- FR-019: Redis MUST be deployed to cluster for state store
- FR-020: All components MUST have health checks configured

**CI/CD Pipeline (FR-021 to FR-028)**:
- FR-021: GitHub Actions MUST trigger on push to main branch
- FR-022: Pipeline MUST run tests before deployment
- FR-023: Pipeline MUST build frontend and backend images
- FR-024: Pipeline MUST push images to container registry
- FR-025: Pipeline MUST deploy via Helm upgrade
- FR-026: Pipeline MUST run database migrations
- FR-027: Pipeline MUST notify on deployment status
- FR-028: Pipeline deployment time MUST be under 10 minutes

**Monitoring (FR-029 to FR-034)**:
- FR-029: System MUST deploy Prometheus for metrics collection
- FR-030: System MUST deploy Grafana for metrics visualization
- FR-031: System MUST deploy Loki for log aggregation
- FR-032: System MUST deploy Promtail for log shipping
- FR-033: Dashboards MUST include: request rate, error rate, latency
- FR-034: Alerts MUST be configured for critical failures

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cloud K8s Cluster                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Frontend   │  │   Backend   │  │   Worker    │              │
│  │  (Next.js)  │  │  (FastAPI)  │  │ (Reminder)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                │                │                     │
│         └────────────────┴────────────────┘                     │
│                          │                                      │
│  ┌─────────────┐  ┌──────┴───────┐  ┌─────────────┐            │
│  │   Redpanda  │  │    Redis    │  │ PostgreSQL  │            │
│  │   (Kafka)   │  │  (State)    │  │  (Neon)     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                    Ingress Controller               │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Name / DNS                          │
└─────────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy-cloud.yml
name: Deploy to Cloud

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    steps:
      - Checkout code
      - Run tests (pytest, npm test)
      - Build frontend image
      - Build backend image
      - Push to container registry
      - Deploy Redis to cluster
      - Deploy Redpanda to cluster
      - Deploy app via Helm upgrade
      - Run smoke tests
```

### values-cloud.yaml

```yaml
# Production cloud values
registry: "your-registry.azurecr.io"
images:
  frontend:
    repository: todo-frontend
    tag: "v1.0.0"
  backend:
    repository: todo-backend
    tag: "v1.0.0"

replicas:
  frontend: 3
  backend: 3
  worker: 2

resources:
  frontend:
    requests: { cpu: "100m", memory: "128Mi" }
    limits: { cpu: "500m", memory: "512Mi" }
  backend:
    requests: { cpu: "200m", memory: "256Mi" }
    limits: { cpu: "1000m", memory: "1Gi" }

ingress:
  enabled: true
  host: "todo-app.yourdomain.com"
  tls: true
```

## Success Criteria

- SC-001: Cloud cluster provisions in under 15 minutes
- SC-002: Application deploys to cloud in under 10 minutes
- SC-003: All components are accessible via external domain
- SC-004: CI/CD pipeline runs end-to-end in under 15 minutes
- SC-005: Monitoring dashboards show real-time metrics
- SC-006: Deployment survives node failures

## Dependencies

1. **010-dapr-integration** - All features must be Dapr-enabled
2. **Cloud Provider Account** - Azure/AWS/Google Cloud account with quota
3. **Domain Name** - For external ingress (optional but recommended)
4. **GitHub Repository** - For GitHub Actions

## Out of Scope

1. Multi-region deployment - Single region only
2. Disaster recovery - Backup/DR is separate phase
3. Cost optimization - Rightsizing for cost is separate effort
4. Security hardening - Advanced security is separate phase
5. Compliance - SOC2, HIPAA, etc not addressed
