#!/bin/bash
# Deploy the Todo List application to Minikube using Helm
# Usage: ./scripts/deploy-all.sh

set -e

echo "=== Deploying Todo List to Minikube ==="

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

# Change to Helm chart directory
cd "$(dirname "$0")/../k8s/todo-list-hackathon"

# Install or upgrade Helm release
echo "[1/2] Installing/upgrading Helm release..."
if helm status todo-list -n todo-list >/dev/null 2>&1; then
    helm upgrade todo-list . --set frontend.image.tag=v1.0.1 -f values-local.yaml --namespace todo-list
    echo "${GREEN}✓ Helm release upgraded${NC}"
else
    helm install todo-list . --set frontend.image.tag=v1.0.1 -f values-local.yaml --namespace todo-list --create-namespace
    echo "${GREEN}✓ Helm release installed${NC}"
fi

# Wait for pods to be ready
echo "[2/2] Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n todo-list --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend -n todo-list --timeout=120s
echo "${GREEN}✓ All pods are ready${NC}"

echo ""
echo "${GREEN}=== Deployment successful ===${NC}"
echo ""
echo "To access the application:"
echo "  minikube service -n todo-list todo-list-todo-list-hackathon-frontend --url"
echo ""
echo "To run Helm tests:"
echo "  helm test todo-list --namespace todo-list --logs"
