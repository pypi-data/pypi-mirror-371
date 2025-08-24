#!/usr/bin/env python3
"""
Command-line interface for the Desktop Access MCP Server.

This script provides a simple CLI to test the desktop controller functionality.
"""

import argparse
import asyncio
import base64
import sys
import os

# Add the parent directory to the path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.desktop_controller import DesktopController

async def take_screenshot(args):
    """Take a screenshot and save it to a file."""
    controller = DesktopController()
    
    # Prepare arguments
    arguments = {}
    if args.format:
        arguments["format"] = args.format
    if args.quality:
        arguments["quality"] = args.quality
    if args.monitor is not None:
        arguments["monitor"] = args.monitor
    
    result = await controller.take_screenshot(arguments)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    # Save to file
    filename = args.output or f"screenshot.{result['format']}"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(result["data"]))
    
    print(f"Screenshot saved as {filename}")
    print(f"Size: {result['size']['width']}x{result['size']['height']}")
    print(f"Format: {result['format']}")
    print(f"Monitor: {result['monitor']}")
    return 0

async def keyboard_input(args):
    """Simulate keyboard input."""
    controller = DesktopController()
    
    # Prepare arguments
    arguments = {}
    if args.text:
        arguments["text"] = args.text
        if args.delay is not None:
            arguments["delay"] = args.delay
    elif args.combination:
        arguments["key_combination"] = args.combination
    else:
        print("Error: Either --text or --combination must be specified")
        return 1
    
    result = await controller.keyboard_input(arguments)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    print(f"Keyboard input successful: {result}")
    return 0

async def mouse_action(args):
    """Perform a mouse action."""
    controller = DesktopController()
    
    # Prepare arguments
    arguments = {"action": args.action}
    
    if args.action == "move":
        if args.x is None or args.y is None:
            print("Error: --x and --y must be specified for move action")
            return 1
        arguments["x"] = args.x
        arguments["y"] = args.y
    elif args.action in ["click", "double_click", "right_click"]:
        if args.button:
            arguments["button"] = args.button
    elif args.action == "scroll":
        if args.amount is None:
            print("Error: --amount must be specified for scroll action")
            return 1
        arguments["scroll_amount"] = args.amount
    elif args.action == "drag":
        if args.from_x is None or args.from_y is None or args.to_x is None or args.to_y is None:
            print("Error: --from-x, --from-y, --to-x, and --to-y must be specified for drag action")
            return 1
        arguments["from_x"] = args.from_x
        arguments["from_y"] = args.from_y
        arguments["to_x"] = args.to_x
        arguments["to_y"] = args.to_y
        if args.duration is not None:
            arguments["duration"] = args.duration
    
    result = await controller.mouse_action(arguments)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    print(f"Mouse action successful: {result}")
    return 0

async def main():
    parser = argparse.ArgumentParser(description="Desktop Access MCP Server CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Screenshot command
    screenshot_parser = subparsers.add_parser("screenshot", help="Take a screenshot")
    screenshot_parser.add_argument("-o", "--output", help="Output filename (default: screenshot.<format>)")
    screenshot_parser.add_argument("-f", "--format", choices=["png", "jpeg"], help="Image format (default: png)")
    screenshot_parser.add_argument("-q", "--quality", type=int, help="JPEG quality (1-100, only for jpeg format)")
    screenshot_parser.add_argument("-m", "--monitor", type=int, help="Monitor index (0 for all monitors)")
    
    # Keyboard command
    keyboard_parser = subparsers.add_parser("keyboard", help="Simulate keyboard input")
    keyboard_parser.add_argument("-t", "--text", help="Text to type")
    keyboard_parser.add_argument("-c", "--combination", help="Key combination to press (e.g., 'ctrl+c')")
    keyboard_parser.add_argument("-d", "--delay", type=float, help="Delay between key presses in seconds (for text)")
    
    # Mouse command
    mouse_parser = subparsers.add_parser("mouse", help="Perform mouse action")
    mouse_parser.add_argument("action", choices=["move", "click", "double_click", "right_click", "scroll", "drag"], 
                             help="Mouse action to perform")
    mouse_parser.add_argument("-x", type=float, help="X coordinate for move action")
    mouse_parser.add_argument("-y", type=float, help="Y coordinate for move action")
    mouse_parser.add_argument("-a", "--amount", type=float, help="Scroll amount for scroll action")
    mouse_parser.add_argument("-b", "--button", choices=["left", "right", "middle"], help="Mouse button for click actions")
    mouse_parser.add_argument("--from-x", type=float, help="Starting X coordinate for drag action")
    mouse_parser.add_argument("--from-y", type=float, help="Starting Y coordinate for drag action")
    mouse_parser.add_argument("--to-x", type=float, help="Ending X coordinate for drag action")
    mouse_parser.add_argument("--to-y", type=float, help="Ending Y coordinate for drag action")
    mouse_parser.add_argument("--duration", type=float, help="Duration for drag action in seconds")
    
    args = parser.parse_args()
    
    if args.command == "screenshot":
        return await take_screenshot(args)
    elif args.command == "keyboard":
        return await keyboard_input(args)
    elif args.command == "mouse":
        return await mouse_action(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))