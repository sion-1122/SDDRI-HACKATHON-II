#!/bin/bash
# Frontend Docker Build Script
# Builds the frontend Next.js application as a Docker image with nginx

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

IMAGE_NAME="todo-list-frontend"
IMAGE_TAG="${1:-v1.0.0}"

echo "=========================================="
echo "Building Frontend Docker Image"
echo "=========================================="
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Frontend directory: ${FRONTEND_DIR}"
echo ""

# Check if Dockerfile exists
if [ ! -f "$FRONTEND_DIR/Dockerfile" ]; then
    echo "❌ ERROR: Dockerfile not found in ${FRONTEND_DIR}"
    exit 1
fi

# Build the image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest "$FRONTEND_DIR"

# Display image size
echo ""
echo "=========================================="
echo "✅ Build Complete!"
echo "=========================================="
docker images ${IMAGE_NAME}:${IMAGE_TAG} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo ""
echo "To run the container:"
echo "  docker run -p 8080:80 ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "To load into Minikube:"
echo "  minikube image load ${IMAGE_NAME}:${IMAGE_TAG}"
