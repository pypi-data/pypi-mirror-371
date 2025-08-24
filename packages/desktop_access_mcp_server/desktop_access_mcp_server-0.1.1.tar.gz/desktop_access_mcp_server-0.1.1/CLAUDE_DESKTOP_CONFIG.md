# Claude Desktop MCP Configuration Guide

This guide explains how to configure the Desktop Access MCP Server with Claude Desktop to enable visual and input capabilities for Claude.

## Prerequisites

1. Install Claude Desktop from [Anthropic's website](https://claude.ai/download)
2. Ensure Python 3.8+ is installed on your system
3. Install uvx (part of uv package) or install this package locally

## Configuration Steps

### Step 1: Locate the Configuration File

Claude Desktop uses a JSON configuration file to manage MCP servers:

- **macOS**: `~/Library/Application Support/Claude/mcp-config.json`
- **Windows**: `%APPDATA%\Claude\mcp-config.json`
- **Linux**: `~/.config/Claude/mcp-config.json`

### Step 2: Create or Edit the Configuration File

If the file doesn't exist, create it. Add the Desktop Access MCP Server configuration:

#### Option 1: Using uvx (No Installation Required)

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

#### Option 2: After Installing the Package

First install the package:
```bash
# Build the package
python -m build

# Install the package
pip install dist/desktop_access_mcp_server-0.1.0-py3-none-any.whl
```

Then use the direct command in the configuration:
```json
{
  "mcpServers": {
    "desktop-access": {
      "command": "desktop-access-mcp-server"
    }
  }
}
```

### Step 3: Restart Claude Desktop

After saving the configuration file, restart Claude Desktop to load the new MCP server.

## Verification

To verify the configuration is working:

1. Open Claude Desktop
2. Start a new conversation
3. Ask Claude to take a screenshot:
   - "Can you take a screenshot of my desktop?"
   - "Show me what you see on my screen"

If configured correctly, Claude should be able to capture and describe your desktop.

## Available Capabilities

Once configured, Claude can:

### Visual Perception
- Take screenshots of your entire desktop or specific monitors
- Capture images in PNG or JPEG formats
- View your screen to understand visual context

### Input Control
- Type text in any application
- Execute keyboard shortcuts (Ctrl+C, Alt+Tab, etc.)
- Move and click the mouse
- Scroll through pages
- Drag and drop elements

## Example Prompts

Try these prompts to test the capabilities:

1. **Screenshot**: "Take a screenshot of my desktop and describe what you see"
2. **Typing**: "Type 'Hello from Claude!' in the current text editor"
3. **Navigation**: "Press Alt+Tab to switch to the next application"
4. **Mouse Control**: "Click on the center of the screen"
5. **Complex Task**: "Take a screenshot, then open a text editor and type a description of what you saw"

## Troubleshooting

### Common Issues

1. **Server Not Found**: Ensure the command is accessible in your system PATH
2. **Permission Errors**: Grant screen recording and input monitoring permissions to Claude Desktop
3. **Python Dependencies**: Make sure all required Python packages are installed

### Permission Requirements

- **macOS**: Grant screen recording and accessibility permissions
- **Windows**: Run as administrator or grant input simulation permissions
- **Linux**: Add user to input group and ensure X11/Wayland access

### Debugging

To test the server independently:
```bash
# Test with uvx
uvx --from desktop-access-mcp-server desktop-access-mcp-server

# Or test with direct execution (if installed)
desktop-access-mcp-server
```

## Security Considerations

⚠️ **Important**: This server provides full desktop access capabilities. Only use it with trusted LLMs and be cautious about granting access to sensitive information or systems.

- The server can capture screenshots of your entire desktop
- The server can simulate keyboard and mouse input
- Always review prompts before allowing complex interactions
- Consider using a separate user account for sensitive tasks

## Advanced Configuration

### Multiple Monitor Setup

The server supports multiple monitors. You can specify which monitor to capture:
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

Then use the monitor parameter in requests:
- Monitor 0: All monitors combined (default)
- Monitor 1: First monitor
- Monitor 2: Second monitor, etc.

### Custom Quality Settings

Adjust screenshot quality for bandwidth considerations:
```prompt
"Take a screenshot with JPEG quality 70"
```

## Support

For issues with the Desktop Access MCP Server, please check:
- GitHub repository issues
- Ensure all dependencies are correctly installed
- Verify Python version compatibility (3.8+)