# Desktop Access MCP Server - Configuration Guide

This guide explains how to use the Desktop Access MCP Server with uvx and configure it in your MCP client.

## Installation

### Install from PyPI (Recommended)
```bash
pip install desktop-access-mcp-server
```

### Install from local source (for development)
```bash
# Navigate to the project directory
cd /path/to/desktop-access-mcp-server

# Install in development mode
pip install -e .
```

## Using with uvx

uvx allows you to run the server directly from the package without permanent installation. 
Note: uvx requires the package to be published to PyPI or installed locally.

### With locally built package:
```bash
# Install the package locally first
pip install dist/desktop_access_mcp_server-0.1.0-py3-none-any.whl

# Then run the MCP server
uvx desktop-access-mcp-server

# Run the CLI for testing
uvx desktop-cli screenshot -o test.png
```

### With published package (after publishing to PyPI):
```bash
# Run the MCP server directly from PyPI
uvx desktop-access-mcp-server

# Run the CLI for testing
uvx desktop-cli screenshot -o test.png
```

## Configuring with MCP Clients

### Claude Desktop Configuration

To use this server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "desktop-access": {
      "command": "uvx",
      "args": [
        "desktop-access-mcp-server"
      ]
    }
  }
}
```

### Manual Configuration File Location

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Alternative: Direct Binary Path

If you prefer to use the direct binary path instead of uvx:

```json
{
  "mcpServers": {
    "desktop-access": {
      "command": "desktop-access-mcp-server"
    }
  }
}
```

## Testing the Installation

After configuration:

1. Restart your MCP client (e.g., Claude Desktop)
2. The server should automatically connect
3. Test functionality with these tools:
   - `take_screenshot` - Capture desktop screenshots
   - `keyboard_input` - Simulate typing and key combinations
   - `mouse_action` - Control mouse movements and clicks

## CLI Usage Examples

You can also test the server functionality using the CLI:

```bash
# Take a screenshot
desktop-cli screenshot -o screenshot.png

# Take a screenshot of a specific monitor
desktop-cli screenshot -m 1 -o monitor1.png

# Take a JPEG screenshot with quality setting
desktop-cli screenshot -f jpeg -q 90 -o screenshot.jpg

# Type text with a delay between characters
desktop-cli keyboard -t "Hello, World!" -d 0.1

# Press a key combination
desktop-cli keyboard -c "ctrl+c"

# Move mouse to coordinates
desktop-cli mouse move -x 100 -y 200

# Click at current mouse position
desktop-cli mouse click

# Scroll up
desktop-cli mouse scroll -a 5

# Drag from one point to another
desktop-cli mouse drag --from-x 100 --from-y 100 --to-x 200 --to-y 200
```

## Troubleshooting

### Permission Issues

On macOS, you may need to grant screen recording permissions:
1. Open System Preferences
2. Go to Security & Privacy > Privacy
3. Select "Screen Recording" from the left sidebar
4. Add your terminal application (Terminal, iTerm, etc.) to the list

On Linux, ensure you have access to the display server:
```bash
# For X11
xhost +SI:localuser:$USER

# For Wayland, you may need to set:
export WAYLAND_DISPLAY=wayland-0
```

### Installation Issues

If you encounter issues with the installation, try:
```bash
pip install --upgrade pip
pip install --force-reinstall desktop-access-mcp-server
```

### Running with Debug Logging

To see detailed logs:
```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG
uvx desktop-access-mcp-server
```