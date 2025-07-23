@echo off
echo Starting ShadowHawk Database Browser...
cd /d "%~dp0"

REM Try to find the correct Python executable
set PYTHON_EXE=python

REM Check for Python in common locations
if exist "C:\Python313\python.exe" (
    set PYTHON_EXE=C:\Python313\python.exe
    echo Using Python at C:\Python313\python.exe
) else if exist "C:\Python312\python.exe" (
    set PYTHON_EXE=C:\Python312\python.exe
    echo Using Python at C:\Python312\python.exe
) else if exist "C:\Python311\python.exe" (
    set PYTHON_EXE=C:\Python311\python.exe
    echo Using Python at C:\Python311\python.exe
) else (
    echo Using system Python
)

echo.
%PYTHON_EXE% main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Failed to start the application.
    echo.
    echo Troubleshooting:
    echo 1. Make sure you have run install.bat first
    echo 2. Check that all packages are installed for the correct Python version
    echo 3. Try running: %PYTHON_EXE% -c "import pandas; print('pandas OK')"
    echo.
    echo Current Python executable: %PYTHON_EXE%
    %PYTHON_EXE% --version
    echo.
    pause
)
