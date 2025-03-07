@echo off
echo SafetyCulture API - Exact Format Test
echo ------------------------------------
echo This script tests the SafetyCulture API using the exact format from the documentation.
echo.

if "%~1"=="" (
    echo Please provide your API key as a parameter:
    echo test_exact_format.bat YOUR_API_KEY
    echo.
    echo Or run without parameters to be prompted:
    python test_exact_format.py
    goto :end
) else (
    python test_exact_format.py %1
)

:end
pause 