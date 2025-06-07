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
        return False
    
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