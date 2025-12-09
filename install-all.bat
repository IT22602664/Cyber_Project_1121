@echo off
echo ========================================
echo Zero Trust Telehealth Platform
echo Installing All Dependencies...
echo ========================================
echo.

echo [1/5] Installing Voice Recognition dependencies...
cd "Voiceprint Analysis"
pip install -r requirements.txt
cd ..
echo.

echo [2/5] Installing Keystroke Dynamics dependencies...
cd "Keystroke Dynamics"
pip install -r requirements.txt
cd ..
echo.

echo [3/5] Installing Mouse Movement dependencies...
cd "Mouse Movement Analysis"
pip install -r requirements.txt
cd ..
echo.

echo [4/5] Installing Backend dependencies...
cd Backend
call npm install
cd ..
echo.

echo [5/5] Installing Frontend dependencies...
cd Client
call npm install
cd ..
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run start-all-services.bat to start all services
echo   2. Open http://localhost:5173 in your browser
echo   3. Register a new doctor account
echo.
pause

