# Desktop Access MCP Server - LLM Agent Guide

This guide explains how LLM agents can use the Desktop Access MCP Server as their "eyes and hands" to interact with desktop environments.

## Overview

The Desktop Access MCP Server provides three core capabilities to LLM agents:

1. **Eyes** - Take screenshots of the desktop to understand the current state
2. **Hands** - Simulate keyboard and mouse input to interact with applications
3. **Multi-monitor support** - Work with single or multiple monitor setups

## Available Tools

### 1. `take_screenshot`

Capture a screenshot of the desktop for visual understanding.

**Parameters:**
- `format` (string, optional): Image format - "png" or "jpeg" (default: "png")
- `quality` (integer, optional): JPEG quality 1-100 (default: 85, only for jpeg format)
- `monitor` (integer, optional): Monitor index (0 for all monitors, 1+ for specific monitor, default: 0)

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `format` (string): Image format used
- `data` (string): Base64-encoded image data
- `size` (object): Image dimensions {width, height}
- `monitor` (integer): Monitor index used

**Example Usage:**
```json
{
  "name": "take_screenshot",
  "arguments": {
    "format": "jpeg",
    "quality": 75
  }
}
```

### 2. `keyboard_input`

Simulate keyboard input to type text or press key combinations.

**Parameters:**
- `text` (string, optional): Text to type
- `key_combination` (string, optional): Key combination to press (e.g., "ctrl+c")
- `delay` (number, optional): Delay between key presses in seconds (default: 0.01, only for text)

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `action` (string): Action performed ("type" or "key_combination")
- Additional action-specific details

**Example Usage:**
```json
{
  "name": "keyboard_input",
  "arguments": {
    "text": "Hello World",
    "delay": 0.1
  }
}
```

```json
{
  "name": "keyboard_input",
  "arguments": {
    "key_combination": "ctrl+v"
  }
}
```

### 3. `mouse_action`

Perform mouse actions to interact with the desktop.

**Parameters:**
- `action` (string, required): Mouse action to perform
  - "move": Move mouse cursor
  - "click": Click mouse button
  - "double_click": Double-click mouse button
  - "right_click": Right-click mouse button
  - "scroll": Scroll vertically
  - "drag": Drag from one position to another
- `x`, `y` (number, optional): Coordinates for move action
- `scroll_amount` (number, optional): Scroll amount (positive = up, negative = down)
- `button` (string, optional): Mouse button - "left", "right", or "middle" (default: "left")
- `from_x`, `from_y`, `to_x`, `to_y` (number, optional): Coordinates for drag action
- `duration` (number, optional): Duration for drag action in seconds (default: 1.0)

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `action` (string): Action performed
- Additional action-specific details

**Example Usage:**
```json
{
  "name": "mouse_action",
  "arguments": {
    "action": "move",
    "x": 100,
    "y": 200
  }
}
```

```json
{
  "name": "mouse_action",
  "arguments": {
    "action": "click",
    "button": "left"
  }
}
```

```json
{
  "name": "mouse_action",
  "arguments": {
    "action": "drag",
    "from_x": 100,
    "from_y": 100,
    "to_x": 200,
    "to_y": 200,
    "duration": 0.5
  }
}
```

## Typical LLM Agent Workflow

1. **Observe**: Take a screenshot to understand the current desktop state
2. **Analyze**: Process the screenshot to identify UI elements and targets
3. **Plan**: Determine the next action based on the goal
4. **Act**: Execute keyboard or mouse actions
5. **Verify**: Take another screenshot to confirm the action's effect
6. **Repeat**: Continue until the goal is achieved

## Example Use Cases

### Web Browsing
```
1. Take screenshot -> Identify browser window
2. Move mouse to URL bar -> Click -> Type URL -> Press Enter
3. Take screenshot -> Verify page loaded
4. Find search box -> Type query -> Submit
```

### Document Editing
```
1. Take screenshot -> Locate text editor
2. Type text with appropriate delays
3. Use key combinations (Ctrl+S) to save
4. Take screenshot -> Verify document saved
```

### File Management
```
1. Take screenshot -> Find file explorer
2. Navigate to directory
3. Select file -> Right-click -> Choose action
4. Confirm action in dialog box
```

## Best Practices for LLM Agents

1. **Use appropriate delays**: When typing, use small delays (0.01-0.1s) to simulate human typing
2. **Verify actions**: Always take a screenshot after important actions to confirm they worked
3. **Handle errors gracefully**: Check for error responses and adapt behavior accordingly
4. **Be precise with coordinates**: For mouse actions, use coordinates based on screenshot analysis
5. **Use key combinations**: Leverage shortcuts (Ctrl+C, Ctrl+V, etc.) for efficiency
6. **Work with monitors**: Use monitor-specific screenshots when working with multi-monitor setups

## Error Handling

All tools will return an error response if something goes wrong:
```json
{
  "error": "Description of what went wrong"
}
```

Common errors include:
- Invalid parameters
- Permission issues (especially for screenshot/input on some systems)
- System resource limitations

When an error occurs, the agent should either:
1. Try a different approach
2. Ask for human assistance
3. Retry the operation
4. Abort the task

## System Requirements

- **Operating Systems**: Linux, macOS, or Windows
- **Display Server**: X11 or Wayland (Linux), Aqua (macOS), or Windows Display Driver
- **Permissions**: Appropriate permissions for screen capture and input simulation
- **Dependencies**: Python 3.8+, Pillow, pynput, mss

## Security Considerations

- The server has full access to the desktop environment
- Keyboard and mouse input simulation can execute any action
- Screenshots may contain sensitive information
- Access should be restricted to trusted LLM agents only