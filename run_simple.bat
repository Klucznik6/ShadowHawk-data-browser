@echo off
echo Starting ShadowHawk Database Browser (Simple Version)...
cd /d "%~dp0"
"C:\Python313\python.exe" simple_browser.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Failed to start the application.
    echo Python executable: C:\Python313\python.exe
    pause
)
