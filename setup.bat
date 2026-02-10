@echo off
REM NetworkzeroMonitor Setup Script for Windows
REM Ionity (Pty) Ltd - www.ionity.today

echo ========================================
echo NetworkzeroMonitor Setup
echo Ionity (Pty) Ltd
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the application:
echo   1. Run: venv\Scripts\activate.bat
echo   2. For GUI: python networkzero_gui.py
echo   3. For CLI: python networkzero_cli.py --help
echo.
pause
