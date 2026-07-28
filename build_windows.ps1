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
& $python -m PyInstaller --noconfirm --clean --onedir --noupx --windowed --name SurumIstasyonu `
    --icon "assets\app_icon.ico" yazilim_surumleri.py

New-Item -ItemType Directory -Force -Path release | Out-Null
$releaseDirectory = Join-Path $PSScriptRoot "release\SurumIstasyonu"
Remove-Item $releaseDirectory -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $PSScriptRoot "release\SurumIstasyonu.exe") -Force -ErrorAction SilentlyContinue
Copy-Item (Join-Path $PSScriptRoot "dist\SurumIstasyonu") $releaseDirectory -Recurse
Write-Host "Hazır: $releaseDirectory\SurumIstasyonu.exe"
