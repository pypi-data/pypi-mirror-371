#!/usr/bin/env python3
"""
Comprehensive screenshot test script.
This script captures various types of screenshots with detailed naming for easy review.
"""

import asyncio
import sys
import os
import datetime
import json
import base64
from PIL import Image
from io import BytesIO

# Add the project root to the path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.desktop_controller import DesktopController

def get_timestamp():
    """Get current timestamp for filenames."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

async def capture_screenshot_with_details(controller, test_name, arguments={}, test_dir="test_screenshots"):
    """Capture a screenshot with detailed information in the filename."""
    print(f"Capturing {test_name}...")
    
    # Take screenshot
    result = await controller.take_screenshot(arguments)
    
    if "error" in result:
        print(f"  ✗ {test_name} failed: {result['error']}")
        # Create error log file
        timestamp = get_timestamp()
        error_filename = f"{test_dir}/{timestamp}_{test_name.replace(' ', '_')}_ERROR.txt"
        with open(error_filename, "w") as f:
            f.write(f"Error: {result['error']}\n")
            f.write(f"Arguments: {json.dumps(arguments, indent=2)}\n")
        print(f"  Error logged to: {error_filename}")
        return False
    else:
        # Parse result details
        format_ext = result['format'] if result['format'] != 'jpg' else 'jpeg'
        width = result['size']['width']
        height = result['size']['height']
        monitor = result['monitor']
        platform_name = result['platform']
        
        # Get timestamp for filename
        timestamp = get_timestamp()
        
        # Create descriptive filename
        filename = f"{test_dir}/{timestamp}_{test_name.replace(' ', '_')}_M{monitor}_{width}x{height}.{format_ext}"
        
        # Save screenshot
        try:
            # Decode base64 data
            img_binary = base64.b64decode(result['data'])
            
            with open(filename, "wb") as f:
                f.write(img_binary)
                
            print(f"  ✓ {test_name} saved: {os.path.basename(filename)}")
            print(f"    Size: {width}x{height}, Format: {format_ext}, Monitor: {monitor}")
            
            # Also save metadata
            metadata = {
                "timestamp": timestamp,
                "test_name": test_name,
                "arguments": arguments,
                "result": {
                    "format": result['format'],
                    "size": result['size'],
                    "monitor": result['monitor'],
                    "platform": result['platform']
                },
                "filename": os.path.basename(filename)
            }
            
            metadata_filename = filename.replace(f".{format_ext}", f"_metadata.json")
            with open(metadata_filename, "w") as f:
                json.dump(metadata, f, indent=2)
                
            return True
        except Exception as e:
            print(f"  ✗ Failed to save {test_name}: {e}")
            return False

def get_monitor_info(controller):
    """Get detailed monitor information."""
    try:
        monitors = controller.get_monitor_layout()
        return monitors
    except:
        # Fallback monitor info
        return [
            {"id": 0, "name": "eDP-1", "x": 0, "y": 876, "width": 1366, "height": 768},
            {"id": 1, "name": "HDMI-1", "x": 1366, "y": 0, "width": 1080, "height": 1920}
        ]

async def main():
    """Run comprehensive screenshot tests."""
    print("Running comprehensive screenshot tests...")
    print("=" * 60)
    
    # Create test directory if it doesn't exist
    test_dir = "test_screenshots"
    os.makedirs(test_dir, exist_ok=True)
    
    # Get monitor information
    print("Getting monitor information...")
    controller = DesktopController()
    monitors = get_monitor_info(controller)
    print(f"Detected {len(monitors)} monitors:")
    for i, monitor in enumerate(monitors):
        print(f"  Monitor {i}: {monitor['name']} at ({monitor['x']}, {monitor['y']}) - {monitor['width']}x{monitor['height']}")
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Combined screenshot of all monitors
    total_tests += 1
    if await capture_screenshot_with_details(controller, "Combined_All_Monitors", {"monitor": 0}, test_dir):
        success_count += 1
    
    # Test 2: Individual monitor screenshots
    for i, monitor in enumerate(monitors):
        total_tests += 1
        monitor_args = {"monitor": i + 1}  # 1-indexed for individual monitors
        test_name = f"Monitor_{i}_{monitor['name']}"
        if await capture_screenshot_with_details(controller, test_name, monitor_args, test_dir):
            success_count += 1
    
    # Test 3: Different formats
    formats = ["png", "jpeg"]
    for fmt in formats:
        total_tests += 1
        args = {"format": fmt, "monitor": 0}
        if fmt == "jpeg":
            args["quality"] = 75
        test_name = f"Combined_{fmt.upper()}_Format"
        if await capture_screenshot_with_details(controller, test_name, args, test_dir):
            success_count += 1
    
    # Test 4: Individual monitors with different formats
    for i, monitor in enumerate(monitors):
        for fmt in formats:
            total_tests += 1
            args = {"format": fmt, "monitor": i + 1}
            if fmt == "jpeg":
                args["quality"] = 75
            test_name = f"Monitor_{i}_{monitor['name']}_{fmt.upper()}"
            if await capture_screenshot_with_details(controller, test_name, args, test_dir):
                success_count += 1
    
    print("=" * 60)
    print(f"Test Results: {success_count}/{total_tests} tests successful")
    
    # Create summary report
    timestamp = get_timestamp()
    summary_file = f"{test_dir}/test_summary_{timestamp}.txt"
    with open(summary_file, "w") as f:
        f.write("Screenshot Test Summary\n")
        f.write("=" * 30 + "\n")
        f.write(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"Successful Tests: {success_count}\n")
        f.write(f"Failed Tests: {total_tests - success_count}\n")
        f.write("\nMonitor Information:\n")
        for i, monitor in enumerate(monitors):
            f.write(f"  Monitor {i}: {monitor['name']} at ({monitor['x']}, {monitor['y']}) - {monitor['width']}x{monitor['height']}\n")
        f.write("\nFiles Generated:\n")
        for filename in sorted(os.listdir(test_dir)):
            if filename.endswith(('.png', '.jpeg', '.jpg')):
                f.write(f"  {filename}\n")
    
    print(f"Summary report saved to: {os.path.basename(summary_file)}")
    print("Check the test_screenshots directory for all captured images.")
    
    return 0 if success_count == total_tests else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))