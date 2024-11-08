from typing import Dict, Any
import os
import time
from datetime import datetime
import platform
import sys

# Lazy import of pyautogui to handle potential import errors gracefully
pyautogui = None

def init_pyautogui():
    """Initialize pyautogui with proper error handling for different platforms"""
    global pyautogui
    print(f"[DEBUG] Initializing pyautogui on platform: {platform.system()}")
    if pyautogui is not None:
        print("[DEBUG] PyAutoGUI already initialized")
        return True, None
    
    try:
        import pyautogui
        print("[DEBUG] Successfully imported pyautogui")
        
        # Configure pyautogui settings
        pyautogui.PAUSE = 0.5
        pyautogui.FAILSAFE = True
        print(f"[DEBUG] PyAutoGUI settings configured - PAUSE: {pyautogui.PAUSE}, FAILSAFE: {pyautogui.FAILSAFE}")
        
        # Handle Linux-specific display requirements
        if platform.system() == 'Linux':
            print("[DEBUG] Checking Linux display settings")
            if 'DISPLAY' not in os.environ:
                print("[ERROR] No display available in Linux environment")
                return False, "Error: No display available. Make sure you're running in a graphical environment."
            print(f"[DEBUG] Linux DISPLAY environment variable: {os.environ.get('DISPLAY')}")
        
        return True, None
    except ImportError as e:
        print(f"[ERROR] PyAutoGUI import error: {str(e)}")
        return False, f"Error importing pyautogui: {str(e)}"
    except Exception as e:
        print(f"[ERROR] PyAutoGUI initialization error: {str(e)}")
        return False, f"Error initializing automation: {str(e)}"

# Tool Specification
TOOL_SPEC = {
    "name": "computer_automation",
    "description": "Cross-platform computer automation for mouse movements, clicks, typing, and screenshots",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "The action to perform",
                "enum": ["move_mouse", "click", "type", "type_enter", "screenshot"]
            },
            "x": {
                "type": "number",
                "description": "X coordinate for mouse movement/click (relative to screen resolution)"
            },
            "y": {
                "type": "number",
                "description": "Y coordinate for mouse movement/click (relative to screen resolution)"
            },
            "text": {
                "type": "string",
                "description": "Text to type when using the type action"
            }
        },
        "required": ["action"]
    }
}

