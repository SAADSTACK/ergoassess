@echo off
setlocal enabledelayedexpansion
title ErgoAnalyzer - Building Professional Installer
cd /d "%~dp0"

echo.
echo ============================================================
echo   ErgoAnalyzer - Professional Installer Builder
echo ============================================================
echo.

:: Create directories
if not exist "dist" mkdir "dist"
if not exist "dist\ErgoAnalyzer" mkdir "dist\ErgoAnalyzer"
if not exist "installer" mkdir "installer"

echo [Step 1/5] Copying application files...
echo.

:: Copy all application files
xcopy /E /I /Y "core" "dist\ErgoAnalyzer\core" >nul
xcopy /E /I /Y "scoring" "dist\ErgoAnalyzer\scoring" >nul
xcopy /E /I /Y "recommendations" "dist\ErgoAnalyzer\recommendations" >nul
xcopy /E /I /Y "reports" "dist\ErgoAnalyzer\reports" >nul
xcopy /E /I /Y "templates" "dist\ErgoAnalyzer\templates" >nul
xcopy /E /I /Y "static" "dist\ErgoAnalyzer\static" >nul
if exist "tests" xcopy /E /I /Y "tests" "dist\ErgoAnalyzer\tests" >nul

copy /Y "app.py" "dist\ErgoAnalyzer\" >nul
copy /Y "config.py" "dist\ErgoAnalyzer\" >nul
copy /Y "launcher.py" "dist\ErgoAnalyzer\" >nul
copy /Y "requirements.txt" "dist\ErgoAnalyzer\" >nul
copy /Y "README.md" "dist\ErgoAnalyzer\" >nul

echo    Done!
echo.

echo [Step 2/5] Creating launcher executable...
echo.

:: Create a simple VBS launcher that can be converted to EXE
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo Set fso = CreateObject^("Scripting.FileSystemObject"^)
echo.
echo ' Get script directory
echo scriptPath = WScript.ScriptFullName
echo scriptDir = fso.GetParentFolderName^(scriptPath^)
echo.
echo ' Change to script directory
echo WshShell.CurrentDirectory = scriptDir
echo.
echo ' Run Python app
echo WshShell.Run "cmd /c python launcher.py", 1, False
) > "dist\ErgoAnalyzer\ErgoAnalyzer.vbs"

:: Create batch launcher
(
echo @echo off
echo cd /d "%%~dp0"
echo title ErgoAnalyzer - Ergonomic Posture Analysis
echo echo.
echo echo ============================================================
echo echo   ErgoAnalyzer - Starting...
echo echo ============================================================
echo echo.
echo start "" "http://localhost:5000" 
echo timeout /t 3 /nobreak ^>nul
echo python launcher.py
echo pause
) > "dist\ErgoAnalyzer\ErgoAnalyzer.bat"

:: Create start menu compatible launcher
(
echo @echo off
echo cd /d "%%~dp0"
echo start "" cmd /c "python launcher.py"
) > "dist\ErgoAnalyzer\Start ErgoAnalyzer.bat"

echo    Done!
echo.

echo [Step 3/5] Creating installation script...
echo.

