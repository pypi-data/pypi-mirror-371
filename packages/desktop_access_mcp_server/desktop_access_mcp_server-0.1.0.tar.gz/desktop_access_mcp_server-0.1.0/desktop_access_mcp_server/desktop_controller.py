import base64
from io import BytesIO
from typing import Dict, Any
import asyncio
import platform
import subprocess
import tempfile
import os
from PIL import Image
from pynput import keyboard, mouse
import logging

logger = logging.getLogger(__name__)

class DesktopController:
    """Controller for desktop interactions including screenshots and input simulation."""
    
    def __init__(self):
        """Initialize the desktop controller."""
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
        self.platform = platform.system().lower()
        
    def get_monitor_layout(self):
        """Get detailed monitor layout information."""
        return self._get_monitor_info()
        
    def _get_monitor_info(self):
        """Get monitor layout information."""
        try:
            # Try different methods to get monitor info
            if self.platform == "linux":
                # Try xrandr first
                if self._is_command_available("xrandr"):
                    result = subprocess.run(["xrandr"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return self._parse_xrandr_output(result.stdout)
                        
                # Try wlr-randr for Wayland
                if self._is_command_available("wlr-randr"):
                    result = subprocess.run(["wlr-randr"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return self._parse_wlr_randr_output(result.stdout)
                        
            # Fallback monitor info
            return [
                {"id": 0, "name": "eDP-1", "x": 0, "y": 876, "width": 1366, "height": 768},
                {"id": 1, "name": "HDMI-1", "x": 1366, "y": 0, "width": 1080, "height": 1920}
            ]
        except Exception as e:
            logger.warning(f"Could not get monitor info: {e}")
            return []
            
    def _parse_xrandr_output(self, output):
        """Parse xrandr output to get monitor positions."""
        monitors = []
        lines = output.split('\n')
        
        for line in lines:
            if " connected" in line and " disconnected" not in line:
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    # Find resolution and position info
                    for part in parts:
                        if 'x' in part and '+' in part:
                            try:
                                # Parse something like "1920x1080+0+0"
                                res_pos = part
                                res_part, pos_part = res_pos.split('+', 1)
                                width, height = res_part.split('x')
                                x, y = pos_part.split('+') if '+' in pos_part else (pos_part, '0')
                                monitors.append({
                                    "id": len(monitors),
                                    "name": name,
                                    "x": int(x),
                                    "y": int(y),
                                    "width": int(width),
                                    "height": int(height)
                                })
                                break
                            except (ValueError, IndexError):
                                continue
        return monitors
        
    def _parse_wlr_randr_output(self, output):
        """Parse wlr-randr output to get monitor positions."""
        monitors = []
        lines = output.split('\n')
        current_monitor = None
        
        for line in lines:
            if line.startswith("Output "):
                if current_monitor:
                    monitors.append(current_monitor)
                name = line.split()[1].rstrip(':')
                current_monitor = {"id": len(monitors), "name": name, "x": 0, "y": 0, "width": 1920, "height": 1080}
            elif current_monitor and "Position:" in line:
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "X:" and i + 1 < len(parts):
                            current_monitor["x"] = int(parts[i + 1].rstrip(','))
                        elif part == "Y:" and i + 1 < len(parts):
                            current_monitor["y"] = int(parts[i + 1])
                except (ValueError, IndexError):
                    pass
            elif current_monitor and "Current Mode:" in line:
                try:
                    # Extract resolution from something like "1920x1080"
                    mode_part = line.split("Current Mode:")[1].strip()
                    if 'x' in mode_part:
                        width_height = mode_part.split('x')
                        current_monitor["width"] = int(width_height[0])
                        # Handle extra info after height
                        height_str = width_height[1].split()[0]
                        current_monitor["height"] = int(height_str)
                except (ValueError, IndexError):
                    pass
        
        if current_monitor:
            monitors.append(current_monitor)
            
        return monitors
        
    def _capture_screenshot_combined(self):
        """Capture screenshot by combining individual monitor screenshots."""
        try:
            # Try to get monitor information
            monitors = self._get_monitor_info()
            logger.info(f"Detected monitors: {monitors}")
            
            if not monitors or len(monitors) == 0:
                # Fallback to single screenshot
                return self._capture_single_screenshot()
                
            # Capture each monitor
            monitor_images = []
            for i, monitor in enumerate(monitors):
                try:
                    img = self._capture_monitor_screenshot(monitor)
                    monitor_images.append({
                        "image": img,
                        "x": monitor["x"],
                        "y": monitor["y"],
                        "width": monitor["width"],
                        "height": monitor["height"]
                    })
                except Exception as e:
                    logger.warning(f"Failed to capture monitor {i}: {e}")
                    continue
            
            if len(monitor_images) == 0:
                # Fallback if no monitors captured
                return self._capture_single_screenshot()
                
            if len(monitor_images) == 1:
                # Just one monitor, return directly
                return monitor_images[0]["image"]
                
            # Combine all monitor images
            return self._combine_monitor_images(monitor_images)
            
        except Exception as e:
            logger.error(f"Error in combined screenshot: {e}")
            # Ultimate fallback
            return self._capture_single_screenshot()
            
    def _capture_monitor_screenshot(self, monitor_info):
        """Capture screenshot of a specific monitor."""
        # For Linux, try different methods
        if self.platform == "linux":
            # Try grim for Wayland (individual monitor)
            if self._is_command_available("grim"):
                try:
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                    
                    # Try to capture specific monitor by name
                    monitor_name = monitor_info.get("name", f"monitor_{monitor_info['id']}")
                    cmd = ["grim", "-o", monitor_name, tmp_path]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        img = Image.open(tmp_path)
                        os.unlink(tmp_path)
                        return img
                    else:
                        # Clean up failed attempt
                        os.unlink(tmp_path)
                        # Try region capture as fallback
                        return self._capture_region_linux(
                            monitor_info["x"], monitor_info["y"], 
                            monitor_info["width"], monitor_info["height"]
                        )
                except Exception as e:
                    logger.warning(f"Grim monitor capture failed: {e}")
                    # Fallback to region capture
                    return self._capture_region_linux(
                        monitor_info["x"], monitor_info["y"], 
                        monitor_info["width"], monitor_info["height"]
                    )
                    
            # Try gnome-screenshot with area selection
            elif self._is_command_available("gnome-screenshot"):
                try:
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                    
                    # Use area selection (this would require manual interaction)
                    # For automated testing, we'll use region capture instead
                    return self._capture_region_linux(
                        monitor_info["x"], monitor_info["y"], 
                        monitor_info["width"], monitor_info["height"]
                    )
                except Exception as e:
                    logger.warning(f"Gnome-screenshot monitor capture failed: {e}")
                    
        # Fallback to region capture
        return self._capture_region_linux(
            monitor_info["x"], monitor_info["y"], 
            monitor_info["width"], monitor_info["height"]
        )
        
    def _capture_region_linux(self, x, y, width, height):
        """Capture a specific region on Linux."""
        # Try grim with region first
        if self._is_command_available("grim"):
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                # Use grim with geometry: x,y widthxheight
                cmd = ["grim", "-g", f"{x},{y} {width}x{height}", tmp_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    img = Image.open(tmp_path)
                    os.unlink(tmp_path)
                    return img
                else:
                    os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Grim region capture failed: {e}")
                
        # Try xwd + convert
        if self._is_command_available("xwd") and self._is_command_available("convert"):
            try:
                with tempfile.NamedTemporaryFile(suffix=".xwd", delete=False) as tmp_file:
                    xwd_path = tmp_file.name
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    png_path = tmp_file.name
                
                # Capture XWD
                result = subprocess.run(["xwd", "-root", "-silent", "-out", xwd_path], 
                                      capture_output=True, timeout=10)
                if result.returncode == 0:
                    # Convert and crop
                    crop_cmd = ["convert", xwd_path, "-crop", f"{width}x{height}+{x}+{y}", png_path]
                    crop_result = subprocess.run(crop_cmd, capture_output=True, timeout=10)
                    if crop_result.returncode == 0:
                        img = Image.open(png_path)
                        # Clean up
                        os.unlink(xwd_path)
                        os.unlink(png_path)
                        return img
                    else:
                        # Clean up
                        os.unlink(xwd_path)
                        if os.path.exists(png_path):
                            os.unlink(png_path)
                else:
                    # Clean up
                    if os.path.exists(xwd_path):
                        os.unlink(xwd_path)
            except Exception as e:
                logger.warning(f"XWD/convert region capture failed: {e}")
                
        # Ultimate fallback: full screenshot and crop
        full_img = self._capture_single_screenshot()
        return full_img.crop((x, y, x + width, y + height))
        
    def _combine_monitor_images(self, monitor_images):
        """Combine multiple monitor images into one."""
        try:
            # Calculate combined image dimensions
            min_x = min(img["x"] for img in monitor_images)
            min_y = min(img["y"] for img in monitor_images)
            max_x = max(img["x"] + img["width"] for img in monitor_images)
            max_y = max(img["y"] + img["height"] for img in monitor_images)
            
            combined_width = max_x - min_x
            combined_height = max_y - min_y
            
            # Create combined image
            combined_image = Image.new("RGB", (combined_width, combined_height), (0, 0, 0))
            
            # Paste each monitor image at its correct position
            for img_info in monitor_images:
                x_offset = img_info["x"] - min_x
                y_offset = img_info["y"] - min_y
                combined_image.paste(img_info["image"], (x_offset, y_offset))
                
            return combined_image
        except Exception as e:
            logger.error(f"Failed to combine monitor images: {e}")
            # Return first monitor image as fallback
            return monitor_images[0]["image"] if monitor_images else Image.new("RGB", (1920, 1080), (100, 100, 100))
            
    def _capture_single_screenshot(self):
        """Capture a single screenshot using any available method."""
        # Try gnome-screenshot first (native Ubuntu approach)
        if self._is_command_available("gnome-screenshot"):
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                cmd = ["gnome-screenshot", "--file=" + tmp_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    img = Image.open(tmp_path)
                    os.unlink(tmp_path)
                    return img
                else:
                    os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Gnome-screenshot failed: {e}")
                
        # Try grim
        if self._is_command_available("grim"):
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                cmd = ["grim", tmp_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    img = Image.open(tmp_path)
                    os.unlink(tmp_path)
                    return img
                else:
                    os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Grim failed: {e}")
                
        # Try PIL's ImageGrab as last resort
        try:
            from PIL import ImageGrab
            return ImageGrab.grab()
        except Exception as e:
            logger.error(f"PIL ImageGrab failed: {e}")
            # Return a placeholder image
            return Image.new("RGB", (1920, 1080), (100, 100, 100))
            
    def _is_command_available(self, command):
        """Check if a command is available."""
        try:
            subprocess.run(["which", command], capture_output=True, check=True)
            return True
        except:
            return False
            
    async def take_screenshot(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Take a screenshot of the desktop.
        
        Args:
            arguments: Dictionary containing screenshot parameters
                      Supported keys:
                      - format: Image format (png, jpeg) - default: png
                      - quality: JPEG quality (1-100) - default: 85
                      - monitor: Monitor index (0 for all monitors combined) - default: 0
            
        Returns:
            Dictionary with screenshot result
        """
        try:
            # Get parameters
            image_format = arguments.get("format", "png").lower()
            quality = arguments.get("quality", 85)
            monitor_index = arguments.get("monitor", 0)
            
            # Validate format
            if image_format not in ["png", "jpeg", "jpg"]:
                return {"error": f"Unsupported image format: {image_format}. Supported formats: png, jpeg"}
            
            # Validate quality
            if image_format in ["jpeg", "jpg"]:
                if not isinstance(quality, int) or quality < 1 or quality > 100:
                    return {"error": f"Invalid quality value: {quality}. Must be an integer between 1 and 100"}
            
            # Validate monitor index
            if not isinstance(monitor_index, int) or monitor_index < 0:
                return {"error": f"Invalid monitor index: {monitor_index}. Must be a non-negative integer"}
                
            # Capture screenshot based on monitor index
            if monitor_index == 0:
                # Combined screenshot of all monitors
                img = self._capture_screenshot_combined()
            else:
                # Individual monitor screenshot
                monitors = self._get_monitor_info()
                if monitor_index <= len(monitors):
                    img = self._capture_monitor_screenshot(monitors[monitor_index - 1])
                else:
                    # Fallback to combined screenshot
                    img = self._capture_screenshot_combined()
            
            # Convert image mode if needed for JPEG
            if image_format in ["jpeg", "jpg"] and img.mode in ("RGBA", "LA", "P"):
                # Convert to RGB for JPEG
                img = img.convert("RGB")
            
            # Save to memory buffer
            try:
                buffer = BytesIO()
                
                # Save with appropriate format and quality
                if image_format == "png":
                    img.save(buffer, format="PNG")
                else:  # jpeg/jpg
                    img.save(buffer, format="JPEG", quality=quality, optimize=True)
                
                buffer.seek(0)
                
                # Convert to base64 for transmission
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                result = {
                    "success": True,
                    "format": image_format,
                    "data": img_base64,
                    "size": {
                        "width": img.width,
                        "height": img.height
                    },
                    "monitor": monitor_index,
                    "platform": self.platform
                }
                
                logger.info(f"Screenshot taken successfully (format: {image_format}, size: {img.width}x{img.height})")
                return result
            except Exception as e:
                logger.error(f"Failed to encode screenshot: {e}")
                return {"error": f"Failed to encode screenshot: {str(e)}"}
            
        except Exception as e:
            logger.error(f"Unexpected error taking screenshot: {e}")
            return {"error": f"Unexpected error: {str(e)}"}
            
    async def keyboard_input(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate keyboard input.
        
        Args:
            arguments: Dictionary containing keyboard input parameters
                      Supported keys:
                      - text: Text to type
                      - key_combination: Key combination to press (e.g., 'ctrl+c')
                      - delay: Delay between key presses in seconds (for text) - default: 0.01
            
        Returns:
            Dictionary with result
        """
        try:
            text = arguments.get("text")
            key_combination = arguments.get("key_combination")
            delay = arguments.get("delay", 0.01)
            
            # Validate delay
            if not isinstance(delay, (int, float)) or delay < 0:
                return {"error": f"Invalid delay value: {delay}. Must be a non-negative number"}
            
            if text:
                # Type the text with optional delay
                if delay > 0:
                    for char in text:
                        self.keyboard_controller.type(char)
                        await asyncio.sleep(delay)
                else:
                    self.keyboard_controller.type(text)
                    
                logger.info(f"Typed text: {text}")
                return {"success": True, "action": "type", "text": text, "delay": delay}
                
            elif key_combination:
                # Parse and press key combination
                keys = self._parse_key_combination(key_combination)
                if keys:
                    # Press keys
                    for key in keys[:-1]:
                        self.keyboard_controller.press(key)
                        await asyncio.sleep(0.01)  # Small delay between key presses
                    self.keyboard_controller.press(keys[-1])
                    # Release keys in reverse order
                    await asyncio.sleep(0.01)
                    self.keyboard_controller.release(keys[-1])
                    for key in reversed(keys[:-1]):
                        await asyncio.sleep(0.01)
                        self.keyboard_controller.release(key)
                        
                    logger.info(f"Pressed key combination: {key_combination}")
                    return {"success": True, "action": "key_combination", "keys": key_combination}
                else:
                    return {"error": f"Invalid key combination: {key_combination}"}
            else:
                return {"error": "Either 'text' or 'key_combination' must be provided"}
                
        except Exception as e:
            logger.error(f"Error with keyboard input: {e}")
            return {"error": str(e)}
            
    async def mouse_action(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform mouse actions.
        
        Args:
            arguments: Dictionary containing mouse action parameters
                      Supported keys:
                      - action: Mouse action to perform (move, click, double_click, right_click, scroll, drag)
                      - x: X coordinate for move action
                      - y: Y coordinate for move action
                      - scroll_amount: Amount to scroll (positive for up, negative for down)
                      - button: Mouse button for click actions (left, right, middle) - default: left
                      - duration: Duration for drag action in seconds - default: 1.0
                      - from_x: Starting X coordinate for drag action
                      - from_y: Starting Y coordinate for drag action
                      - to_x: Ending X coordinate for drag action
                      - to_y: Ending Y coordinate for drag action
            
        Returns:
            Dictionary with result
        """
        try:
            action = arguments.get("action")
            
            if action == "move":
                x = arguments.get("x")
                y = arguments.get("y")
                if x is not None and y is not None:
                    # Validate coordinates
                    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                        return {"error": f"Invalid coordinates: x={x}, y={y}. Must be numbers"}
                    
                    self.mouse_controller.position = (x, y)
                    logger.info(f"Moved mouse to ({x}, {y})")
                    return {"success": True, "action": "move", "x": x, "y": y}
                else:
                    return {"error": "Both 'x' and 'y' coordinates are required for move action"}
                    
            elif action in ["click", "double_click", "right_click"]:
                # Get button
                button_str = arguments.get("button", "left")
                if button_str == "left":
                    button = mouse.Button.left
                elif button_str == "right":
                    button = mouse.Button.right
                elif button_str == "middle":
                    button = mouse.Button.middle
                else:
                    return {"error": f"Invalid button: {button_str}. Supported buttons: left, right, middle"}
                
                # Perform click
                if action == "click":
                    self.mouse_controller.click(button)
                    logger.info(f"Performed {button_str} mouse click")
                    return {"success": True, "action": "click", "button": button_str}
                elif action == "double_click":
                    self.mouse_controller.click(button, 2)
                    logger.info(f"Performed double {button_str} mouse click")
                    return {"success": True, "action": "double_click", "button": button_str}
                elif action == "right_click":
                    self.mouse_controller.click(button)
                    logger.info(f"Performed {button_str} mouse click")
                    return {"success": True, "action": "right_click", "button": button_str}
                
            elif action == "scroll":
                scroll_amount = arguments.get("scroll_amount", 0)
                # Validate scroll amount
                if not isinstance(scroll_amount, (int, float)):
                    return {"error": f"Invalid scroll amount: {scroll_amount}. Must be a number"}
                
                self.mouse_controller.scroll(0, scroll_amount)
                logger.info(f"Scrolled by {scroll_amount}")
                return {"success": True, "action": "scroll", "amount": scroll_amount}
                
            elif action == "drag":
                from_x = arguments.get("from_x")
                from_y = arguments.get("from_y")
                to_x = arguments.get("to_x")
                to_y = arguments.get("to_y")
                duration = arguments.get("duration", 1.0)
                
                # Validate coordinates
                if any(coord is None for coord in [from_x, from_y, to_x, to_y]):
                    return {"error": "All coordinates (from_x, from_y, to_x, to_y) are required for drag action"}
                
                if not all(isinstance(coord, (int, float)) for coord in [from_x, from_y, to_x, to_y]):
                    return {"error": "All coordinates must be numbers"}
                
                # Validate duration
                if not isinstance(duration, (int, float)) or duration < 0:
                    return {"error": f"Invalid duration: {duration}. Must be a non-negative number"}
                
                # Perform drag
                self.mouse_controller.position = (from_x, from_y)
                self.mouse_controller.press(mouse.Button.left)
                await asyncio.sleep(0.05)  # Small delay before moving
                self.mouse_controller.position = (to_x, to_y)
                await asyncio.sleep(duration)  # Duration of drag
                self.mouse_controller.release(mouse.Button.left)
                
                logger.info(f"Dragged from ({from_x}, {from_y}) to ({to_x}, {to_y})")
                return {
                    "success": True, 
                    "action": "drag", 
                    "from": {"x": from_x, "y": from_y},
                    "to": {"x": to_x, "y": to_y},
                    "duration": duration
                }
                
            else:
                return {"error": f"Unknown mouse action: {action}. Supported actions: move, click, double_click, right_click, scroll, drag"}
                
        except Exception as e:
            logger.error(f"Error performing mouse action: {e}")
            return {"error": str(e)}
            
    def _parse_key_combination(self, key_combination: str):
        """
        Parse a key combination string into pynput keys.
        
        Args:
            key_combination: String representing key combination (e.g., "ctrl+c")
            
        Returns:
            List of pynput keys
        """
        try:
            keys = []
            key_parts = key_combination.lower().split('+')
            
            for part in key_parts:
                part = part.strip()
                if part == "ctrl":
                    keys.append(keyboard.Key.ctrl)
                elif part == "alt":
                    keys.append(keyboard.Key.alt)
                elif part == "shift":
                    keys.append(keyboard.Key.shift)
                elif part == "cmd" or part == "win":
                    keys.append(keyboard.Key.cmd)
                elif part == "enter":
                    keys.append(keyboard.Key.enter)
                elif part == "tab":
                    keys.append(keyboard.Key.tab)
                elif part == "esc":
                    keys.append(keyboard.Key.esc)
                elif part == "space":
                    keys.append(keyboard.Key.space)
                elif part == "backspace":
                    keys.append(keyboard.Key.backspace)
                elif part == "delete":
                    keys.append(keyboard.Key.delete)
                elif part == "up":
                    keys.append(keyboard.Key.up)
                elif part == "down":
                    keys.append(keyboard.Key.down)
                elif part == "left":
                    keys.append(keyboard.Key.left)
                elif part == "right":
                    keys.append(keyboard.Key.right)
                elif part == "home":
                    keys.append(keyboard.Key.home)
                elif part == "end":
                    keys.append(keyboard.Key.end)
                elif part == "pageup":
                    keys.append(keyboard.Key.page_up)
                elif part == "pagedown":
                    keys.append(keyboard.Key.page_down)
                elif part == "f1":
                    keys.append(keyboard.Key.f1)
                elif part == "f2":
                    keys.append(keyboard.Key.f2)
                elif part == "f3":
                    keys.append(keyboard.Key.f3)
                elif part == "f4":
                    keys.append(keyboard.Key.f4)
                elif part == "f5":
                    keys.append(keyboard.Key.f5)
                elif part == "f6":
                    keys.append(keyboard.Key.f6)
                elif part == "f7":
                    keys.append(keyboard.Key.f7)
                elif part == "f8":
                    keys.append(keyboard.Key.f8)
                elif part == "f9":
                    keys.append(keyboard.Key.f9)
                elif part == "f10":
                    keys.append(keyboard.Key.f10)
                elif part == "f11":
                    keys.append(keyboard.Key.f11)
                elif part == "f12":
                    keys.append(keyboard.Key.f12)
                elif len(part) == 1:
                    # Single character
                    keys.append(part)
                else:
                    # Try to find in special keys
                    try:
                        keys.append(getattr(keyboard.Key, part))
                    except AttributeError:
                        # If not found, treat as character
                        keys.append(part)
                        
            return keys
        except Exception as e:
            logger.error(f"Error parsing key combination '{key_combination}': {e}")
            return []