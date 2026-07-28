$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python Launcher bulunamadı. Python 3.11 veya üstünü kurun."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $python -m pip install -e ".[dev]"
& $python -m pytest
& $python -m package_builder.icon assets
& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name SurumIstasyonu `
    --icon "assets\app_icon.ico" yazilim_surumleri.py

New-Item -ItemType Directory -Force -Path release | Out-Null
$executable = Join-Path $PSScriptRoot "dist\SurumIstasyonu.exe"
$releaseExecutable = Join-Path $PSScriptRoot "release\SurumIstasyonu.exe"
Copy-Item $executable $releaseExecutable -Force
Write-Host "Hazır: $releaseExecutable"
