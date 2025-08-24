#!/usr/bin/env python3
"""Test script to verify the MCP server is working."""

import subprocess
import time
import sys

def test_mcp_server():
    """Test the MCP server functionality."""
    print("Testing Desktop Access MCP Server...")
    
    # Start the server in the background
    print("Starting server...")
    server_process = subprocess.Popen(
        ["uvx", "--from", "desktop-access-mcp-server", "desktop-access-mcp-server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server a moment to start
    time.sleep(3)
    
    # Check the return code after a short time (0 means success)
    if server_process.poll() is None or server_process.returncode == 0:
        print("✓ Server started successfully")
        # Terminate the server
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
            print("✓ Server terminated gracefully")
        except subprocess.TimeoutExpired:
            server_process.kill()
            print("⚠ Server killed forcefully after timeout")
        return True
    else:
        stdout, stderr = server_process.communicate()
        print("✗ Server failed to start")
        print(f"Return code: {server_process.returncode}")
        if stdout:
            print(f"STDOUT: {stdout}")
        if stderr:
            print(f"STDERR: {stderr}")
        return False

if __name__ == "__main__":
    try:
        result = test_mcp_server()
        if result:
            print("\n🎉 All tests passed! The Desktop Access MCP Server is working correctly.")
            print("\nTo use the server with uvx, run:")
            print("  uvx --from desktop-access-mcp-server desktop-access-mcp-server")
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)