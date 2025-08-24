# Desktop Access MCP Server - Usage Guide

## Installation

To install the package:

```bash
# Build the package
python -m build

# Install the package
pip install dist/desktop_access_mcp_server-0.1.0-py3-none-any.whl
```

Or for development:

```bash
pip install -e .
```

## Running the Server

### Method 1: Direct execution (after installation)
```bash
desktop-access-mcp-server
```

### Method 2: Using uvx (without installation)
```bash
uvx --from desktop-access-mcp-server desktop-access-mcp-server
```

## JSON Configuration for MCP Clients

### Claude Desktop Configuration

To use this server with Claude Desktop, add the following to your MCP configuration file:

```json
{
  "mcpServers": {
    "desktop-access": {
      "command": "uvx",
      "args": [
        "--from",
        "desktop-access-mcp-server",
        "desktop-access-mcp-server"
      ]
    }
  }
}
```

If you have installed the package locally, you can use the direct command instead:

```json
{
  "mcpServers": {
    "desktop-access": {
      "command": "desktop-access-mcp-server"
    }
  }
}
```

### Generic MCP Client Configuration

For other MCP clients that use JSON configuration files, the general format is:

```json
{
  "mcpServers": {
    "desktop-access": {
      "command": "uvx",
      "args": [
        "--from",
        "desktop-access-mcp-server",
        "desktop-access-mcp-server"
      ]
    }
  }
}
```

### Configuration File Locations

- **Claude Desktop**: `~/Library/Application Support/Claude/mcp-config.json` (macOS) or `%APPDATA%\Claude\mcp-config.json` (Windows)
- **Generic MCP Clients**: Check your client's documentation for the configuration file location

## Using with MCP Clients

Once the server is running, you can connect to it using any MCP-compliant client:

### Method 1: Direct execution (after installation)
```python
# Example with Python MCP client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="desktop-access-mcp-server"
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Take a screenshot
        screenshot = await session.call_tool("take_screenshot", {
            "format": "jpeg",
            "quality": 85
        })
        
        # Type text
        await session.call_tool("keyboard_input", {
            "text": "Hello from LLM!",
            "delay": 0.05
        })
```

### Method 2: Using uvx (without installation)
```python
# Example with Python MCP client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command=["uvx", "--from", "desktop-access-mcp-server", "desktop-access-mcp-server"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Take a screenshot
        screenshot = await session.call_tool("take_screenshot", {
            "format": "jpeg",
            "quality": 85
        })
        
        # Type text
        await session.call_tool("keyboard_input", {
            "text": "Hello from LLM!",
            "delay": 0.05
        })
```

## Available Tools

### `take_screenshot`
Capture a screenshot of the desktop for visual understanding.

**Parameters:**
- `format`: Image format (`png` or `jpeg`) - default: `png`
- `quality`: JPEG quality (1-100) - default: 85
- `monitor`: Monitor index (0=all, 1+=specific) - default: 0

### `keyboard_input`
Simulate keyboard input to type text or press key combinations.

**Parameters:**
- `text`: Text to type
- `key_combination`: Key combination (e.g., `ctrl+c`)
- `delay`: Delay between key presses (seconds) - default: 0.01

### `mouse_action`
Perform mouse actions to interact with the desktop.

**Parameters:**
- `action`: Mouse action (`move`, `click`, `double_click`, `right_click`, `scroll`, `drag`)
- `x`, `y`: Coordinates for move action
- `scroll_amount`: Amount to scroll
- `button`: Mouse button (`left`, `right`, `middle`) - default: `left`
- `from_x`, `from_y`, `to_x`, `to_y`: Coordinates for drag action
- `duration`: Duration for drag action (seconds) - default: 1.0

## CLI Interface

The package also includes a comprehensive CLI for testing:

```bash
# Screenshot commands
desktop-cli screenshot -o screenshot.png
desktop-cli screenshot -f jpeg -q 90 -m 1 -o monitor1.jpg

# Keyboard commands
desktop-cli keyboard -t "Type this text" -d 0.1
desktop-cli keyboard -c "ctrl+c"

# Mouse commands
desktop-cli mouse move -x 100 -y 200
desktop-cli mouse click -b left
desktop-cli mouse scroll -a 5
desktop-cli mouse drag --from-x 100 --from-y 100 --to-x 200 --to-y 200
```