@echo off
title ErgoAnalyzer - Installation
cd /d "%~dp0"

echo ============================================================
echo   ErgoAnalyzer Installation
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo [1/3] Python found. Installing dependencies...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/3] Dependencies installed successfully.
echo.

:: Create desktop shortcut
echo [3/3] Creating desktop shortcut...

set SCRIPT="%TEMP%\CreateShortcut.vbs"
set SHORTCUT="%USERPROFILE%\Desktop\ErgoAnalyzer.lnk"
set TARGET="%~dp0Run ErgoAnalyzer.bat"
set ICON="%~dp0static\icon.ico"

echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = %SHORTCUT% >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = %TARGET% >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "ErgoAnalyzer - RULA and REBA Posture Analysis" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo A shortcut "ErgoAnalyzer" has been created on your Desktop.
echo.
echo To run the app:
echo   1. Double-click "ErgoAnalyzer" on your Desktop
echo   2. Or double-click "Run ErgoAnalyzer.bat" in this folder
echo.
echo The app will automatically open in your browser.
echo.
echo ============================================================
pause
