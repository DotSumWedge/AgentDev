#!/bin/bash

# Phase 1: Basic Development Container Setup Script
set -e

echo "🚀 Setting up AI Agent Development Environment - Phase 1"
echo "========================================================"

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker Engine 24.0+"
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose v2 is not available. Please install Docker Compose v2.20+"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        echo "❌ Docker daemon is not running. Please start Docker"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Create project structure
create_structure() {
    echo "📁 Creating project structure..."
    
    # Create directories
    mkdir -p src/{agents,utils,config}
    mkdir -p logs
    mkdir -p data
    mkdir -p config
    mkdir -p tests
    
    # Create initial source files
    cat > src/__init__.py << 'EOF'
"""AI Agent Development Environment"""
__version__ = "0.1.0"
EOF

    cat > src/agents/__init__.py << 'EOF'
"""Agent implementations"""
EOF

    cat > src/utils/__init__.py << 'EOF'
"""Utility functions"""
EOF

    # Create a sample agent for testing
    cat > src/agents/sample_agent.py << 'EOF'
"""Sample agent for testing the development environment."""

try:
    import google_adk
    print("✅ Google ADK is available")
except ImportError:
    print("❌ Google ADK not found")

class SampleAgent:
    """A basic agent for testing."""
    
    def __init__(self, name="SampleAgent"):
        self.name = name
        print(f"Agent {self.name} initialized")
    
    def greet(self):
        return f"Hello from {self.name}!"

if __name__ == "__main__":
    agent = SampleAgent()
    print(agent.greet())
EOF

    # Create environment template
    cat > .env.template << 'EOF'
# Phase 1: Basic Configuration
DEV_MODE=true
LOG_LEVEL=DEBUG

# Phase 2: LLM Backend Configuration (choose one)
LLM_PROVIDER=lm_studio
# LLM_PROVIDER=openai
# LLM_PROVIDER=google
# LLM_PROVIDER=ollama

# LM Studio Configuration
LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1

# Cloud API Configuration (uncomment as needed)
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_API_KEY=your_google_key_here

# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434/v1
EOF

    echo "✅ Project structure created"
}

# Build and test container
build_container() {
    echo "🔨 Building development container..."
    
    # Build the container
    docker compose build adk-dev
    
    echo "✅ Container built successfully"
}

# Test the container
test_container() {
    echo "🧪 Testing container functionality..."
    
    # Start the container
    docker compose up -d adk-dev
    
    # Wait for container to be ready
    echo "⏳ Waiting for container to be ready..."
    sleep 10
    
    # Run health check
    if docker compose exec adk-dev python health_check.py; then
        echo "✅ Container health check passed"
    else
        echo "❌ Container health check failed"
        docker compose logs adk-dev
        exit 1
    fi
    
    # Test Google ADK import
    echo "🔍 Testing Google ADK availability..."
    if docker compose exec adk-dev python -c "import google_adk; print('Google ADK imported successfully')"; then
        echo "✅ Google ADK test passed"
    else
        echo "⚠️  Google ADK test failed - this is expected if google-adk package doesn't exist yet"
        echo "    The container is still functional for development"
    fi
    
    # Test sample agent
    echo "🤖 Testing sample agent..."
    docker compose exec adk-dev python /app/src/agents/sample_agent.py
    
    echo "✅ All tests completed"
}

# Main setup process
main() {
    check_prerequisites
    create_structure
    build_container
    test_container
    
    echo ""
    echo "🎉 Phase 1 Setup Complete!"
    echo "=========================="
    echo ""
    echo "Your development environment is ready. Here's what you can do:"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Access the container: docker compose exec adk-dev bash"
    echo "  2. Run Python interactively: docker compose exec adk-dev python"
    echo "  3. Test the sample agent: docker compose exec adk-dev python /app/src/agents/sample_agent.py"
    echo "  4. View logs: docker compose logs adk-dev"
    echo "  5. Stop environment: docker compose down"
    echo ""
    echo "📁 Project Structure:"
    echo "  - src/: Your source code (mounted in container)"
    echo "  - logs/: Application logs"  
    echo "  - data/: Persistent data storage"
    echo "  - config/: Configuration files"
    echo ""
    echo "🔧 Container Management:"
    echo "  - Start: docker compose up -d"
    echo "  - Stop: docker compose down" 
    echo "  - Rebuild: docker compose build adk-dev"
    echo "  - Shell access: docker compose exec adk-dev bash"
    echo ""
    echo "Ready for Phase 2! 🚀"
}

# Run with error handling
if ! main; then
    echo "❌ Setup failed. Check the error messages above."
    echo "💡 Try running: docker compose down && docker compose build --no-cache"
    exit 1
fi