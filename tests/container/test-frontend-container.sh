#!/bin/bash
# Test frontend container - build, run, and health check

set -e

echo "=== Frontend Container Test ==="

# Variables
IMAGE_NAME="todo-list-frontend:v1.0.0"
CONTAINER_NAME="test-frontend-$$"
HEALTH_URL="http://localhost:8080"
TIMEOUT=30

# Step 1: Check if image exists
echo "[1/4] Checking if image exists..."
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "❌ FAIL: Image $IMAGE_NAME not found"
    echo "Run: docker build -t $IMAGE_NAME ./frontend"
    exit 1
fi
echo "✅ Image found"

# Step 2: Start container
echo "[2/4] Starting container..."
docker run -d --name "$CONTAINER_NAME" -p 8080:80 "$IMAGE_NAME" >/dev/null 2>&1 || {
    echo "❌ FAIL: Failed to start container"
    exit 1
}
echo "✅ Container started: $CONTAINER_NAME"

# Step 3: Wait for container to be healthy
echo "[3/4] Waiting for container to be healthy (max ${TIMEOUT}s)..."
for i in $(seq 1 $TIMEOUT); do
    if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
        echo "✅ Container is healthy after ${i}s"
        break
    fi
    if [ $i -eq $TIMEOUT ]; then
        echo "❌ FAIL: Container not healthy after ${TIMEOUT}s"
        docker logs "$CONTAINER_NAME" 2>&1 || true
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
        exit 1
    fi
    sleep 1
done

# Step 4: Check container health status
echo "[4/4] Checking container health status..."
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")
if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ Container health status: $HEALTH_STATUS"
else
    echo "⚠️  Container health status: $HEALTH_STATUS (might be still starting)"
fi

# Cleanup
echo ""
echo "Cleaning up..."
docker stop "$CONTAINER_NAME" >/dev/null 2>&1
docker rm "$CONTAINER_NAME" >/dev/null 2>&1
echo "✅ Cleanup complete"

echo ""
echo "=== Frontend Container Test: PASSED ==="
