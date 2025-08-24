#!/usr/bin/env python3
"""
Test client for the Desktop Access MCP Server.

This script demonstrates how to connect to and use the Desktop Access MCP Server
as an MCP client.
"""

import asyncio
import json
import base64
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the Desktop Access MCP Server."""
    print("Testing Desktop Access MCP Server...")
    
    # Start the server process
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "desktop_access_mcp_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # List available tools
            print("\n1. Listing available tools...")
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            # Test take_screenshot tool
            print("\n2. Testing take_screenshot tool...")
            try:
                result = await session.call_tool("take_screenshot", {})
                if "error" in result:
                    print(f"Screenshot failed: {result['error']}")
                else:
                    print(f"Screenshot successful!")
                    print(f"  Format: {result['format']}")
                    print(f"  Size: {result['size']['width']}x{result['size']['height']}")
                    print(f"  Platform: {result['platform']}")
                    print(f"  Monitor: {result['monitor']}")
                    
                    # Save screenshot to file
                    with open("mcp_test_screenshot.png", "wb") as f:
                        f.write(base64.b64decode(result["data"]))
                    print("  Screenshot saved as mcp_test_screenshot.png")
            except Exception as e:
                print(f"Error calling take_screenshot: {e}")
            
            # Test take_screenshot with JPEG format
            print("\n3. Testing take_screenshot with JPEG format...")
            try:
                arguments = {"format": "jpeg", "quality": 75}
                result = await session.call_tool("take_screenshot", arguments)
                if "error" in result:
                    print(f"JPEG screenshot failed: {result['error']}")
                else:
                    print(f"JPEG screenshot successful!")
                    print(f"  Format: {result['format']}")
                    print(f"  Size: {result['size']['width']}x{result['size']['height']}")
                    
                    # Save screenshot to file
                    with open("mcp_test_screenshot.jpg", "wb") as f:
                        f.write(base64.b64decode(result["data"]))
                    print("  Screenshot saved as mcp_test_screenshot.jpg")
            except Exception as e:
                print(f"Error calling take_screenshot with JPEG: {e}")
            
            # Test keyboard_input tool
            print("\n4. Testing keyboard_input tool...")
            try:
                # Test typing text (safely - just a few characters)
                arguments = {"text": "MCP", "delay": 0.1}
                result = await session.call_tool("keyboard_input", arguments)
                if "error" in result:
                    print(f"Keyboard input failed: {result['error']}")
                else:
                    print(f"Keyboard input successful: {result}")
            except Exception as e:
                print(f"Error calling keyboard_input: {e}")
            
            # Test mouse_action tool
            print("\n5. Testing mouse_action tool...")
            try:
                # Test mouse move
                arguments = {"action": "move", "x": 100, "y": 100}
                result = await session.call_tool("mouse_action", arguments)
                if "error" in result:
                    print(f"Mouse move failed: {result['error']}")
                else:
                    print(f"Mouse move successful: {result}")
            except Exception as e:
                print(f"Error calling mouse_action: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())