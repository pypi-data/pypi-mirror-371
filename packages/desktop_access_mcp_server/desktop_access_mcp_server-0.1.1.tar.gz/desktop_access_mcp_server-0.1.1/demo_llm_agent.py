#!/usr/bin/env python3
"""
Demonstration of how an LLM agent would use the Desktop Access MCP Server.

This script simulates how an LLM agent would interact with the Desktop Access MCP Server
to act as the "eyes and hands" of the agent by providing screenshots and executing
keyboard/mouse actions.
"""

import asyncio
import base64
from desktop_access_mcp_server.desktop_controller import DesktopController

async def demo_llm_agent_interaction():
    """Demonstrate how an LLM agent would interact with the Desktop Access MCP Server."""
    print("=== Desktop Access MCP Server Demo ===")
    print("This demonstrates how an LLM agent would use this server as its 'eyes and hands'")
    print()
    
    # Initialize the controller (this would be handled by the MCP server in real usage)
    controller = DesktopController()
    
    # Simulate an LLM agent workflow:
    print("1. Agent requests a screenshot to understand the current desktop state...")
    screenshot_result = await controller.take_screenshot({})
    
    if "error" in screenshot_result:
        print(f"   Error: {screenshot_result['error']}")
        return
    
    print(f"   ✓ Screenshot captured successfully!")
    print(f"   ✓ Size: {screenshot_result['size']['width']}x{screenshot_result['size']['height']}")
    print(f"   ✓ Format: {screenshot_result['format']}")
    print(f"   ✓ Data size: {len(screenshot_result['data'])} characters (base64 encoded)")
    
    # Save the screenshot for demonstration
    with open("demo_screenshot.png", "wb") as f:
        f.write(base64.b64decode(screenshot_result["data"]))
    print("   ✓ Screenshot saved as demo_screenshot.png")
    print()
    
    # Simulate the LLM analyzing the screenshot and deciding to type something
    print("2. Agent analyzes screenshot and decides to type 'Hello World'...")
    keyboard_result = await controller.keyboard_input({"text": "Hello World", "delay": 0.1})
    
    if "error" in keyboard_result:
        print(f"   Error: {keyboard_result['error']}")
    else:
        print(f"   ✓ Typed 'Hello World' with delay of 0.1s between characters")
        print(f"   ✓ Result: {keyboard_result}")
    print()
    
    # Simulate the LLM deciding to move the mouse
    print("3. Agent decides to move mouse to position (100, 100)...")
    mouse_result = await controller.mouse_action({"action": "move", "x": 100, "y": 100})
    
    if "error" in mouse_result:
        print(f"   Error: {mouse_result['error']}")
    else:
        print(f"   ✓ Mouse moved to (100, 100)")
        print(f"   ✓ Result: {mouse_result}")
    print()
    
    # Simulate the LLM deciding to take another screenshot to verify the state
    print("4. Agent takes another screenshot to verify the current state...")
    screenshot_result2 = await controller.take_screenshot({"format": "jpeg", "quality": 75})
    
    if "error" in screenshot_result2:
        print(f"   Error: {screenshot_result2['error']}")
    else:
        print(f"   ✓ JPEG screenshot captured successfully!")
        print(f"   ✓ Size: {screenshot_result2['size']['width']}x{screenshot_result2['size']['height']}")
        print(f"   ✓ Format: {screenshot_result2['format']}")
        
        # Save the JPEG screenshot for demonstration
        with open("demo_screenshot.jpg", "wb") as f:
            f.write(base64.b64decode(screenshot_result2["data"]))
        print("   ✓ Screenshot saved as demo_screenshot.jpg")
    print()
    
    # Simulate the LLM deciding to click the mouse
    print("5. Agent decides to click the left mouse button...")
    click_result = await controller.mouse_action({"action": "click", "button": "left"})
    
    if "error" in click_result:
        print(f"   Error: {click_result['error']}")
    else:
        print(f"   ✓ Left mouse button clicked")
        print(f"   ✓ Result: {click_result}")
    print()
    
    print("=== Demo Complete ===")
    print("The LLM agent has successfully:")
    print("  1. Captured screenshots of the desktop (in both PNG and JPEG formats)")
    print("  2. Typed text on the desktop")
    print("  3. Moved the mouse cursor")
    print("  4. Clicked the mouse")
    print()
    print("This demonstrates how the Desktop Access MCP Server provides the 'eyes and hands'")
    print("for an LLM agent to interact with a desktop environment.")

if __name__ == "__main__":
    asyncio.run(demo_llm_agent_interaction())