from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json
from datetime import datetime
import requests
from urllib.parse import urlparse
import time
from dynaconf import Dynaconf

# Initialize dynaconf
settings = Dynaconf(
    settings_files=['settings.yaml'],
    environments=True,
    env='default'
)

class WebsiteArchiver:
    def __init__(self, output_dir="website_archives"):
        """Initialize the archiver with configuration"""
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directories
        self.session_dir = os.path.join(output_dir, self.timestamp)
        self.screenshots_dir = os.path.join(self.session_dir, "screenshots")
        self.html_dir = os.path.join(self.session_dir, "html")
        
        for directory in [self.session_dir, self.screenshots_dir, self.html_dir]:
          os.makedirs(directory, exist_ok=True)
        
        # Set up Chrome driver path
        user_home = os.path.expanduser("~")
        chrome_driver_path = os.path.join(user_home, "Downloads", "chromedriver-win64", "chromedriver-win64", "chromedriver.exe")
        
        # Check if the Chrome driver exists at the specified path
        if not os.path.exists(chrome_driver_path):
            print(f"Chrome driver not found at {chrome_driver_path}. Please download it from https://sites.google.com/chromium.org/driver/ and place it in the specified location.")
            exit(1)
        
        # Set up Chrome options based on configuration
        chrome_options = Options()
        
        if settings.get('use_existing_chrome', False):
            print("Connecting to existing Chrome session at 127.0.0.1:9222...")
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        else:
            print("Starting new Chrome session...")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
        
        # Initialize Chrome driver
        service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def get_safe_filename(self, url):
        """Convert URL to a safe filename"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace(".", "_")
        return f"{domain}_{self.timestamp}"

    def take_full_page_screenshot(self, url, filename):
        """Take a screenshot of the entire page"""
        try:
            # Get page height
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Set window size to capture everything
            self.driver.set_window_size(1920, total_height)
            
            # Take screenshot
            screenshot_path = os.path.join(self.screenshots_dir, f"{filename}.png")
            self.driver.save_screenshot(screenshot_path)
            return screenshot_path
        except Exception as e:
            print(f"Error taking screenshot of {url}: {str(e)}")
            return None

    def save_html(self, url, filename):
        """Save the page's HTML content"""
        try:
            html_content = self.driver.page_source
            html_path = os.path.join(self.html_dir, f"{filename}.html")
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return html_path
        except Exception as e:
            print(f"Error saving HTML for {url}: {str(e)}")
            return None

    def process_urls(self, urls, delay=2):
        """Process multiple URLs, taking screenshots and saving HTML"""
        results = []
        
        for url in urls:
            try:
                print(f"\nProcessing: {url}")
                
                # Navigate to the URL
                self.driver.get(url)
                
                # Wait for page to load
                time.sleep(delay)
                
                # Generate safe filename for this URL
                filename = self.get_safe_filename(url)
                
                # Take screenshot and save HTML
                screenshot_path = self.take_full_page_screenshot(url, filename)
                html_path = self.save_html(url, filename)
                
                results.append({
                    'url': url,
                    'timestamp': self.timestamp,
                    'screenshot_path': screenshot_path,
                    'html_path': html_path
                })
                
            except Exception as e:
                print(f"Error processing {url}: {str(e)}")
                results.append({
                    'url': url,
                    'timestamp': self.timestamp,
                    'error': str(e)
                })
        
        # Save results to JSON
        results_path = os.path.join(self.session_dir, 'results.json')
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results

    def __del__(self):
        """Clean up by closing the browser"""
        try:
            if hasattr(self, 'driver') and not settings.get('use_existing_chrome', False):
                self.driver.quit()
        except Exception as e:
            print(f"Error closing browser: {str(e)}")

def main():
    try:
        # Create archiver with configuration from dynaconf
        archiver = WebsiteArchiver(output_dir=settings.output_dir)
        results = archiver.process_urls(settings.urls, delay=settings.delay_between_pages)
        
        print("\nArchiving complete! Summary:")
        for result in results:
            print(f"\nURL: {result['url']}")
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Screenshot: {result['screenshot_path']}")
                print(f"HTML: {result['html_path']}")
                
    except Exception as e:
        print(f"Error during archiving: {str(e)}")

if __name__ == "__main__":
    main()
