from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
            result = subprocess.run(['lsof', '-i', ':9222'], capture_output=True, text=True)
            if not result.stdout:
                logger.info("Starting Chrome with remote debugging...")
                chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                subprocess.Popen([
                    chrome_path,
                    '--remote-debugging-port=9222',
                    '--user-data-dir=/tmp/chrome_debug_profile'
                ])
                time.sleep(3)
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
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
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

    def compose_email(self, recipient, subject, message):
        """Compose a new email in Gmail with recipient, subject, and message"""
        try:
            logger.info("Attempting to compose new email")
            
            wait = WebDriverWait(self.driver, 20)
            compose_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][gh="cm"]'))
            )
            compose_button.click()
            logger.info("Clicked compose button")
            
            time.sleep(2)
            
            to_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[role="combobox"][type="text"]'))
            )
            to_field.send_keys(recipient)
            logger.info("Entered recipient")
            
            subject_field = wait.until(
                EC.presence_of_element_located((By.NAME, 'subjectbox'))
            )
            subject_field.send_keys(subject)
            logger.info("Entered subject")
            
            try:
                # Method 1: Using iframe
                iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"] iframe')))
                self.driver.switch_to.frame(iframe)
                body = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"]')))
                body.send_keys(message)
                logger.info("Entered message using iframe method")
                self.driver.switch_to.default_content()
            except Exception as e:
                logger.info(f"Iframe method failed: {str(e)}, trying alternate method")
                
                # Method 2: Direct message body
                self.driver.switch_to.default_content()
                body = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"][aria-label="Message Body"]')))
                body.send_keys(message)
                logger.info("Entered message using direct method")
            
            # Pause for 5 seconds
            logger.info("Pausing for 5 seconds before sending...")
            time.sleep(5)
            
            send_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="dialog"] div[role="button"][aria-label*="Send"]'))
            )
            send_button.click()
            logger.info("Clicked send button")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in compose_email: {str(e)}")
            self.driver.switch_to.default_content()  # Reset frame focus
            raise

browser_controller = BrowserControl()

@tool
def browser_control(command: str) -> str:
    """Controls browser actions like switching tabs or navigating to websites"""
    logger.info(f"Received command: {command}")
    
    try:
        if "compose" in command.lower() or "write" in command.lower():
            if "email" in command.lower() or "gmail" in command.lower():
                success = browser_controller.switch_to_tab("gmail")
                if not success:
                    return "Failed to access Gmail"
                
                time.sleep(2)  # Give Gmail time to load
                recipient = "emailypark@gmail.com"
                subject = "testing for bci agents group"
                message = "hello this is emily :)))"
                
                if browser_controller.compose_email(recipient, subject, message):
                    return "Successfully sent email"
                return "Failed to compose email"
                
        elif "click on" in command.lower() or "switch to" in command.lower():
            if "gmail" in command.lower():
                success = browser_controller.switch_to_tab("gmail")
                if success:
                    return "Successfully switched to Gmail tab"
                return "Failed to find or open Gmail tab"
        
        return "Command not recognized"
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return f"Error: {str(e)}"