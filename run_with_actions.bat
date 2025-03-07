@echo off
echo SafetyCulture MCP Server with Enhanced Action Support
echo -------------------------------------------------
echo.
echo This server now has enhanced support for SafetyCulture Actions:
echo.
echo ACTION TOOLS:
echo - get_actions: List actions with filtering options
echo   * Filter by status (in_progress, completed, overdue)
echo   * Filter by priority (low, medium, high)
echo   * View detailed information for each action
echo.
echo - get_action_details: Get full details about a specific action by ID
echo.
echo INSPECTION TOOLS:
echo - authenticate: Authenticate with your API key
echo - get_inspections: List inspections for a time period
echo - get_inspection_trends: View inspection trends over time
echo - compare_injury_reports: Compare data between time periods
echo.
echo Press Ctrl+C to stop the server
echo.

set DEBUG=True
set PYTHONPATH=.
python -u src/main.py
pause 