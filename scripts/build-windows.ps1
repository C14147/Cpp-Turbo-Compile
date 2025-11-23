<#
Build script for Windows (PowerShell) using PyInstaller

Usage:
  In PowerShell run:
    .\scripts\build-windows.ps1     # uses `python` from PATH
    .\scripts\build-windows.ps1 --onefile --noconsole  # pass extra PyInstaller args

Notes:
  - This script calls `pyinstaller` so ensure your Python environment
    has `pyinstaller` installed (e.g. `python -m pip install pyinstaller`).
  - Extra arguments passed to the script are forwarded to PyInstaller.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
$SrcDir = Join-Path $ProjectRoot 'src'
$BuildDir = Join-Path $ProjectRoot 'build'

if (-Not (Test-Path $SrcDir)) {
    Write-Error "Source folder not found: $SrcDir"
    exit 1
}

Write-Host "Cleaning build folder: $BuildDir"
if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }

$Entrypoint = Join-Path $SrcDir 'main.py'
if (-Not (Test-Path $Entrypoint)) {
    Write-Error "Entrypoint not found: $Entrypoint"
    exit 1
}

Write-Host "Building $Entrypoint with PyInstaller..."

# Ensure build dir exists and is clean
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

$PyInstallerArgs = @(
  '--clean',
  '--noconfirm',
  '--distpath', $BuildDir,
  '--workpath', (Join-Path $BuildDir 'build_work'),
  '--specpath', (Join-Path $BuildDir 'spec')
)

# Default to one-folder; allow overriding via script args
if ($args -contains '--onefile' -or $args -contains '-F') {
  $PyInstallerArgs += '--onefile'
} else {
  # produce onedir by default
  $PyInstallerArgs += '--onedir'
}

# Forward any other args except our handled --onefile
$forward = $args | Where-Object { $_ -ne '--onefile' -and $_ -ne '-F' }

try {
  & python -m PyInstaller @PyInstallerArgs $forward "$Entrypoint"
} catch {
  Write-Error "Build failed: $_"
  exit 1
}

Write-Host "Build finished. Output located in:" -NoNewline
Write-Host " $BuildDir" -ForegroundColor Green

Write-Host "Run the produced executable from the dist folder inside $BuildDir."