class ComputerAutomation:
    def __init__(self):
        print("[DEBUG] Initializing ComputerAutomation class")
        self.screenshot_dir = "automation_screenshots"
        if not os.path.exists(self.screenshot_dir):
            print(f"[DEBUG] Creating screenshot directory: {self.screenshot_dir}")
            os.makedirs(self.screenshot_dir)

    def move_mouse(self, x: int, y: int) -> Dict:
        """Move mouse to specified coordinates"""
        print(f"[DEBUG] Attempting to move mouse to coordinates ({x}, {y})")
        success, error = init_pyautogui()
        if not success:
            print(f"[ERROR] PyAutoGUI initialization failed: {error}")
            return {"error": error}
        
        try:
            screen_size = pyautogui.size()
            print(f"[DEBUG] Screen size: {screen_size}")
            if x > screen_size[0] or y > screen_size[1]:
                print(f"[WARNING] Coordinates ({x}, {y}) may be outside screen bounds")
            
            pyautogui.moveTo(x, y)
            print(f"[DEBUG] Successfully moved mouse to ({x}, {y})")
            return {"result": f"Mouse moved to coordinates ({x}, {y})"}
        except Exception as e:
            print(f"[ERROR] Mouse movement failed: {str(e)}")
            return {"error": f"Failed to move mouse: {str(e)}"}

    def click(self, x: int, y: int) -> Dict:
        """Click at specified coordinates"""
        print(f"[DEBUG] Attempting to click at coordinates ({x}, {y})")
        success, error = init_pyautogui()
        if not success:
            print(f"[ERROR] PyAutoGUI initialization failed: {error}")
            return {"error": error}
        
        try:
            screen_size = pyautogui.size()
            print(f"[DEBUG] Screen size: {screen_size}")
            if x > screen_size[0] or y > screen_size[1]:
                print(f"[WARNING] Click coordinates ({x}, {y}) may be outside screen bounds")
            
            pyautogui.click(x, y)
            print(f"[DEBUG] Successfully clicked at ({x}, {y})")
            return {"result": f"Clicked at coordinates ({x}, {y})"}
        except Exception as e:
            print(f"[ERROR] Click operation failed: {str(e)}")
            return {"error": f"Failed to click: {str(e)}"}

    def type_text(self, text: str, hit_enter: bool = False) -> Dict:
        """Type specified text and optionally hit enter"""
        print(f"[DEBUG] Attempting to type text: '{text}' (hit_enter={hit_enter})")
        success, error = init_pyautogui()
        if not success:
            print(f"[ERROR] PyAutoGUI initialization failed: {error}")
            return {"error": error}
        
        try:
            pyautogui.write(text)
            print("[DEBUG] Text typed successfully")
            if hit_enter:
                print("[DEBUG] Pressing Enter key")
                pyautogui.press('enter')
            return {"result": f"Typed text: {text}" + (" and pressed Enter" if hit_enter else "")}
        except Exception as e:
            print(f"[ERROR] Typing operation failed: {str(e)}")
            return {"error": f"Failed to type text: {str(e)}"}

    def take_screenshot(self) -> Dict:
        """Take a screenshot of the entire screen"""
        print("[DEBUG] Attempting to take screenshot")
        success, error = init_pyautogui()
        if not success:
            print(f"[ERROR] PyAutoGUI initialization failed: {error}")
            return {"error": error}
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            print(f"[DEBUG] Screenshot will be saved to: {filepath}")
            
            # Handle platform-specific screenshot requirements
            if platform.system() == 'Linux':
                print("[DEBUG] Using Linux-specific screenshot handling")
                try:
                    import pyscreenshot as ImageGrab
                    print("[DEBUG] Using pyscreenshot for Linux")
                    screenshot = ImageGrab.grab()
                except ImportError:
                    print("[DEBUG] Falling back to pyautogui screenshot for Linux")
                    screenshot = pyautogui.screenshot()
            else:
                print("[DEBUG] Using standard pyautogui screenshot")
                screenshot = pyautogui.screenshot()
                
            screenshot.save(filepath)
            print(f"[DEBUG] Screenshot successfully saved")
            return {"result": f"Screenshot saved to {filepath}"}
        except Exception as e:
            print(f"[ERROR] Screenshot operation failed: {str(e)}")
            return {"error": f"Failed to take screenshot: {str(e)}"}

def computer_automation(action: str, x: int = None, y: int = None, text: str = None) -> Dict:
    """
    Main function implementing cross-platform computer automation functionality
    
    Args:
        action (str): The action to perform (move_mouse, click, type, type_enter, screenshot)
        x (int, optional): X coordinate for mouse movement/click
        y (int, optional): Y coordinate for mouse movement/click
        text (str, optional): Text to type when using the type action
        
    Returns:
        Dict: Result dictionary containing either:
            - Success case: Action result message
            - Error case: {"error": "error message"}
    """
    print(f"[DEBUG] Computer automation called with action: {action}, x: {x}, y: {y}, text: {text}")
    automation = ComputerAutomation()
    
    try:
        if action == "move_mouse":
            if x is None or y is None:
                print("[ERROR] Missing coordinates for mouse movement")
                return {"error": "X and Y coordinates required for mouse movement"}
            return automation.move_mouse(x, y)
        
        elif action == "click":
            if x is None or y is None:
                print("[ERROR] Missing coordinates for click")
                return {"error": "X and Y coordinates required for click"}
            return automation.click(x, y)
        
        elif action == "type":
            if text is None:
                print("[ERROR] Missing text for type action")
                return {"error": "Text required for type action"}
            return automation.type_text(text, hit_enter=False)
        
        elif action == "type_enter":
            if text is None:
                print("[ERROR] Missing text for type_enter action")
                return {"error": "Text required for type_enter action"}
            return automation.type_text(text, hit_enter=True)
        
        elif action == "screenshot":
            return automation.take_screenshot()
        
        else:
            print(f"[ERROR] Unknown action requested: {action}")
            return {"error": f"Unknown action: {action}"}
            
    except Exception as e:
        print(f"[ERROR] Unexpected automation error: {str(e)}")
        return {"error": f"Automation error: {str(e)}"}
