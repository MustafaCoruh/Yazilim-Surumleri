@echo off
setlocal
cd /d "%~dp0"

if exist "release\SurumIstasyonu.exe" (
    start "" "release\SurumIstasyonu.exe"
    exit /b 0
)

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
    echo Bu kaynak klasorunu calistirmak icin Python kurun veya release\SurumIstasyonu.exe dosyasini kullanin.
    pause
    exit /b 1
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if errorlevel 1 (
        echo Tasinmis veya uyumsuz .venv temizleniyor...
        rmdir /s /q ".venv"
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo Python ortami hazirlaniyor...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" yazilim_surumleri.py
if errorlevel 1 goto :error
exit /b 0

:error
echo Uygulama baslatilamadi. Yukaridaki hata ayrintilarini kontrol edin.
pause
exit /b 1
