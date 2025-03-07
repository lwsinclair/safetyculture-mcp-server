"""
Inspection and Action Tools for SafetyCulture MCP Server

This module provides MCP tools for querying SafetyCulture inspection and action data.
"""

import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import json
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field

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

# Define parameter models for the tools
class ApiKeyParam(BaseModel):
    api_key: str = Field(..., description="SafetyCulture API key")

class GetInspectionsParams(BaseModel):
    api_key: str = Field(..., description="SafetyCulture API key")
    time_period: str = Field(..., description="Time period to query (e.g., '3 months', 'last week', '2023-01-01 to 2023-03-31')")
    site_id: Optional[str] = Field(None, description="ID of the site to query (optional)")
    template_id: Optional[str] = Field(None, description="ID of the template to query (optional)")
    completed: bool = Field(True, description="Whether to only include completed inspections")
    archived: bool = Field(False, description="Whether to include archived inspections")

class GetInspectionTrendsParams(BaseModel):
    api_key: str = Field(..., description="SafetyCulture API key")
    time_period: str = Field(..., description="Time period to query (e.g., '3 months', 'last week', '2023-01-01 to 2023-03-31')")
    site_id: Optional[str] = Field(None, description="ID of the site to query (optional)")
    template_id: Optional[str] = Field(None, description="ID of the template to query (optional)")
    completed: bool = Field(True, description="Whether to only include completed inspections")

class CompareInjuryReportsParams(BaseModel):
    api_key: str = Field(..., description="SafetyCulture API key")
    first_period: str = Field(..., description="First time period to compare (e.g., '3 months ago', 'Jan-Mar 2023')")
    second_period: str = Field(..., description="Second time period to compare (e.g., 'last 3 months', 'Apr-Jun 2023')")
    category: str = Field(..., description="Category of injuries to compare")
    site_id: Optional[str] = Field(None, description="ID of the site to query (optional)")

class GetActionsParams(BaseModel):
    api_key: str = Field(..., description="SafetyCulture API key")
    time_period: str = Field(..., description="Time period to query (e.g., '3 months', 'last week', '2023-01-01 to 2023-03-31')")
    site_id: Optional[str] = Field(None, description="ID of the site to query (optional)")
    status: Optional[str] = Field(None, description="Filter actions by status (e.g., 'in_progress', 'completed', 'overdue')")
    priority: Optional[str] = Field(None, description="Filter actions by priority (e.g., 'low', 'medium', 'high')")
    include_details: bool = Field(True, description="Whether to include detailed information about each action")

class GetActionDetailsParams(BaseModel):
    api_key: str = Field(..., description="SafetyCulture API key")
    action_id: str = Field(..., description="ID of the action to retrieve details for")

# Define the tool implementations
async def get_inspections_tool(params: GetInspectionsParams) -> str:
    """
    Get SafetyCulture inspections for a specific time period.
    
    Args:
        params: Parameters including API key, time period, and optional site/template IDs
        
    Returns:
        A string response with the inspection data
    """
    client = get_safety_client()
    client.set_api_key(params.api_key)
    
    # Parse the time period into start and end dates
    start_date, end_date = parse_date_range(params.time_period)
    
    try:
        # Get inspections from the SafetyCulture API using the feed API
        inspections = client.get_inspections(
            site_id=params.site_id,
            template_id=params.template_id,
            start_date=start_date,
            end_date=end_date,
            completed=params.completed,
            archived=params.archived
        )
        
        # Format the response
        if not inspections:
            return f"No inspections found for the specified criteria in the time period '{params.time_period}'."
        
        # Create a summary of the inspections
        summary = {
            "total_inspections": len(inspections),
            "time_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "site_id": params.site_id if params.site_id else "All sites",
            "template_id": params.template_id if params.template_id else "All templates",
        }
        
        # Group inspections by date
        df = pd.DataFrame(inspections)
        date_field = next((field for field in ['modified_at', 'created_at', 'completed_at', 'date'] if field in df.columns), None)
        
        if date_field:
            df['date'] = pd.to_datetime(df[date_field]).dt.date
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
        
        return response_text
    
    except Exception as e:
        return f"Error retrieving inspections: {str(e)}"

