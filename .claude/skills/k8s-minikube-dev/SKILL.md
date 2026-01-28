---
name: k8s-minikube-dev
description: Local Kubernetes development and deployment automation using Minikube. Use when deploying containerized applications to local Kubernetes clusters - tasks include Minikube cluster management, Docker image building and loading, kubectl operations, Helm chart management, deployment automation, and troubleshooting K8s resources
---

# K8s Minikube Dev

Local Kubernetes development patterns using Minikube, Docker, kubectl, and Helm.

## Quick Start

```bash
# First-time deployment
minikube start --driver=docker --cpus=2 --memory=3072
./scripts/build-and-load-all.sh
./scripts/deploy-all.sh

# After code changes
./scripts/build-and-load-all.sh
./scripts/deploy-all.sh

# Cleanup
./scripts/cleanup.sh
```

## Core Capabilities

### 1. Minikube Cluster Management

```bash
# Start/stop cluster
minikube start --driver=docker --cpus=2 --memory=3072
minikube status
minikube stop

# Check status
kubectl cluster-info
kubectl get nodes
```

### 2. Docker Image Management

```bash
# Build and load to Minikube
docker build -t <name>:<tag> ./<dir>
minikube image load <name>:<tag>
minikube image ls | grep <name>
```

### 3. Kubernetes Operations (kubectl)

```bash
# Pod status and logs
kubectl get pods -n <namespace>
kubectl logs -n <namespace> <pod-name> --tail=50
kubectl describe pod -n <namespace> <pod-name>

# Debug and exec
kubectl exec -it -n <namespace> <pod-name> -- /bin/sh
kubectl rollout restart deployment/<name> -n <namespace>
kubectl scale deployment/<name> --replicas=3 -n <namespace>
```

### 4. Helm Chart Management

```bash
# Validate and install
helm lint
helm template <release> .
helm install <release> . -f values-local.yaml -n <namespace> --create-namespace

# Upgrade and rollback
helm upgrade <release> . -f values-local.yaml -n <namespace>
helm rollback <release> -n <namespace>
helm history <release> -n <namespace>
```

## Deployment Patterns

### Standard Full Deployment

```bash
minikube start --driver=docker --cpus=2 --memory=3072
docker build -t myapp-frontend:v1.0.0 ./frontend
docker build -t myapp-backend:v1.0.0 ./backend
minikube image load myapp-frontend:v1.0.0
minikube image load myapp-backend:v1.0.0
cd k8s/myapp-chart
helm install myapp . -f values-local.yaml -n myapp --create-namespace
```

### Debugging Failing Pods

```bash
kubectl get pods -n myapp
kubectl describe pod -n myapp <failing-pod>
kubectl logs -n myapp <failing-pod> --tail=100
```

### Quick Redeploy After Code Changes

```bash
docker build -t myapp-frontend:v1.0.1 ./frontend
minikube image load myapp-frontend:v1.0.1
cd k8s/myapp-chart
helm upgrade myapp . --set frontend.image.tag=v1.0.1 -f values-local.yaml -n myapp
```

## Conventions

- **Image naming:** `<project>-<service>:v<semver>`
- **Namespace:** `<project>` or `<environment>`
- **Helm release:** Simple name like `todo-list`, `myapp`
- **Health paths:** Frontend `/`, Backend `/health`

## Resources

- **scripts/**: Build, load, deploy, cleanup automation
- **references/**: K8s patterns, Helm conventions
- **assets/chart-templates/**: Reusable Helm templates
