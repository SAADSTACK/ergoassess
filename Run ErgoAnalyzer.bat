@echo off
title ErgoAnalyzer - Starting...
cd /d "%~dp0"

echo ============================================================
echo   ErgoAnalyzer - Ergonomic Posture Analysis System
echo   RULA and REBA Assessment Tool
echo ============================================================
echo.
echo Starting server... Please wait.
echo.
echo Once ready, your browser will open automatically.
echo Keep this window open while using the application.
echo Press Ctrl+C to stop the server.
echo.
echo ============================================================

:: Wait a moment then open browser
start "" cmd /c "timeout /t 8 /nobreak >nul && start http://localhost:5000"

:: Start the Flask server
python app.py

pause
