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