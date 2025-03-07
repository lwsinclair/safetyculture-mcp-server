"""
Test SafetyCulture API using the correct endpoints for listing inspections.
"""

import requests
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_safetyculture_api(api_key):
    """Test using the correct endpoints for listing inspections."""
    
    # Base URL for the API
    base_url = "https://api.safetyculture.io"
    
    # Headers for the request
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # List of endpoints to try
    endpoints = [
        # Try the search endpoint for listing inspections
        f"{base_url}/inspections/v1/search",
        
        # Try the inspections endpoint with various query parameters
        f"{base_url}/inspections/v1/inspections?limit=10",
        f"{base_url}/inspections/v1/inspections?archived=false",
        
        # Try listing the templates
        f"{base_url}/inspections/v1/templates",
        
        # Try listing scheduled inspections
        f"{base_url}/inspections/v1/scheduled-inspections",
        
        # Try other potential endpoints
        f"{base_url}/inspections/v1/users",
        f"{base_url}/inspections/v1/sites",
        f"{base_url}/inspections/v1/groups"
    ]
    
    logger.info(f"Using headers: {headers}")
    
    for endpoint in endpoints:
        logger.info(f"\nTesting endpoint: {endpoint}")
        
        try:
            response = requests.get(endpoint, headers=headers)
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("SUCCESS! Connected to the API successfully.")
                try:
                    data = response.json()
                    logger.info(f"Response data (sample): {str(data)[:200]}...")
                    logger.info(f"This endpoint works! Use this for listing data.")
                except:
                    logger.info(f"Raw response: {response.text[:100]}...")
                
            elif response.status_code == 401 or response.status_code == 403:
                logger.warning("Authentication failed. Check your API key.")
                try:
                    error_details = response.json()
                    logger.warning(f"Error details: {error_details}")
                except:
                    logger.warning(f"Raw error response: {response.text[:100]}...")
                
            elif response.status_code == 400:
                logger.warning("Bad request. The endpoint might need additional parameters.")
                try:
                    error_details = response.json()
                    logger.warning(f"Error details: {error_details}")
                except:
                    logger.warning(f"Raw error response: {response.text[:100]}...")
                
            else:
                logger.warning(f"Request failed with status code: {response.status_code}")
                try:
                    error_details = response.json()
                    logger.warning(f"Error details: {error_details}")
                except:
                    logger.warning(f"Raw error response: {response.text[:100]}...")
                
        except Exception as e:
            logger.error(f"Request failed with error: {str(e)}")
    
    # Check with other authentication methods if nothing worked
    logger.info("\nTrying with API key without Bearer prefix...")
    
    # Try without Bearer prefix
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    
    # Try the search endpoint which is most likely to work
    endpoint = f"{base_url}/inspections/v1/search"
    try:
        response = requests.get(endpoint, headers=headers)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("SUCCESS! Connected using direct API key authentication.")
    except Exception as e:
        logger.error(f"Request failed with error: {str(e)}")
    
    # If API key doesn't work, provide guidance
    logger.info("\nImportant Note on SafetyCulture API:")
    logger.info("Based on the test results and error messages, it appears the SafetyCulture API")
    logger.info("requires specific endpoints for different operations:")
    logger.info("1. To list inspections: Use the /search endpoint or query parameters")
    logger.info("2. To get a specific inspection: Use /inspections/v1/inspections/{id}")
    logger.info("   where {id} must be a valid UUID format inspection ID")
    logger.info("\nTo get a valid SafetyCulture API key:")
    logger.info("1. Log in to your SafetyCulture account")
    logger.info("2. Go to Profile/Account settings → API Access")
    logger.info("3. Generate a new API key")
    logger.info("4. Ensure the key has permissions for inspections")
    logger.info("\nFor more information, visit: https://developer.safetyculture.com/reference/introduction")

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