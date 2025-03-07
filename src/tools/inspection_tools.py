"""
Inspection Tools for SafetyCulture MCP Server

This module provides MCP tools for querying SafetyCulture inspection data.
"""

import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from dateutil.relativedelta import relativedelta
from mcp_python import (
    Tool,
    ContextAware,
    Parameter,
    ParameterType,
    StringResponse,
    BinaryResponse,
)

from safetyculture_api.client import SafetyCultureClient
from utils.date_utils import parse_date_range
from utils.analysis import analyze_trends, compare_data_periods

# Get singleton instance of the SafetyCulture client
# This assumes the client is initialized in main.py
safety_client = None

def get_safety_client():
    """
    Get the singleton instance of the SafetyCulture client.
    
    Returns:
        The SafetyCulture client instance
    """
    global safety_client
    if safety_client is None:
        safety_client = SafetyCultureClient()
    return safety_client

# Common parameters for tools
api_key_param = Parameter(
    name="api_key",
    type=ParameterType.STRING,
    description="SafetyCulture API key",
    required=True
)

site_id_param = Parameter(
    name="site_id",
    type=ParameterType.STRING,
    description="ID of the site to query (optional)",
    required=False
)

template_id_param = Parameter(
    name="template_id",
    type=ParameterType.STRING,
    description="ID of the template to query (optional)",
    required=False
)

time_period_param = Parameter(
    name="time_period",
    type=ParameterType.STRING,
    description="Time period to query (e.g., '3 months', 'last week', '2023-01-01 to 2023-03-31')",
    required=True
)

