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