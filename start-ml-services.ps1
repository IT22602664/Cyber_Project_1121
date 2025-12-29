# Zero Trust Telehealth Platform - ML Services Startup Script
# This script starts all 3 ML API services in separate PowerShell windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Zero Trust Telehealth Platform" -ForegroundColor Cyan
Write-Host "ML Services Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will start all 3 ML API services in separate terminals." -ForegroundColor Yellow
Write-Host "Each service will activate its own virtual environment." -ForegroundColor Yellow
Write-Host ""
Write-Host "Services:" -ForegroundColor Green
Write-Host "  1. Voice Recognition API (Port 8001)" -ForegroundColor White
Write-Host "  2. Keystroke Dynamics API (Port 8002)" -ForegroundColor White
Write-Host "  3. Mouse Movement Analysis API (Port 8003)" -ForegroundColor White
Write-Host ""

$rootPath = $PSScriptRoot

# Start Voice Recognition API
Write-Host "Starting Voice Recognition API (Port 8001)..." -ForegroundColor Green
$voicePath = Join-Path $rootPath "Voiceprint Analysis"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$voicePath'; .\venv\Scripts\Activate.ps1; python main.py api"
Start-Sleep -Seconds 3

# Start Keystroke Dynamics API
Write-Host "Starting Keystroke Dynamics API (Port 8002)..." -ForegroundColor Green
$keystrokePath = Join-Path $rootPath "Keystroke Dynamics"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$keystrokePath'; .\venv\Scripts\Activate.ps1; python main.py api"
Start-Sleep -Seconds 3

# Start Mouse Movement API
Write-Host "Starting Mouse Movement API (Port 8003)..." -ForegroundColor Green
$mousePath = Join-Path $rootPath "Mouse Movement Analysis"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$mousePath'; .\venv\Scripts\Activate.ps1; python main.py api"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All ML services are starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please wait for all services to initialize." -ForegroundColor Yellow
Write-Host "Check each terminal window for status." -ForegroundColor Yellow
Write-Host ""
Write-Host "Services should be available at:" -ForegroundColor Green
Write-Host "  - Voice API: http://localhost:8001/health" -ForegroundColor White
Write-Host "  - Keystroke API: http://localhost:8002/health" -ForegroundColor White
Write-Host "  - Mouse API: http://localhost:8003/health" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

