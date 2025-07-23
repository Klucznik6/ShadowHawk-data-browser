@echo off
echo Installing ShadowHawk Database Browser...
echo.

REM Try to find Python executable
set PYTHON_EXE=python
set PIP_EXE=pip

REM Check for Python in common locations
if exist "C:\Python313\python.exe" (
    set PYTHON_EXE=C:\Python313\python.exe
    set PIP_EXE=C:\Python313\Scripts\pip.exe
    echo Found Python at C:\Python313\python.exe
) else if exist "C:\Python312\python.exe" (
    set PYTHON_EXE=C:\Python312\python.exe
    set PIP_EXE=C:\Python312\Scripts\pip.exe
    echo Found Python at C:\Python312\python.exe
) else if exist "C:\Python311\python.exe" (
    set PYTHON_EXE=C:\Python311\python.exe
    set PIP_EXE=C:\Python311\Scripts\pip.exe
    echo Found Python at C:\Python311\python.exe
) else (
    echo Using system Python
    python --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Python is not installed or not in PATH.
        echo Please install Python 3.8 or later from https://python.org
        pause
        exit /b 1
    )
)

echo Python version:
%PYTHON_EXE% --version
echo.

echo Installing required packages...
echo.

REM Install required packages using the correct pip
%PIP_EXE% install pandas>=2.0.0
%PIP_EXE% install ttkthemes>=3.2.2
%PIP_EXE% install openpyxl>=3.1.0
%PIP_EXE% install Pillow>=10.0.0

REM Try to install pyodbc (optional, for Access database support)
echo.
echo Installing optional Access database support...
%PIP_EXE% install pyodbc

echo.
echo Testing installation...
%PYTHON_EXE% -c "import pandas, ttkthemes, openpyxl; print('All packages installed successfully!')"

echo.
echo Installation complete!
echo Python executable: %PYTHON_EXE%
echo.
echo You can now run the application by double-clicking run.bat
echo or by running: %PYTHON_EXE% main.py
echo.
pause
