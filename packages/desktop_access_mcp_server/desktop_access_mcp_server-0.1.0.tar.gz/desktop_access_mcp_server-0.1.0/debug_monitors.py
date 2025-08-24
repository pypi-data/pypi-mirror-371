#!/usr/bin/env python3
"""
Debug script to understand multi-monitor screenshot behavior.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.desktop_controller import DesktopController
import asyncio

async def debug_monitor_layout():
    """Debug monitor layout detection."""
    print("Debugging monitor layout...")
    controller = DesktopController()
    print(f"Platform: {controller.platform}")
    print(f"Display server: {controller.display_server}")
    
    # Get monitor layout
    try:
        monitors = controller._get_monitor_layout()
        print(f"Detected monitors: {len(monitors)}")
        for i, monitor in enumerate(monitors):
            print(f"  Monitor {i}: {monitor}")
    except Exception as e:
        print(f"Failed to get monitor layout: {e}")
        
    # Test individual monitor screenshots
    print("\nTesting individual monitor screenshots...")
    for i in range(len(monitors) if 'monitors' in locals() else 2):
        print(f"  Testing monitor {i}...")
        try:
            # Try to take screenshot of individual monitor
            result = await controller.take_screenshot({"monitor": i+1})  # 1-indexed for individual monitors
            if "error" in result:
                print(f"    Failed: {result['error']}")
            else:
                print(f"    Success: {result['size']['width']}x{result['size']['height']}")
        except Exception as e:
            print(f"    Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_monitor_layout())