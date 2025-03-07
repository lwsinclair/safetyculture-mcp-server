"""
Test SafetyCulture API using the exact format from the documentation.
"""

import requests
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_safetyculture_api(api_key):
    """Test using the exact format from the documentation."""
    
    # Base URL for the API
    base_url = "https://api.safetyculture.io"
    
    # Testing general inspections endpoint (no ID)
    inspection_url = f"{base_url}/inspections/v1/inspections"
    
    # Test with Authorization header in Bearer format
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    logger.info(f"Testing connection to: {inspection_url}")
    logger.info(f"Using headers: {headers}")
    
    try:
        response = requests.get(inspection_url, headers=headers)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("SUCCESS! Connected to the API successfully.")
            try:
                data = response.json()
                logger.info(f"Response data: {data}")
            except:
                logger.info(f"Raw response: {response.text[:100]}...")
            return True
        else:
            logger.warning(f"Request failed with status code: {response.status_code}")
            try:
                error_details = response.json()
                logger.warning(f"Error details: {error_details}")
            except:
                logger.warning(f"Raw error response: {response.text[:100]}...")
    except Exception as e:
        logger.error(f"Request failed with error: {str(e)}")
    
    logger.info("\nTrying with API key without Bearer prefix...")
    
    # Try without Bearer prefix
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    
    try:
        response = requests.get(inspection_url, headers=headers)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("SUCCESS! Connected to the API successfully.")
            try:
                data = response.json()
                logger.info(f"Response data: {data}")
            except:
                logger.info(f"Raw response: {response.text[:100]}...")
            return True
    except Exception as e:
        logger.error(f"Request failed with error: {str(e)}")
    
    # If API key doesn't work, provide guidance
    logger.error("\nFailed to connect to the API with the provided key.")
    logger.info("\nTo get a valid SafetyCulture API key:")
    logger.info("1. Log in to your SafetyCulture account")
    logger.info("2. Go to Profile/Account settings → API Access")
    logger.info("3. Generate a new API key")
    logger.info("4. Ensure the key has permissions for inspections")
    logger.info("\nFor more information, visit: https://developer.safetyculture.com/reference/introduction")
    
    return False

if __name__ == "__main__":
    # Get API key from command line argument or prompt user
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your SafetyCulture API key: ")
    
    # Test the API key
    test_safetyculture_api(api_key)
    
    # Keep terminal open
    input("\nPress Enter to exit...") 