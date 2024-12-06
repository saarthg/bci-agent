from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from crewai_tools import tool
import logging
import sys
import subprocess
import time
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class BrowserControl:
    def __init__(self):
        self.driver = None
        
    def start_chrome_debugger(self):
        """Start Chrome with debugging port if not already running"""
        try:
            # Check if Chrome is running with debug port
            result = subprocess.run(['lsof', '-i', ':9222'], capture_output=True, text=True)
            if not result.stdout:
                logger.info("Starting Chrome with remote debugging...")
                chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                subprocess.Popen([
                    chrome_path,
                    '--remote-debugging-port=9222',
                    '--user-data-dir=/tmp/chrome_debug_profile'
                ])
                time.sleep(3)  # Wait for Chrome to start
        except Exception as e:
            logger.error(f"Error starting Chrome: {str(e)}")
            raise

    def initialize_driver(self):
        """Initialize the Chrome driver if not already running"""
        if not self.driver:
            try:
                logger.debug("Setting up Chrome options...")
                options = webdriver.ChromeOptions()
                options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                
                # Add these options to help with debugging
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--remote-debugging-port=9222')
                
                # Start Chrome if not running
                self.start_chrome_debugger()
                
                logger.debug("Attempting to connect to Chrome...")
                service = Service()
                self.driver = webdriver.Chrome(service=service, options=options)
                logger.info("Successfully connected to Chrome")
                
            except Exception as e:
                logger.error(f"Error initializing driver: {str(e)}")
                raise

    def switch_to_tab(self, search_term):
        """Switch to a tab containing the specified search term in its title or URL"""
        logger.debug(f"Attempting to switch to tab containing: {search_term}")
        self.initialize_driver()
        found = False
        
        try:
            logger.info(f"Looking for tab containing: {search_term}")
            handles = self.driver.window_handles
            logger.info(f"Found {len(handles)} window handles")
            
            for handle in handles:
                logger.debug(f"Checking handle: {handle}")
                self.driver.switch_to.window(handle)
                title = self.driver.title
                url = self.driver.current_url
                logger.info(f"Checking tab - Title: {title}, URL: {url}")
                
                if search_term.lower() in title.lower() or search_term.lower() in url.lower():
                    found = True
                    logger.info(f"Found matching tab: {title}")
                    break
                    
            if not found:
                logger.info(f"Tab not found, opening new tab for: {search_term}")
                if search_term.lower() == 'gmail':
                    self.driver.execute_script("window.open('https://gmail.com', '_blank');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    found = True
                    
            return found
            
        except Exception as e:
            logger.error(f"Error in switch_to_tab: {str(e)}")
            raise

# Create a singleton instance
browser_controller = BrowserControl()

@tool
def browser_control(command: str) -> str:
    """Controls browser actions like switching tabs or navigating to websites"""
    logger.info(f"Received command: {command}")
    
    try:
        # Parse the command
        if "click on" in command.lower() or "switch to" in command.lower():
            if "gmail" in command.lower():
                logger.info("Attempting to switch to Gmail tab")
                success = browser_controller.switch_to_tab("gmail")
                if success:
                    return "Successfully switched to Gmail tab"
                return "Failed to find or open Gmail tab"
        
        return "Command not recognized"
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return f"Error: {str(e)}"