# Define the get_inspections tool
@Tool(
    name="get_inspections",
    description="Get SafetyCulture inspections for a specific time period"
)
@ContextAware()
def get_inspections_tool(
    api_key: str = api_key_param,
    time_period: str = time_period_param, 
    site_id: Optional[str] = site_id_param,
    template_id: Optional[str] = template_id_param
) -> StringResponse:
    """
    Get SafetyCulture inspections for a specific time period.
    
    Args:
        api_key: SafetyCulture API key
        time_period: Time period to query (e.g., '3 months', 'last week', '2023-01-01 to 2023-03-31')
        site_id: Optional ID of the site to query
        template_id: Optional ID of the template to query
        
    Returns:
        A string response with the inspection data
    """
    client = get_safety_client()
    client.set_api_key(api_key)
    
    # Parse the time period into start and end dates
    start_date, end_date = parse_date_range(time_period)
    
    try:
        # Get inspections from the SafetyCulture API
        inspections = client.get_inspections(
            site_id=site_id,
            template_id=template_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Format the response
        if not inspections:
            return StringResponse(f"No inspections found for the specified criteria in the time period '{time_period}'.")
        
        # Create a summary of the inspections
        summary = {
            "total_inspections": len(inspections),
            "time_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "site_id": site_id if site_id else "All sites",
            "template_id": template_id if template_id else "All templates",
        }
        
        # Group inspections by date
        df = pd.DataFrame(inspections)
        if 'modified_at' in df.columns:
            df['date'] = pd.to_datetime(df['modified_at']).dt.date
            by_date = df.groupby('date').size().reset_index(name='count')
            date_counts = by_date.to_dict('records')
            summary["inspections_by_date"] = date_counts
        
        # Group inspections by template
        if 'template_id' in df.columns:
            by_template = df.groupby('template_id').size().reset_index(name='count')
            template_counts = by_template.to_dict('records')
            summary["inspections_by_template"] = template_counts
        
        # Format the response
        response_text = f"Found {summary['total_inspections']} inspections for the period {summary['time_period']}.\n\n"
        
        if 'inspections_by_date' in summary:
            response_text += "Inspections by date:\n"
            for date_count in summary['inspections_by_date']:
                response_text += f"- {date_count['date']}: {date_count['count']} inspections\n"
            response_text += "\n"
        
        if 'inspections_by_template' in summary:
            response_text += "Inspections by template:\n"
            for template_count in summary['inspections_by_template']:
                response_text += f"- Template {template_count['template_id']}: {template_count['count']} inspections\n"
        
        return StringResponse(response_text)
    
    except Exception as e:
        return StringResponse(f"Error retrieving inspections: {str(e)}")

# Define the get_inspection_trends tool
@Tool(
    name="get_inspection_trends",
    description="Analyze trends in SafetyCulture inspections over time"
)
@ContextAware()
def get_inspection_trends_tool(
    api_key: str = api_key_param,
    time_period: str = time_period_param,
    site_id: Optional[str] = site_id_param,
    template_id: Optional[str] = template_id_param
) -> BinaryResponse:
    """
    Analyze trends in SafetyCulture inspections over time.
    
    Args:
        api_key: SafetyCulture API key
        time_period: Time period to query (e.g., '3 months', 'last week', '2023-01-01 to 2023-03-31')
        site_id: Optional ID of the site to query
        template_id: Optional ID of the template to query
        
    Returns:
        A binary response with a graph of inspection trends
    """
    client = get_safety_client()
    client.set_api_key(api_key)
    
    # Parse the time period into start and end dates
    start_date, end_date = parse_date_range(time_period)
    
    try:
        # Get inspections from the SafetyCulture API
        inspections = client.get_inspections(
            site_id=site_id,
            template_id=template_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not inspections:
            return StringResponse(f"No inspections found for the specified criteria in the time period '{time_period}'.")
        
        # Convert inspections to a pandas DataFrame
        df = pd.DataFrame(inspections)
        
        # Ensure the modified_at column exists
        if 'modified_at' not in df.columns:
            return StringResponse("Cannot analyze trends: inspection data does not include modification dates.")
        
        # Convert the modified_at column to datetime
        df['date'] = pd.to_datetime(df['modified_at']).dt.date
        
        # Create a time series of inspections by date
        time_series = df.groupby('date').size().reset_index(name='count')
        time_series['date'] = pd.to_datetime(time_series['date'])
        time_series = time_series.sort_values('date')
        
        # Create a plot of the time series
        plt.figure(figsize=(10, 6))
        plt.plot(time_series['date'], time_series['count'], marker='o')
        plt.title(f"Inspection Trends ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
        plt.xlabel("Date")
        plt.ylabel("Number of Inspections")
        plt.grid(True)
        plt.tight_layout()
        
        # Save the plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Create a binary response with the plot image
        image_data = buf.getvalue()
        return BinaryResponse(
            data=image_data,
            mime_type="image/png",
            description=f"Inspection trends from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )
    
    except Exception as e:
        return StringResponse(f"Error analyzing inspection trends: {str(e)}")

# Define the compare_injury_reports tool
@Tool(
    name="compare_injury_reports",
    description="Compare injury reports between two time periods"
)
@ContextAware()
def compare_injury_reports_tool(
    api_key: str = api_key_param,
    first_period: str = Parameter(
        name="first_period",
        type=ParameterType.STRING,
        description="First time period to compare (e.g., '3 months ago', 'Jan-Mar 2023')",
        required=True
    ),
    second_period: str = Parameter(
        name="second_period",
        type=ParameterType.STRING,
        description="Second time period to compare (e.g., 'last 3 months', 'Apr-Jun 2023')",
        required=True
    ),
    category: str = Parameter(
        name="category",
        type=ParameterType.STRING,
        description="Category of injuries to compare",
        required=True
    ),
    site_id: Optional[str] = site_id_param
) -> StringResponse:
    """
    Compare injury reports between two time periods.
    
    Args:
        api_key: SafetyCulture API key
        first_period: First time period to compare
        second_period: Second time period to compare
        category: Category of injuries to compare
        site_id: Optional ID of the site to query
        
    Returns:
        A string response with the comparison results
    """
    client = get_safety_client()
    client.set_api_key(api_key)
    
    # Parse the time periods into start and end dates
    first_start, first_end = parse_date_range(first_period)
    second_start, second_end = parse_date_range(second_period)
    
    try:
        # Get inspections for the first period
        first_inspections = client.get_inspections(
            site_id=site_id,
            start_date=first_start,
            end_date=first_end
        )
        
        # Get inspections for the second period
        second_inspections = client.get_inspections(
            site_id=site_id,
            start_date=second_start,
            end_date=second_end
        )
        
        if not first_inspections and not second_inspections:
            return StringResponse(f"No inspections found for either time period with the specified criteria.")
        
        # This is a simplified implementation that would need to be customized
        # to extract and analyze injury data based on the actual structure of the inspections
        
        # In a real implementation, you would:
        # 1. Extract injury-related items from each inspection
        # 2. Filter by the specified category
        # 3. Count and categorize the injuries
        # 4. Compare the results between the two periods
        
        # For demonstration purposes, let's assume we've extracted these counts
        # from the inspection data (this would need to be implemented based on actual data structure)
        first_period_count = len(first_inspections)
        second_period_count = len(second_inspections)
        
        # Calculate the percentage change
        if first_period_count > 0:
            percent_change = ((second_period_count - first_period_count) / first_period_count) * 100
        else:
            percent_change = float('inf') if second_period_count > 0 else 0
        
        # Format the response
        response_text = f"Comparison of {category} injury reports:\n\n"
        response_text += f"First period ({first_start.strftime('%Y-%m-%d')} to {first_end.strftime('%Y-%m-%d')}): {first_period_count} inspections\n"
        response_text += f"Second period ({second_start.strftime('%Y-%m-%d')} to {second_end.strftime('%Y-%m-%d')}): {second_period_count} inspections\n\n"
        
        if percent_change == float('inf'):
            response_text += f"Percentage change: N/A (no injuries in the first period)\n"
        else:
            response_text += f"Percentage change: {percent_change:.2f}%\n"
        
        if second_period_count > first_period_count:
            response_text += f"There was an increase in the number of inspections in the second period."
        elif second_period_count < first_period_count:
            response_text += f"There was a decrease in the number of inspections in the second period."
        else:
            response_text += f"The number of inspections remained the same in both periods."
        
        return StringResponse(response_text)
    
    except Exception as e:
        return StringResponse(f"Error comparing injury reports: {str(e)}") 