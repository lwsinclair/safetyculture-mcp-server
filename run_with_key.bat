@echo off
echo SafetyCulture MCP Server - Quick Start with API Key
echo -------------------------------------------------
echo.

if "%~1"=="" (
    echo Please provide your API key as a parameter:
    echo run_with_key.bat YOUR_API_KEY
    goto :end
)

echo Setting API key and starting server...
set SAFETYCULTURE_API_KEY=%1
call run_server.bat

:end
exit /b 0 