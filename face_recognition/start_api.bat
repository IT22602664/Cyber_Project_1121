@echo off
REM ============================================================
REM  Startup Script for Face Recognition API (Windows)
REM  Model  : ResNet50 Triplet Embedding
REM  Checkpoint Path:
REM    face_recognition\models\best_resnet50_triplet.pth
REM  Platform: Zero Trust Telehealth
REM ============================================================

REM ------------------------------------------------------------
REM Print a startup banner so the operator clearly sees
REM which service is being launched.
REM ------------------------------------------------------------
echo ========================================
echo Face Recognition API
echo ResNet50 Triplet Embedding Model
echo Zero Trust Telehealth Platform
echo ========================================
echo.

REM ------------------------------------------------------------
REM Verify that Python is installed and available in PATH.
REM python --version returns a non-zero exit code if Python
REM is missing or misconfigured.
REM ------------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Print the detected Python version for visibility.
REM ------------------------------------------------------------
echo Python found:
python --version
echo.

REM ------------------------------------------------------------
REM Check whether a Python virtual environment already exists.
REM If not, create one to isolate dependencies.
REM ------------------------------------------------------------
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created successfully
    echo.
)

REM ------------------------------------------------------------
REM Activate the virtual environment.
REM "call" is required so execution returns to this script.
REM ------------------------------------------------------------
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM ------------------------------------------------------------
REM Install or update all required Python packages listed
REM in requirements.txt inside the virtual environment.
REM ------------------------------------------------------------
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo.

REM ------------------------------------------------------------
REM Verify that the trained face recognition model exists.
REM The API can start without it, but verification will fail.
REM ------------------------------------------------------------
if not exist "face_recognition\models\best_resnet50_triplet.pth" (
    echo WARNING: Face recognition model not found!
    echo Expected path:
    echo   face_recognition\models\best_resnet50_triplet.pth
    echo.
    echo Please ensure the trained model checkpoint is available.
    echo The API will start, but verification requests will fail.
    echo.
    pause
)

REM ------------------------------------------------------------
REM Start the FastAPI server using Uvicorn.
REM
REM src.api:app means:
REM   - src/api.py is the Python file
REM   - app is the FastAPI instance inside that file
REM
REM --host 0.0.0.0  -> listen on all interfaces
REM --port 8000     -> API available at http://localhost:8000
REM --reload        -> auto-restart on code changes (DEV ONLY)
REM ------------------------------------------------------------
echo Starting Face Recognition API...
echo API will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

REM ------------------------------------------------------------
REM After the server stops (Ctrl+C), deactivate the virtual
REM environment to return to the system Python context.
REM ------------------------------------------------------------
deactivate
