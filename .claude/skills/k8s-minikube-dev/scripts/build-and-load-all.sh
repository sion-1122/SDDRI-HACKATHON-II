#!/bin/bash
# Build both Docker images and load them into Minikube
# Usage: ./scripts/build-and-load-all.sh

set -e

echo "=== Building and Loading Docker Images to Minikube ==="

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

# Build frontend
echo "[1/4] Building frontend image..."
docker build -t todo-list-frontend:v1.0.1 ./frontend
echo "${GREEN}✓ Frontend image built${NC}"

# Build backend
echo "[2/4] Building backend image..."
docker build -t todo-list-backend:v1.0.0 ./backend
echo "${GREEN}✓ Backend image built${NC}"

# Load frontend to Minikube
echo "[3/4] Loading frontend image to Minikube..."
minikube image load todo-list-frontend:v1.0.1
echo "${GREEN}✓ Frontend image loaded${NC}"

# Load backend to Minikube
echo "[4/4] Loading backend image to Minikube..."
minikube image load todo-list-backend:v1.0.0
echo "${GREEN}✓ Backend image loaded${NC}"

echo ""
echo "${GREEN}=== All images built and loaded successfully ===${NC}"
echo ""
echo "Next steps:"
echo "  cd k8s/todo-list-hackathon"
echo "  helm upgrade todo-list . -f values-local.yaml --namespace todo-list"
