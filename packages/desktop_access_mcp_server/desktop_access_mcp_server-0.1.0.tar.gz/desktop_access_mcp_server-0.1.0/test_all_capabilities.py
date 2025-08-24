#!/usr/bin/env python3
"""
Comprehensive test of all Desktop Access MCP Server capabilities.

This script tests all the functionality that would be available to an LLM agent
through the MCP server interface.
"""

import asyncio
import base64
import json
from desktop_access_mcp_server.desktop_controller import DesktopController

async def test_all_capabilities():
    """Test all capabilities of the Desktop Access MCP Server."""
    print("=== Comprehensive Test of Desktop Access MCP Server ===")
    print()
    
    # Initialize the controller
    controller = DesktopController()
    
    # Test 1: Basic screenshot
    print("1. Testing basic screenshot capability...")
    result = await controller.take_screenshot({})
    if "error" in result:
        print(f"   ✗ Failed: {result['error']}")
    else:
        print(f"   ✓ Success: {result['size']['width']}x{result['size']['height']} {result['format']}")
        with open("test_basic_screenshot.png", "wb") as f:
            f.write(base64.b64decode(result["data"]))
    print()
    
    # Test 2: JPEG screenshot with quality setting
    print("2. Testing JPEG screenshot with quality setting...")
    result = await controller.take_screenshot({"format": "jpeg", "quality": 50})
    if "error" in result:
        print(f"   ✗ Failed: {result['error']}")
    else:
        print(f"   ✓ Success: {result['size']['width']}x{result['size']['height']} {result['format']} (quality 50)")
        with open("test_jpeg_screenshot.jpg", "wb") as f:
            f.write(base64.b64decode(result["data"]))
    print()
    
    # Test 3: Individual monitor screenshots
    print("3. Testing individual monitor screenshots...")
    # Get monitor info first
    monitors = controller.get_monitor_layout()
    print(f"   Detected {len(monitors)} monitors")
    
    for i in range(min(3, len(monitors))):  # Test up to 3 monitors
        result = await controller.take_screenshot({"monitor": i + 1})
        if "error" in result:
            print(f"   ✗ Monitor {i + 1} failed: {result['error']}")
        else:
            print(f"   ✓ Monitor {i + 1} success: {result['size']['width']}x{result['size']['height']}")
            with open(f"test_monitor_{i + 1}_screenshot.png", "wb") as f:
                f.write(base64.b64decode(result["data"]))
    print()
    
    # Test 4: Keyboard input - typing text
    print("4. Testing keyboard input - typing text...")
    result = await controller.keyboard_input({"text": "MCP Test", "delay": 0.05})
    if "error" in result:
        print(f"   ✗ Failed: {result['error']}")
    else:
        print(f"   ✓ Success: Typed 'MCP Test' with 0.05s delay")
    print()
    
    # Test 5: Keyboard input - key combinations
    print("5. Testing keyboard input - key combinations...")
    result = await controller.keyboard_input({"key_combination": "ctrl+a"})
    if "error" in result:
        print(f"   ✗ Failed: {result['error']}")
    else:
        print(f"   ✓ Success: Pressed Ctrl+A")
    print()
    
    # Test 6: Mouse actions - move
    print("6. Testing mouse action - move...")
    result = await controller.mouse_action({"action": "move", "x": 200, "y": 200})
    if "error" in result:
        print(f"   ✗ Failed: {result['error']}")
    else:
        print(f"   ✓ Success: Moved mouse to (200, 200)")
    print()
    
    # Test 7: Mouse actions - click
    print("7. Testing mouse action - click...")
    result = await controller.mouse_action({"action": "click", "button": "left"})
    if "error" in result:
        print(f"   ✗ Failed: {result['error']}")
    else:
        print(f"   ✓ Success: Left click")
    print()
    
    # Test 8: Mouse actions - scroll
    print("8. Testing mouse action - scroll...")
    result = await controller.mouse_action({"action": "scroll", "scroll_amount": 5})
    if "error" in result:
        print(f"   ✗ Failed: {result['error']}")
    else:
        print(f"   ✓ Success: Scrolled up by 5 units")
    print()
    
    # Test 9: Mouse actions - drag
    print("9. Testing mouse action - drag...")
    result = await controller.mouse_action({
        "action": "drag",
        "from_x": 200,
        "from_y": 200,
        "to_x": 300,
        "to_y": 300,
        "duration": 0.5
    })
    if "error" in result:
        print(f"   ✗ Failed: {result['error']}")
    else:
        print(f"   ✓ Success: Dragged from (200, 200) to (300, 300) over 0.5s")
    print()
    
    # Test 10: Complex workflow simulation
    print("10. Testing complex workflow simulation...")
    # Take initial screenshot
    result1 = await controller.take_screenshot({})
    if "error" not in result1:
        print("    ✓ Initial screenshot taken")
        
        # Type some text
        result2 = await controller.keyboard_input({"text": "Workflow Test", "delay": 0.02})
        if "error" not in result2:
            print("    ✓ Text typed")
            
            # Move and click
            result3 = await controller.mouse_action({"action": "move", "x": 150, "y": 150})
            if "error" not in result3:
                result4 = await controller.mouse_action({"action": "click"})
                if "error" not in result4:
                    print("    ✓ Mouse moved and clicked")
                    
                    # Final screenshot
                    result5 = await controller.take_screenshot({"format": "jpeg", "quality": 80})
                    if "error" not in result5:
                        print("    ✓ Final screenshot taken")
                        print("    ✓ Complex workflow completed successfully")
                    else:
                        print(f"    ✗ Final screenshot failed: {result5['error']}")
                else:
                    print(f"    ✗ Click failed: {result4['error']}")
            else:
                print(f"    ✗ Mouse move failed: {result3['error']}")
        else:
            print(f"    ✗ Text typing failed: {result2['error']}")
    else:
        print(f"    ✗ Initial screenshot failed: {result1['error']}")
    print()
    
    print("=== Test Summary ===")
    print("The Desktop Access MCP Server provides the following capabilities to LLM agents:")
    print("  ✓ Desktop screenshots (PNG/JPEG, full or per-monitor)")
    print("  ✓ Keyboard input (typing with delay, key combinations)")
    print("  ✓ Mouse control (move, click, scroll, drag)")
    print("  ✓ Multi-monitor support")
    print("  ✓ Configurable image quality and formats")
    print()
    print("This makes it a complete 'eyes and hands' interface for LLM agents to interact")
    print("with desktop environments through the MCP protocol.")

if __name__ == "__main__":
    asyncio.run(test_all_capabilities())