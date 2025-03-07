@echo off
echo SafetyCulture MCP Server - Try API Key
echo -------------------------------------
echo.

if "%~1"=="" (
    echo Please provide your API key as a parameter:
    echo try_api_key.bat YOUR_API_KEY_HERE
    goto :end
)

echo Setting environment variables...
set SAFETYCULTURE_API_KEY=%1
set DEBUG=True
set PYTHONPATH=.

echo.
echo Running MCP server with API key: %1
echo.
echo Press Ctrl+C to stop the server

python -u src/main.py

:end
pause 