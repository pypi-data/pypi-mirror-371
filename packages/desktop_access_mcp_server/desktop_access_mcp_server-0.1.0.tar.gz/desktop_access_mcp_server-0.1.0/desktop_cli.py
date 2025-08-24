#!/usr/bin/env python3
"""
Command-line interface for the Desktop Access MCP Server.

This script provides a simple CLI to test the desktop controller functionality.
"""

import argparse
import asyncio
import base64
import sys
from desktop_access_mcp_server.desktop_controller import DesktopController

async def take_screenshot(args):
    """Take a screenshot and save it to a file."""
    controller = DesktopController()
    result = await controller.take_screenshot({})
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    # Save to file
    filename = args.output or "screenshot.png"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(result["data"]))
    
    print(f"Screenshot saved as {filename}")
    print(f"Size: {result['size']['width']}x{result['size']['height']}")
    return 0

async def keyboard_input(args):
    """Simulate keyboard input."""
    controller = DesktopController()
    
    if args.text:
        result = await controller.keyboard_input({"text": args.text})
    elif args.combination:
        result = await controller.keyboard_input({"key_combination": args.combination})
    else:
        print("Error: Either --text or --combination must be specified")
        return 1
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    print(f"Keyboard input successful: {result}")
    return 0

async def mouse_action(args):
    """Perform a mouse action."""
    controller = DesktopController()
    
    if args.action == "move":
        if args.x is None or args.y is None:
            print("Error: --x and --y must be specified for move action")
            return 1
        result = await controller.mouse_action({"action": "move", "x": args.x, "y": args.y})
    elif args.action in ["click", "double_click", "right_click"]:
        result = await controller.mouse_action({"action": args.action})
    elif args.action == "scroll":
        if args.amount is None:
            print("Error: --amount must be specified for scroll action")
            return 1
        result = await controller.mouse_action({"action": "scroll", "scroll_amount": args.amount})
    else:
        print(f"Error: Unknown action {args.action}")
        return 1
    
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
    screenshot_parser.add_argument("-o", "--output", help="Output filename (default: screenshot.png)")
    
    # Keyboard command
    keyboard_parser = subparsers.add_parser("keyboard", help="Simulate keyboard input")
    keyboard_parser.add_argument("-t", "--text", help="Text to type")
    keyboard_parser.add_argument("-c", "--combination", help="Key combination to press (e.g., 'ctrl+c')")
    
    # Mouse command
    mouse_parser = subparsers.add_parser("mouse", help="Perform mouse action")
    mouse_parser.add_argument("action", choices=["move", "click", "double_click", "right_click", "scroll"], 
                             help="Mouse action to perform")
    mouse_parser.add_argument("-x", type=int, help="X coordinate for move action")
    mouse_parser.add_argument("-y", type=int, help="Y coordinate for move action")
    mouse_parser.add_argument("-a", "--amount", type=int, help="Scroll amount for scroll action")
    
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