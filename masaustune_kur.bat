@echo off
setlocal
cd /d "%~dp0"

if not exist "release\SurumIstasyonu.exe" (
    call build_windows.bat
    if errorlevel 1 exit /b 1
)

for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop 2^>nul ^| find /i "Desktop"') do set "DESKTOP=%%B"
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"
call set "DESKTOP=%DESKTOP%"

copy /y "release\SurumIstasyonu.exe" "%DESKTOP%\SurumIstasyonu.exe" >nul
if errorlevel 1 (
    echo Program masaustune kopyalanamadi.
    pause
    exit /b 1
)

echo Masaustu programi hazir: %DESKTOP%\SurumIstasyonu.exe
pause
