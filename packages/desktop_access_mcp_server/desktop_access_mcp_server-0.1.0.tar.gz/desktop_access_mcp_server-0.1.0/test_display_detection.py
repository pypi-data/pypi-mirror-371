#!/usr/bin/env python3
"""
Test script to check display server detection and screenshot capabilities.
"""

import sys
import os
import subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.desktop_controller import DesktopController

def detect_display_server():
    """Detect the current display server."""
    # Try to detect Wayland
    if "WAYLAND_DISPLAY" in os.environ or "WAYLAND_SOCKET" in os.environ:
        return "wayland"
    
    # Try to detect X11
    if "DISPLAY" in os.environ:
        return "x11"
        
    # Fallback check
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        if "Xwayland" in result.stdout:
            return "wayland"
        elif "Xorg" in result.stdout:
            return "x11"
    except:
        pass
    
    return "unknown"

def test_display_detection():
    """Test display server detection."""
    print("Testing display server detection...")
    controller = DesktopController()
    print(f"Platform: {controller.platform}")
    
    # Detect display server manually
    display_server = detect_display_server()
    print(f"Display server: {display_server}")
    
    # Try to get monitor info to see what methods are being used
    try:
        monitors = controller._get_monitor_info()
        print(f"Detected {len(monitors)} monitors:")
        for i, monitor in enumerate(monitors):
            print(f"  Monitor {i}: {monitor['name']} at ({monitor['x']}, {monitor['y']}) - {monitor['width']}x{monitor['height']}")
    except Exception as e:
        print(f"Error getting monitor info: {e}")
    
    # Check if required tools are available based on detected display server
    if display_server == "wayland":
        tools = ["grim", "gnome-screenshot", "wlr-randr"]
        for tool in tools:
            available = controller._is_command_available(tool)
            print(f"Tool '{tool}' available: {available}")
    elif display_server == "x11":
        tools = ["xwd", "convert", "xrandr"]
        for tool in tools:
            available = controller._is_command_available(tool)
            print(f"Tool '{tool}' available: {available}")

if __name__ == "__main__":
    test_display_detection()