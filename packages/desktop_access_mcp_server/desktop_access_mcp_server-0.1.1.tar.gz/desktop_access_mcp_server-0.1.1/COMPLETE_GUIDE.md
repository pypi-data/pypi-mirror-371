# Desktop Access MCP Server - Complete Guide

## Overview

The Desktop Access MCP Server is a Python-based Model Context Protocol (MCP) server that provides comprehensive desktop access capabilities to LLM agents, enabling them to see and interact with desktop environments through screenshots and input simulation.

## Features

### Eyes - Visual Perception
- Full Desktop Screenshots in PNG or JPEG formats
- Multi-Monitor Support - Capture individual monitors or combined view
- Configurable Quality - Adjust JPEG compression for balance of size and quality
- Base64 Encoding - Ready for direct LLM consumption

### Hands - Input Control
- Keyboard Simulation:
  - Type text with configurable delays
  - Execute key combinations (Ctrl+C, Alt+Tab, etc.)
- Mouse Control:
  - Move cursor to precise coordinates
  - Click, double-click, and right-click
  - Scroll vertically
  - Drag from one point to another

## Installation

### From Source (Development)
```bash
git clone https://github.com/your-username/desktop-access-mcp-server.git
cd desktop-access-mcp-server
pip install -e .
```

### Dependencies
- Python 3.8+
- mcp>=1.0.0
- Pillow>=9.0.0
- pynput>=1.7.0
- mss>=9.0.0

## Usage

### As an MCP Server
```bash
desktop-access-mcp-server
```

### Command Line Interface
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

## MCP Tools API

### `take_screenshot`
Capture a screenshot of the desktop for visual understanding.

Parameters:
- `format`: Image format (png or jpeg, default: png)
- `quality`: JPEG quality (1-100, default: 85)
- `monitor`: Monitor index (0=all, 1+=specific, default: 0)

### `keyboard_input`
Simulate keyboard input to type text or press key combinations.

Parameters:
- `text`: Text to type
- `key_combination`: Key combo (e.g., ctrl+c)
- `delay`: Delay between key presses (seconds, default: 0.01)

### `mouse_action`
Perform mouse actions to interact with the desktop.

Parameters:
- `action`: move, click, double_click, right_click, scroll, drag
- `x`, `y`: Coordinates for move action
- `scroll_amount`: Amount to scroll
- `button`: Mouse button (left/right/middle, default: left)
- `from_x`, `from_y`, `to_x`, `to_y`: Coordinates for drag action
- `duration`: Duration for drag action (seconds, default: 1.0)

## Configuration with MCP Clients

### Claude Desktop Configuration
Add to your `claude_desktop_config.json`:
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

## Publishing to PyPI

Follow the instructions in `PUBLISHING_INSTRUCTIONS.md` to publish this package to PyPI.

## Troubleshooting

### Screenshot Issues
- Linux: Ensure X11/Wayland access with `xhost +SI:localuser:$USER`
- macOS: Grant screen recording permissions
- Windows: Run as administrator if needed

### Permission Errors
```bash
# Add user to input group (Linux)
sudo adduser $USER input
```

## Development

### Setup Development Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Code Quality
```bash
# Format code
black .

# Check code style
flake8 .

# Run tests
python -m pytest
```