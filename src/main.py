"""
SafetyCulture MCP Server - Main Application

This module serves as the entry point for the SafetyCulture MCP server.
It sets up the MCP server and registers the necessary tools for querying SafetyCulture data.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from mcp_python import (
    create_mcp_server,
    ContextAware,
    Tool,
    Parameter,
    ParameterType,
    StringResponse,
)

# Import custom tools and utilities
from tools.inspection_tools import (
    get_inspections_tool,
    get_inspection_trends_tool,
    compare_injury_reports_tool,
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
mcp_server = create_mcp_server(app)

# Register tools with the MCP server
mcp_server.register_tool(get_inspections_tool)
mcp_server.register_tool(get_inspection_trends_tool)
mcp_server.register_tool(compare_injury_reports_tool)

# API key parameter - shared across tools
api_key_param = Parameter(
    name="api_key",
    type=ParameterType.STRING,
    description="SafetyCulture API key",
    required=True
)

# Register API key authentication tool
@mcp_server.tool("authenticate")
@ContextAware()
def authenticate(api_key: str = api_key_param) -> StringResponse:
    """
    Authenticate with the SafetyCulture API using an API key.
    
    Args:
        api_key: SafetyCulture API key
        
    Returns:
        A response indicating whether authentication was successful
    """
    try:
        safety_client.set_api_key(api_key)
        safety_client.test_connection()
        return StringResponse("Authentication successful! You can now query your SafetyCulture data.")
    except Exception as e:
        return StringResponse(f"Authentication failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 