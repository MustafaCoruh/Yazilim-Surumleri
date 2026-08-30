$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$source = Join-Path $PSScriptRoot "release\SurumIstasyonu"
if (-not (Test-Path (Join-Path $source "SurumIstasyonu.exe"))) {
    & (Join-Path $PSScriptRoot "build_windows.ps1")
}

$installDirectory = Join-Path $env:LOCALAPPDATA "Programs\SurumIstasyonu"
$executable = Join-Path $installDirectory "SurumIstasyonu.exe"
Remove-Item $installDirectory -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item $source $installDirectory -Recurse

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
