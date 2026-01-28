# Kubernetes Patterns

## Resource Limits

**Development (Minikube):**
```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
```

## Health Probes

**Next.js Frontend:**
```yaml
livenessProbe:
  httpGet:
    path: /
    port: http
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /
    port: http
  failureThreshold: 30
  periodSeconds: 5
```

**FastAPI Backend:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: http
```

## Common Issues

- **Image pull errors:** Run `minikube image load <name>:<tag>`
- **CrashLoopBackOff:** Check logs for app errors
- **OOMKilled:** Increase `resources.limits.memory`
- **Startup probe failed:** Increase `failureThreshold` or `periodSeconds`
