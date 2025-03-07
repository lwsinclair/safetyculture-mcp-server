"""
Test SafetyCulture Feed API endpoints.
"""

import requests
import logging
import sys
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_feed_api(api_key):
    """Test the SafetyCulture Feed API endpoints."""
    
    # Base URL for the API
    base_url = "https://api.safetyculture.io"
    
    # Headers for the request - exactly as specified in the example
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Test endpoints for the feed API
    endpoints = [
        # Inspections feed with query parameters
        f"{base_url}/feed/inspections?archived=false&completed=true&web_report_link=private",
        
        # Actions feed
        f"{base_url}/feed/actions",
        
        # Try with different query parameters
        f"{base_url}/feed/inspections?limit=10",
        f"{base_url}/feed/inspections?modified_after=2023-01-01T00:00:00Z",
        
        # Try without query parameters
        f"{base_url}/feed/inspections"
    ]
    
    logger.info(f"Using authorization header: Bearer {api_key[:5]}...")
    
    for endpoint in endpoints:
        logger.info(f"\nTesting endpoint: {endpoint}")
        
        try:
            response = requests.get(endpoint, headers=headers)
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ SUCCESS! Connected to the Feed API successfully.")
                try:
                    data = response.json()
                    # Pretty print a sample of the response
                    formatted_data = json.dumps(data, indent=2)
                    logger.info(f"Response preview (first 500 chars):\n{formatted_data[:500]}...")
                    logger.info(f"This endpoint works! Use this for accessing the data.")
                    
                    # Count items if possible
                    if isinstance(data, dict) and 'count' in data:
                        logger.info(f"Total count: {data['count']}")
                    elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                        logger.info(f"Items in response: {len(data['data'])}")
                    elif isinstance(data, list):
                        logger.info(f"Items in response: {len(data)}")
                    
                except:
                    logger.info(f"Raw response preview: {response.text[:200]}...")
                
            elif response.status_code == 401 or response.status_code == 403:
                logger.warning("Authentication failed. Check your API key.")
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
    
    # Provide guidance
    logger.info("\nImportant Note on SafetyCulture Feed API:")
    logger.info("The feed API is designed for listing collections of resources without needing individual IDs.")
    logger.info("- Use /feed/inspections for listing inspections")
    logger.info("- Use /feed/actions for listing actions")
    logger.info("- Add query parameters to filter the results")
    logger.info("\nTo get a valid SafetyCulture API key:")
    logger.info("1. Log in to your SafetyCulture account")
    logger.info("2. Go to Profile/Account settings → API Access")
    logger.info("3. Generate a new API key")
    logger.info("4. Ensure the key has permissions for feed access")

if __name__ == "__main__":
    # Get API key from command line argument or prompt user
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your SafetyCulture API key: ")
    
    # Test the API key
    test_feed_api(api_key)
    
    # Keep terminal open
    input("\nPress Enter to exit...") 