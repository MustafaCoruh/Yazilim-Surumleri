@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>nul
    if errorlevel 1 (
        echo Python bulunamadi. Python 3.11 veya ustunu python.org adresinden kurun.
        pause
        exit /b 1
    )
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" yazilim_surumleri.py
if errorlevel 1 goto :error
exit /b 0

:error
echo Uygulama baslatilamadi. Yukaridaki hata ayrintilarini kontrol edin.
pause
exit /b 1
