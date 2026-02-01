@echo off
echo ========================================
echo   Stopping All Services
echo ========================================
echo.

echo Stopping Redis...
taskkill /F /IM redis-server.exe 2>NUL
if "%ERRORLEVEL%"=="0" (
    echo Redis stopped ✓
) else (
    echo Redis was not running
)

echo.
echo Stopping Neo4j...
cd /d "D:\neo4j-community-2025.12.1-windows\neo4j-community-2025.12.1\bin"
neo4j.bat stop 2>NUL
echo Neo4j stopped ✓

echo.
echo ========================================
echo   Services stopped
echo ========================================
echo.
echo Note: PostgreSQL must be stopped manually
echo through pgAdmin or Services
echo.
pause
