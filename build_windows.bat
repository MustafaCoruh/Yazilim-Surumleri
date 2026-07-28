@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)
if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)
if not defined PYTHON_CMD (
    echo Python 3.11 veya ustu bulunamadi.
    pause
    exit /b 1
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if errorlevel 1 rmdir /s /q ".venv"
)
if not exist ".venv\Scripts\python.exe" (
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :error
)

set "VENV_PYTHON=.venv\Scripts\python.exe"
echo Bagimliliklar kuruluyor...
"%VENV_PYTHON%" -m pip install -e ".[dev]"
if errorlevel 1 goto :error
echo Testler calistiriliyor...
"%VENV_PYTHON%" -m pytest
if errorlevel 1 goto :error
"%VENV_PYTHON%" -m package_builder.icon assets
if errorlevel 1 goto :error
echo Windows programi olusturuluyor...
"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed --name SurumIstasyonu --icon "assets\app_icon.ico" yazilim_surumleri.py
if errorlevel 1 goto :error

if not exist release mkdir release
copy /y "dist\SurumIstasyonu.exe" "release\SurumIstasyonu.exe" >nul
if errorlevel 1 goto :error
echo.
echo Hazir: %CD%\release\SurumIstasyonu.exe
pause
exit /b 0

:error
echo.
echo Program olusturulamadi. Yukaridaki hata ayrintilarini kontrol edin.
pause
exit /b 1
