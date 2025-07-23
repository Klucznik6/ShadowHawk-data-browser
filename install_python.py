#!/usr/bin/env python3
"""
ShadowHawk Database Browser - Installation Script
This script ensures packages are installed to the correct Python environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status"""
    try:
        print(f"Running: {description or ' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Error: Python 3.8+ required, but found Python {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} found")
    return True

def install_packages():
    """Install required packages"""
    packages = [
        "pandas>=2.0.0",
        "ttkthemes>=3.2.2", 
        "openpyxl>=3.1.0",
        "Pillow>=10.0.0"
    ]
    
    optional_packages = [
        "pyodbc>=4.0.39"  # For Access database support
    ]
    
    print("\n" + "="*50)
    print("Installing required packages...")
    print("="*50)
    
    success = True
    
    # Install required packages
    for package in packages:
        print(f"\nInstalling {package}...")
        if not run_command([sys.executable, "-m", "pip", "install", package]):
            print(f"✗ Failed to install {package}")
            success = False
        else:
            print(f"✓ {package} installed successfully")
    
    # Install optional packages
    print(f"\n{'-'*30}")
    print("Installing optional packages...")
    print(f"{'-'*30}")
    
    for package in optional_packages:
        print(f"\nInstalling {package} (optional)...")
        if not run_command([sys.executable, "-m", "pip", "install", package]):
            print(f"⚠ Failed to install {package} (optional - continuing)")
        else:
            print(f"✓ {package} installed successfully")
    
    return success

def test_installation():
    """Test if all packages can be imported"""
    print(f"\n{'-'*30}")
    print("Testing installation...")
    print(f"{'-'*30}")
    
    required_imports = [
        ("pandas", "import pandas as pd"),
        ("tkinter", "import tkinter"),
        ("sqlite3", "import sqlite3"),
        ("json", "import json"),
        ("threading", "import threading")
    ]
    
    optional_imports = [
        ("ttkthemes", "from ttkthemes import ThemedTk"),
        ("openpyxl", "import openpyxl"),
        ("PIL/Pillow", "from PIL import Image"),
        ("pyodbc", "import pyodbc")
    ]
    
    success = True
    
    # Test required imports
    for name, import_cmd in required_imports:
        try:
            exec(import_cmd)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name} - {e}")
            success = False
    
    # Test optional imports
    for name, import_cmd in optional_imports:
        try:
            exec(import_cmd)
            print(f"✓ {name} (optional)")
        except ImportError:
            print(f"⚠ {name} (optional - not available)")
    
    return success

def create_launcher():
    """Create a launcher script that uses the correct Python"""
    launcher_content = f'''@echo off
echo Starting ShadowHawk Database Browser...
cd /d "%~dp0"
"{sys.executable}" main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Failed to start the application.
    echo Python executable: {sys.executable}
    pause
)
'''
    
    launcher_path = Path("run_python.bat")
    try:
        with open(launcher_path, "w") as f:
            f.write(launcher_content)
        print(f"✓ Created launcher: {launcher_path.absolute()}")
        return True
    except Exception as e:
        print(f"✗ Failed to create launcher: {e}")
        return False

def main():
    """Main installation function"""
    print("ShadowHawk Database Browser - Installation Script")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return False
    
    print(f"Python executable: {sys.executable}")
    
    # Install packages
    if not install_packages():
        print("\n✗ Some required packages failed to install")
        input("Press Enter to exit...")
        return False
    
    # Test installation
    if not test_installation():
        print("\n✗ Installation test failed")
        input("Press Enter to exit...")
        return False
    
    # Create launcher
    create_launcher()
    
    print("\n" + "="*50)
    print("✓ Installation completed successfully!")
    print("="*50)
    print("\nYou can now run the application using:")
    print("1. Double-click 'run_python.bat'")
    print(f"2. Or run: {sys.executable} main.py")
    print("\nSample files available:")
    print("- sample_data.db (SQLite database)")
    print("- sample_employees.csv (CSV file)")
    print("- sample_products.json (JSON file)")
    
    input("\nPress Enter to exit...")
    return True

if __name__ == "__main__":
    main()
