@echo off
echo SafetyCulture Feed API Test
echo ----------------------------
echo Testing the SafetyCulture Feed API endpoints for inspections and actions.
echo.

if "%~1"=="" (
    echo Please provide your API key as a parameter:
    echo test_feed.bat YOUR_API_KEY
    echo.
    echo Or run without parameters to be prompted:
    python test_feed_api.py
    goto :end
) else (
    python test_feed_api.py %1
)

:end
pause 