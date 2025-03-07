@echo off
echo SafetyCulture MCP Server with Feed API
echo --------------------------------------
echo.
echo This server uses the SafetyCulture Feed API to retrieve inspections and actions.
echo The Feed API is a better approach for listing collections of resources.
echo.
echo Available tools:
echo - authenticate: Authenticate with your SafetyCulture API key
echo - get_inspections: Get inspections for a specific time period
echo - get_inspection_trends: Analyze trends in inspection data over time
echo - get_actions: Get actions for a specific time period
echo - compare_injury_reports: Compare inspections between two time periods
echo.
echo Press Ctrl+C to stop the server
echo.

set DEBUG=True
set PYTHONPATH=.
python -u src/main.py
pause 