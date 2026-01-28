# Helm Conventions

## Chart Structure

```
<chart-name>/
├── Chart.yaml
├── values.yaml
├── values-local.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    └── tests/
        └── test-connection.yaml
```

## Commands

```bash
helm lint
helm install <release> . -f values-local.yaml -n <namespace> --create-namespace
helm upgrade <release> . -f values-local.yaml -n <namespace>
helm rollback <release> -n <namespace>
helm test <release> -n <namespace> --logs
```

## Naming

- Chart: `<project>-<app>`
- Release: `<namespace>` or simple name
- Service: `<release>-<chart-name>-<service>`
