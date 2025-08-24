import asyncio
import logging
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .desktop_controller import DesktopController

# Set up logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "mcp-puppeteer.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Desktop Access MCP Server."""
    logger.info("Starting Desktop Access MCP Server")
    
    # Create the server
    server = Server("desktop-access-mcp-server")
    controller = DesktopController()
    
    # Register tools
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        try:
            if name == "take_screenshot":
                return await controller.take_screenshot(arguments)
            elif name == "keyboard_input":
                return await controller.keyboard_input(arguments)
            elif name == "mouse_action":
                return await controller.mouse_action(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            # Return error in MCP format
            return {"error": str(e)}
    
    # Define the tools the server provides
    tools = [
        Tool(
            name="take_screenshot",
            description="Take a screenshot of the desktop",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["png", "jpeg"],
                        "description": "Image format for the screenshot (default: png)"
                    },
                    "quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "JPEG quality (1-100, only applies to jpeg format, default: 85)"
                    },
                    "monitor": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Monitor index (0 for all monitors, default: 0)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="keyboard_input",
            description="Simulate keyboard input",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    },
                    "key_combination": {
                        "type": "string",
                        "description": "Key combination to press (e.g., 'ctrl+c')"
                    },
                    "delay": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Delay between key presses in seconds (for text, default: 0.01)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="mouse_action",
            description="Perform mouse actions",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["move", "click", "double_click", "right_click", "scroll", "drag"],
                        "description": "Mouse action to perform"
                    },
                    "x": {
                        "type": "number",
                        "description": "X coordinate for move action"
                    },
                    "y": {
                        "type": "number",
                        "description": "Y coordinate for move action"
                    },
                    "scroll_amount": {
                        "type": "number",
                        "description": "Amount to scroll (positive for up, negative for down)"
                    },
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "middle"],
                        "description": "Mouse button for click actions (default: left)"
                    },
                    "from_x": {
                        "type": "number",
                        "description": "Starting X coordinate for drag action"
                    },
                    "from_y": {
                        "type": "number",
                        "description": "Starting Y coordinate for drag action"
                    },
                    "to_x": {
                        "type": "number",
                        "description": "Ending X coordinate for drag action"
                    },
                    "to_y": {
                        "type": "number",
                        "description": "Ending Y coordinate for drag action"
                    },
                    "duration": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Duration for drag action in seconds (default: 1.0)"
                    }
                },
                "required": ["action"]
            }
        )
    ]
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.list_tools,
            tools,
            server.call_tool
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)