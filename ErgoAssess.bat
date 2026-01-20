@echo off
cd /d "C:\Users\saad\Desktop\MY HFE L Project\"
title ErgoAssess - RULA/REBA Calculator
echo Starting ErgoAssess...
echo.
echo Server starting at http://localhost:5000
echo Keep this window open while using the app.
echo.
start "" cmd /c "timeout /t 10 /nobreak >nul && start http://localhost:5000"
python app.py
pause
