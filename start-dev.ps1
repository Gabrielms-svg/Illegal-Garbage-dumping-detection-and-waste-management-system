# Automated development server startup script
# Usage: .\start-dev.ps1
# Starts mediamtx, rtsp stream processor, activates venv, and runs Django dev server

param(
    [switch]$SkipMediamtx = $false,
    [switch]$SkipRtsp = $false
)

# Colors for output
$InformationColor = "Cyan"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$ErrorColor = "Red"

Write-Host "=" * 80 -ForegroundColor $InformationColor
Write-Host "Illegal Garbage Dump Detection System - Development Startup" -ForegroundColor $InformationColor
Write-Host "=" * 80 -ForegroundColor $InformationColor
Write-Host ""

# Get script directory (project root)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$GarbmgmtDir = Join-Path $ProjectRoot "garbmgmt"
$CctvcamstreamDir = Join-Path $GarbmgmtDir "login" "cctvcamstream"
$VenvPath = Join-Path $ProjectRoot "garbenv"

# Verify key paths exist
$errors = @()
if (-not (Test-Path $ProjectRoot)) { $errors += "Project root not found: $ProjectRoot" }
if (-not (Test-Path $GarbmgmtDir)) { $errors += "garbmgmt directory not found: $GarbmgmtDir" }
if (-not (Test-Path $VenvPath)) { $errors += "Virtual environment not found: $VenvPath" }

if ($errors.Count -gt 0) {
    Write-Host "ERROR: Missing required paths:" -ForegroundColor $ErrorColor
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor $ErrorColor }
    exit 1
}

Write-Host "[1/4] Starting mediamtx.exe..." -ForegroundColor $InformationColor
$mediamtxExe = Join-Path $CctvcamstreamDir "mediamtx_v1.15.6_windows_amd64" "mediamtx.exe"
if (Test-Path $mediamtxExe) {
    if ($SkipMediamtx) {
        Write-Host "      (Skipped)" -ForegroundColor $WarningColor
    } else {
        try {
            Start-Process -FilePath $mediamtxExe -WorkingDirectory (Split-Path $mediamtxExe -Parent) -NoNewWindow
            Write-Host "      ✓ Started in background" -ForegroundColor $SuccessColor
            Start-Sleep -Milliseconds 500
        } catch {
            Write-Host "      ✗ Failed to start: $_" -ForegroundColor $ErrorColor
            exit 1
        }
    }
} else {
    Write-Host "      ✗ mediamtx.exe not found at: $mediamtxExe" -ForegroundColor $ErrorColor
    Write-Host "      Continuing without it..." -ForegroundColor $WarningColor
}

Write-Host "[2/4] Starting RTSP stream processor (rtsp.py)..." -ForegroundColor $InformationColor
$rtspScript = Join-Path $CctvcamstreamDir "rtsp.py"
if (Test-Path $rtspScript) {
    if ($SkipRtsp) {
        Write-Host "      (Skipped)" -ForegroundColor $WarningColor
    } else {
        try {
            # Run in background using Python from venv
            $pythonExe = Join-Path $VenvPath "Scripts" "python.exe"
            if (Test-Path $pythonExe) {
                Start-Process -FilePath $pythonExe -ArgumentList $rtspScript -WorkingDirectory $CctvcamstreamDir -NoNewWindow
                Write-Host "      ✓ Started in background" -ForegroundColor $SuccessColor
                Start-Sleep -Milliseconds 500
            } else {
                Write-Host "      ✗ Python not found in venv" -ForegroundColor $ErrorColor
            }
        } catch {
            Write-Host "      ✗ Failed to start: $_" -ForegroundColor $ErrorColor
        }
    }
} else {
    Write-Host "      ✗ rtsp.py not found at: $rtspScript" -ForegroundColor $ErrorColor
    Write-Host "      Continuing without it..." -ForegroundColor $WarningColor
}

Write-Host "[3/4] Activating virtual environment..." -ForegroundColor $InformationColor
$activateScript = Join-Path $VenvPath "Scripts" "Activate.ps1"
if (Test-Path $activateScript) {
    try {
        & $activateScript
        Write-Host "      ✓ Virtual environment activated" -ForegroundColor $SuccessColor
    } catch {
        Write-Host "      ✗ Failed to activate: $_" -ForegroundColor $ErrorColor
        exit 1
    }
} else {
    Write-Host "      ✗ Activate script not found: $activateScript" -ForegroundColor $ErrorColor
    exit 1
}

Write-Host "[4/4] Starting Django development server..." -ForegroundColor $InformationColor
Push-Location $GarbmgmtDir
Write-Host "      Working directory: $GarbmgmtDir" -ForegroundColor $InformationColor
Write-Host "      Running: python manage.py runserver 0.0.0.0:8000" -ForegroundColor $InformationColor
Write-Host ""
Write-Host "=" * 80 -ForegroundColor $SuccessColor
Write-Host "All services started. Django server is running on http://127.0.0.1:8000/" -ForegroundColor $SuccessColor
Write-Host "Press Ctrl+C to stop the Django server." -ForegroundColor $SuccessColor
Write-Host "=" * 80 -ForegroundColor $SuccessColor
Write-Host ""

try {
    python manage.py runserver 0.0.0.0:8000
} catch {
    Write-Host "ERROR starting Django server: $_" -ForegroundColor $ErrorColor
    exit 1
} finally {
    Pop-Location
}
