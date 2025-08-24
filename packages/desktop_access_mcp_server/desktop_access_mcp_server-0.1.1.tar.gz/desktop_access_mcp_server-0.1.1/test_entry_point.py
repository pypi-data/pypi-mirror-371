#!/usr/bin/env python3
"""Simple test to check if the entry point works correctly."""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_entry_point():
    """Test the entry point."""
    try:
        from desktop_access_mcp_server.entry_point import run_server
        print("Entry point imported successfully")
        print(f"run_server function: {run_server}")
        print(f"run_server type: {type(run_server)}")
        return True
    except Exception as e:
        print(f"Error importing entry point: {e}")
        return False

if __name__ == "__main__":
    success = test_entry_point()
    if success:
        print("Test passed")
        sys.exit(0)
    else:
        print("Test failed")
        sys.exit(1)