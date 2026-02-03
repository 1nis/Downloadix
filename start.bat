@echo off
title Downloadix Launcher
color 0A

echo ========================================
echo         DOWNLOADIX LAUNCHER
echo ========================================
echo.

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [OK] Python found
echo [OK] Node.js found
echo.

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

echo [INFO] Starting Backend (Flask) on port 5000...
start "Downloadix Backend" cmd /k "cd /d %SCRIPT_DIR%backend && python app.py"

:: Wait a moment for backend to start
timeout /t 2 /nobreak >nul

echo [INFO] Starting Frontend (Vite) on port 3000...
start "Downloadix Frontend" cmd /k "cd /d %SCRIPT_DIR%frontend && npm run dev"

:: Wait a moment for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo          DOWNLOADIX STARTED!
echo ========================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:3000
echo.
echo   Opening browser...
echo.
echo   Press any key to stop all servers
echo ========================================

:: Open browser
timeout /t 2 /nobreak >nul
start http://localhost:3000

:: Wait for user input
pause >nul

:: Kill the processes
echo.
echo [INFO] Stopping servers...
taskkill /FI "WINDOWTITLE eq Downloadix Backend*" /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq Downloadix Frontend*" /F >nul 2>nul

echo [OK] Servers stopped
echo.
