@echo off
setlocal enabledelayedexpansion
title ErgoAssess Setup
mode con: cols=70 lines=35
color 1F

echo.
echo  ==============================================================
echo  #                                                            #
echo  #              ErgoAssess Setup Wizard                       #
echo  #              Version 1.0.0                                 #
echo  #                                                            #
echo  #  Professional RULA ^& REBA Calculator                       #
echo  #  AI-Powered Ergonomic Posture Assessment                   #
echo  #                                                            #
echo  ==============================================================
echo.
echo  Welcome to ErgoAssess Setup!
echo.
echo  This wizard will install ErgoAssess on your computer.
echo.
echo  Features:
echo    - Automatic RULA ^& REBA scoring
echo    - AI-powered pose detection
echo    - PDF report generation
echo    - 100%% offline operation
echo.
echo  Press any key to continue...
pause >nul

:: Check Python
cls
echo.
echo  Checking system requirements...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    color 4F
    echo  ============================================================
    echo  ERROR: Python is not installed!
    echo  ============================================================
    echo.
    echo  Please install Python 3.9+ from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, make sure to check:
    echo  [x] Add Python to PATH
    echo.
    echo  After installing Python, run this setup again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% found!
echo.

:: Default to user folder - no admin needed!
set "DEFAULT_DIR=%USERPROFILE%\ErgoAssess"
echo  Where do you want to install ErgoAssess?
echo.
echo  (Recommended: %DEFAULT_DIR%)
echo.
set /p "INSTALL_DIR=  Install location [%DEFAULT_DIR%]: "
if "%INSTALL_DIR%"=="" set "INSTALL_DIR=%DEFAULT_DIR%"

echo.
echo  Installing to: %INSTALL_DIR%
echo.
echo  Press any key to begin installation...
pause >nul

cls
echo.
echo  Installing ErgoAssess...
echo.

:: Create directory
echo  [1/5] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" 2>nul
if errorlevel 1 (
    echo.
    echo  Trying alternative location...
    set "INSTALL_DIR=%USERPROFILE%\Documents\ErgoAssess"
    mkdir "%INSTALL_DIR%" 2>nul
)
echo        OK
echo.

:: Extract files
echo  [2/5] Extracting application files...
if exist "ErgoAssess.zip" (
    powershell -Command "Expand-Archive -Path 'ErgoAssess.zip' -DestinationPath '%INSTALL_DIR%' -Force" 2>nul
) else (
    xcopy /E /I /Y "ErgoAssess" "%INSTALL_DIR%" >nul 2>&1
)
echo        OK
echo.

:: Install Python packages
echo  [3/5] Installing Python packages...
echo        This may take 2-5 minutes...
pushd "%INSTALL_DIR%"
pip install -r requirements.txt -q 2>nul
pip install mediapipe==0.10.9 -q 2>nul
popd
echo        OK
echo.

:: Create shortcuts
echo  [4/5] Creating shortcuts...

:: Desktop shortcut
set SCRIPT="%TEMP%\CreateShortcut.vbs"
set SHORTCUT="%USERPROFILE%\Desktop\ErgoAssess.lnk"
set TARGET="%INSTALL_DIR%\ErgoAssess.bat"

echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = %SHORTCUT% >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = %TARGET% >> %SCRIPT%
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> %SCRIPT%
echo oLink.Description = "ErgoAssess - RULA and REBA Calculator" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT% >nul 2>&1
del %SCRIPT% 2>nul

:: Start Menu shortcut
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set SHORTCUT="%STARTMENU%\ErgoAssess.lnk"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = %SHORTCUT% >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = %TARGET% >> %SCRIPT%
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> %SCRIPT%
echo oLink.Description = "ErgoAssess - RULA and REBA Calculator" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT% >nul 2>&1
del %SCRIPT% 2>nul

echo        OK
echo.

:: Create files
echo  [5/5] Creating launcher and uninstaller...

:: Create uninstaller
(
echo @echo off
echo title Uninstall ErgoAssess
echo echo.
echo echo  Uninstalling ErgoAssess...
echo echo.
echo del "%USERPROFILE%\Desktop\ErgoAssess.lnk" 2^>nul
echo del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\ErgoAssess.lnk" 2^>nul
echo rmdir /s /q "%INSTALL_DIR%"
echo echo.
echo echo  ErgoAssess has been uninstalled successfully.
echo echo.
echo pause
) > "%INSTALL_DIR%\Uninstall.bat"

:: Create launcher
(
echo @echo off
echo cd /d "%%~dp0"
echo title ErgoAssess - RULA ^& REBA Calculator
echo echo.
echo echo  ============================================================
echo echo  #              ErgoAssess                                  #
echo echo  #              RULA ^& REBA Calculator                      #
echo echo  ============================================================
echo echo.
echo echo  Starting server... Your browser will open automatically.
echo echo  Keep this window open while using the app.
echo echo  Press Ctrl+C to stop.
echo echo.
echo start "" cmd /c "timeout /t 8 /nobreak >nul && start http://localhost:5000"
echo python app.py
echo pause
) > "%INSTALL_DIR%\ErgoAssess.bat"

echo        OK
echo.

color 2F
cls
echo.
echo  ==============================================================
echo  #                                                            #
echo  #              Installation Complete!                        #
echo  #                                                            #
echo  ==============================================================
echo.
echo  ErgoAssess has been installed successfully!
echo.
echo  Installed to: %INSTALL_DIR%
echo.
echo  You can run ErgoAssess from:
echo    - Desktop shortcut: "ErgoAssess"
echo    - Start Menu: "ErgoAssess"
echo.
echo  To uninstall: Run %INSTALL_DIR%\Uninstall.bat
echo.
echo  ==============================================================
echo.
set /p "LAUNCH=  Launch ErgoAssess now? [Y/n]: "
if /i "%LAUNCH%"=="n" goto :end
if /i "%LAUNCH%"=="N" goto :end

echo.
echo  Starting ErgoAssess...
start "" "%INSTALL_DIR%\ErgoAssess.bat"

:end
echo.
echo  Thank you for installing ErgoAssess!
echo  Visit our website for documentation and updates.
echo.
timeout /t 3 >nul
