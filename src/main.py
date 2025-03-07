"""
SafetyCulture MCP Server - Main Application

This module serves as the entry point for the SafetyCulture MCP server.
It sets up the MCP server and registers the necessary tools for querying SafetyCulture data.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from mcp.server import FastMCP
from mcp import Tool
from pydantic import BaseModel, Field
from typing import Optional

# Import custom tools and utilities
from tools.inspection_tools import (
    get_inspections_tool,
    get_inspection_trends_tool,
    compare_injury_reports_tool,
    GetInspectionsParams,
    GetInspectionTrendsParams,
    CompareInjuryReportsParams,
    ApiKeyParam
)
from safetyculture_api.client import SafetyCultureClient

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SafetyCulture MCP Server",
    description="A Model Context Protocol server for querying SafetyCulture data",
    version="0.1.0",
)

# Initialize SafetyCulture API client
safety_client = SafetyCultureClient()

# Create MCP server
mcp_server = FastMCP("safetyculture")

# Register API key authentication tool
@mcp_server.tool()
async def authenticate(params: ApiKeyParam) -> str:
    """
    Authenticate with the SafetyCulture API using an API key.
    
    Args:
        params: Object containing the API key
        
    Returns:
        A response indicating whether authentication was successful
    """
    try:
        safety_client.set_api_key(params.api_key)
        safety_client.test_connection()
        return "Authentication successful! You can now query your SafetyCulture data."
    except Exception as e:
        return f"Authentication failed: {str(e)}"

# Register inspection tools
@mcp_server.tool()
async def get_inspections(params: GetInspectionsParams) -> str:
    """
    Get SafetyCulture inspections for a specific time period.
    
    Args:
        params: Parameters including API key, time period, and optional site/template IDs
        
    Returns:
        A string response with the inspection data
    """
    return await get_inspections_tool(params)

@mcp_server.tool()
async def get_inspection_trends(params: GetInspectionTrendsParams) -> dict:
    """
    Analyze trends in SafetyCulture inspections over time.
    
    Args:
        params: Parameters including API key, time period, and optional site/template IDs
        
    Returns:
        A binary response with a graph of inspection trends
    """
    return await get_inspection_trends_tool(params)

@mcp_server.tool()
async def compare_injury_reports(params: CompareInjuryReportsParams) -> str:
    """
    Compare injury reports between two time periods.
    
    Args:
        params: Parameters including API key, time periods, category and optional site ID
        
    Returns:
        A string response with the comparison results
    """
    return await compare_injury_reports_tool(params)

if __name__ == "__main__":
    # Run the MCP server using stdio transport
    mcp_server.run(transport="stdio")
    
    # For development/debugging, you can also run with FastAPI/uvicorn:
    # import uvicorn
    # app.include_router(mcp_server.get_router())
    # port = int(os.getenv("PORT", "8000"))
    # uvicorn.run(app, host="0.0.0.0", port=port, reload=True) 