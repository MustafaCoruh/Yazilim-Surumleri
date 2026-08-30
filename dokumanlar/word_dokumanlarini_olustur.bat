@echo off
setlocal
cd /d "%~dp0\.."

where py >nul 2>nul
if not errorlevel 1 (
    py -3 dokumanlar\docx_olustur.py
) else (
    python dokumanlar\docx_olustur.py
)

if errorlevel 1 (
    echo Word dokumanlari olusturulamadi.
    pause
    exit /b 1
)

echo Word dokumanlari dokumanlar klasorunde hazir.
pause
