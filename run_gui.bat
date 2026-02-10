@echo off
REM Quick launcher for NetworkzeroMonitor GUI
REM Ionity (Pty) Ltd - www.ionity.today

echo Starting NetworkzeroMonitor GUI...
call venv\Scripts\activate.bat
python networkzero_gui.py
pause
