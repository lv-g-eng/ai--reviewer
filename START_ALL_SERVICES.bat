@echo off
echo ========================================
echo   Starting All Services
echo ========================================
echo.

REM Check if services are already running
echo [1/4] Checking existing services...
echo.

REM Start PostgreSQL (if not running)
echo [2/4] Starting PostgreSQL...
tasklist /FI "IMAGENAME eq postgres.exe" 2>NUL | find /I /N "postgres.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo PostgreSQL is already running ✓
) else (
    echo Starting PostgreSQL...
    start "" "D:\PostgreSQL\pgAdmin 4\runtime\pgAdmin4.exe"
    timeout /t 3 /nobreak >nul
)
echo.

REM Start Redis
echo [3/4] Starting Redis...
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Redis is already running ✓
) else (
    echo Starting Redis...
    start "Redis Server" /D "D:\redis-5.0.4" redis-server.exe
    timeout /t 2 /nobreak >nul
)
echo.

REM Start Neo4j
echo [4/4] Starting Neo4j...
tasklist /FI "IMAGENAME eq java.exe" 2>NUL | find /I /N "neo4j">NUL
if "%ERRORLEVEL%"=="0" (
    echo Neo4j might be running ✓
) else (
    echo Starting Neo4j...
    start "Neo4j Server" /D "D:\neo4j-community-2025.12.1-windows\neo4j-community-2025.12.1\bin" neo4j.bat console
    timeout /t 5 /nobreak >nul
)
echo.

echo ========================================
echo   All database services started!
echo ========================================
echo.
echo PostgreSQL: localhost:5432
echo Redis:      localhost:6379
echo Neo4j:      localhost:7687 (bolt)
echo            http://localhost:7474 (browser)
echo.
echo Waiting 10 seconds for services to initialize...
timeout /t 10 /nobreak >nul
echo.

echo ========================================
echo   Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

echo Starting FastAPI on http://localhost:8000
echo.
echo Press Ctrl+C to stop the backend
echo (Database services will continue running)
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
