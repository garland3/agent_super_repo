from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime
from typing import Dict, Optional
import time

# Tool specification
TOOL_SPEC = {
    "name": "selenium_browser_action",
    "description": "Perform web automation tasks using Selenium browser",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "The automation action to perform",
                "enum": ["navigate", "screenshot", "save_html"]
            },
            "url": {
                "type": "string",
                "description": "URL to perform the action on"
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save outputs (optional)",
                "default": "selenium_outputs"
            }
        },
        "required": ["action", "url"]
    }
}

class SeleniumBrowserTool:
    def __init__(self, output_dir: str = "selenium_outputs"):
        """Initialize the Selenium browser tool"""
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up Chrome driver path
        user_home = os.path.expanduser("~")
        self.chrome_driver_path = os.path.join(user_home, "Downloads", "chromedriver-win64", "chromedriver-win64", "chromedriver.exe")
        
        # Initialize driver as None - will be created when needed
        self.driver = None
        
    def _initialize_driver(self):
        """Initialize the Chrome driver if not already initialized"""
        if self.driver is None:
            if not os.path.exists(self.chrome_driver_path):
                raise Exception(f"Chrome driver not found at {self.chrome_driver_path}")
            
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            
            service = Service(self.chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)

    def _get_safe_filename(self, url: str) -> str:
        """Convert URL to a safe filename"""
        return url.replace("://", "_").replace("/", "_").replace(".", "_")[:100]

    def navigate(self, url: str) -> Dict:
        """Navigate to a URL"""
        try:
            self._initialize_driver()
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            return {"success": True, "message": f"Successfully navigated to {url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def take_screenshot(self, url: str) -> Dict:
        """Take a screenshot of the current page"""
        try:
            self._initialize_driver()
            
            # Navigate to URL if not already there
            if self.driver.current_url != url:
                self.navigate(url)
            
            # Get page height and set window size
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.set_window_size(1920, total_height)
            
            # Take screenshot
            filename = f"{self._get_safe_filename(url)}_{self.timestamp}.png"
            screenshot_path = os.path.join(self.output_dir, filename)
            self.driver.save_screenshot(screenshot_path)
            
            return {
                "success": True,
                "file_path": screenshot_path,
                "message": f"Screenshot saved to {screenshot_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_html(self, url: str) -> Dict:
        """Save the current page's HTML"""
        try:
            self._initialize_driver()
            
            # Navigate to URL if not already there
            if self.driver.current_url != url:
                self.navigate(url)
            
            # Save HTML
            filename = f"{self._get_safe_filename(url)}_{self.timestamp}.html"
            html_path = os.path.join(self.output_dir, filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            return {
                "success": True,
                "file_path": html_path,
                "message": f"HTML saved to {html_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def __del__(self):
        """Clean up by closing the browser"""
        try:
            if self.driver is not None:
                self.driver.quit()
        except Exception:
            pass

def selenium_browser_action(action: str, url: str, output_dir: str = "selenium_outputs") -> Dict:
    """
    Perform Selenium web automation actions
    
    Args:
        action (str): Action to perform (navigate, screenshot, save_html)
        url (str): URL to perform the action on
        output_dir (str): Directory to save outputs (optional)
        
    Returns:
        Dict: Result of the action or error message
    """
    try:
        tool = SeleniumBrowserTool(output_dir)
        
        if action == "navigate":
            return tool.navigate(url)
        elif action == "screenshot":
            return tool.take_screenshot(url)
        elif action == "save_html":
            return tool.save_html(url)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}
