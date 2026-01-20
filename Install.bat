@echo off
title ErgoAssess - One Click Installer
color 1F
mode con: cols=60 lines=30

echo.
echo  ========================================================
echo  #                                                      #
echo  #           ErgoAssess - RULA/REBA Calculator          #
echo  #           One Click Installer                        #
echo  #                                                      #
echo  ========================================================
echo.
echo  This will install ErgoAssess on your computer.
echo.
echo  Requirements: Python 3.9+ (python.org/downloads)
echo.
echo  Press any key to install...
pause >nul

echo.
echo  Checking Python...
echo.

python --version
if errorlevel 1 (
    color 4F
    echo.
    echo  ========================================================
    echo  ERROR: Python not found!
    echo  ========================================================
    echo.
    echo  Please install Python from:
    echo  https://python.org/downloads
    echo.
    echo  IMPORTANT: Check "Add Python to PATH" during install!
    echo.
    echo  After installing Python, run this INSTALL.bat again.
    echo.
    echo  Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo  [OK] Python found!
echo.
echo  Installing packages (this takes 2-5 minutes)...
echo  Please wait...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    color 4F
    echo.
    echo  ERROR: Package installation failed!
    echo  Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo  Creating desktop shortcut...

:: Get script directory
set "APPDIR=%~dp0"

:: Create launcher batch
(
echo @echo off
echo cd /d "%APPDIR%"
echo title ErgoAssess - RULA/REBA Calculator
echo echo Starting ErgoAssess...
echo echo.
echo echo Server starting at http://localhost:5000
echo echo Keep this window open while using the app.
echo echo.
echo start "" cmd /c "timeout /t 10 /nobreak >nul && start http://localhost:5000"
echo python app.py
echo pause
) > "%APPDIR%ErgoAssess.bat"

:: Create desktop shortcut
set SCRIPT="%TEMP%\shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\ErgoAssess.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%APPDIR%ErgoAssess.bat" >> %SCRIPT%
echo oLink.WorkingDirectory = "%APPDIR%" >> %SCRIPT%
echo oLink.Description = "ErgoAssess - RULA and REBA Calculator" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

color 2F
echo.
echo  ========================================================
echo  #                                                      #
echo  #           Installation Complete!                     #
echo  #                                                      #
echo  ========================================================
echo.
echo  Desktop shortcut "ErgoAssess" created!
echo.
echo  To run: Double-click "ErgoAssess" on your Desktop
echo.
echo  Press any key to launch ErgoAssess now...
pause >nul

start "" "%APPDIR%ErgoAssess.bat"
