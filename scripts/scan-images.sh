#!/bin/bash
# Container Security Scanning Script
# Scans Docker images for vulnerabilities using Trivy and Docker Scout

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

# Image names
FRONTEND_IMAGE="todo-list-frontend"
BACKEND_IMAGE="todo-list-backend"
IMAGE_TAG="${1:-v1.0.0}"

# Check if Trivy is installed
check_trivy() {
    if ! command -v trivy &> /dev/null; then
        print_warning "Trivy not found. Installing..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
            echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
            sudo apt-get update
            sudo apt-get install trivy -y
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install trivy
        else
            print_error "Unsupported OS. Please install Trivy manually: https://aquasecurity.github.io/trivy/"
            exit 1
        fi
        print_success "Trivy installed"
    fi
}

# Check if Docker Scout is available (Docker Desktop feature)
check_docker_scout() {
    if docker scout 2>/dev/null | grep -q "scout"; then
        return 0
    else
        return 1
    fi
}

# Scan image with Trivy
scan_trivy() {
    local image=$1
    local severity="${2:-CRITICAL,HIGH}"

    print_info "Scanning $image with Trivy (severity: $severity)..."

    if trivy image --severity "$severity" --exit-code 1 --no-progress "$image:$IMAGE_TAG"; then
        print_success "$image: No $severity vulnerabilities found"
        return 0
    else
        print_error "$image: Vulnerabilities detected!"
        return 1
    fi
}

# Scan image with Docker Scout
scan_docker_scout() {
    local image=$1

    print_info "Scanning $image with Docker Scout..."

    if docker scout cves "$image:$IMAGE_TAG"; then
        print_success "$image: Docker Scout scan completed"
        return 0
    else
        print_warning "$image: Docker Scout found issues"
        return 1
    fi
}

# Full vulnerability report
full_report() {
    local image=$1

    print_info "Generating full vulnerability report for $image..."

    trivy image "$image:$IMAGE_TAG" \
        --format json \
        --output "$SCRIPT_DIR/../reports/${image}-scan-report.json" \
        --severity CRITICAL,HIGH,MEDIUM

    print_success "Report saved to reports/${image}-scan-report.json"
}

# Generate HTML report
generate_html_report() {
    local image=$1

    print_info "Generating HTML report for $image..."

    trivy image "$image:$IMAGE_TAG" \
        --format template \
        --template "@contrib/html.tpl" \
        --output "$SCRIPT_DIR/../reports/${image}-scan-report.html" \
        --severity CRITICAL,HIGH,MEDIUM

    print_success "HTML report saved to reports/${image}-scan-report.html"
}

# Create reports directory
mkdir -p "$PROJECT_ROOT/reports"

print_info "Starting Container Security Scan"
echo "======================================"

# Check for scanning tools
check_trivy

if check_docker_scout; then
    print_success "Docker Scout available"
    USE_DOCKER_SCOUT=true
else
    print_warning "Docker Scout not available. Using Trivy only."
    USE_DOCKER_SCOUT=false
fi

# Check if images exist
print_info "Checking if images exist..."
if ! docker image inspect "$FRONTEND_IMAGE:$IMAGE_TAG" &> /dev/null; then
    print_error "Frontend image $FRONTEND_IMAGE:$IMAGE_TAG not found"
    print_info "Build it with: docker build -t $FRONTEND_IMAGE:$IMAGE_TAG ./frontend"
    exit 1
fi

if ! docker image inspect "$BACKEND_IMAGE:$IMAGE_TAG" &> /dev/null; then
    print_error "Backend image $BACKEND_IMAGE:$IMAGE_TAG not found"
    print_info "Build it with: docker build -t $BACKEND_IMAGE:$IMAGE_TAG ./backend"
    exit 1
fi

print_success "All images found"

# Scan frontend
echo ""
print_info "Scanning Frontend Image..."
echo "------------------------------"

SCAN_FRONTEND_FAILED=0

if scan_trivy "$FRONTEND_IMAGE" "CRITICAL,HIGH"; then
    :
else
    SCAN_FRONTEND_FAILED=1
fi

if [ "$USE_DOCKER_SCOUT" = true ]; then
    scan_docker_scout "$FRONTEND_IMAGE" || true
fi

# Scan backend
echo ""
print_info "Scanning Backend Image..."
echo "------------------------------"

SCAN_BACKEND_FAILED=0

if scan_trivy "$BACKEND_IMAGE" "CRITICAL,HIGH"; then
    :
else
    SCAN_BACKEND_FAILED=1
fi

if [ "$USE_DOCKER_SCOUT" = true ]; then
    scan_docker_scout "$BACKEND_IMAGE" || true
fi

# Generate reports
echo ""
print_info "Generating Vulnerability Reports..."
echo "----------------------------------------"

full_report "$FRONTEND_IMAGE"
full_report "$BACKEND_IMAGE"

generate_html_report "$FRONTEND_IMAGE"
generate_html_report "$BACKEND_IMAGE"

# Summary
echo ""
echo "======================================"
print_info "Scan Summary"

if [ $SCAN_FRONTEND_FAILED -eq 0 ] && [ $SCAN_BACKEND_FAILED -eq 0 ]; then
    print_success "All images passed security scan!"
    echo ""
    echo "📊 Reports available in:"
    echo "   - $PROJECT_ROOT/reports/${FRONTEND_IMAGE}-scan-report.html"
    echo "   - $PROJECT_ROOT/reports/${BACKEND_IMAGE}-scan-report.html"
    echo "   - $PROJECT_ROOT/reports/${FRONTEND_IMAGE}-scan-report.json"
    echo "   - $PROJECT_ROOT/reports/${BACKEND_IMAGE}-scan-report.json"
    exit 0
else
    print_error "Security scan found vulnerabilities!"
    echo ""
    echo "Review the reports for details:"
    if [ $SCAN_FRONTEND_FAILED -eq 1 ]; then
        echo "   - $PROJECT_ROOT/reports/${FRONTEND_IMAGE}-scan-report.html"
    fi
    if [ $SCAN_BACKEND_FAILED -eq 1 ]; then
        echo "   - $PROJECT_ROOT/reports/${BACKEND_IMAGE}-scan-report.html"
    fi
    echo ""
    echo "Recommendations:"
    echo "  1. Update base images to latest versions"
    echo "  2. Update dependencies (npm, pip)"
    echo "  3. Review and fix identified vulnerabilities"
    echo "  4. Re-scan after fixes"
    exit 1
fi
