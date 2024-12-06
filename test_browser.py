from browser_control import browser_control
import logging
import sys

"""
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug_profile
"""

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_browser():
    try:
        logger.info("Starting browser control test...")
        result = browser_control.run("computer: click on my gmail tab on chrome")
        logger.info(f"Switching to Gmail result: {result}")
        
        result = browser_control.run("computer: compose email with message hello")
        logger.info(f"Composing email result: {result}")
        
        print(f"Final result: {result}")
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_browser()