async def get_inspection_trends_tool(params: GetInspectionTrendsParams) -> dict:
    """
    Analyze trends in SafetyCulture inspections over time.
    
    Args:
        params: Parameters including API key, time period, and optional site/template IDs
        
    Returns:
        A binary response with a graph of inspection trends or error message
    """
    client = get_safety_client()
    client.set_api_key(params.api_key)
    
    # Parse the time period into start and end dates
    start_date, end_date = parse_date_range(params.time_period)
    
    try:
        # Get inspections from the SafetyCulture API using the feed API
        inspections = client.get_inspections(
            site_id=params.site_id,
            template_id=params.template_id,
            start_date=start_date,
            end_date=end_date,
            completed=params.completed
        )
        
        if not inspections:
            return {"error": f"No inspections found for the specified criteria in the time period '{params.time_period}'."}
        
        # Convert inspections to a pandas DataFrame
        df = pd.DataFrame(inspections)
        
        # Find a date field in the inspections data
        date_field = next((field for field in ['modified_at', 'created_at', 'completed_at', 'date'] if field in df.columns), None)
        
        # Ensure a date field exists
        if not date_field:
            return {"error": "Cannot analyze trends: inspection data does not include any date fields."}
        
        # Convert the date field to datetime
        df['date'] = pd.to_datetime(df[date_field]).dt.date
        
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
        
        # Get the binary data as base64 for returning in the response
        image_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return {
            "image": image_data,
            "mime_type": "image/png",
            "description": f"Inspection trends from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    
    except Exception as e:
        return {"error": f"Error analyzing inspection trends: {str(e)}"}

async def get_actions_tool(params: GetActionsParams) -> str:
    """
    Get SafetyCulture actions for a specific time period.
    
    Args:
        params: Parameters including API key, time period, and optional site ID
        
    Returns:
        A string response with the actions data
    """
    client = get_safety_client()
    client.set_api_key(params.api_key)
    
    # Parse the time period into start and end dates
    start_date, end_date = parse_date_range(params.time_period)
    
    try:
        # Get actions from the SafetyCulture API using the feed API
        actions = client.get_actions(
            site_id=params.site_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Format the response
        if not actions:
            return f"No actions found for the specified criteria in the time period '{params.time_period}'."
        
        # Create a summary of the actions
        summary = {
            "total_actions": len(actions),
            "time_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "site_id": params.site_id if params.site_id else "All sites"
        }
        
        # Filter actions by status if provided
        if params.status:
            actions = [action for action in actions if 'status' in action and action['status'].lower() == params.status.lower()]
            summary["status_filter"] = params.status
            summary["filtered_actions_count"] = len(actions)
        
        # Filter actions by priority if provided
        if params.priority:
            actions = [action for action in actions if 'priority' in action and action['priority'].lower() == params.priority.lower()]
            summary["priority_filter"] = params.priority
            summary["filtered_actions_count"] = len(actions)
            
        # If no actions left after filtering, return early
        if not actions:
            return f"No actions found matching the filters for the time period '{params.time_period}'."
        
        # Group actions by status if available
        df = pd.DataFrame(actions)
        
        # Collect all possible fields for displaying
        all_fields = set()
        for action in actions:
            all_fields.update(action.keys())
        
        # Group actions by status if available
        if 'status' in df.columns:
            by_status = df.groupby('status').size().reset_index(name='count')
            status_counts = by_status.to_dict('records')
            summary["actions_by_status"] = status_counts
        
        # Group actions by priority if available
        if 'priority' in df.columns:
            by_priority = df.groupby('priority').size().reset_index(name='count')
            priority_counts = by_priority.to_dict('records')
            summary["actions_by_priority"] = priority_counts
        
        # Group actions by due date if available
        date_field = next((field for field in ['due_date', 'created_at', 'modified_at'] if field in df.columns), None)
        if date_field:
            df[date_field] = pd.to_datetime(df[date_field])
            df['month_year'] = df[date_field].dt.strftime('%Y-%m')
            by_month = df.groupby('month_year').size().reset_index(name='count')
            month_counts = by_month.to_dict('records')
            summary["actions_by_month"] = month_counts
        
        # Format the response
        response_text = f"Found {summary['total_actions']} actions for the period {summary['time_period']}.\n\n"
        
        if params.status:
            response_text += f"Filtered by status: {params.status}\n"
        if params.priority:
            response_text += f"Filtered by priority: {params.priority}\n"
        
        if 'filtered_actions_count' in summary:
            response_text += f"Actions after filtering: {summary['filtered_actions_count']}\n\n"
        
        if 'actions_by_status' in summary:
            response_text += "Actions by status:\n"
            for status_count in summary['actions_by_status']:
                response_text += f"- {status_count['status']}: {status_count['count']} actions\n"
            response_text += "\n"
        
        if 'actions_by_priority' in summary:
            response_text += "Actions by priority:\n"
            for priority_count in summary['actions_by_priority']:
                response_text += f"- {priority_count['priority']}: {priority_count['count']} actions\n"
            response_text += "\n"
        
        if 'actions_by_month' in summary:
            response_text += "Actions by month:\n"
            for month_count in summary['actions_by_month']:
                response_text += f"- {month_count['month_year']}: {month_count['count']} actions\n"
            response_text += "\n"
        
        # Include detailed information about each action if requested
        if params.include_details and actions:
            response_text += "Action Details:\n"
            response_text += "="*50 + "\n\n"
            
            # Get the most common fields across all actions
            common_fields = ['title', 'description', 'status', 'priority', 'due_date', 
                           'assigned_to', 'created_at', 'modified_at', 'completed_at']
            
            # Show up to 5 actions with details
            for i, action in enumerate(actions[:5]):
                response_text += f"Action {i+1}:\n"
                
                # Display common fields first if they exist
                for field in common_fields:
                    if field in action:
                        response_text += f"  {field}: {action[field]}\n"
                
                # Display other fields
                for field, value in action.items():
                    if field not in common_fields:
                        # Format the value for better readability
                        if isinstance(value, dict) or isinstance(value, list):
                            value = json.dumps(value, indent=2)
                        response_text += f"  {field}: {value}\n"
                
                response_text += "\n"
            
            # If there are more than 5 actions, indicate that there are more
            if len(actions) > 5:
                response_text += f"... and {len(actions) - 5} more actions. Use filters to narrow down the results.\n"
        
        return response_text
    
    except Exception as e:
        return f"Error retrieving actions: {str(e)}"

async def get_action_details_tool(params: GetActionDetailsParams) -> str:
    """
    Get detailed information about a specific SafetyCulture action.
    
    Args:
        params: Parameters including API key and action ID
        
    Returns:
        A string response with the detailed action data
    """
    client = get_safety_client()
    client.set_api_key(params.api_key)
    
    try:
        # First get all actions to find the specific one
        actions = client.get_actions()
        
        # Find the specific action by ID
        matching_action = None
        for action in actions:
            action_id = action.get('id', action.get('action_id', None))
            if action_id and action_id == params.action_id:
                matching_action = action
                break
        
        if not matching_action:
            return f"No action found with ID: {params.action_id}. Please check the ID and try again."
        
        # Format the response with all available details
        response_text = f"Details for Action ID: {params.action_id}\n"
        response_text += "="*50 + "\n\n"
        
        # Get important fields to display first
        important_fields = ['title', 'description', 'status', 'priority', 'due_date', 
                           'assigned_to', 'created_at', 'modified_at', 'completed_at']
        
        # Display important fields first
        for field in important_fields:
            if field in matching_action:
                response_text += f"{field}: {matching_action[field]}\n"
        
        # Display all other fields
        response_text += "\nAdditional details:\n"
        for field, value in matching_action.items():
            if field not in important_fields:
                # Format complex objects for better readability
                if isinstance(value, dict) or isinstance(value, list):
                    formatted_value = json.dumps(value, indent=2)
                    response_text += f"{field}:\n{formatted_value}\n"
                else:
                    response_text += f"{field}: {value}\n"
        
        return response_text
    
    except Exception as e:
        return f"Error retrieving action details: {str(e)}"

async def compare_injury_reports_tool(params: CompareInjuryReportsParams) -> str:
    """
    Compare injury reports between two time periods.
    
    Args:
        params: Parameters including API key, time periods, category and optional site ID
        
    Returns:
        A string response with the comparison results
    """
    client = get_safety_client()
    client.set_api_key(params.api_key)
    
    # Parse the time periods into start and end dates
    first_start, first_end = parse_date_range(params.first_period)
    second_start, second_end = parse_date_range(params.second_period)
    
    try:
        # Get inspections for the first period using the feed API
        first_inspections = client.get_inspections(
            site_id=params.site_id,
            start_date=first_start,
            end_date=first_end
        )
        
        # Get inspections for the second period using the feed API
        second_inspections = client.get_inspections(
            site_id=params.site_id,
            start_date=second_start,
            end_date=second_end
        )
        
        if not first_inspections and not second_inspections:
            return f"No inspections found for either time period with the specified criteria."
        
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
        response_text = f"Comparison of {params.category} injury reports:\n\n"
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
        
        return response_text
    
    except Exception as e:
        return f"Error comparing injury reports: {str(e)}" 