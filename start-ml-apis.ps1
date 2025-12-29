# PowerShell script to start all ML API servers
# This script starts Voice, Keystroke, and Mouse Movement APIs in separate terminals

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting ML API Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to start API in new terminal
function Start-MLApi {
    param(
        [string]$Name,
        [string]$Path,
        [int]$Port
    )
    
    Write-Host "Starting $Name API on port $Port..." -ForegroundColor Yellow
    
    $command = @"
cd '$Path'
Write-Host '========================================' -ForegroundColor Green
Write-Host '  $Name API Server' -ForegroundColor Green
Write-Host '  Port: $Port' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host ''
Write-Host 'Activating virtual environment...' -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1
Write-Host 'Starting API server...' -ForegroundColor Cyan
python main.py api
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
    Start-Sleep -Seconds 2
}

# Get the current directory
$rootPath = Get-Location

# Start Voice API (Port 8001)
$voicePath = Join-Path $rootPath "Voiceprint Analysis"
Start-MLApi -Name "Voice Print" -Path $voicePath -Port 8001

# Start Keystroke API (Port 8002)
$keystrokePath = Join-Path $rootPath "Keystroke Dynamics"
Start-MLApi -Name "Keystroke Dynamics" -Path $keystrokePath -Port 8002

# Start Mouse Movement API (Port 8003)
$mousePath = Join-Path $rootPath "Mouse Movement Analysis"
Start-MLApi -Name "Mouse Movement" -Path $mousePath -Port 8003

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All ML APIs Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  - Voice Print API:       http://localhost:8001" -ForegroundColor White
Write-Host "  - Keystroke Dynamics:    http://localhost:8002" -ForegroundColor White
Write-Host "  - Mouse Movement:        http://localhost:8003" -ForegroundColor White
Write-Host ""
Write-Host "Health Check URLs:" -ForegroundColor Cyan
Write-Host "  - http://localhost:8001/health" -ForegroundColor White
Write-Host "  - http://localhost:8002/health" -ForegroundColor White
Write-Host "  - http://localhost:8003/health" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

