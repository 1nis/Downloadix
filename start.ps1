# Downloadix Launcher Script
# Run with: powershell -ExecutionPolicy Bypass -File start.ps1

$Host.UI.RawUI.WindowTitle = "Downloadix Launcher"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "         DOWNLOADIX LAUNCHER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $scriptDir "backend"
$frontendDir = Join-Path $scriptDir "frontend"

# Check Python
try {
    $null = Get-Command python -ErrorAction Stop
    Write-Host "[OK] Python found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
try {
    $null = Get-Command node -ErrorAction Stop
    Write-Host "[OK] Node.js found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Start Backend
Write-Host "[INFO] Starting Backend (Flask) on port 5000..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $backendDir -PassThru -WindowStyle Minimized

Start-Sleep -Seconds 2

# Start Frontend
Write-Host "[INFO] Starting Frontend (Vite) on port 3000..." -ForegroundColor Yellow
$frontendProcess = Start-Process -FilePath "cmd" -ArgumentList "/c npm run dev" -WorkingDirectory $frontendDir -PassThru -WindowStyle Minimized

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "          DOWNLOADIX STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "   Backend:  " -NoNewline; Write-Host "http://localhost:5000" -ForegroundColor Cyan
Write-Host "   Frontend: " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Open browser
Start-Process "http://localhost:3000"

Write-Host "   Press ENTER to stop all servers..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host

# Stop processes
Write-Host "[INFO] Stopping servers..." -ForegroundColor Yellow

try {
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
} catch {}

try {
    Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
} catch {}

# Also kill any remaining node processes for this project
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*vite*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "[OK] Servers stopped" -ForegroundColor Green
Write-Host ""
