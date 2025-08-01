@echo off
echo.
echo ==========================================
echo  ShadowHawk Database Browser v3.0
echo  Starting Application...
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if required modules are installed
echo Checking dependencies...
python -c "import customtkinter, polars, pandas" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting ShadowHawk Database Browser...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
