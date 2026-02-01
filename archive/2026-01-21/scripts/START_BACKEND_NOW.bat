@echo off
echo ========================================
echo   Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/3] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.11 or later
    pause
    exit /b 1
)

echo.
echo [2/3] Checking dependencies...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [3/3] Starting FastAPI server...
echo.
echo ========================================
echo   Backend will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/docs (API docs)
echo   http://localhost:8000/health (health check)
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
