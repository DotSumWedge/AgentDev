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