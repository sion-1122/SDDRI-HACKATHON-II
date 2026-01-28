# Kubernetes Deployment Troubleshooting Guide

**Feature**: 006-k8s-deployment
**Purpose**: Common issues and solutions for Minikube and Kubernetes deployment

---

## Table of Contents

1. [Minikube Issues](#minikube-issues)
2. [Docker Build Issues](#docker-build-issues)
3. [Pod Issues](#pod-issues)
4. [Service Issues](#service-issues)
5. [Helm Issues](#helm-issues)
6. [Networking Issues](#networking-issues)
7. [Resource Issues](#resource-issues)
8. [Authentication Issues](#authentication-issues)

---

## Minikube Issues

### Issue: Minikube fails to start

**Symptoms:**
```bash
$ minikube start
❌ Exiting due to PROVIDER_DOCKER_NOT_FOUND: Docker is not installed
```

**Solutions:**

1. **Verify Docker Desktop is running:**
   ```bash
   docker --version
   docker ps
   ```

2. **Check available drivers:**
   ```bash
   minikube start --driver=help
   ```

3. **Try alternative driver:**
   ```bash
   minikube start --driver=podman
   # or
   minikube start --driver=hyperkit
   ```

### Issue: Insufficient memory

**Symptoms:**
```bash
$ minikube start --memory=8192
❌ Exiting due to HOST_INSUFFICIENT_MEMORY: Available memory is only 4096MB
```

**Solutions:**

1. **Reduce Minikube memory allocation:**
   ```bash
   minikube start --memory=3072 --cpus=2
   ```

2. **Increase Docker Desktop memory:**
   - Open Docker Desktop
   - Settings → Resources → Memory
   - Increase to 8GB or more
   - Restart Docker Desktop

3. **Free up system memory:**
   ```bash
   # Stop unnecessary applications
   # Clear Docker cache
   docker system prune -a
   ```

### Issue: Minikube stuck in "Starting" state

**Symptoms:**
```bash
$ minikube status
host: Running
kubelet: Stopped
```

**Solutions:**

1. **Check Minikube logs:**
   ```bash
   minikube logs
   ```

2. **Delete and restart Minikube:**
   ```bash
   minikube delete
   minikube start --driver=docker
   ```

3. **Update Minikube:**
   ```bash
   # macOS/Linux
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```

---

## Docker Build Issues

### Issue: Docker build fails with "no space left on device"

**Symptoms:**
```bash
$ docker build -t todo-list-frontend:v1.0.0 ./frontend
ERROR: failed to solve: failed to register layer: no space left on device
```

**Solutions:**

1. **Clean Docker build cache:**
   ```bash
   docker builder prune -a
   ```

2. **Remove unused Docker resources:**
   ```bash
   docker system prune -a --volumes
   ```

3. **Increase Docker disk size:**
   - Docker Desktop → Settings → Resources → Disk Image Size
   - Increase to 64GB or more

### Issue: Build fails with "module not found"

**Symptoms:**
```bash
$ docker build -t todo-list-frontend:v1.0.0 ./frontend
error: Could not resolve module
```

**Solutions:**

1. **Verify dependencies are in package.json:**
   ```bash
   cat frontend/package.json | grep dependencies
   ```

2. **Rebuild with fresh layer:**
   ```bash
   docker build --no-cache -t todo-list-frontend:v1.0.0 ./frontend
   ```

3. **Check .dockerignore is not excluding needed files:**
   ```bash
   cat frontend/.dockerignore
   # Ensure node_modules is NOT ignored during build
   ```

---

## Pod Issues

### Issue: Pod stuck in CrashLoopBackOff

**Symptoms:**
```bash
$ kubectl get pods
NAME                      READY   STATUS              RESTARTS   AGE
todo-list-backend-xxx     0/1     CrashLoopBackOff    5          3m
```

**Solutions:**

1. **Check pod logs:**
   ```bash
   kubectl logs todo-list-backend-xxx
   kubectl logs todo-list-backend-xxx --previous
   ```

2. **Describe pod for events:**
   ```bash
   kubectl describe pod todo-list-backend-xxx
   ```

3. **Common causes and fixes:**

   **a) Database connection failed:**
   ```bash
   # Check DATABASE_URL is set correctly
   kubectl get secret todo-list-backend-secret -o jsonpath='{.data}'
   ```

   **b) Missing environment variables:**
   ```yaml
   # Add to deployment.yaml
   env:
     - name: DATABASE_URL
       valueFrom:
         secretKeyRef:
           name: todo-list-backend-secret
           key: database-url
   ```

   **c) Port already in use:**
   ```bash
   # Check if port 8000 is available
   kubectl exec todo-list-backend-xxx -- netstat -tuln | grep 8000
   ```

### Issue: Pod stuck in ImagePullBackOff

**Symptoms:**
```bash
$ kubectl get pods
NAME                      READY   STATUS              RESTARTS   AGE
todo-list-backend-xxx     0/1     ImagePullBackOff    0          2m
```

**Solutions:**

1. **Verify image exists:**
   ```bash
   docker images | grep todo-list-backend
   ```

2. **Load image into Minikube:**
   ```bash
   minikube image load todo-list-backend:v1.0.0
   ```

3. **Check imagePullPolicy:**
   ```yaml
   # For local development, use:
   imagePullPolicy: Never
   # For production, use:
   imagePullPolicy: Always
   ```

4. **Verify image tag matches:**
   ```bash
   kubectl get deployment todo-list-backend -o jsonpath='{.spec.template.spec.containers[0].image}'
   ```

### Issue: Pod stuck in Pending state

**Symptoms:**
```bash
$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
todo-list-backend-xxx     0/1     Pending   0          5m
```

**Solutions:**

1. **Check pod events:**
   ```bash
   kubectl describe pod todo-list-backend-xxx | grep -A 10 Events
   ```

2. **Common causes:**

   **a) Insufficient resources:**
   ```bash
   # Check node resources
   kubectl top nodes
   kubectl describe node minikube
   ```

   **b) Node selector not matching:**
   ```bash
   # Check node labels
   kubectl get nodes --show-labels
   ```

   **c) Taints preventing scheduling:**
   ```bash
   # Check node taints
   kubectl describe node minikube | grep Taints
   ```

### Issue: Health probes failing

**Symptoms:**
```bash
$ kubectl describe pod todo-list-backend-xxx
Warning: Unhealthy Readiness probe failed: Get http://10.244.0.5:8000/health: dial tcp 10.244.0.5:8000: connect: connection refused
```

**Solutions:**

1. **Test health endpoint from within pod:**
   ```bash
   kubectl exec todo-list-backend-xxx -- curl http://localhost:8000/health
   ```

2. **Adjust probe timing:**
   ```yaml
   # Increase initialDelaySeconds
   readinessProbe:
     httpGet:
       path: /health
       port: 8000
     initialDelaySeconds: 30  # Increase from 10
     periodSeconds: 5
     timeoutSeconds: 3
     failureThreshold: 2
   ```

3. **Verify health endpoint exists:**
   ```bash
   kubectl exec todo-list-backend-xxx -- curl http://localhost:8000/health
   # Should return: {"status": "healthy"}
   ```

---

## Service Issues

### Issue: Service not routing traffic

**Symptoms:**
```bash
$ kubectl get svc todo-list-backend
NAME                 TYPE        CLUSTER-IP      PORT(S)
todo-list-backend    ClusterIP   10.96.123.45    8000/TCP

$ curl http://10.96.123.45:8000/health
curl: (7) Failed to connect to 10.96.123.45 port 8000: Connection refused
```

**Solutions:**

1. **Check service endpoints:**
   ```bash
   kubectl get endpoints todo-list-backend
   # Should show pod IPs
   ```

2. **Verify selector matches pods:**
   ```bash
   kubectl get pods --show-labels
   kubectl get svc todo-list-backend -o jsonpath='{.spec.selector}'
   ```

3. **Test pod directly:**
   ```bash
   kubectl port-forward todo-list-backend-xxx 8000:8000
   curl http://localhost:8000/health
   ```

### Issue: Service has no endpoints

**Symptoms:**
```bash
$ kubectl get endpoints todo-list-backend
NAME                 ENDPOINTS   AGE
todo-list-backend    <none>      5m
```

**Solutions:**

1. **Verify pod labels match service selector:**
   ```bash
   kubectl get pods -l app=backend
   kubectl get svc todo-list-backend -o yaml | grep selector -A 2
   ```

2. **Check pods are Ready:**
   ```bash
   kubectl get pods -l app=backend
   ```

3. **Verify service port:**
   ```yaml
   # Service port must match container port
   spec:
     ports:
       - port: 8000        # Service port
         targetPort: 8000   # Container port
   ```

---

## Helm Issues

### Issue: Helm install fails with "rendering template"

**Symptoms:**
```bash
$ helm install todo-list ./k8s/todo-list-hackathon
Error: execution error at (todo-list-hackathon/templates/deployment.yaml:42:10): Unexpected character
```

**Solutions:**

1. **Validate Helm syntax:**
   ```bash
   helm lint ./k8s/todo-list-hackathon
   ```

2. **Debug template rendering:**
   ```bash
   helm template todo-list ./k8s/todo-list-hackathon --debug
   ```

3. **Check YAML indentation:**
   ```yaml
   # Ensure correct indentation in templates
   spec:
     containers:
       - name: backend
         image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
   ```

### Issue: Helm upgrade fails

**Symptoms:**
```bash
$ helm upgrade todo-list ./k8s/todo-list-hackathon
Error: UPGRADE FAILED: another operation (install/upgrade/rollback) is in progress
```

**Solutions:**

1. **Check Helm release status:**
   ```bash
   helm status todo-list
   ```

2. **Wait for pending operations:**
   ```bash
   kubectl get deployments -l app.kubernetes.io/instance=todo-list
   ```

3. **Force rollback if stuck:**
   ```bash
   helm rollback todo-list
   ```

### Issue: Helm test fails

**Symptoms:**
```bash
$ helm test todo-list --logs
Pod todo-list-test-connection failed
```

**Solutions:**

1. **Check test pod logs:**
   ```bash
   kubectl logs todo-list-test-connection
   ```

2. **Verify test container image:**
   ```yaml
   # Ensure test image has curl
   spec:
     containers:
       - name: test
         image: busybox:latest  # or curlimages/curl:latest
         command:
           - sh
           - -c
           - |
             wget -O- http://backend:8000/health
   ```

---

## Networking Issues

### Issue: Frontend cannot connect to backend

**Symptoms:**
```bash
# Frontend logs
Failed to fetch: http://backend:8000/api/tasks
```

**Solutions:**

1. **Verify backend service exists:**
   ```bash
   kubectl get svc backend
   ```

2. **Test DNS resolution:**
   ```bash
   kubectl exec -it <frontend-pod> -- nslookup backend
   ```

3. **Test connectivity from frontend pod:**
   ```bash
   kubectl exec -it <frontend-pod> -- wget -O- http://backend:8000/health
   ```

4. **Check service is in same namespace:**
   ```bash
   kubectl get svc -A | grep backend
   ```

### Issue: Port forwarding not working

**Symptoms:**
```bash
$ kubectl port-forward svc/frontend 8080:80
error: unable to listen on port 8080: All listeners failed to bind
```

**Solutions:**

1. **Use different local port:**
   ```bash
   kubectl port-forward svc/frontend 9090:80
   ```

2. **Check if port is in use:**
   ```bash
   lsof -i :8080
   netstat -tuln | grep 8080
   ```

3. **Kill existing process:**
   ```bash
   kill -9 $(lsof -t -i:8080)
   ```

---

## Resource Issues

### Issue: Pod OOMKilled

**Symptoms:**
```bash
$ kubectl get pods
NAME                      READY   STATUS      RESTARTS   AGE
todo-list-backend-xxx     0/1     OOMKilled   3          5m
```

**Solutions:**

1. **Check pod memory usage:**
   ```bash
   kubectl top pod todo-list-backend-xxx --containers
   ```

2. **Increase memory limit:**
   ```yaml
   resources:
     limits:
       memory: 1Gi  # Increase from 512Mi
     requests:
       memory: 256Mi
   ```

3. **Profile application memory:**
   ```bash
   kubectl exec todo-list-backend-xxx -- python -m memory_profiler main.py
   ```

### Issue: Pod throttled due to CPU limits

**Symptoms:**
```bash
$ kubectl top pod todo-list-backend-xxx --containers
POD                      NAME    CPU(cores)    MEMORY(bytes)
todo-list-backend-xxx    backend 500m (100%)   256Mi
```

**Solutions:**

1. **Increase CPU limit:**
   ```yaml
   resources:
     limits:
       cpu: 1000m  # Increase from 500m
     requests:
       cpu: 200m
   ```

2. **Check CPU throttling:**
   ```bash
   kubectl describe pod todo-list-backend-xxx | grep throttling
   ```

---

## Authentication Issues

### Issue: JWT verification failing

**Symptoms:**
```bash
# Backend logs
ERROR: Invalid token signature
```

**Solutions:**

1. **Verify JWT_SECRET is set:**
   ```bash
   kubectl get secret todo-list-backend-secret -o jsonpath='{.data.JWT_SECRET}' | base64 -d
   ```

2. **Check frontend and backend use same secret:**
   ```yaml
   # Both must share the same JWT_SECRET
   ```

3. **Verify token is being sent:**
   ```bash
   kubectl logs <frontend-pod> | grep Authorization
   ```

### Issue: Database connection failing

**Symptoms:**
```bash
# Backend logs
ERROR: Connection refused to postgresql://...
```

**Solutions:**

1. **Verify DATABASE_URL:**
   ```bash
   kubectl get secret todo-list-backend-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d
   ```

2. **Test database connectivity:**
   ```bash
   kubectl exec todo-list-backend-xxx -- pg_isready -h <db-host> -p 5432
   ```

3. **Check Neon PostgreSQL status:**
   - Login to Neon console
   - Verify database is active
   - Check connection string

---

## Quick Diagnostic Commands

```bash
# Overall cluster status
kubectl cluster-info
kubectl top nodes
kubectl top pods -A

# Check all resources in namespace
kubectl get all -n todo-list

# Describe problematic resource
kubectl describe pod <pod-name>
kubectl describe svc <service-name>
kubectl describe deployment <deployment-name>

# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
kubectl logs -f <pod-name>  # Follow logs

# Port forwarding for testing
kubectl port-forward svc/backend 8000:8000
kubectl port-forward svc/frontend 8080:80

# Exec into pod for debugging
kubectl exec -it <pod-name> -- /bin/sh
kubectl exec -it <pod-name> -- /bin/bash

# Check events
kubectl get events -n todo-list --sort-by='.lastTimestamp'

# Resource usage
kubectl top pods -n todo-list
kubectl top nodes
```

---

## Getting Help

If issues persist:

1. **Check logs:**
   ```bash
   journalctl -u docker -n 100
   minikube logs
   kubectl logs -n kube-system
   ```

2. **Reset Minikube:**
   ```bash
   minikube delete
   minikube start --driver=docker
   ```

3. **Consult documentation:**
   - [Kubernetes Documentation](https://kubernetes.io/docs/)
   - [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
   - [Helm Documentation](https://helm.sh/docs/)

4. **Use AI DevOps tools:**
   - See `k8s/ai-devops.md` for kubectl-ai and kagent usage
