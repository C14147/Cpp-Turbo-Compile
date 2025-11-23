<#
Build script for Windows (PowerShell) using Nuitka

Usage:
  In PowerShell run:
    .\scripts\build-windows.ps1     # uses `python` from PATH
    .\scripts\build-windows.ps1 --windows-disable-console  # pass extra nuitka args

Notes:
  - This script calls `python -m nuitka` so ensure your Python environment
    has `nuitka` installed (e.g. `python -m pip install nuitka`).
  - Extra arguments passed to the script are forwarded to Nuitka.
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

Write-Host "Building $Entrypoint with Nuitka..."

try {
    # Forward any additional args to Nuitka
    & python -m nuitka --standalone --output-dir="$BuildDir" --remove-output --show-progress --follow-imports "$Entrypoint" @args
} catch {
    Write-Error "Build failed: $_"
    exit 1
}

Write-Host "Build finished. Output located in:" -NoNewline
Write-Host " $BuildDir" -ForegroundColor Green

Write-Host "Run the produced executable from the standalone folder (check subfolder next to main binary)."
