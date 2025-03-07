@echo off
echo SafetyCulture API URL Check
echo --------------------------
echo This script will try to ping different SafetyCulture API endpoints
echo to help determine which one your account uses.
echo.

echo Testing main base URLs:
echo ------------------------
echo Testing api.safetyculture.io...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.io

echo.
echo Testing api.safetyculture.com...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.com

echo.
echo Testing api.eu.safetyculture.io (EU region)...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.eu.safetyculture.io

echo.
echo Testing api.au.safetyculture.io (AU region)...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.au.safetyculture.io

echo.
echo Testing correct inspection endpoints:
echo -----------------------------------
echo Testing https://api.safetyculture.io/inspections/v1/inspections/...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.io/inspections/v1/inspections/

echo.
echo Testing https://api.safetyculture.io/inspections/v1/templates/...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.io/inspections/v1/templates/

echo.
echo Testing legacy endpoints:
echo -----------------------
echo Testing https://api.safetyculture.io/v1/audits...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.io/v1/audits

echo.
echo Testing https://api.safetyculture.io/v1/templates...
curl -s -o nul -w "Status: %%{http_code}\n" https://api.safetyculture.io/v1/templates

echo.
echo.
echo Notes on status codes:
echo - 200: Endpoint exists and is accessible
echo - 401/403: Endpoint exists but requires authentication
echo - 404: Endpoint doesn't exist or is at a different URL
echo.
echo If any of these return Status: 200 or Status: 401/403, that's likely your API endpoint.
echo.
pause 