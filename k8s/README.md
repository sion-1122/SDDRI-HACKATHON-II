# Kubernetes Deployment Guide

## Prerequisites

- Docker Desktop running
- Minikube installed and running
- kubectl configured
- Helm 3.0+ installed

## Quick Start

### 1. Start Minikube

```bash
minikube start --driver=docker --cpus=2 --memory=3072
```

### 2. Build and Load Images

```bash
./scripts/build-and-load-all.sh
```

### 3. Deploy Application

```bash
./scripts/deploy-all.sh
```

### 4. Access Application

Get the frontend URL:
```bash
minikube service -n todo-list todo-list-todo-list-hackathon-frontend --url
```

Or use port-forwarding:
```bash
kubectl port-forward -n todo-list svc/todo-list-todo-list-hackathon-frontend 8080:3000
# Open browser to http://localhost:8080
```

### 5. Run Tests

```bash
helm test todo-list --namespace todo-list --logs
```

## Architecture

### Components

- **Frontend**: Next.js 16.1.1 standalone server running on Node.js 20-alpine
- **Backend**: FastAPI backend running on Python 3.13-slim
- **Database**: Neon PostgreSQL (external cloud-hosted)

### Services

| Service | Type | Port | Description |
|---------|------|------|-------------|
| todo-list-todo-list-hackathon-frontend | ClusterIP | 3000 | Frontend UI |
| todo-list-todo-list-hackathon-backend | ClusterIP | 8000 | Backend API |

## Configuration

### Environment Variables (Backend)

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | `sqlite:////tmp/todo.db` |
| JWT_SECRET | JWT signing secret | `change-me-in-production` |
| OPENAI_API_KEY | OpenAI API key for chatbot | `sk-...` |
| FRONTEND_URL | Frontend URL for CORS | `http://localhost` |

### Values Files

- `values.yaml` - Default values (production-like)
- `values-local.yaml` - Minikube overrides (minimal resources, local images)

## Operations

### Upgrade Application

```bash
helm upgrade todo-list . -f values-local.yaml --namespace todo-list
```

### Rollback

```bash
helm rollback todo-list --namespace todo-list
```

### View Logs

```bash
# Frontend logs
kubectl logs -n todo-list deployment/todo-list-todo-list-hackathon-frontend --tail=50

# Backend logs
kubectl logs -n todo-list deployment/todo-list-todo-list-hackathon-backend --tail=50
```

### Scale Deployment

```bash
kubectl scale deployment/todo-list-todo-list-hackathon-frontend --replicas=3 -n todo-list
```

## Troubleshooting

### Pods not starting

```bash
kubectl get pods -n todo-list
kubectl describe pod -n todo-list <pod-name>
kubectl logs -n todo-list <pod-name>
```

### Image pull errors

Ensure images are loaded into Minikube:
```bash
minikube image ls | grep todo-list
```

### Health check failures

Check health endpoint:
```bash
kubectl exec -n todo-list <backend-pod> -- curl http://localhost:8000/health
```

### Cleanup

```bash
./scripts/cleanup.sh
# Or to also stop Minikube:
./scripts/cleanup.sh --stop-minikube
```
