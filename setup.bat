@echo off
REM NetworkzeroMonitor - Windows Setup Script
REM Ionity (Pty) Ltd - www.ionity.today

echo ============================================
echo   NetworkzeroMonitor  .  Ionity (Pty) Ltd
echo   Setup Script
echo ============================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo Found Python %PY_VER%

echo.
echo Creating virtual environment in .\venv ...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
pip install --upgrade pip --quiet

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet

echo.
echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo   Activate the environment:
echo     venv\Scripts\activate.bat
echo.
echo   Launch the GUI:
echo     run_gui.bat
echo.
echo   Launch the CLI:
echo     run_cli.bat --help
echo.
pause
