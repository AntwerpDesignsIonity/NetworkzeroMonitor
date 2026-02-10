@echo off
REM Quick launcher for NetworkzeroMonitor CLI
REM Ionity (Pty) Ltd - www.ionity.today

call venv\Scripts\activate.bat
python networkzero_cli.py %*
