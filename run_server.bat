@echo off
echo SafetyCulture MCP Server
echo ----------------------
echo.
echo This server allows querying SafetyCulture data with natural language using Claude.
echo The server uses the SafetyCulture Feed API for optimal data access.
echo.
echo AVAILABLE TOOLS:
echo.
echo [Authentication]
echo - authenticate: Connect with your SafetyCulture API key
echo.
echo [Inspection Tools]
echo - get_inspections: Get inspections for a specific time period
echo - get_inspection_trends: Analyze trends in inspection data over time
echo - compare_injury_reports: Compare data between two time periods
echo.
echo [Action Tools]
echo - get_actions: List actions with powerful filtering options
echo   * Filter by status (in_progress, completed, overdue)
echo   * Filter by priority (low, medium, high)
echo   * View detailed information for each action
echo - get_action_details: Get full details about a specific action by ID
echo.
echo CONFIGURATION: 
echo - Edit the .env file to set your API key for persistent configuration
echo - Or set the SAFETYCULTURE_API_KEY environment variable before running
echo.
echo Press Ctrl+C to stop the server
echo.

set DEBUG=True
set PYTHONPATH=.
python -u src/main.py
pause 