"""
SafetyCulture API Client

This module provides a client for interacting with the SafetyCulture API.
"""

import requests
import datetime
from typing import Dict, List, Optional, Any, Union
import logging
import json

logger = logging.getLogger(__name__)

class SafetyCultureClient:
    """Client for the SafetyCulture API."""
    
    BASE_URL = "https://api.safetyculture.io"
    API_VERSION = "v1"
    
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
    
    def _set_auth_header(self, api_key: str) -> None:
        """
        Set the authorization header with the API key.
        
        Args:
            api_key: SafetyCulture API key
        """
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def test_connection(self) -> bool:
        """
        Test the connection to the SafetyCulture API.
        
        Returns:
            True if the connection is successful, False otherwise
        
        Raises:
            Exception: If the API key is not set or the connection fails
        """
        if not self.api_key:
            raise Exception("API key not set. Please set an API key first.")
        
        # Try to get the current user's profile as a connection test
        response = self.session.get(f"{self.BASE_URL}/{self.API_VERSION}/groups/mine")
        
        if response.status_code != 200:
            raise Exception(f"Failed to connect to SafetyCulture API: {response.text}")
        
        return True
    
    def get_inspections(
        self, 
        site_id: Optional[str] = None, 
        template_id: Optional[str] = None,
        start_date: Optional[Union[str, datetime.datetime]] = None,
        end_date: Optional[Union[str, datetime.datetime]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get inspections from SafetyCulture.
        
        Args:
            site_id: Optional site ID to filter inspections
            template_id: Optional template ID to filter inspections
            start_date: Optional start date to filter inspections
            end_date: Optional end date to filter inspections
            limit: Maximum number of inspections to return
            
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
        
        # Build query parameters
        params = {'limit': limit}
        if site_id:
            params['site_id'] = site_id
        if template_id:
            params['template_id'] = template_id
        if start_date:
            params['modified_after'] = start_date
        if end_date:
            params['modified_before'] = end_date
        
        # Make the API request
        response = self.session.get(
            f"{self.BASE_URL}/{self.API_VERSION}/audits", 
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get inspections: {response.text}")
        
        return response.json().get('audits', [])
    
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
        
        response = self.session.get(
            f"{self.BASE_URL}/{self.API_VERSION}/audits/{inspection_id}"
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get inspection details: {response.text}")
        
        return response.json()
    
    def get_sites(self) -> List[Dict[str, Any]]:
        """
        Get all sites available to the authenticated user.
        
        Returns:
            List of site data dictionaries
            
        Raises:
            Exception: If the API key is not set or the request fails
        """
        if not self.api_key:
            raise Exception("API key not set. Please set an API key first.")
        
        response = self.session.get(
            f"{self.BASE_URL}/{self.API_VERSION}/sites"
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get sites: {response.text}")
        
        return response.json().get('sites', [])
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        Get all templates available to the authenticated user.
        
        Returns:
            List of template data dictionaries
            
        Raises:
            Exception: If the API key is not set or the request fails
        """
        if not self.api_key:
            raise Exception("API key not set. Please set an API key first.")
        
        response = self.session.get(
            f"{self.BASE_URL}/{self.API_VERSION}/templates"
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get templates: {response.text}")
        
        return response.json().get('templates', []) 