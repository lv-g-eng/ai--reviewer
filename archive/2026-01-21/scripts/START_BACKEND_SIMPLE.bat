@echo off
echo ========================================
echo   Starting Backend (No Database Mode)
echo ========================================
echo.
echo This will start the backend without
echo requiring PostgreSQL, Neo4j, or Redis.
echo.
echo The /health endpoint will work, but
echo most API features will be limited.
echo.

cd /d "%~dp0backend"

echo Starting FastAPI server...
echo.
echo Backend available at:
echo   http://localhost:8000
echo   http://localhost:8000/docs
echo   http://localhost:8000/health
echo.
echo Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
