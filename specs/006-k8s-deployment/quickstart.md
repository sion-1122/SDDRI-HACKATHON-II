# Quickstart Guide: Kubernetes Deployment

**Feature**: 006-k8s-deployment
**Date**: 2025-01-27
**Purpose**: Get Phase IV Todo Chatbot running on Minikube in under 15 minutes

## Prerequisites

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Docker Desktop | Latest | Build and run containers | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| Minikube | Latest | Local Kubernetes cluster | [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start/) |
| Helm | 3.0+ | Package manager for K8s | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |
| kubectl | Latest | Kubernetes CLI | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| pnpm | 8+ | Frontend package manager | [pnpm.io/installation](https://pnpm.io/installation) |
| Python | 3.13+ | Backend runtime | [python.org/downloads](https://www.python.org/downloads/) |
| uv | Latest | Python package manager | [astral.sh/uv](https://astral.sh/uv/) |

### Verify Installation

```bash
# Check versions
docker --version
minikube version
helm version
kubectl version --client
pnpm --version
python --version
uv --version
```

### Optional Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| kubectl-ai | AI-assisted K8s operations | [github.com/ebrym1/kubectl-ai](https://github.com/ebrym1/kubectl-ai) |
| kagent | Cluster monitoring | [kagent.ai](https://kagent.ai) |

## Step 1: Start Minikube (2 minutes)

```bash
# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=8192

# Verify Minikube is running
minikube status

# Enable necessary addons (optional)
minikube addons enable ingress
```

**Expected Output**:
```
✅ minikube
📌 Control Plane: docker
🔉 Starting VM...
🐳 Preparing Kubernetes v1.x.x...
🚀 Launching Kubernetes...
🏄 Done! kubectl is now configured to use "minikube" cluster
```

**Troubleshooting**:
- If Docker driver fails, try `minikube start --driver=podman`
- If resources insufficient, increase memory: `minikube start --memory=10240`

## Step 2: Build Docker Images (5 minutes)

```bash
# Navigate to project root
cd /path/to/todo-list-hackathon

# Build frontend image
docker build -t todo-list-frontend:v1.0.0 ./frontend

# Build backend image
docker build -t todo-list-backend:v1.0.0 ./backend

# Verify images are built
docker images | grep todo-list
```

**Expected Output**:
```
todo-list-frontend   v1.0.0   abc123def456   2 minutes ago   180MB
todo-list-backend    v1.0.0   ghi789jkl012   3 minutes ago   120MB
```

**Troubleshooting**:
- If build fails, check Dockerfile syntax and dependencies
- If size exceeds limits, check `.dockerignore` files

## Step 3: Load Images into Minikube (1 minute)

```bash
# Load frontend image
minikube image load todo-list-frontend:v1.0.0

# Load backend image
minikube image load todo-list-backend:v1.0.0

# Verify images are loaded
minikube image ls | grep todo-list
```

**Expected Output**:
```
| docker.io/library/todo-list-frontend | v1.0.0 | 63ebfd09da89 | 180MB |
| docker.io/library/todo-list-backend  | v1.0.0 | 7a2b3c4d5e6f | 120MB |
```

**Troubleshooting**:
- If load fails, ensure Minikube is running: `minikube status`
- If images don't appear, try `eval $(minikube docker-env)` first

## Step 4: Configure Secrets (1 minute)

```bash
# Create namespace (optional)
kubectl create namespace todo-list

# Create secret with sensitive data
kubectl create secret generic todo-list-backend-secret \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db" \
  --from-literal=JWT_SECRET="your-jwt-secret-here" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-key-here" \
  --namespace=todo-list
```

**Replace Values**:
- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `JWT_SECRET`: Random string for JWT signing
- `OPENAI_API_KEY`: Your OpenAI API key

**Troubleshooting**:
- If secret creation fails, check for special characters (use `--from-file` instead)
- Verify secret: `kubectl get secret todo-list-backend-secret -n todo-list`

## Step 5: Deploy with Helm (2 minutes)

```bash
# Navigate to Helm chart directory
cd k8s/todo-list-hackathon

# Install Helm chart
helm install todo-list . \
  -f values-local.yaml \
  --namespace todo-list \
  --create-namespace

# Wait for deployment
kubectl wait --for=condition=ready pod -l app=frontend -n todo-list --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend -n todo-list --timeout=120s
```

**Expected Output**:
```
NAME: todo-list
LAST DEPLOYED: Mon Jan 27 10:00:00 2025
NAMESPACE: todo-list
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

**Troubleshooting**:
- If pods don't start, check logs: `kubectl logs -n todo-list deployment/backend`
- If images don't pull, verify `imagePullPolicy: Never` in values-local.yaml
- If secrets missing, check: `kubectl get secrets -n todo-list`

## Step 6: Access Application (2 minutes)

### Option A: Port Forwarding

```bash
# Forward frontend port
kubectl port-forward -n todo-list svc/frontend 8080:80

# Access in browser
open http://localhost:8080
```

### Option B: Minikube Tunnel

```bash
# Start tunnel (in separate terminal)
minikube tunnel

# Get frontend URL
minikube service frontend -n todo-list --url
```

### Option C: NodePort (if enabled in values)

```bash
# Get NodePort
kubectl get svc frontend -n todo-list

# Access via Minikube IP
minikube ip
open http://$(minikube ip):<NODEPORT>
```

**Expected Result**:
- Frontend loads at localhost:8080
- Backend API accessible at `http://localhost:8080/api/*`
- Login page appears

## Step 7: Run Helm Tests (1 minute)

```bash
# Run Helm tests
helm test todo-list -n todo-list --logs
```

**Expected Output**:
```
Pod todo-list-test-connection started
Pod todo-list-test-connection passed
```

## Step 8: Verify Health (1 minute)

```bash
# Check pod status
kubectl get pods -n todo-list

# Check pod health
kubectl describe pod -n todo-list -l app=backend

# Check services
kubectl get svc -n todo-list

# Check logs
kubectl logs -n todo-list deployment/backend --tail=50
kubectl logs -n todo-list deployment/frontend --tail=50
```

**Expected Output**:
```
NAME                              READY   STATUS    RESTARTS   AGE
todo-list-backend-xxx-xxx         1/1     Running   0          2m
todo-list-frontend-xxx-xxx        1/1     Running   0          2m
```

## Upgrade and Rollback

### Upgrade Application

```bash
# Build new images
docker build -t todo-list-frontend:v1.1.0 ./frontend
docker build -t todo-list-backend:v1.1.0 ./backend

# Load new images
minikube image load todo-list-frontend:v1.1.0
minikube image load todo-list-backend:v1.1.0

# Upgrade Helm release
helm upgrade todo-list . \
  -f values-local.yaml \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0 \
  --namespace todo-list
```

### Rollback if Needed

```bash
# View upgrade history
helm history todo-list -n todo-list

# Rollback to previous version
helm rollback todo-list -n todo-list

# Rollback to specific revision
helm rollback todo-list 2 -n todo-list
```

## Clean Up

```bash
# Uninstall Helm release
helm uninstall todo-list -n todo-list

# Delete namespace
kubectl delete namespace todo-list

# Stop Minikube (optional)
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## AI DevOps Tools (Optional)

### Using kubectl-ai

```bash
# Generate deployment manifest
kubectl-ai "Create a Kubernetes Deployment for FastAPI backend with 2 replicas, health checks, and resource limits"

# Diagnose issues
kubectl-ai "Diagnose why my backend pod is in CrashLoopBackOff state"

# Get recommendations
kubectl-ai "Suggest CPU and memory limits for a Next.js frontend pod"
```

### Using kagent

```bash
# Monitor cluster health
kagent monitor --namespace todo-list

# Analyze pod performance
kagent analyze pods --selector app=backend --metrics cpu,memory

# Get scaling recommendations
kagent recommend --resource deployments --app backend
```

## Troubleshooting Common Issues

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-list

# Describe pod for details
kubectl describe pod -n todo-list <pod-name>

# Check pod logs
kubectl logs -n todo-list <pod-name> --previous
```

### Image Pull Errors

```bash
# Verify images are loaded
minikube image ls | grep todo-list

# Check imagePullPolicy
kubectl get deployment -n todo-list backend -o yaml | grep imagePullPolicy

# Reload image
minikube image load todo-list-backend:v1.0.0
```

### Health Check Failures

```bash
# Check health endpoint
kubectl exec -n todo-list <backend-pod> -- curl http://localhost:8000/health

# Adjust probe timing in values-local.yaml
# Change initialDelaySeconds, periodSeconds, or timeoutSeconds
```

### Connection Issues

```bash
# Verify services
kubectl get svc -n todo-list

# Check service endpoints
kubectl get endpoints -n todo-list

# Test connectivity from frontend pod
kubectl exec -n todo-list <frontend-pod> -- curl http://backend:8000/health
```

### Resource Exhaustion

```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n todo-list

# Adjust resource limits in values-local.yaml
# Increase requests.limits.cpu or requests.limits.memory
```

## Success Criteria

You have successfully deployed when:

- ✅ Both pods are `Running` and `READY 1/1`
- ✅ Frontend accessible at `http://localhost:8080`
- ✅ Backend health endpoint returns `{"status": "healthy"}`
- ✅ Helm tests pass (`helm test` succeeds)
- ✅ Can login and view tasks
- ✅ Chat interface responds to messages

**Time to Complete**: 10-15 minutes for first deployment, 2-5 minutes for subsequent deployments.

## Next Steps

1. ✅ Quickstart complete: Application running on Minikube
2. 📚 Read `plan.md` for detailed architecture
3. 📋 Read `tasks.md` for implementation tasks (when generated)
4. 🚀 Deploy to production cloud K8s (Phase V)
5. 📊 Add monitoring and observability (Phase V)
