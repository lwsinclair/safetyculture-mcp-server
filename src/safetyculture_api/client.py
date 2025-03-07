"""
SafetyCulture API Client

This module provides a client for interacting with the SafetyCulture API.
"""

import requests
import datetime
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafetyCultureClient:
    """Client for the SafetyCulture API."""
    
    # URL structure based on SafetyCulture documentation
    BASE_URL = "https://api.safetyculture.io"
    FEED_PATH = "feed"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SafetyCulture API client.
        
        Args:
            api_key: Optional API key for authentication
        """
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self._set_auth_header(api_key)
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key for authentication.
        
        Args:
            api_key: SafetyCulture API key
        """
        self.api_key = api_key
        self._set_auth_header(api_key)
        logger.info("API key set")
    
    def _set_auth_header(self, api_key: str) -> None:
        """
        Set the authorization header with the API key.
        
        Args:
            api_key: SafetyCulture API key
        """
        key_length = len(api_key) if api_key else 0
        logger.debug(f"Setting auth header with API key (length: {key_length})")
        
        # Set headers exactly as specified in the feed API example
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "accept": "application/json"
        })
    
    def test_connection(self) -> bool:
        """
        Test the connection to the SafetyCulture API.
        
        Returns:
            True if the connection is successful, False otherwise
        
        Raises:
            Exception: If the API key is not set or the connection fails
        """
        if not self.api_key:
            logger.error("API key not set")
            raise Exception("API key not set. Please set an API key first.")
        
        # Test connection using the feed/inspections endpoint as specified
        endpoint = f"{self.BASE_URL}/{self.FEED_PATH}/inspections"
        
        # Log connection attempt
        logger.info(f"Testing connection to {endpoint}")
        
        try:
            response = self.session.get(endpoint)
            logger.info(f"API response status code: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("Successfully connected to SafetyCulture API!")
                return True
            elif response.status_code in (401, 403):
                logger.warning(f"Authentication failed with status: {response.status_code}")
                logger.warning("This could indicate an invalid API key or insufficient permissions")
                raise Exception(f"Authentication failed: Status {response.status_code}")
            else:
                # Try alternative endpoint if inspections doesn't work
                actions_endpoint = f"{self.BASE_URL}/{self.FEED_PATH}/actions"
                logger.info(f"Trying alternative endpoint: {actions_endpoint}")
                
                actions_response = self.session.get(actions_endpoint)
                if actions_response.status_code == 200:
                    logger.info("Successfully connected to SafetyCulture API using actions endpoint!")
                    return True
                elif actions_response.status_code in (401, 403):
                    logger.warning(f"Authentication failed with status: {actions_response.status_code}")
                    raise Exception(f"Authentication failed: Status {actions_response.status_code}")
                
                logger.error(f"Failed to connect: Status {response.status_code}, Response: {response.text}")
                raise Exception(f"Failed to connect to SafetyCulture API: Status {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error connecting to SafetyCulture API: {str(e)}")
            raise Exception(f"Network error connecting to SafetyCulture API: {str(e)}")
    
    def get_inspections(
        self, 
        site_id: Optional[str] = None, 
        template_id: Optional[str] = None,
        start_date: Optional[Union[str, datetime.datetime]] = None,
        end_date: Optional[Union[str, datetime.datetime]] = None,
        limit: int = 100,
        completed: bool = True,
        archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get inspections from SafetyCulture using the feed API.
        
        Args:
            site_id: Optional site ID to filter inspections
            template_id: Optional template ID to filter inspections
            start_date: Optional start date to filter inspections
            end_date: Optional end date to filter inspections
            limit: Maximum number of inspections to return
            completed: Whether to only include completed inspections
            archived: Whether to include archived inspections
            
        Returns:
            List of inspection data dictionaries
            
        Raises:
            Exception: If the API key is not set or the request fails
        """
        if not self.api_key:
            raise Exception("API key not set. Please set an API key first.")
        
        # Convert datetime objects to ISO format strings if needed
        if isinstance(start_date, datetime.datetime):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.isoformat()
        
        # Build query parameters as specified in the feed API example
        params = {
            'limit': limit,
            'archived': str(archived).lower(),
            'completed': str(completed).lower(),
            'web_report_link': 'private'
        }
        
        if site_id:
            params['site_id'] = site_id
        if template_id:
            params['template_id'] = template_id
        if start_date:
            params['modified_after'] = start_date
        if end_date:
            params['modified_before'] = end_date
        
        # Use the feed/inspections endpoint as specified
        endpoint = f"{self.BASE_URL}/{self.FEED_PATH}/inspections"
        
        try:
            logger.info(f"Getting inspections from feed API: {endpoint}")
            logger.debug(f"Parameters: {params}")
            
            # Make the API request
            response = self.session.get(endpoint, params=params)
            logger.info(f"API response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved inspections data")
                
                # Extract inspections from the response
                if isinstance(data, dict) and 'data' in data:
                    return data.get('data', [])
                elif isinstance(data, list):
                    return data
                else:
                    # If we can't determine the structure, return the whole data
                    return [data]
            else:
                logger.error(f"Failed to get inspections: Status {response.status_code}, Response: {response.text}")
                raise Exception(f"Failed to get inspections: Status {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting inspections: {str(e)}")
            raise Exception(f"Network error getting inspections: {str(e)}")
    
    def get_inspection_details(self, inspection_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific inspection.
        
        Args:
            inspection_id: The ID of the inspection to retrieve
            
        Returns:
            Dictionary containing inspection details
            
        Raises:
            Exception: If the API key is not set or the request fails
        """
        if not self.api_key:
            raise Exception("API key not set. Please set an API key first.")
        
        # Use the feed API to get inspection details
        # First try to find it in the feed with a filter
        endpoint = f"{self.BASE_URL}/{self.FEED_PATH}/inspections"
        params = {'inspection_id': inspection_id}
        
        try:
            logger.info(f"Getting inspection details for ID: {inspection_id}")
            
            response = self.session.get(endpoint, params=params)
            logger.info(f"API response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Try to find the specific inspection in the response
                if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                    for inspection in data['data']:
                        if inspection.get('inspection_id') == inspection_id or inspection.get('id') == inspection_id:
                            return inspection
                    
                    # If we couldn't find the specific inspection, but got a successful response,
                    # return the first one or an empty dict
                    if data['data']:
                        return data['data'][0]
                    return {}
                else:
                    return data
            else:
                logger.error(f"Failed to get inspection details: Status {response.status_code}, Response: {response.text}")
                raise Exception(f"Failed to get inspection details: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting inspection details: {str(e)}")
            raise Exception(f"Network error getting inspection details: {str(e)}")
    
    def get_actions(
        self,
        site_id: Optional[str] = None,
        start_date: Optional[Union[str, datetime.datetime]] = None,
        end_date: Optional[Union[str, datetime.datetime]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get actions from the SafetyCulture API.
        
        Args:
            site_id: Optional site ID to filter actions
            start_date: Optional start date to filter actions
            end_date: Optional end date to filter actions
            limit: Maximum number of actions to return
            
        Returns:
            List of action data dictionaries
            
        Raises:
            Exception: If the API key is not set or the request fails
        """
        if not self.api_key:
            raise Exception("API key not set. Please set an API key first.")
        
        # Convert datetime objects to ISO format strings if needed
        if isinstance(start_date, datetime.datetime):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.isoformat()
        
        # Build query parameters
        params = {'limit': limit}
        if site_id:
            params['site_id'] = site_id
        if start_date:
            params['modified_after'] = start_date
        if end_date:
            params['modified_before'] = end_date
        
        # Use the feed/actions endpoint as specified
        endpoint = f"{self.BASE_URL}/{self.FEED_PATH}/actions"
        
        try:
            logger.info(f"Getting actions from feed API: {endpoint}")
            logger.debug(f"Parameters: {params}")
            
            # Make the API request
            response = self.session.get(endpoint, params=params)
            logger.info(f"API response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved actions data")
                
                # Extract actions from the response
                if isinstance(data, dict) and 'data' in data:
                    return data.get('data', [])
                elif isinstance(data, list):
                    return data
                else:
                    # If we can't determine the structure, return the whole data
                    return [data]
            else:
                logger.error(f"Failed to get actions: Status {response.status_code}, Response: {response.text}")
                raise Exception(f"Failed to get actions: Status {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting actions: {str(e)}")
            raise Exception(f"Network error getting actions: {str(e)}") 