@echo off
echo SafetyCulture API - Testing List Endpoints
echo ------------------------------------
echo This script will test various SafetyCulture API endpoints to find the correct one for listing inspections.
echo.

if "%~1"=="" (
    echo Please provide your API key as a parameter:
    echo test_list.bat YOUR_API_KEY
    echo.
    echo Or run without parameters to be prompted:
    python test_safetyculture_list.py
    goto :end
) else (
    python test_safetyculture_list.py %1
)

:end
pause 