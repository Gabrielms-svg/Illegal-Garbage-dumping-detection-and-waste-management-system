@echo off
REM Automated development server startup script (batch version)
REM Usage: start-dev.bat
REM Starts mediamtx, rtsp stream processor, activates venv, and runs Django dev server

setlocal enabledelayedexpansion

REM Get script directory (project root)
set "ProjectRoot=%~dp0"
set "ProjectRoot=%ProjectRoot:~0,-1%"
set "GarbmgmtDir=%ProjectRoot%\garbmgmt"
set "CctvcamstreamDir=%GarbmgmtDir%\login\cctvcamstream"
set "VenvPath=%ProjectRoot%\garbenv"

echo.
echo ================================================================================
echo Illegal Garbage Dump Detection System - Development Startup
echo ================================================================================
echo.

REM Verify key paths exist
if not exist "%ProjectRoot%" (
    echo ERROR: Project root not found: %ProjectRoot%
    exit /b 1
)
if not exist "%GarbmgmtDir%" (
    echo ERROR: garbmgmt directory not found: %GarbmgmtDir%
    exit /b 1
)
if not exist "%VenvPath%" (
    echo ERROR: Virtual environment not found: %VenvPath%
    exit /b 1
)

REM [1/3] Start mediamtx.exe in background
echo [1/3] Starting mediamtx.exe...
set "MediamtxExe=%CctvcamstreamDir%\mediamtx_v1.15.6_windows_amd64\mediamtx.exe"
if exist "%MediamtxExe%" (
    start "" "%MediamtxExe%"
    echo       Started in background
    timeout /t 1 /nobreak >nul
) else (
    echo       WARNING: mediamtx.exe not found. Continuing without it...
)

REM [2/3] Start rtsp.py in background
echo [2/3] Starting RTSP stream processor (rtsp.py)...
set "RtspScript=%CctvcamstreamDir%\rtsp.py"
set "PythonExe=%VenvPath%\Scripts\python.exe"
if exist "%RtspScript%" (
    if exist "%PythonExe%" (
        start "" "%PythonExe%" "%RtspScript%"
        echo       Started in background
        timeout /t 1 /nobreak >nul
    ) else (
        echo       WARNING: Python not found in venv
    )
) else (
    echo       WARNING: rtsp.py not found. Continuing without it...
)

REM [3/3] Activate venv and start Django
echo [3/3] Activating virtual environment and starting Django...
call "%VenvPath%\Scripts\activate.bat"
cd /d "%GarbmgmtDir%"

echo.
echo ================================================================================
echo All services started. Django server starting on http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server.
echo ================================================================================
echo.

python manage.py runserver 0.0.0.0:8000

endlocal
