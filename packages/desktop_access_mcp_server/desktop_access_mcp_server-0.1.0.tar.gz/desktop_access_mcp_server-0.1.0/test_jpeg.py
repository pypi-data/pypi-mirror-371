#!/usr/bin/env python3
"""
Test script to check JPEG screenshot functionality.
"""

import sys
import os
import base64
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.desktop_controller import DesktopController
import asyncio

async def test_jpeg_screenshot():
    """Test JPEG screenshot functionality."""
    print("Testing JPEG screenshot functionality...")
    controller = DesktopController()
    
    # Try to take a JPEG screenshot
    result = await controller.take_screenshot({"format": "jpeg", "quality": 50})
    
    if "error" in result:
        print(f"JPEG screenshot failed: {result['error']}")
        return False
    else:
        print(f"JPEG screenshot successful!")
        print(f"  Format: {result['format']}")
        print(f"  Size: {result['size']['width']}x{result['size']['height']}")
        print(f"  Data length: {len(result['data'])} characters")
        print(f"  Platform: {result['platform']}")
        print(f"  Monitor: {result['monitor']}")
        
        # Try to save the screenshot
        try:
            filename = f"screenshot_test.{result['format']}"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(result["data"]))
            print(f"  Screenshot saved as {filename}")
            return True
        except Exception as e:
            print(f"  Failed to save screenshot: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(test_jpeg_screenshot())