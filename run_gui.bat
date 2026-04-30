@echo off
REM NetworkzeroMonitor - Launch GUI (Windows)
REM Ionity (Pty) Ltd - www.ionity.today

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

venv\Scripts\python.exe networkzero_gui.py
