@echo off
echo.
echo ==========================================
echo  ShadowHawk Database Browser v3.0
echo  Installation Script
echo ==========================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not found in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo.
echo Python found! Installing dependencies...
echo.

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing ShadowHawk dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some dependencies
    echo.
    echo Try running this as Administrator, or install manually:
    echo pip install customtkinter polars pandas openpyxl
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  Installation Complete!
echo ==========================================
echo.
echo You can now run ShadowHawk Database Browser with:
echo   start.bat    (recommended)
echo   python main.py
echo.
echo Press any key to start the application now...
pause >nul

echo Starting ShadowHawk Database Browser...
python main.py
