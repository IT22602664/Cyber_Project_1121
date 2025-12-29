# Test ML Services Health Check Script
# This script checks if all ML services are running and healthy

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ML Services Health Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="Voice Recognition API"; URL="http://localhost:8001/health"; Port=8001},
    @{Name="Keystroke Dynamics API"; URL="http://localhost:8002/health"; Port=8002},
    @{Name="Mouse Movement API"; URL="http://localhost:8003/health"; Port=8003}
)

$allHealthy = $true

foreach ($service in $services) {
    Write-Host "Checking $($service.Name)..." -ForegroundColor Yellow -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $service.URL -Method Get -TimeoutSec 5 -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            Write-Host " ✓ HEALTHY" -ForegroundColor Green
            Write-Host "  Response: $($response.Content)" -ForegroundColor Gray
        } else {
            Write-Host " ✗ UNHEALTHY (Status: $($response.StatusCode))" -ForegroundColor Red
            $allHealthy = $false
        }
    }
    catch {
        Write-Host " ✗ NOT RUNNING" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
        $allHealthy = $false
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "All ML services are healthy! ✓" -ForegroundColor Green
} else {
    Write-Host "Some ML services are not running or unhealthy! ✗" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start the services, run:" -ForegroundColor Yellow
    Write-Host "  .\start-ml-services.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