:: Create the installer batch that will be included
(
echo @echo off
echo setlocal enabledelayedexpansion
echo title ErgoAnalyzer Setup
echo mode con: cols=70 lines=30
echo color 1F
echo.
echo echo.
echo echo  旼컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴커
echo echo  �                                                                  �
echo echo  �              ErgoAnalyzer Setup Wizard                           �
echo echo  �              Version 1.0.0                                       �
echo echo  �                                                                  �
echo echo  �  Ergonomic Posture Analysis System                               �
echo echo  �  RULA ^& REBA Assessment Tool                                     �
echo echo  �                                                                  �
echo echo  읕컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴켸
echo echo.
echo echo  Welcome to the ErgoAnalyzer Setup Wizard.
echo echo.
echo echo  This wizard will install ErgoAnalyzer on your computer.
echo echo.
echo echo  Requirements:
echo echo    - Python 3.9 or higher
echo echo    - 500 MB free disk space
echo echo    - Windows 10/11
echo echo.
echo pause
echo.
echo :: Check Python
echo cls
echo echo.
echo echo  Checking system requirements...
echo echo.
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     color 4F
echo     echo  ERROR: Python is not installed!
echo     echo.
echo     echo  Please install Python 3.9+ from:
echo     echo  https://www.python.org/downloads/
echo     echo.
echo     echo  IMPORTANT: During installation, check the box:
echo     echo  "Add Python to PATH"
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo echo  [OK] Python found!
echo echo.
echo.
echo :: Ask for install location
echo set "DEFAULT_DIR=%%PROGRAMFILES%%\ErgoAnalyzer"
echo set /p "INSTALL_DIR=  Install location [%%DEFAULT_DIR%%]: "
echo if "%%INSTALL_DIR%%"=="" set "INSTALL_DIR=%%DEFAULT_DIR%%"
echo.
echo echo.
echo echo  Installing to: %%INSTALL_DIR%%
echo echo.
echo echo  Press any key to begin installation...
echo pause ^>nul
echo.
echo :: Create directory
echo echo.
echo echo  [1/4] Creating installation directory...
echo if not exist "%%INSTALL_DIR%%" mkdir "%%INSTALL_DIR%%"
echo if errorlevel 1 ^(
echo     echo  ERROR: Cannot create directory. Try running as Administrator.
echo     pause
echo     exit /b 1
echo ^)
echo echo        Done!
echo.
echo :: Copy files
echo echo  [2/4] Copying application files...
echo xcopy /E /I /Y "ErgoAnalyzer" "%%INSTALL_DIR%%" ^>nul
echo echo        Done!
echo.
echo :: Install dependencies
echo echo  [3/4] Installing Python packages ^(this may take a few minutes^)...
echo pushd "%%INSTALL_DIR%%"
echo pip install -r requirements.txt -q
echo popd
echo echo        Done!
echo.
echo :: Create shortcuts
echo echo  [4/4] Creating shortcuts...
echo.
echo :: Desktop shortcut
echo set SCRIPT="%%TEMP%%\CreateShortcut.vbs"
echo set SHORTCUT="%%USERPROFILE%%\Desktop\ErgoAnalyzer.lnk"
echo set TARGET="%%INSTALL_DIR%%\ErgoAnalyzer.bat"
echo.
echo echo Set oWS = WScript.CreateObject^("WScript.Shell"^) ^> %%SCRIPT%%
echo echo sLinkFile = %%SHORTCUT%% ^>^> %%SCRIPT%%
echo echo Set oLink = oWS.CreateShortcut^(sLinkFile^) ^>^> %%SCRIPT%%
echo echo oLink.TargetPath = %%TARGET%% ^>^> %%SCRIPT%%
echo echo oLink.WorkingDirectory = "%%INSTALL_DIR%%" ^>^> %%SCRIPT%%
echo echo oLink.Description = "ErgoAnalyzer - Ergonomic Posture Analysis" ^>^> %%SCRIPT%%
echo echo oLink.Save ^>^> %%SCRIPT%%
echo cscript /nologo %%SCRIPT%% ^>nul
echo del %%SCRIPT%%
echo.
echo :: Start Menu shortcut
echo set "STARTMENU=%%APPDATA%%\Microsoft\Windows\Start Menu\Programs"
echo set SHORTCUT="%%STARTMENU%%\ErgoAnalyzer.lnk"
echo echo Set oWS = WScript.CreateObject^("WScript.Shell"^) ^> %%SCRIPT%%
echo echo sLinkFile = %%SHORTCUT%% ^>^> %%SCRIPT%%
echo echo Set oLink = oWS.CreateShortcut^(sLinkFile^) ^>^> %%SCRIPT%%
echo echo oLink.TargetPath = %%TARGET%% ^>^> %%SCRIPT%%
echo echo oLink.WorkingDirectory = "%%INSTALL_DIR%%" ^>^> %%SCRIPT%%
echo echo oLink.Description = "ErgoAnalyzer - Ergonomic Posture Analysis" ^>^> %%SCRIPT%%
echo echo oLink.Save ^>^> %%SCRIPT%%
echo cscript /nologo %%SCRIPT%% ^>nul
echo del %%SCRIPT%%
echo.
echo echo        Done!
echo.
echo :: Create uninstaller
echo ^(
echo echo @echo off
echo echo title Uninstall ErgoAnalyzer
echo echo echo Uninstalling ErgoAnalyzer...
echo echo del "%%USERPROFILE%%\Desktop\ErgoAnalyzer.lnk" 2^>nul
echo echo del "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\ErgoAnalyzer.lnk" 2^>nul
echo echo rmdir /s /q "%%INSTALL_DIR%%"
echo echo echo ErgoAnalyzer has been uninstalled.
echo echo pause
echo ^) ^> "%%INSTALL_DIR%%\Uninstall.bat"
echo.
echo color 2F
echo echo.
echo echo  旼컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴커
echo echo  �                                                                  �
echo echo  �              Installation Complete!                              �
echo echo  �                                                                  �
echo echo  읕컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴켸
echo echo.
echo echo  ErgoAnalyzer has been installed successfully!
echo echo.
echo echo  You can now run ErgoAnalyzer from:
echo echo    - Desktop shortcut: "ErgoAnalyzer"
echo echo    - Start Menu: "ErgoAnalyzer"
echo echo.
echo echo  To uninstall, run: %%INSTALL_DIR%%\Uninstall.bat
echo echo.
echo set /p "LAUNCH=  Launch ErgoAnalyzer now? [Y/n]: "
echo if /i "%%LAUNCH%%"=="n" goto :end
echo if /i "%%LAUNCH%%"=="N" goto :end
echo start "" "%%INSTALL_DIR%%\ErgoAnalyzer.bat"
echo :end
echo echo.
echo pause
) > "dist\Setup.bat"

