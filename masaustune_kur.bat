@echo off
setlocal
cd /d "%~dp0"

if not exist "release\SurumIstasyonu\SurumIstasyonu.exe" (
    call build_windows.bat
    if errorlevel 1 exit /b 1
)

set "INSTALL=%LOCALAPPDATA%\Programs\SurumIstasyonu"
if exist "%INSTALL%" rmdir /s /q "%INSTALL%"
xcopy "release\SurumIstasyonu" "%INSTALL%\" /e /i /y >nul
if errorlevel 1 goto :error

for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop 2^>nul ^| find /i "Desktop"') do set "DESKTOP=%%B"
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"
call set "DESKTOP=%DESKTOP%"

set "VBS=%TEMP%\surum_istasyonu_shortcut.vbs"
>"%VBS%" echo Set shell = CreateObject("WScript.Shell")
>>"%VBS%" echo Set link = shell.CreateShortcut("%DESKTOP%\Surum Istasyonu.lnk")
>>"%VBS%" echo link.TargetPath = "%INSTALL%\SurumIstasyonu.exe"
>>"%VBS%" echo link.WorkingDirectory = "%INSTALL%"
>>"%VBS%" echo link.IconLocation = "%INSTALL%\SurumIstasyonu.exe,0"
>>"%VBS%" echo link.Save
cscript //nologo "%VBS%" >nul
del "%VBS%" >nul 2>nul
if errorlevel 1 goto :error

echo Masaustu kisayolu hazir: %DESKTOP%\Surum Istasyonu.lnk
pause
exit /b 0

:error
echo Program kurulamadi. Yukaridaki hata ayrintilarini kontrol edin.
pause
exit /b 1
