#!/usr/bin/env python3
"""
Example usage of the Desktop Access MCP Server.

This script demonstrates how to use the desktop controller directly.
"""

import asyncio
import base64
from desktop_access_mcp_server.desktop_controller import DesktopController

async def example_usage():
    """Example of using the desktop controller."""
    # Create controller
    controller = DesktopController()
    
    # Take a screenshot
    print("Taking screenshot...")
    screenshot_result = await controller.take_screenshot({})
    
    if "error" in screenshot_result:
        print(f"Error taking screenshot: {screenshot_result['error']}")
    else:
        print(f"Screenshot taken successfully!")
        print(f"Size: {screenshot_result['size']['width']}x{screenshot_result['size']['height']}")
        
        # Save screenshot to file as an example
        with open("example_screenshot.png", "wb") as f:
            f.write(base64.b64decode(screenshot_result["data"]))
        print("Screenshot saved as example_screenshot.png")
    
    # Example keyboard input (commented out for safety)
    # print("Typing 'Hello World'...")
    # keyboard_result = await controller.keyboard_input({"text": "Hello World"})
    # print(f"Keyboard input result: {keyboard_result}")
    
    # Example mouse action (commented out for safety)
    # print("Moving mouse to (100, 100)...")
    # mouse_result = await controller.mouse_action({"action": "move", "x": 100, "y": 100})
    # print(f"Mouse action result: {mouse_result}")

if __name__ == "__main__":
    asyncio.run(example_usage())