#!/bin/bash
# Backend Docker Build Script
# Builds the backend FastAPI application as a Docker image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

IMAGE_NAME="todo-list-backend"
IMAGE_TAG="${1:-v1.0.0}"

echo "=========================================="
echo "Building Backend Docker Image"
echo "=========================================="
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Backend directory: ${BACKEND_DIR}"
echo ""

# Check if Dockerfile exists
if [ ! -f "$BACKEND_DIR/Dockerfile" ]; then
    echo "❌ ERROR: Dockerfile not found in ${BACKEND_DIR}"
    exit 1
fi

# Build the image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest "$BACKEND_DIR"

# Display image size
echo ""
echo "=========================================="
echo "✅ Build Complete!"
echo "=========================================="
docker images ${IMAGE_NAME}:${IMAGE_TAG} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo ""
echo "To run the container:"
echo "  docker run -p 8000:8000 -e DATABASE_URL='postgresql://user:pass@host:5432/db' ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "To load into Minikube:"
echo "  minikube image load ${IMAGE_NAME}:${IMAGE_TAG}"
