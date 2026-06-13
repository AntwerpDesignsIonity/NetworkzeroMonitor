@echo off
REM NetworkzeroMonitor - Mobile API server launcher (Windows)
REM Ionity (Pty) Ltd - www.ionity.today
cd /d "%~dp0"

if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat

if "%NZM_HOST%"=="" set NZM_HOST=0.0.0.0
if "%NZM_PORT%"=="" set NZM_PORT=8088

echo Open NetworkzeroMonitor on your phone (same Wi-Fi): http://YOUR-PC-IP:%NZM_PORT%
echo.

python api_server.py
