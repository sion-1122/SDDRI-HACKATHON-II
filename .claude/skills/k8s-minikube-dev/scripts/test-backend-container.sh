#!/bin/bash
# Test backend container - build, run, and health check

set -e

echo "=== Backend Container Test ==="

# Variables
IMAGE_NAME="todo-list-backend:v1.0.0"
CONTAINER_NAME="test-backend-$$"
HEALTH_URL="http://localhost:8000/health"
TIMEOUT=30

# Step 1: Check if image exists
echo "[1/5] Checking if image exists..."
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "❌ FAIL: Image $IMAGE_NAME not found"
    echo "Run: docker build -t $IMAGE_NAME ./backend"
    exit 1
fi
echo "✅ Image found"

# Step 2: Start container with test environment
echo "[2/5] Starting container..."
docker run -d --name "$CONTAINER_NAME" \
    -p 8000:8000 \
    -e DATABASE_URL="sqlite:////tmp/test.db" \
    -e JWT_SECRET="test-secret-for-container-testing" \
    -e OPENAI_API_KEY="sk-test-key-for-container-testing" \
    -e FRONTEND_URL="http://localhost:3000" \
    "$IMAGE_NAME" >/dev/null 2>&1 || {
    echo "❌ FAIL: Failed to start container"
    exit 1
}
echo "✅ Container started: $CONTAINER_NAME"

# Step 3: Wait for container to be healthy
echo "[3/5] Waiting for container to be healthy (max ${TIMEOUT}s)..."
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

# Step 4: Check health endpoint response
echo "[4/5] Checking health endpoint response..."
HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" 2>/dev/null || echo "{}")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health endpoint responding: $HEALTH_RESPONSE"
else
    echo "⚠️  Health endpoint response: $HEALTH_RESPONSE"
fi

# Step 5: Check container health status
echo "[5/5] Checking container health status..."
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
echo "=== Backend Container Test: PASSED ==="
