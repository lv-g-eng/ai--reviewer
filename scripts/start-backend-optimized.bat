@echo off
echo ========================================
echo AI Code Review Platform - Backend Startup
echo ========================================

echo.
echo [1/5] Checking database services...

REM Check if PostgreSQL is running
docker ps | findstr postgres-ai-review >nul
if %errorlevel% neq 0 (
    echo Starting PostgreSQL...
    docker run -d --name postgres-ai-review ^
      -e POSTGRES_DB=ai_code_review ^
      -e POSTGRES_USER=postgres ^
      -e POSTGRES_PASSWORD=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 ^
      -p 5432:5432 ^
      postgres:16-alpine
    timeout /t 10 /nobreak >nul
) else (
    echo PostgreSQL already running
)

REM Check if Redis is running
docker ps | findstr redis-ai-review >nul
if %errorlevel% neq 0 (
    echo Starting Redis...
    docker run -d --name redis-ai-review ^
      -p 6379:6379 ^
      redis:7-alpine redis-server --requirepass c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8
    timeout /t 5 /nobreak >nul
) else (
    echo Redis already running
)

REM Check if Neo4j is running
docker ps | findstr neo4j-ai-review >nul
if %errorlevel% neq 0 (
    echo Starting Neo4j...
    docker run -d --name neo4j-ai-review ^
      -e NEO4J_AUTH=neo4j/b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7 ^
      -e NEO4J_PLUGINS=["apoc"] ^
      -p 7474:7474 -p 7687:7687 ^
      neo4j:5.15-community
    timeout /t 15 /nobreak >nul
) else (
    echo Neo4j already running
)

echo.
echo [2/5] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [3/5] Testing database connections...

REM Test PostgreSQL
echo Testing PostgreSQL...
docker exec postgres-ai-review psql -U postgres -d ai_code_review -c "SELECT 1;" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL connection successful
) else (
    echo ❌ PostgreSQL connection failed
)

REM Test Redis
echo Testing Redis...
docker exec redis-ai-review redis-cli -a c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8 ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis connection successful
) else (
    echo ❌ Redis connection failed
)

echo.
echo [4/5] Starting FastAPI backend...
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo [5/5] Backend startup complete!
echo Backend available at: http://localhost:8000
echo Health check: http://localhost:8000/health
echo API docs: http://localhost:8000/docs