# Context for Directory: `C:\Projects\AgentBuildingFramework`

---

**File:** `.env.template`

```template
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
```

---

**File:** `compile_context.py`

```py
import os
import argparse
from pathlib import Path

# --- Configuration ---
# Add directories or files you want to ignore by default.
# This helps keep the context file clean and focused.
DEFAULT_IGNORE_PATTERNS = [
    '.git',
    '__pycache__',
    'node_modules',
    '.vscode',
    '.idea',
    'dist',
    'build',
    '.DS_Store',
    '*.pyc',
    '*.swp',
    '*.env'
]
# -------------------

def should_ignore(path, ignore_patterns):
    """Check if a file or directory path matches any of the ignore patterns."""
    path_parts = path.parts
    for pattern in ignore_patterns:
        # Check for direct name match in any part of the path (e.g., '.git')
        if pattern in path_parts:
            return True
        # Check for glob patterns (e.g., '*.pyc')
        if any(part.endswith(pattern.strip('*')) for part in path_parts if pattern.startswith('*')):
            return True
    return False


def create_context_file(directory_path, output_file, use_ignore_list=True):
    """
    Walks through a directory, reads all non-ignored files, and writes their
    paths and contents to a single Markdown file.
    """
    input_path = Path(directory_path)
    if not input_path.is_dir():
        print(f"Error: The path '{directory_path}' is not a valid directory.")
        return

    ignore_list = DEFAULT_IGNORE_PATTERNS if use_ignore_list else []
    
    try:
        with open(output_file, 'w', encoding='utf-8', errors='ignore') as md_file:
            md_file.write(f"# Context for Directory: `{input_path.resolve()}`\n\n")

            # Using Path.rglob for a more Pythonic way to traverse files
            for file_path in sorted(input_path.rglob('*')):
                if file_path.is_file():
                    relative_path = file_path.relative_to(input_path)
                    
                    if use_ignore_list and should_ignore(relative_path, ignore_list):
                        print(f"Ignoring: {relative_path}")
                        continue

                    print(f"Processing: {relative_path}")
                    
                    md_file.write(f"---\n\n")
                    md_file.write(f"**File:** `{relative_path}`\n\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                            content = f_in.read()
                            # Use a language hint based on file extension for better syntax highlighting
                            lang = file_path.suffix.lstrip('.')
                            md_file.write(f"```{lang}\n")
                            md_file.write(content.strip())
                            md_file.write(f"\n```\n\n")
                    except Exception:
                        # This will catch binary files or other read errors
                        md_file.write("```\n")
                        md_file.write("[Could not read file content (e.g., binary file, permission error)]")
                        md_file.write("\n```\n\n")

        print(f"\n✅ Success! All context has been compiled into '{output_file}'")

    except IOError as e:
        print(f"Error: Could not write to the file '{output_file}'. Reason: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Compile all file contents in a directory into a single Markdown file for context.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'directory_path',
        help="The path to the directory you want to process."
    )
    parser.add_argument(
        '-o', '--output',
        default='directory_context.md',
        help="The name of the output Markdown file. (default: directory_context.md)"
    )
    parser.add_argument(
        '--no-ignore',
        action='store_false',
        dest='use_ignore_list',
        help="Include all files, even those in the default ignore list (like .git, node_modules, etc.)."
    )
    
    args = parser.parse_args()
    
    create_context_file(args.directory_path, args.output, args.use_ignore_list)

if __name__ == '__main__':
    main()
```

---

**File:** `directory_context.md`

```md

```

---

**File:** `docker-compose.yml`

```yml
services:
  # Phase 1: Basic ADK Development Container
  adk-dev:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: adk-dev-container
    ports:
      - "8000:8000"  # Development server
      - "8001:8001"  # Additional service port
    volumes:
      - ./src:/app/src:rw           # Source code mounting
      - ./logs:/app/logs:rw         # Log files
      - ./data:/app/data:rw         # Data persistence
      - ./config:/app/config:ro     # Configuration files
    environment:
      - PYTHONPATH=/app
      - DEV_MODE=true
      - LOG_LEVEL=DEBUG
    networks:
      - adk-network
    restart: unless-stopped
    stdin_open: true    # Keep STDIN open for interactive use
    tty: true          # Allocate a pseudo-TTY

  # Phase 3: SQLite Database (for later phases)
  database:
    image: alpine:latest
    container_name: adk-database
    volumes:
      - agent_data:/data
    command: |
      sh -c "
        apk add --no-cache sqlite &&
        mkdir -p /data &&
        sqlite3 /data/agents.db 'CREATE TABLE IF NOT EXISTS agent_state (
          id TEXT PRIMARY KEY,
          data TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );' &&
        tail -f /dev/null
      "
    networks:
      - adk-network
    profiles:
      - full-dev
    restart: unless-stopped

  # Phase 2C: Ollama Container (Alternative LLM Backend)
  ollama:
    image: ollama/ollama:latest
    container_name: adk-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    networks:
      - adk-network
    profiles:
      - ollama
      - full-dev
    restart: unless-stopped

