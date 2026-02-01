@echo off
REM Cleanup unnecessary virtual environments
REM Keep only backend/venv which is the one actually used

echo ============================================================
echo Cleaning Up Redundant Virtual Environments
echo ============================================================
echo.

echo This will remove:
echo   - venv/ (root directory)
echo   - .venv/ (root directory)
echo.
echo This will KEEP:
echo   - backend/venv/ (used by backend Python application)
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cleanup cancelled.
    exit /b 0
)

echo.
echo Removing venv/...
if exist venv (
    rmdir /s /q venv
    echo   [OK] Removed venv/
) else (
    echo   [SKIP] venv/ not found
)

echo.
echo Removing .venv/...
if exist .venv (
    rmdir /s /q .venv
    echo   [OK] Removed .venv/
) else (
    echo   [SKIP] .venv/ not found
)

echo.
echo ============================================================
echo Cleanup Complete!
echo ============================================================
echo.
echo Remaining virtual environment:
echo   - backend/venv/ (Python 3.13.9)
echo.
echo To use the backend environment:
echo   cd backend
echo   venv\Scripts\activate
echo.
echo Or use Docker (recommended):
echo   docker-compose up -d
echo.

pause
