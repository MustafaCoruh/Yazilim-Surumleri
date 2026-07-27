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
& $python -m PyInstaller --noconfirm --clean --windowed --name YazilimSurumleri yazilim_surumleri.py

New-Item -ItemType Directory -Force -Path release | Out-Null
$archive = Join-Path $PSScriptRoot "release\YazilimSurumleri-windows.zip"
Remove-Item $archive -Force -ErrorAction SilentlyContinue
Compress-Archive -Path "dist\YazilimSurumleri\*" -DestinationPath $archive
Write-Host "Hazır: $archive"
