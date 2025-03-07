"""
Configuration Module for SafetyCulture MCP Server

This module manages configuration settings for the SafetyCulture MCP server.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# SafetyCulture API configuration
SAFETYCULTURE_API_KEY = os.getenv("SAFETYCULTURE_API_KEY", "")
SAFETYCULTURE_API_BASE_URL = os.getenv("SAFETYCULTURE_API_BASE_URL", "https://api.safetyculture.io")
SAFETYCULTURE_API_VERSION = os.getenv("SAFETYCULTURE_API_VERSION", "v1")

# MCP configuration
MCP_MODEL_NAME = os.getenv("MCP_MODEL_NAME", "claude-3-sonnet-20240229")
MCP_PROMPT_SYSTEM = os.getenv(
    "MCP_PROMPT_SYSTEM", 
    """
    You are an assistant that helps users analyze SafetyCulture inspection data.
    You have access to tools that can retrieve and analyze data from the SafetyCulture API.
    Help the user by determining which tools would be most helpful for their query and use them appropriately.
    Always respond in a helpful, concise manner.
    """
)

def get_config():
    """
    Get the current configuration settings.
    
    Returns:
        A dictionary containing all configuration settings
    """
    return {
        "server": {
            "port": PORT,
            "host": HOST,
            "debug": DEBUG
        },
        "safetyculture_api": {
            "api_key": SAFETYCULTURE_API_KEY,
            "base_url": SAFETYCULTURE_API_BASE_URL,
            "api_version": SAFETYCULTURE_API_VERSION
        },
        "mcp": {
            "model_name": MCP_MODEL_NAME,
            "prompt_system": MCP_PROMPT_SYSTEM
        }
    } 