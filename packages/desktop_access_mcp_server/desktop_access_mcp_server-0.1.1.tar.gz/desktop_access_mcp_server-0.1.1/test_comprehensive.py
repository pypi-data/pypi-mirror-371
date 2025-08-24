#!/usr/bin/env python3
"""
Comprehensive test script for the Desktop Access MCP Server.
This script tests all functionalities of the desktop controller.
"""

import asyncio
import base64
import sys
import os

# Add the project root to the path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.desktop_controller import DesktopController

async def test_screenshot():
    """Test the screenshot functionality."""
    print("Testing screenshot functionality...")
    controller = DesktopController()
    print(f"Platform: {controller.platform}")
    
    # Test basic screenshot (combined monitors)
    result = await controller.take_screenshot({})
    if "error" in result:
        print(f"  ✗ Basic screenshot failed: {result['error']}")
        return False
    else:
        print(f"  ✓ Basic screenshot successful!")
        print(f"    Size: {result['size']['width']}x{result['size']['height']}")
        print(f"    Format: {result['format']}")
        
    # Test JPEG format with quality
    result = await controller.take_screenshot({"format": "jpeg", "quality": 50})
    if "error" in result:
        print(f"  ⚠ JPEG screenshot failed: {result['error']}")
    else:
        print(f"  ✓ JPEG screenshot successful!")
        print(f"    Size: {result['size']['width']}x{result['size']['height']}")
        print(f"    Format: {result['format']}")
        
    # Test monitor selection
    result = await controller.take_screenshot({"monitor": 1})
    if "error" in result:
        print(f"  ⚠ Monitor 1 selection failed: {result['error']}")
    else:
        print(f"  ✓ Monitor 1 selection successful!")
        print(f"    Size: {result['size']['width']}x{result['size']['height']}")
        
    result = await controller.take_screenshot({"monitor": 2})
    if "error" in result:
        print(f"  ⚠ Monitor 2 selection failed: {result['error']}")
    else:
        print(f"  ✓ Monitor 2 selection successful!")
        print(f"    Size: {result['size']['width']}x{result['size']['height']}")
        
    return True

async def test_keyboard_input():
    """Test the keyboard input functionality."""
    print("Testing keyboard input functionality...")
    controller = DesktopController()
    
    # Test typing text with delay
    result = await controller.keyboard_input({"text": "Hello World", "delay": 0.05})
    if "error" in result:
        print(f"  ✗ Keyboard typing with delay failed: {result['error']}")
        return False
    else:
        print(f"  ✓ Keyboard typing with delay successful: {result}")
    
    # Test key combination
    result = await controller.keyboard_input({"key_combination": "shift+shift"})
    if "error" in result:
        print(f"  ✗ Key combination failed: {result['error']}")
        return False
    else:
        print(f"  ✓ Key combination successful: {result}")
        
    # Test special keys
    result = await controller.keyboard_input({"key_combination": "ctrl+alt+delete"})
    if "error" in result:
        print(f"  ⚠ Special key combination failed: {result['error']}")
    else:
        print(f"  ✓ Special key combination successful: {result}")
        
    return True

async def test_mouse_action():
    """Test the mouse action functionality."""
    print("Testing mouse action functionality...")
    controller = DesktopController()
    
    # Test mouse move
    result = await controller.mouse_action({"action": "move", "x": 100, "y": 100})
    if "error" in result:
        print(f"  ✗ Mouse move failed: {result['error']}")
        return False
    else:
        print(f"  ✓ Mouse move successful: {result}")
    
    # Test mouse click with different buttons
    result = await controller.mouse_action({"action": "click", "button": "left"})
    if "error" in result:
        print(f"  ✗ Left mouse click failed: {result['error']}")
        return False
    else:
        print(f"  ✓ Left mouse click successful: {result}")
        
    result = await controller.mouse_action({"action": "click", "button": "right"})
    if "error" in result:
        print(f"  ⚠ Right mouse click failed: {result['error']}")
    else:
        print(f"  ✓ Right mouse click successful: {result}")
    
    # Test scroll
    result = await controller.mouse_action({"action": "scroll", "scroll_amount": 10})
    if "error" in result:
        print(f"  ✗ Mouse scroll failed: {result['error']}")
        return False
    else:
        print(f"  ✓ Mouse scroll successful: {result}")
        
    # Test drag (this might not work in all environments)
    result = await controller.mouse_action({
        "action": "drag",
        "from_x": 50,
        "from_y": 50,
        "to_x": 100,
        "to_y": 100,
        "duration": 0.5
    })
    if "error" in result:
        print(f"  ⚠ Mouse drag failed: {result['error']}")
    else:
        print(f"  ✓ Mouse drag successful: {result}")
        
    return True

async def main():
    """Run all tests."""
    print("Running comprehensive tests for Desktop Access MCP Server...")
    print("=" * 60)
    
    success = True
    
    # Test each functionality
    success &= await test_screenshot()
    print()
    success &= await test_keyboard_input()
    print()
    success &= await test_mouse_action()
    
    print("=" * 60)
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))