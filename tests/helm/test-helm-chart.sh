#!/bin/bash
# Helm Chart Test Script
# Tests Helm chart installation, upgrade, rollback, and connectivity

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHART_DIR="$PROJECT_ROOT/k8s/todo-list-hackathon"
RELEASE_NAME="todo-list-test"
NAMESPACE="todo-list-test"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ $1${NC}"; }

# Cleanup function
cleanup() {
    print_info "Cleaning up test resources..."
    helm uninstall "$RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null || true
    kubectl delete namespace "$NAMESPACE" 2>/dev/null || true
}

# Set trap for cleanup
trap cleanup EXIT

print_info "Starting Helm Chart Test Suite"
echo "======================================"

# Test 1: Create namespace
print_info "Test 1: Creating test namespace..."
kubectl create namespace "$NAMESPACE" || kubectl get namespace "$NAMESPACE"
print_success "Namespace created/verified"

# Test 2: Helm lint
print_info "Test 2: Running helm lint..."
if helm lint "$CHART_DIR"; then
    print_success "Helm lint passed"
else
    print_error "Helm lint failed"
    exit 1
fi

# Test 3: Helm install
print_info "Test 3: Installing Helm chart..."
if helm install "$RELEASE_NAME" "$CHART_DIR" \
    -f "$CHART_DIR/values-local.yaml" \
    -n "$NAMESPACE" \
    --create-namespace \
    --wait \
    --timeout 5m; then
    print_success "Helm install passed"
else
    print_error "Helm install failed"
    exit 1
fi

# Test 4: Verify pods are running
print_info "Test 4: Verifying pods are ready..."
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/instance="$RELEASE_NAME" \
    -n "$NAMESPACE" \
    --timeout=120s
print_success "All pods are ready"

# Test 5: Verify services
print_info "Test 5: Verifying services..."
FRONTEND_SVC=$(kubectl get svc -n "$NAMESPACE" -l app=frontend -o name)
BACKEND_SVC=$(kubectl get svc -n "$NAMESPACE" -l app=backend -o name)

if [ -n "$FRONTEND_SVC" ] && [ -n "$BACKEND_SVC" ]; then
    print_success "Services created: $FRONTEND_SVC, $BACKEND_SVC"
else
    print_error "Services not found"
    exit 1
fi

# Test 6: Helm test (connectivity)
print_info "Test 6: Running Helm connectivity tests..."
if helm test "$RELEASE_NAME" -n "$NAMESPACE" --logs; then
    print_success "Helm connectivity tests passed"
else
    print_error "Helm connectivity tests failed"
    exit 1
fi

# Test 7: Helm upgrade
print_info "Test 7: Testing Helm upgrade..."
# Simulate upgrade by changing replica count
if helm upgrade "$RELEASE_NAME" "$CHART_DIR" \
    -f "$CHART_DIR/values-local.yaml" \
    --set frontend.replicaCount=2 \
    --set backend.replicaCount=2 \
    -n "$NAMESPACE" \
    --wait \
    --timeout 5m; then
    print_success "Helm upgrade passed"
else
    print_error "Helm upgrade failed"
    exit 1
fi

# Verify pods scaled up
print_info "Verifying scaled pods..."
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/instance="$RELEASE_NAME" \
    -n "$NAMESPACE" \
    --timeout=120s
print_success "Scaled pods are ready"

# Test 8: Helm rollback
print_info "Test 8: Testing Helm rollback..."
REVISION=$(helm history "$RELEASE_NAME" -n "$NAMESPACE" -o json | jq -r 'length')
if [ "$REVISION" -gt 1 ]; then
    if helm rollback "$RELEASE_NAME" -n "$NAMESPACE" --wait; then
        print_success "Helm rollback passed"
    else
        print_error "Helm rollback failed"
        exit 1
    fi
else
    print_info "Only one revision, skipping rollback test"
fi

# Test 9: Verify deployment status
print_info "Test 9: Verifying final deployment status..."
helm status "$RELEASE_NAME" -n "$NAMESPACE"
print_success "Deployment status verified"

echo "======================================"
print_success "All Helm chart tests passed!"
echo ""
print_info "Test Summary:"
echo "  - Namespace: $NAMESPACE"
echo "  - Release: $RELEASE_NAME"
echo "  - Chart: $CHART_DIR"
echo "  - All tests: PASSED"
