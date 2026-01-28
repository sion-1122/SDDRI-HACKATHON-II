# todo-list-hackathon

A Helm chart for deploying the Todo List Hackathon application on Kubernetes.

## Introduction

This chart bootstraps a [Todo List Hackathon](https://github.com/GrowWidTalha/todo-list-hackathon) deployment on a [Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure

## Installing the Chart

To install the chart with the release name `todo-list` in namespace `todo-list`:

```bash
helm install todo-list . -f values-local.yaml --namespace todo-list --create-namespace
```

## Uninstalling the Chart

To uninstall/delete the `todo-list` deployment:

```bash
helm uninstall todo-list --namespace todo-list
```

## Upgrading the Chart

To upgrade the `todo-list` release:

```bash
helm upgrade todo-list . -f values-local.yaml --namespace todo-list
```

## Rollback

To rollback to a previous revision:

```bash
helm rollback todo-list --namespace todo-list
```

## Configuration

The following table lists the configurable parameters of the todo-list-hackathon chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.replicaCount` | Number of frontend replicas | `2` |
| `frontend.image.repository` | Frontend image repository | `todo-list-frontend` |
| `frontend.image.tag` | Frontend image tag | `v1.0.0` |
| `frontend.image.pullPolicy` | Frontend image pull policy | `IfNotPresent` |
| `frontend.service.port` | Frontend service port | `80` |
| `frontend.resources` | Frontend resource requests/limits | `{}` |
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.replicaCount` | Number of backend replicas | `2` |
| `backend.image.repository` | Backend image repository | `todo-list-backend` |
| `backend.image.tag` | Backend image tag | `v1.0.0` |
| `backend.image.pullPolicy` | Backend image pull policy | `IfNotPresent` |
| `backend.service.port` | Backend service port | `8000` |
| `backend.resources` | Backend resource requests/limits | `{}` |
| `backend.env.databaseUrl` | Database connection string | `postgresql://...` |
| `backend.env.jwtSecret` | JWT secret for authentication | `change-me` |
| `backend.env.openaiApiKey` | OpenAI API key | `sk-...` |
| `backend.env.frontendUrl` | Frontend URL for CORS | `http://localhost:3000` |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example:

```bash
helm install todo-list . --set frontend.replicaCount=3
```

Alternatively, a YAML file that specifies the values for the above parameters can be provided while installing the chart. For example:

```bash
helm install todo-list . -f values-local.yaml
```

## Values Files

### values.yaml

Default values for production deployment.

### values-local.yaml

Override values for local Minikube development with minimal resources and local image loading.

### values-production.yaml

Override values for production with higher resource limits and strict security settings.

## Accessing the Application

After installation, use port-forwarding to access the application:

```bash
# Forward frontend to localhost:8080
kubectl port-forward -n todo-list svc/todo-list-frontend 8080:80

# Open browser
open http://localhost:8080
```

## Testing

Run Helm tests to verify deployment:

```bash
helm test todo-list --namespace todo-list --logs
```
