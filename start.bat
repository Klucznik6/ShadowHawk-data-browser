@echo off
echo.
echo ==========================================
echo  ShadowHawk Database Browser v3.0
echo  Starting Application...
echo ==========================================
echo.

REM Try to find Python - check full installations first
set PYTHON_CMD=""

REM Check Python 3.13 installation first
C:/Python313/python.exe --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=C:/Python313/python.exe
    goto :found_python
)

REM Check Python 3.12 installation
C:/Python312/python.exe --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=C:/Python312/python.exe
    goto :found_python
)

REM Check Python 3.11 installation
C:/Python311/python.exe --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=C:/Python311/python.exe
    goto :found_python
)

REM Check if python is in PATH (as fallback)
python --version >nul 2>&1
if not errorlevel 1 (
    python -m pip --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=python
        goto :found_python
    )
)

REM Python not found
echo ERROR: Python is not installed or not found
echo Please install Python 3.8+ from https://python.org
echo Make sure to add Python to your PATH during installation
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version

REM Check if required modules are installed
echo Checking dependencies...
%PYTHON_CMD% -c "import customtkinter, polars, pandas" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting ShadowHawk Database Browser...

REM Create ICO icon if it doesn't exist (for better taskbar integration)
if not exist "icon.ico" (
    echo Creating ICO icon for better Windows taskbar integration...
    %PYTHON_CMD% create_icon.py >nul 2>&1
)

echo.
%PYTHON_CMD% main.py

if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
