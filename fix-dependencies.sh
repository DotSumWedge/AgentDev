#!/bin/bash

# Fix Dependencies Script
# Resolves the FastAPI version conflict and rebuilds the container

set -e

echo "🔧 Fixing dependency conflicts..."
echo "=================================="

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker compose down

# Remove existing images to force rebuild
echo "🗑️  Removing existing images..."
docker compose down --rmi local 2>/dev/null || true

# Clean up any dangling images
echo "🧹 Cleaning up Docker cache..."
docker system prune -f

# Rebuild with no cache to ensure fresh dependencies
echo "🔨 Rebuilding container with fixed dependencies..."
docker compose build --no-cache adk-dev

# Start the container
echo "🚀 Starting container..."
docker compose up -d adk-dev

# Wait for startup
echo "⏳ Waiting for container to initialize..."
sleep 15

# Test the container
echo "🧪 Testing container health..."
if docker compose exec adk-dev python health_check.py; then
    echo "✅ Container is now working properly!"
    echo ""
    echo "🎉 Dependency conflict resolved!"
    echo "==============================="
    echo ""
    echo "You can now continue with:"
    echo "  - docker compose exec adk-dev bash"
    echo "  - docker compose exec adk-dev python /app/src/agents/sample_agent.py"
    echo ""
else
    echo "❌ Container health check still failing..."
    echo "Let's check what's happening:"
    docker compose logs adk-dev
    exit 1
fi