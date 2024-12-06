from browser_control import browser_control
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_browser_search():
    try:
        logger.info("Starting browser search test...")
        result = browser_control.run("search for lebron james")
        logger.info(f"Test completed with result: {result}")
        print(f"Final result: {result}")
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_browser_search()