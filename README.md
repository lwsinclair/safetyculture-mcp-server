# SafetyCulture MCP Server

A Model Context Protocol (MCP) server for the SafetyCulture API. This project allows users to ask natural language questions about their SafetyCulture data after providing an API key.

## Features

- Query SafetyCulture data using natural language
- Analyze inspection data and trends
- Compare safety metrics across time periods and categories
- Visualize inspection trends over time

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `example.env` to `.env` and configure your SafetyCulture API key
4. Run the server: `python src/main.py`

## Usage with Claude for Desktop

1. Install [Claude for Desktop](https://claude.ai/desktop)
2. Configure Claude for Desktop to use this MCP server by editing the configuration file at `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
3. Add the following configuration:

```json
{
    "mcpServers": {
        "safetyculture": {
            "command": "python",
            "args": [
                "/path/to/your/project/src/main.py"
            ]
        }
    }
}
```

4. Restart Claude for Desktop
5. Use the MCP tools to query your SafetyCulture data with questions like:
   - "How many inspections were done in this site over the last 3 months?"
   - "Compare any trends in rise of injuries report for this category"

## Available Tools

### Authentication

- `authenticate`: Authenticate with the SafetyCulture API using your API key

### Inspection Data (Using Feed API)

- `get_inspections`: Get SafetyCulture inspections for a specific time period
- `get_inspection_trends`: Analyze trends in SafetyCulture inspections over time
- `compare_injury_reports`: Compare injury reports between two time periods

### Action Data (Using Feed API)

- `get_actions`: Get SafetyCulture actions for a specific time period

## About the Feed API

This MCP server uses the SafetyCulture Feed API, which provides a simple way to access collections of resources:

- `/feed/inspections`: For listing inspections with various filter parameters
- `/feed/actions`: For listing actions with various filter parameters

The Feed API is preferred over the individual resource endpoints when you need to list multiple items.

## Development

### Project Structure

```
.
├── README.md
├── requirements.txt
├── example.env
└── src/
    ├── main.py                      # Main entry point
    ├── safetyculture_api/           # SafetyCulture API client
    │   ├── __init__.py
    │   └── client.py                # API client implementation
    ├── tools/                       # MCP tools
    │   ├── __init__.py
    │   └── inspection_tools.py      # Inspection-related tools
    └── utils/                       # Utility modules
        ├── __init__.py
        ├── analysis.py              # Data analysis utilities
        ├── config.py                # Configuration management
        └── date_utils.py            # Date parsing utilities
```

### Development Log

#### Initial Setup
- Created project structure
- Set up git repository
- Added README and requirements
- Implemented SafetyCulture API client
- Added MCP tools for querying inspection data
- Added utility modules for date parsing and data analysis
- Added configuration management 