volumes:
  agent_data:
    driver: local
  ollama_models:
    driver: local

networks:
  adk-network:
    driver: bridge
    name: adk-development
```

---

**File:** `Dockerfile`

```
# Phase 1: Basic Development Container
FROM python:3.11-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV DEV_MODE=true
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/src /app/logs /app/data && \
    chown -R appuser:appuser /app

# Copy health check script
COPY health_check.py .

# Switch to non-root user
USER appuser

# Expose port for development server
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python health_check.py

# Default command
CMD ["python", "-m", "http.server", "8000", "--directory", "/app"]
```

---

**File:** `fix-dependencies.sh`

```sh
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
```

---

**File:** `health_check.py`

```py
#!/usr/bin/env python3
"""
Health check script for the ADK development container.
Tests basic functionality and dependency availability.
"""

import sys
import os
from pathlib import Path

def check_environment():
    """Check environment variables and paths."""
    required_env = ['PYTHONPATH', 'DEV_MODE']
    missing = [var for var in required_env if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_dependencies():
    """Check if critical dependencies can be imported."""
    # Check Google Generative AI SDK
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI SDK imported successfully")
    except ImportError as e:
        print(f"❌ Could not import Google Generative AI SDK: {e}")
        print("   -> Make sure 'google-generativeai' is in requirements.txt")
        return Falset
    
    # Check essential development tools
    try:
        import pytest
        import black
        import mypy
        import requests
        print("✅ Development tools available")
    except ImportError as e:
        print(f"❌ Missing development tools: {e}")
        return False
    
    # Check web framework tools
    try:
        import fastapi
        import uvicorn
        print("✅ Web framework tools available")
    except ImportError as e:
        print(f"❌ Missing web framework tools: {e}")
        return False
    
    return True

def check_directories():
    """Check if required directories exist."""
    required_dirs = ['/app/src', '/app/logs', '/app/data']
    
    for directory in required_dirs:
        if not Path(directory).exists():
            print(f"❌ Missing directory: {directory}")
            return False
    
    print("✅ Required directories exist")
    return True

def check_permissions():
    """Check if we have proper write permissions."""
    test_file = Path('/app/test_write.tmp')
    
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Write permissions verified")
        return True
    except Exception as e:
        print(f"❌ Write permission test failed: {e}")
        return False

def main():
    """Run all health checks."""
    print("🔍 Running container health checks...")
    
    checks = [
        check_environment,
        check_dependencies, 
        check_directories,
        check_permissions
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    if all_passed:
        print("\n✅ All health checks passed - container is ready!")
        sys.exit(0)
    else:
        print("\n❌ Some health checks failed - container needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

**File:** `README.md`

```md
# AI Agent Development Environment - Phase 1

This is **Phase 1** of the AI Agent Development Environment setup. This phase establishes the basic containerized development environment with Google ADK support.

## 🎯 Phase 1 Goals

- ✅ Working Python development environment with ADK
- ✅ Containerized setup with Docker
- ✅ Source code mounting for live development
- ✅ Basic health checks and testing
- ✅ Development tools (pytest, black, mypy)

## 📋 Prerequisites

- Docker Engine 24.0+
- Docker Compose v2.20+
- Git
- 8GB RAM minimum, 16GB recommended
- 20GB free disk space

## 🚀 Quick Start

### 1. Setup Phase 1

```bash
# Make the setup script executable
chmod +x setup-phase1.sh

# Run the automated setup
./setup-phase1.sh
```

### 2. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create project structure
mkdir -p src/{agents,utils,config} logs data config tests

# Build the container
docker compose build adk-dev

# Start the environment
docker compose up -d adk-dev

# Test the setup
docker compose exec adk-dev python health_check.py
```

## 🔧 Usage

### Access the Development Environment

```bash
# Enter the container shell
docker compose exec adk-dev bash

# Run Python interactively
docker compose exec adk-dev python

# Run the sample agent
docker compose exec adk-dev python /app/src/agents/sample_agent.py
```

### Development Workflow

```bash
# Start the environment
docker compose up -d

# Edit code in ./src/ (changes are live-mounted)
# Test your changes
docker compose exec adk-dev python /app/src/your_script.py

# Run tests
docker compose exec adk-dev pytest /app/tests/

# Format code
docker compose exec adk-dev black /app/src/

# Type checking
docker compose exec adk-dev mypy /app/src/

# Stop the environment
docker compose down
```

## 📁 Project Structure

```
ai-agent-dev/
├── Dockerfile                 # Container definition
├── docker-compose.yml        # Service orchestration
├── requirements.txt          # Python dependencies
├── health_check.py           # Container health validation
├── setup-phase1.sh          # Automated setup script
├── test-phase1.py           # Test suite
├── .env.template            # Environment configuration template
├── src/                     # Your source code (mounted)
│   ├── agents/              # Agent implementations
│   ├── utils/               # Utility functions
│   └── config/              # Configuration modules
├── logs/                    # Application logs (mounted)
├── data/                    # Persistent data (mounted)
├── config/                  # Configuration files (mounted)
└── tests/                   # Test files
```

## 🧪 Testing

### Run the Test Suite

```bash
# Run comprehensive tests
python test-phase1.py

# Run individual container tests
docker compose exec adk-dev python health_check.py
```

### Manual Testing

```bash
# Test Google ADK (may fail if package doesn't exist yet)
docker compose exec adk-dev python -c "import google_adk; print('Success')"

# Test development tools
docker compose exec adk-dev python -c "import pytest, black, mypy; print('Tools OK')"

# Test file mounting
echo "print('Hello from mounted code!')" > src/test.py
docker compose exec adk-dev python /app/src/test.py
```

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs adk-dev

# Rebuild container
docker compose down
docker compose build --no-cache adk-dev
docker compose up -d adk-dev
```

### Health Check Fails

```bash
# Debug health check
docker compose exec adk-dev python health_check.py

# Check environment
docker compose exec adk-dev env | grep -E "(PYTHONPATH|DEV_MODE)"

# Verify directories
docker compose exec adk-dev ls -la /app/
```

### Permission Issues

```bash
# Check file permissions
ls -la src/ logs/ data/

# Fix permissions if needed (Linux/Mac)
sudo chown -R $USER:$USER src/ logs/ data/
```

### Import Errors

```bash
# Check Python path
docker compose exec adk-dev python -c "import sys; print(sys.path)"

# Verify requirements installation
docker compose exec adk-dev pip list

# Reinstall requirements
docker compose exec adk-dev pip install -r requirements.txt
```

## 🎛️ Configuration

### Environment Variables

Copy `.env.template` to `.env` and customize:

```bash
cp .env.template .env
# Edit .env with your preferred settings
```

Key variables for Phase 1:
- `DEV_MODE=true` - Enables development features
- `LOG_LEVEL=DEBUG` - Sets logging verbosity
- `PYTHONPATH=/app` - Python import path

## 📊 Health Checks

The container includes comprehensive health checks:

- ✅ Environment variables
- ✅ Python dependencies
- ✅ Required directories
- ✅ Write permissions
- ✅ Google ADK availability (when installed)

## 🔄 Container Management

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f adk-dev

# Check status
docker compose ps

# Remove containers and volumes
docker compose down -v
```

## 📈 Resource Usage

**Phase 1 Requirements:**
- RAM: ~2GB (container + dependencies)
- CPU: 2+ cores recommended
- Storage: ~5GB (base images + dependencies)
- Network: Internet for initial setup only

## 🚀 Next Steps

Once Phase 1 is complete and tested:

1. **Phase 2A**: LM Studio Integration (Recommended)
2. **Phase 2B**: Cloud API Integration  
3. **Phase 2C**: Ollama Container Integration
4. **Phase 3**: Development Tools & Database
5. **Phase 4**: Agent Framework Integration

## 📝 Notes

- Google ADK import may fail if the package doesn't exist yet - this is normal
- The container runs as a non-root user for security
- All source code changes are immediately available in the container
- Logs and data persist between container restarts

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `python test-phase1.py` for diagnostic information
3. Review container logs: `docker compose logs adk-dev`
4. Ensure Docker has sufficient resources allocated

---

**Phase 1 Status: ✅ Complete**  
**Next Phase: Phase 2 - LLM Service Integration**
```

---

**File:** `requirements.txt`

```txt
# Phase 1: Core Google AI & Development Dependencies
google-generativeai==0.7.2
python-dotenv==1.0.1
requests==2.32.3
openai==1.35.13

# Web Framework (FastAPI is excellent for serving models)
fastapi==0.111.1
uvicorn[standard]==0.30.1

# Development & Testing Tools
pytest==8.3.2
black==24.4.2
mypy==1.11.0
ipython==8.26.0
jupyter==1.0.0

# Logging
structlog==24.1.0

# Protocol Buffers (often a required dependency for Google libs)
protobuf==4.25.3
```

---

**File:** `setup-phase1.sh`

```sh
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
```

---

**File:** `src\__init__.py`

```py
"""AI Agent Development Environment"""
__version__ = "0.1.0"
```

---

**File:** `src\agents\__init__.py`

```py
"""Agent implementations"""
```

---

**File:** `src\agents\sample_agent.py`

```py
"""
Sample agent that uses the LLM Client Factory to work with any
configured LLM provider (Google, LM Studio, etc.).
"""

from src.llm_client import get_llm_client

class SampleAgent:
    """A flexible agent that uses the configured LLM client."""
    
    def __init__(self):
        print("Initializing SampleAgent...")
        try:
            # The magic happens here!
            self.llm_client = get_llm_client()
            self.name = "SampleAgent"
            print(f"✅ Agent '{self.name}' initialized successfully.")
        except Exception as e:
            self.llm_client = None
            print(f"❌ Failed to initialize agent: {e}")

    def ask(self, question):
        if not self.llm_client:
            return "Agent not initialized. Please check your .env configuration and logs."
        
        print(f"\nAsking question: '{question}'")
        try:
            # The client has a unified .generate() method
            response = self.llm_client.generate(question)
            return response
        except Exception as e:
            return f"An error occurred while communicating with the LLM: {e}"

if __name__ == "__main__":
    agent = SampleAgent()
    if agent.llm_client:
        prompt = "In one short sentence, explain why local LLMs are useful for developers."
        answer = agent.ask(prompt)
        print("\nModel Response:")
        print("-----------------")
        print(answer)
        print("-----------------")
```

---

**File:** `src\llm_client.py`

```py
"""
LLM Client Factory
This module reads environment variables to determine which LLM provider
to use and returns a unified client for interacting with it.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# Load environment variables from a .env file
load_dotenv()

class UnifiedLLMClient:
    """A wrapper to provide a consistent .generate() method for different LLMs."""

    def __init__(self, client, provider):
        self._client = client
        self._provider = provider

    def generate(self, prompt, model=None):
        """Generates a response from the LLM using a unified interface."""
        print(f"--- Sending request to {self._provider} ---")
        if self._provider == "google":
            # For Google, the model is part of the client
            model_instance = self._client
            return model_instance.generate_content(prompt).text
        
        elif self._provider in ["lm_studio", "openai", "ollama"]:
            # For OpenAI-compatible APIs
            # LM Studio doesn't use the 'model' parameter in the same way,
            # as the model is pre-loaded in the UI.
            chat_completion = self._client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="local-model", # This is often ignored by LM Studio but is required by the API
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content
        
        else:
            raise ValueError(f"Unknown LLM provider: {self._provider}")


def get_llm_client():
    """
    Reads the environment and returns the appropriate unified LLM client.
    """
    provider = os.getenv("LLM_PROVIDER")
    
    if not provider:
        raise ValueError("LLM_PROVIDER environment variable not set.")

    print(f"Found LLM_PROVIDER: '{provider}'")

    if provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set for the 'google' provider.")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        return UnifiedLLMClient(client=model, provider="google")

    elif provider == "lm_studio":
        base_url = os.getenv("LM_STUDIO_BASE_URL")
        if not base_url:
            raise ValueError("LM_STUDIO_BASE_URL is not set for the 'lm_studio' provider.")
        # LM Studio doesn't require an API key
        client = OpenAI(base_url=base_url, api_key="not-needed")
        return UnifiedLLMClient(client=client, provider="lm_studio")

    # Add other providers like 'openai' or 'ollama' here in the future
    # elif provider == "openai":
    #     ...

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
```

---

**File:** `src\utils\__init__.py`

```py
"""Utility functions"""
```

---

**File:** `test-phase1.py`

```py
#!/usr/bin/env python3
"""
Phase 1 Test Script - Verify basic container functionality
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_docker_setup():
    """Test Docker and Docker Compose availability."""
    print("🔍 Testing Docker setup...")
    
    # Test Docker
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker not available")
        return False
    print(f"✅ Docker: {stdout.strip()}")
    
    # Test Docker Compose
    success, stdout, stderr = run_command("docker compose version")
    if not success:
        print("❌ Docker Compose not available")
        return False
    print(f"✅ Docker Compose: {stdout.strip()}")
    
    return True

def test_container_build():
    """Test container build process."""
    print("🔨 Testing container build...")
    
    # Build container
    success, stdout, stderr = run_command("docker compose build adk-dev")
    if not success:
        print(f"❌ Container build failed: {stderr}")
        return False
    
    print("✅ Container built successfully")
    return True

def test_container_startup():
    """Test container startup and health."""
    print("🚀 Testing container startup...")
    
    # Start container
    success, stdout, stderr = run_command("docker compose up -d adk-dev")
    if not success:
        print(f"❌ Container startup failed: {stderr}")
        return False
    
    # Wait for container to be ready
    print("⏳ Waiting for container to initialize...")
    time.sleep(15)
    
    # Check if container is running
    success, stdout, stderr = run_command("docker compose ps adk-dev")
    if not success or "Up" not in stdout:
        print("❌ Container is not running properly")
        return False
    
    print("✅ Container started successfully")
    return True

def test_container_health():
    """Test container health check."""
    print("🏥 Testing container health...")
    
    # Run health check
    success, stdout, stderr = run_command("docker compose exec -T adk-dev python health_check.py")
    if not success:
        print(f"❌ Health check failed: {stderr}")
        return False
    
    print("✅ Container health check passed")
    return True

def test_python_environment():
    """Test Python environment inside container."""
    print("🐍 Testing Python environment...")
    
    # Test Python version
    success, stdout, stderr = run_command("docker compose exec -T adk-dev python --version")
    if not success:
        print("❌ Python not available in container")
        return False
    print(f"✅ Python: {stdout.strip()}")
    
    # Test pip
    success, stdout, stderr = run_command("docker compose exec -T adk-dev pip --version")
    if not success:
        print("❌ Pip not available in container")
        return False
    print(f"✅ Pip: {stdout.strip()}")
    
    return True

def test_dependencies():
    """Test installed dependencies."""
    print("📦 Testing dependencies...")
    
    # Test basic imports
    test_imports = [
        "import sys; print('Python OK')",
        "import pytest; print('Pytest OK')",
        "import requests; print('Requests OK')",
    ]
    
    for test_import in test_imports:
        success, stdout, stderr = run_command(f"docker compose exec -T adk-dev python -c \"{test_import}\"")
        if not success:
            print(f"❌ Import test failed: {test_import}")
            return False
    
    print("✅ Dependencies available")
    return True

def test_file_structure():
    """Test mounted file structure."""
    print("📁 Testing file structure...")
    
    # Test directory access
    success, stdout, stderr = run_command("docker compose exec -T adk-dev ls -la /app")
    if not success:
        print("❌ Cannot access /app directory")
        return False
    
    # Test source code mounting
    success, stdout, stderr = run_command("docker compose exec -T adk-dev ls -la /app/src")
    if not success:
        print("❌ Source code not mounted properly")
        return False
    
    print("✅ File structure accessible")
    return True

def cleanup():
    """Clean up test environment."""
    print("🧹 Cleaning up...")
    run_command("docker compose down", capture_output=False)

def main():
    """Run all Phase 1 tests."""
    print("🧪 Phase 1 Test Suite")
    print("====================")
    
    tests = [
        ("Docker Setup", test_docker_setup),
        ("Container Build", test_container_build),
        ("Container Startup", test_container_startup),
        ("Container Health", test_container_health),
        ("Python Environment", test_python_environment),
        ("Dependencies", test_dependencies),
        ("File Structure", test_file_structure),
    ]
    
    failed_tests = []
    
    try:
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            if not test_func():
                failed_tests.append(test_name)
                
        print(f"\n📊 Test Results")
        print("================")
        print(f"Total tests: {len(tests)}")
        print(f"Passed: {len(tests) - len(failed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        
        if failed_tests:
            print(f"\n❌ Failed tests: {', '.join(failed_tests)}")
            return False
        else:
            print("\n✅ All tests passed! Phase 1 is ready.")
            return True
            
    finally:
        cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

---

**File:** `TroubleshootingGuide.md`

```md
# Troubleshooting Guide - Dependency Conflicts

## 🔧 Quick Fix for FastAPI/Google-ADK Conflict

The error you encountered is a common dependency conflict. Here's how to resolve it:

### Option 1: Use the Fix Script (Recommended)

```bash
# Make the fix script executable
chmod +x fix-dependencies.sh

# Run the fix
./fix-dependencies.sh
```

### Option 2: Manual Fix Steps

```bash
# 1. Stop and clean up
docker compose down
docker compose down --rmi local

# 2. Clean Docker cache
docker system prune -f

# 3. Rebuild with no cache
docker compose build --no-cache adk-dev

# 4. Start fresh
docker compose up -d adk-dev

# 5. Test
docker compose exec adk-dev python health_check.py
```

### Option 3: Use Basic Requirements (If Google ADK is problematic)

If the Google ADK package continues to cause issues, you can use the basic requirements instead:

```bash
# Replace the requirements file
cp requirements-basic.txt requirements.txt

# Rebuild
docker compose build --no-cache adk-dev
docker compose up -d adk-dev
```

## 🐛 Common Issues and Solutions

### 1. "google-adk" Package Not Found

**Issue**: The `google-adk` package might not exist in PyPI or might be a placeholder.

**Solution**: 
- Use `requirements-basic.txt` instead
- This provides a fully functional development environment without the ADK dependency
- You can add the actual Google ADK package later when it's available

### 2. Dependency Version Conflicts

**Issue**: Package versions conflict with each other.

**Solution**:
- Use version ranges instead of exact versions: `fastapi>=0.115.0`
- Let pip resolve dependencies automatically
- Use `pip-tools` for more precise dependency management

### 3. Docker Compose Version Warning

**Issue**: Warning about obsolete `version` attribute.

**Solution**: 
- Remove the `version: '3.8'` line from docker-compose.yml
- Modern Docker Compose doesn't need this attribute

### 4. Container Won't Start

**Issue**: Container exits immediately or won't start.

**Solution**:
```bash
# Check logs
docker compose logs adk-dev

# Try interactive debugging
docker compose run --rm adk-dev bash

# Test individual components
docker compose run --rm adk-dev python -c "import sys; print(sys.version)"
```

### 5. Permission Issues (Linux/Mac)

**Issue**: Permission denied errors when accessing mounted volumes.

**Solution**:
```bash
# Fix ownership
sudo chown -R $USER:$USER src/ logs/ data/ config/

# Or run with correct user mapping
docker compose run --rm -u $(id -u):$(id -g) adk-dev bash
```

## 🔍 Debugging Commands

### Check Package Installation
```bash
# List installed packages
docker compose exec adk-dev pip list

# Check specific package
docker compose exec adk-dev pip show fastapi

# Test imports
docker compose exec adk-dev python -c "import fastapi; print(fastapi.__version__)"
```

### Check Container Health
```bash
# Run health check
docker compose exec adk-dev python health_check.py

# Check environment
docker compose exec adk-dev env

# Check file system
docker compose exec adk-dev ls -la /app/
```

### Check Docker Resources
```bash
# Check Docker info
docker info

# Check available space
docker system df

# Clean up if needed
docker system prune -a
```

## 📋 Verification Steps

After fixing the issue, verify everything works:

1. **Container Health**: `docker compose exec adk-dev python health_check.py`
2. **Python Environment**: `docker compose exec adk-dev python --version`
3. **Package Imports**: `docker compose exec adk-dev python -c "import fastapi, requests, pytest; print('All imports OK')"`
4. **File Mounting**: `echo "print('Hello World')" > src/test.py && docker compose exec adk-dev python /app/src/test.py`
5. **Development Tools**: `docker compose exec adk-dev black --version`

## 🚀 Next Steps

Once the container is working:

1. Test the sample agent: `docker compose exec adk-dev python /app/src/agents/sample_agent.py`
2. Start interactive development: `docker compose exec adk-dev bash`
3. Run the comprehensive test suite: `python test-phase1.py`
4. Proceed to Phase 2 setup

## 💡 Pro Tips

- Always use `--no-cache` when rebuilding after dependency changes
- Keep a backup of working configurations
- Use `docker compose logs -f adk-dev` to monitor container startup
- Test imports individually to isolate problems
- Use `requirements-basic.txt` as a fallback option
```

