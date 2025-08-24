#!/usr/bin/env python3
"""
Test script for the Desktop Access MCP Server.
This script can be used to test the basic functionality.
"""

import sys
import os

# Add the project root to the path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that we can import all required modules."""
    try:
        import mcp
        import PIL
        import pynput
        import mss
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_controller():
    """Test that we can import our controller."""
    try:
        from desktop_access_mcp_server.desktop_controller import DesktopController
        controller = DesktopController()
        print("✓ DesktopController imported and instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ DesktopController error: {e}")
        return False

if __name__ == "__main__":
    print("Running basic tests for Desktop Access MCP Server...")
    
    success = True
    success &= test_imports()
    success &= test_controller()
    
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)