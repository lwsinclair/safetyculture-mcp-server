"""
Test SafetyCulture API Key

This script tests a SafetyCulture API key to check if it can successfully connect to the API.
"""

import sys
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_key(api_key):
    """Test if the provided API key can connect to the SafetyCulture API."""
    base_url = "https://api.safetyculture.io"
    
    # Endpoints to try - adding the correct inspection endpoint format
    endpoints = [
        # New format endpoints
        f"{base_url}/inspections/v1/inspections",
        f"{base_url}/inspections/v1/templates",
        f"{base_url}/inspections/v1/profiles",
        
        # Legacy endpoints
        f"{base_url}/v1/audits",
        f"{base_url}/v1/templates",
        f"{base_url}/v1/groups/mine",
    ]
    
    # Authorization header formats to try
    auth_headers = [
        {"Authorization": f"Bearer {api_key}"},
        {"Authorization": api_key},
        {"X-Api-Key": api_key}
    ]
    
    logger.info(f"Testing connection with API key: {api_key[:10] if len(api_key) > 10 else api_key}")
    
    # Try each combination of endpoint and auth format
    for endpoint in endpoints:
        for headers in auth_headers:
            logger.info(f"Trying endpoint: {endpoint}")
            logger.info(f"With headers: {headers}")
            
            try:
                session = requests.Session()
                session.headers.update(headers)
                session.headers.update({"Accept": "application/json"})
                
                response = session.get(endpoint)
                logger.info(f"Status code: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info("✅ Successfully connected to the SafetyCulture API!")
                    logger.info(f"Working endpoint: {endpoint}")
                    logger.info(f"Working headers: {headers}")
                    
                    # Try to parse the response
                    try:
                        data = response.json()
                        logger.info(f"Response data: {data}")
                    except:
                        logger.info(f"Raw response: {response.text[:100]}...")
                        
                    return True
                elif response.status_code == 401:
                    logger.warning("Authentication failed (401 Unauthorized) - Invalid API key or format")
                elif response.status_code == 403:
                    logger.warning("Authorization failed (403 Forbidden) - Valid API key but insufficient permissions")
                elif response.status_code == 404:
                    logger.warning("Endpoint not found (404 Not Found) - Endpoint may not exist or require different format")
                else:
                    logger.warning(f"Failed with status {response.status_code}")
                    logger.debug(f"Response: {response.text[:100]}...")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed: {str(e)}")
                continue
    
    # If we get here, all attempts failed
    logger.error("❌ Failed to connect to the SafetyCulture API with all attempted methods")
    
    # Provide suggestions
    logger.info("\nSuggestions:")
    logger.info("1. Check if your API key is correct and has the right permissions")
    logger.info("2. Verify you're using the correct regional API endpoint")
    logger.info("3. Check if your account has access to the API")
    logger.info("4. Visit the SafetyCulture API documentation for more information")
    logger.info("   https://developer.safetyculture.com/reference/introduction")
    
    return False

if __name__ == "__main__":
    # Get API key from command line argument or prompt user
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your SafetyCulture API key: ")
    
    # Test the API key
    test_api_key(api_key)
    
    # Keep terminal open
    input("\nPress Enter to exit...") 