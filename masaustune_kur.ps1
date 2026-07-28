$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$source = Join-Path $PSScriptRoot "release\SurumIstasyonu.exe"
if (-not (Test-Path $source)) {
    & (Join-Path $PSScriptRoot "build_windows.ps1")
}

$installDirectory = Join-Path $env:LOCALAPPDATA "Programs\SurumIstasyonu"
New-Item -ItemType Directory -Force -Path $installDirectory | Out-Null
$executable = Join-Path $installDirectory "SurumIstasyonu.exe"
Copy-Item $source $executable -Force

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Sürüm İstasyonu.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $executable
$shortcut.WorkingDirectory = $installDirectory
$shortcut.IconLocation = "$executable,0"
$shortcut.Description = "SYY, DM ve AKY paketleme uygulaması"
$shortcut.Save()

Write-Host "Masaüstü kısayolu hazır: $shortcutPath"