echo    Done!
echo.

echo [Step 4/5] Creating installer package...
echo.

:: Package everything into a ZIP
cd dist
powershell -Command "Compress-Archive -Path 'ErgoAnalyzer', 'Setup.bat' -DestinationPath '..\installer\ErgoAnalyzer_Installer_v1.0.0.zip' -Force"
cd ..

echo    Done!
echo.

echo [Step 5/5] Creating self-extracting installer...
echo.

:: Create SFX header
(
echo @echo off
echo setlocal
echo title ErgoAnalyzer Installer
echo echo.
echo echo Extracting ErgoAnalyzer installer...
echo echo.
echo set "TEMP_DIR=%%TEMP%%\ErgoAnalyzer_Setup_%%RANDOM%%"
echo mkdir "%%TEMP_DIR%%"
echo cd /d "%%TEMP_DIR%%"
echo.
echo :: Extract the embedded ZIP
echo powershell -Command "$bytes = [System.IO.File]::ReadAllBytes('%~f0'); $marker = [System.Text.Encoding]::ASCII.GetBytes('###ZIP_START###'); for($i=$bytes.Length-1; $i -ge 0; $i--) { $found = $true; for($j=0; $j -lt $marker.Length; $j++) { if($bytes[$i+$j] -ne $marker[$j]) { $found = $false; break } }; if($found) { $start = $i + $marker.Length; $zipBytes = New-Object byte[] ($bytes.Length - $start); [Array]::Copy($bytes, $start, $zipBytes, 0, $zipBytes.Length); [System.IO.File]::WriteAllBytes('package.zip', $zipBytes); break } }"
echo.
echo :: Extract ZIP
echo powershell -Command "Expand-Archive -Path 'package.zip' -DestinationPath '.' -Force"
echo.
echo :: Run setup
echo call Setup.bat
echo.
echo :: Cleanup
echo cd /d "%%TEMP%%"
echo rmdir /s /q "%%TEMP_DIR%%" 2^>nul
echo exit /b
echo ###ZIP_START###
) > "installer\sfx_header.bat"

:: Combine header with ZIP to create self-extracting installer
copy /b "installer\sfx_header.bat"+"installer\ErgoAnalyzer_Installer_v1.0.0.zip" "installer\ErgoAnalyzer_Setup_v1.0.0.exe" >nul
del "installer\sfx_header.bat"

echo    Done!
echo.

echo ============================================================
echo   BUILD COMPLETE!
echo ============================================================
echo.
echo   Created installer at:
echo   %CD%\installer\ErgoAnalyzer_Setup_v1.0.0.exe
echo.
echo   This installer will:
echo   - Let you choose installation location
echo   - Install all required Python packages
echo   - Create Desktop shortcut
echo   - Create Start Menu entry
echo   - Include uninstaller
echo.
echo   Note: Recipients need Python 3.9+ installed
echo.
echo ============================================================

:: Open installer folder
explorer "installer"

pause
