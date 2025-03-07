@echo off
echo SafetyCulture API Test Tool
echo -------------------------
echo.
echo This tool helps you test the SafetyCulture API with your key.
echo.
echo Usage Options:
echo -------------
echo 1. test_api.bat                  - Run all tests (interactive)
echo 2. test_api.bat YOUR_API_KEY     - Run all tests with the provided key
echo 3. test_api.bat feed YOUR_API_KEY - Test just the feed API
echo 4. test_api.bat url              - Check which API URLs are accessible
echo.

if "%~1"=="feed" (
    echo Testing the Feed API endpoints...
    python test_feed_api.py %2
    goto :end
) else if "%~1"=="url" (
    echo Testing API URLs accessibility...
    call :check_urls
    goto :end
) else if "%~1"=="" (
    echo Running interactive API tests...
    python test_feed_api.py
    goto :end
) else (
    echo Running all tests with provided API key...
    python test_feed_api.py %1
)

:end
echo.
echo Testing completed. See above for results.
pause
exit /b 0

:check_urls
echo.
echo Testing main base URLs:
echo ------------------------
echo Testing api.safetyculture.io...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.io

echo.
echo Testing correct feed endpoints:
echo ----------------------------
echo Testing https://api.safetyculture.io/feed/inspections...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.io/feed/inspections

echo.
echo Testing https://api.safetyculture.io/feed/actions...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.io/feed/actions

echo.
echo Notes on status codes:
echo - 200: Endpoint exists and is accessible
echo - 401/403: Endpoint exists but requires authentication
echo - 404: Endpoint doesn't exist or is at a different URL
exit /b 0 