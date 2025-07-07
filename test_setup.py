#!/usr/bin/env python3
"""
Test script to verify the backend setup works correctly.
"""

import sys
import importlib

def test_imports():
    """Test that all required modules can be imported."""
    modules = [
        'fastapi',
        'uvicorn',
        'dotenv',
        'requests',
        'feedparser',
        'app.llm',
        'app.main'
    ]
    
    print("Testing imports...")
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def test_app_creation():
    """Test that the FastAPI app can be created."""
    try:
        from app.main import app
        print("✅ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print()
    
    success = True
    success &= test_imports()
    print()
    success &= test_app_creation()
    
    if success:
        print("\n🎉 All tests passed! Setup is working correctly.")
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1) 