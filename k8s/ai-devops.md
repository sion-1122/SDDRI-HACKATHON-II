# AI DevOps Tool Usage Guide

**Feature**: 006-k8s-deployment
**Purpose**: Guide for using AI-assisted DevOps tools (kubectl-ai, kagent) with Kubernetes deployment

## Overview

This guide demonstrates how to use AI-powered DevOps tools to simplify Kubernetes operations. These tools use LLMs to generate manifests, diagnose issues, and provide operational recommendations.

## Tools

### 1. kubectl-ai

**Description**: Generate Kubernetes manifests and diagnose issues using AI
**Installation**: https://github.com/ebrym1/kubectl-ai

### 2. kagent

**Description**: Cluster monitoring and optimization recommendations
**Installation**: https://kagent.ai

---

## kubectl-ai Examples

### Installation

```bash
# Install kubectl-ai (requires OpenAI API key)
go install github.com/ebrym1/kubectl-ai@latest

# Configure with your OpenAI API key
export OPENAI_API_KEY="sk-your-openai-key"
```

### Generate Deployment Manifests

```bash
# Generate a basic deployment
kubectl-ai "Create a Kubernetes Deployment for FastAPI backend with 3 replicas"

# Generate deployment with specific requirements
kubectl-ai "Create a Deployment for Next.js frontend with:
- 2 replicas
- CPU request: 100m, limit: 500m
- Memory request: 128Mi, limit: 512Mi
- Liveness probe on port 3000, path /health
- Readiness probe on port 3000, path /health
- Rolling update with maxSurge=1, maxUnavailable=0"

# Generate Service
kubectl-ai "Create a ClusterIP Service for the backend deployment on port 8000"

# Generate ConfigMap
kubectl-ai "Create a ConfigMap with application config:
- API_URL: http://backend:8000
- LOG_LEVEL: INFO
- FEATURE_FLAGS: {\"newFeature\": true}"
```

### Diagnose Issues

```bash
# Diagnose pod issues
kubectl-ai "Diagnose why my backend pod is in CrashLoopBackOff state"

# Analyze resource issues
kubectl-ai "Why is my pod being OOMKilled?"

# Debug connectivity
kubectl-ai "My frontend cannot connect to backend. Both are in namespace todo-list"

# Check service issues
kubectl-ai "Service backend is not routing traffic to pods"

# Image pull issues
kubectl-ai "Pod is failing with ErrImageNeverPull"
```

### Get Recommendations

```bash
# Resource optimization
kubectl-ai "Suggest CPU and memory limits for a Next.js frontend pod"

# Security hardening
kubectl-ai "Add security best practices to this Deployment:
- Run as non-root user
- Drop all capabilities
- Read-only root filesystem"

# High availability
kubectl-ai "Configure PodDisruptionBudget for 3 replica deployment"

# Autoscaling
kubectl-ai "Set up HorizontalPodAutoscaler for backend with min 2, max 10 replicas"
```

### Generate Complex Resources

```bash
# Ingress resource
kubectl-ai "Create an Ingress resource for todo-app.example.com with TLS cert"

# NetworkPolicy
kubectl-ai "Create a NetworkPolicy that allows:
- Frontend pods can connect to backend pods on port 8000
- Backend pods can connect to Neon PostgreSQL on port 5432
- Deny all other traffic"

# PersistentVolumeClaim
kubectl-ai "Create a PVC for logs with 5Gi storage and ReadWriteOnce access"
```

---

## kagent Examples

### Installation

```bash
# Install kagent CLI
npm install -g kagent

# or using Go
go install github.com/kagent-dev/kagent@latest
```

### Monitor Cluster Health

```bash
# Monitor all pods in namespace
kagent monitor --namespace todo-list

# Monitor specific deployment
kagent monitor --deployment backend --namespace todo-list

# Monitor with custom interval
kagent monitor --namespace todo-list --interval 30s
```

### Analyze Pod Performance

```bash
# Analyze CPU and memory usage
kagent analyze pods --selector app=backend --metrics cpu,memory

# Analyze pod restarts
kagent analyze pods --selector app=frontend --check restarts

# Find resource hogs
kagent analyze pods --sort-by memory --top 10
```

### Get Scaling Recommendations

```bash
# Get HPA recommendations
kagent recommend --resource deployments --app backend --namespace todo-list

# Autoscaling suggestions
kagent recommend --scaling --namespace todo-list --threshold 70

# Resource optimization
kagent recommend --resources --namespace todo-list
```

### Cluster Health Analysis

```bash
# Overall cluster health
kagent health --cluster

# Namespace health
kagent health --namespace todo-list

# Detailed analysis
kagent health --namespace todo-list --verbose
```

---

## Integration with Deployment Workflow

### Before Deployment

```bash
# Validate manifests with AI
kubectl-ai "Review this deployment.yaml for best practices and security issues" < deployment.yaml

# Get resource recommendations
kubectl-ai "What resource limits should I set for a FastAPI app serving 1000 RPS?"
```

### During Deployment

```bash
# Monitor in real-time
kagent monitor --namespace todo-list &

# Watch for issues
kubectl-ai "Alert me if any pod enters CrashLoopBackOff or OOMKilled state"
```

### After Deployment

