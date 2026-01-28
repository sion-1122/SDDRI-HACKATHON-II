#!/bin/bash
# Cleanup Minikube deployment by uninstalling Helm release and optionally stopping Minikube
# Usage: ./scripts/cleanup.sh [--stop-minikube]

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

STOP_MINIKUBE=false
if [ "$1" = "--stop-minikube" ]; then
    STOP_MINIKUBE=true
fi

echo "=== Cleaning up Todo List Deployment ==="

# Uninstall Helm release
echo "[1/3] Uninstalling Helm release..."
if helm status todo-list -n todo-list >/dev/null 2>&1; then
    helm uninstall todo-list -n todo-list
    echo "${GREEN}✓ Helm release uninstalled${NC}"
else
    echo "Helm release not found, skipping..."
fi

# Delete namespace
echo "[2/3] Deleting namespace..."
if kubectl get namespace todo-list >/dev/null 2>&1; then
    kubectl delete namespace todo-list
    echo "${GREEN}✓ Namespace deleted${NC}"
else
    echo "Namespace not found, skipping..."
fi

# Optionally stop Minikube
if [ "$STOP_MINIKUBE" = true ]; then
    echo "[3/3] Stopping Minikube..."
    minikube stop
    echo "${GREEN}✓ Minikube stopped${NC}"
else
    echo "[3/3] Minikube left running (use --stop-minikube flag to stop)"
fi

echo ""
echo "${GREEN}=== Cleanup complete ===${NC}"
echo ""
echo "To start fresh:"
echo "  ./scripts/build-and-load-all.sh"
echo "  ./scripts/deploy-all.sh"
