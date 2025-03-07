@echo off
echo Starting SafetyCulture MCP Server with debug output...
echo Press Ctrl+C to stop the server

set DEBUG=True
set PYTHONPATH=.
python -u src/main.py
pause 