```bash
# Analyze deployment success
kagent health --namespace todo-list

# Get optimization suggestions
kagent recommend --namespace todo-list

# Troubleshoot issues
kubectl-ai "Check logs of backend pods for errors in last 5 minutes"
```

---

## Practical Workflows

### Workflow 1: Deploy New Application

```bash
# 1. Generate deployment manifest
kubectl-ai "Create a deployment for my FastAPI app with health checks and resource limits" > deployment.yaml

# 2. Generate service manifest
kubectl-ai "Create a ClusterIP service for the deployment on port 8000" > service.yaml

# 3. Apply manifests
kubectl apply -f deployment.yaml -f service.yaml

# 4. Monitor deployment
kagent monitor --namespace todo-list

# 5. Verify health
kubectl-ai "Check if all pods are running and healthy"
```

### Workflow 2: Debug Production Issue

```bash
# 1. Identify problem pod
kubectl get pods -n todo-list

# 2. Get AI diagnosis
kubectl-ai "Pod backend-7f8d9c4b-x2k1p is restarting frequently. Diagnose the issue"

# 3. Check logs
kubectl logs backend-7f8d9c4b-x2k1p -n todo-list --tail=100

# 4. Analyze with kagent
kagent analyze pods --selector app=backend --metrics cpu,memory

# 5. Get fix recommendations
kubectl-ai "The pod is running out of memory. Suggest fixes"
```

### Workflow 3: Optimize Resources

```bash
# 1. Analyze current resource usage
kagent analyze pods --metrics cpu,memory --namespace todo-list

# 2. Get optimization recommendations
kagent recommend --resources --namespace todo-list

# 3. Generate optimized manifests
kubectl-ai "Update resource limits based on actual usage: CPU avg 150m, Memory avg 200Mi"

# 4. Apply changes
kubectl apply -f deployment-optimized.yaml

# 5. Verify improvements
kagent monitor --namespace todo-list
```

---

## Best Practices

### When to Use kubectl-ai

- **Generating boilerplate**: Quickly scaffold standard K8s resources
- **Learning patterns**: Understand best practices for resource configurations
- **Debugging**: Get AI insights when pods/services fail
- **Documentation**: Generate comments and explanations for manifests

### When to Use kagent

- **Monitoring**: Real-time cluster and pod health monitoring
- **Analysis**: Identify resource bottlenecks and performance issues
- **Optimization**: Get scaling and resource recommendations
- **Alerting**: Set up automated health checks

### Limitations

- **AI tools are supplementary**: Always review AI-generated manifests
- **Security**: Never expose secrets in AI prompts
- **Cost**: kubectl-ai uses OpenAI API (consider token costs)
- **Accuracy**: Verify AI suggestions before applying to production

### Fallback

If AI tools are unavailable:
- Use `kubectl explain` to understand resource fields
- Reference official Kubernetes documentation
- Use existing Helm charts as templates
- Manual manifest creation with YAML editors

---

## Example: Complete Deployment with AI Tools

```bash
#!/bin/bash
# deploy-with-ai.sh - Deploy using AI DevOps tools

NAMESPACE="todo-list"
APP_NAME="todo-list"

# 1. Generate deployment with AI
kubectl-ai "Create a production-ready deployment for $APP_NAME with:
- 3 replicas
- Resource limits: CPU 500m, Memory 512Mi
- Health checks on /health
- Graceful shutdown with 30s grace period" > deployment.yaml

# 2. Generate service with AI
kubectl-ai "Create a ClusterIP service for $APP_NAME on port 8000" > service.yaml

# 3. Review manifests
kubectl-ai "Review these manifests for security best practices" < deployment.yaml

# 4. Apply manifests
kubectl apply -f deployment.yaml -f service.yaml -n "$NAMESPACE"

# 5. Monitor deployment
kagent monitor --namespace "$NAMESPACE" &
MONITOR_PID=$!

# 6. Wait for rollout
kubectl rollout status deployment/$APP_NAME -n "$NAMESPACE"

# 7. Verify health
kubectl-ai "Verify all pods are running and healthy in namespace $NAMESPACE"

# 8. Get recommendations
kagent recommend --namespace "$NAMESPACE"

# 9. Cleanup
kill $MONITOR_PID

echo "Deployment complete!"
```

---

## Troubleshooting AI Tools

### kubectl-ai Issues

```bash
# Issue: "OpenAI API key not found"
export OPENAI_API_KEY="sk-your-key"

# Issue: "Invalid manifest generated"
# Review and edit manually, or refine prompt
kubectl-ai "Fix syntax errors in this YAML" < broken-manifest.yaml

# Issue: "Rate limit exceeded"
# Wait and retry, or switch to different API endpoint
```

### kagent Issues

```bash
# Issue: "Cannot connect to cluster"
kubectl config current-context
kubectl cluster-info

# Issue: "Insufficient permissions"
# Check RBAC permissions for kagent service account
kubectl auth can-i --list

# Issue: "No metrics found"
# Ensure metrics-server is installed
kubectl get apiservice v1beta1.metrics.k8s.io
```

---

## References

- [kubectl-ai GitHub](https://github.com/ebrym1/kubectl-ai)
- [kagent Documentation](https://kagent.ai)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

---

**Note**: AI tools are powerful assistants but should not replace human oversight. Always review AI-generated manifests before applying to production clusters.
