@echo off
echo ========================================
echo Zero Trust Telehealth Platform
echo Starting All Services...
echo ========================================
echo.

echo Starting Voice Recognition API (Port 8001)...
start "Voice API" cmd /k "cd "Voiceprint Analysis" && python main.py api"
timeout /t 3 /nobreak >nul

echo Starting Keystroke Dynamics API (Port 8002)...
start "Keystroke API" cmd /k "cd "Keystroke Dynamics" && python main.py api"
timeout /t 3 /nobreak >nul

echo Starting Mouse Movement API (Port 8003)...
start "Mouse API" cmd /k "cd "Mouse Movement Analysis" && python main.py api"
timeout /t 3 /nobreak >nul

echo Starting Backend Server (Port 5000)...
start "Backend Server" cmd /k "cd Backend && npm run dev"
timeout /t 5 /nobreak >nul

echo Starting Frontend App (Port 5173)...
start "Frontend App" cmd /k "cd Client && npm run dev"

echo.
echo ========================================
echo All services are starting!
echo ========================================
echo.
echo Please wait for all services to fully start...
echo.
echo Services:
echo   - Voice API:     http://localhost:8001
echo   - Keystroke API: http://localhost:8002
echo   - Mouse API:     http://localhost:8003
echo   - Backend:       http://localhost:5000
echo   - Frontend:      http://localhost:5173
echo.
echo Open http://localhost:5173 in your browser
echo.
pause

