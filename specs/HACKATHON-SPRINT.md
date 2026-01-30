# Hackathon Sprint Execution Plan
**All 4 Specs (008-011) in 2-6 Hours**

## Parallel Execution Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    HACKATHON TIMELINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HOUR 1-2: Infrastructure (Specs 009, 010)                      │
│  ├── Deploy Redpanda Kafka to Minikube                         │
│  ├── Deploy Redis for Dapr state store                         │
│  ├── Install Dapr on cluster                                   │
│  └── Verify all infrastructure is Ready                         │
│                                                                 │
│  HOUR 2-3: Backend Integration (Specs 009, 010)                 │
│  ├── Add Dapr sidecar annotations to deployments               │
│  ├── Configure Dapr components (pub/sub, state, cron)          │
│  ├── Refactor Chat API to use Dapr pub/sub                     │
│  └── Create reminder worker with Dapr subscriptions            │
│                                                                 │
│  HOUR 3-4: Frontend Features (Spec 008)                         │
│  ├── Add DatePicker to TaskForm (shadcn)                       │
│  ├── Add notification permission request                       │
│  ├── Add recurring task controls (daily/weekly)                │
│  └── Style overdue task indicators                             │
│                                                                 │
│  HOUR 4-5: Cloud Deployment (Spec 011)                          │
│  ├── Create cloud cluster (AKS/GKE/OKE)                        │
│  ├── Set up container registry                                 │
│  ├── Deploy all components to cloud                            │
│  └── Configure ingress and DNS                                 │
│                                                                 │
│  HOUR 5-6: Polish & Demo Prep                                   │
│  ├── Create GitHub Actions CI/CD                               │
│  ├── Deploy monitoring stack                                   │
│  ├── Test all features end-to-end                              │
│  └── Prepare demo script                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Critical Path - What Must Work

### Tier 1: Blocking (DO THESE FIRST)
1. **Kafka deployment** - All pub/sub depends on this
2. **Dapr installation** - All integrations depend on this
3. **Cloud cluster** - Final deployment depends on this

### Tier 2: Core Features
1. **Due dates UI** - Most visible advanced feature
2. **Reminder system** - Shows event-driven architecture
3. **Dapr pub/sub** - Shows modern architecture

### Tier 3: Nice to Have
1. **Recurring tasks** - If time permits
2. **Full CI/CD** - If time permits
3. **Monitoring dashboards** - If time permits

## Quick Start Commands

### 1. Infrastructure Setup (Hour 1)
```bash
# Start Minikube with more resources
minikube start --cpus=4 --memory=8192 --disk-size=50gb

# Install Redpanda Kafka
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda --namespace redpanda --create-namespace

# Install Redis
helm install redis bitnami/redis --set architecture=standalone

# Install Dapr
dapr init -k
dapr dashboard -p &

# Verify
kubectl get pods -A
```

### 2. Dapr Components (Hour 2)
```bash
# Apply Dapr components
kubectl apply -f k8s/dapr/components/

# Enable Dapr on deployments (add annotations)
kubectl patch deployment backend -p '{"spec":{"template":{"metadata":{"annotations":{"dapr.io/enabled":"true","dapr.io/app-id":"backend","dapr.io/app-port":"8000"}}}}}'
```

### 3. Cloud Cluster (Hour 4)
```bash
# Azure AKS example
az group create -n todo-hackathon -l eastus
az aks create -g todo-hackathon -n todo-cluster --node-count 3 --node-vm-size Standard_DS4_v2

# Get credentials
az aks get-credentials -g todo-hackathon -n todo-cluster

# Create ACR
az acr create -g todo-hackathon -n todohackathon --sku Basic
```

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cloud cluster takes too long | Deploy fails | Use Minikube, document cloud setup |
| Kafka/Dapr complexity | Integration fails | Fall back to direct implementation |
| Time runs out | Incomplete features | Prioritize Tier 1 & 2 only |
| Browser notifications blocked | Reminders don't work | Show in-app notifications instead |

## Demo Script (5 Minutes)

1. **Intro** (30s): "Our todo app with event-driven architecture"
2. **Create task** (1m): Show chatbot creating task with due date
3. **Kafka flow** (1m): Show event being published and consumed
4. **Dapr integration** (1m): Show state management persisting conversation
5. **Recurring task** (1m): Create recurring task, show auto-reschedule
6. **Cloud deployment** (30s): Show running on cloud cluster
7. **CI/CD** (30s): Show GitHub Actions running

## Minimum Viable Submission

If time runs critically short, the bare minimum for submission:

1. ✅ Specs 008-011 created (DONE)
2. ✅ Kafka deployed to Minikube
3. ✅ Due dates UI working
4. ✅ Dapr sidecars running
5. ✅ Cloud cluster created (even if not fully deployed)
6. ✅ Architecture diagrams

## Go/No-Go Decision Points

- **After Hour 2**: If Kafka/Dapr not working → Fall back to simpler implementation
- **After Hour 4**: If cloud cluster failing → Document cloud, deploy to Minikube
- **After Hour 5**: If time < 1 hour → Skip monitoring, focus on demo prep
