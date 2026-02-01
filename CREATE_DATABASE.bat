@echo off
echo ========================================
echo   Creating PostgreSQL Database
echo ========================================
echo.

echo This will create the 'ai_code_review' database
echo.

REM Update this path if your PostgreSQL is installed elsewhere
set PSQL_PATH=D:\PostgreSQL\bin\psql.exe

REM Check if psql exists
if not exist "%PSQL_PATH%" (
    echo ERROR: psql.exe not found at %PSQL_PATH%
    echo Please update the PSQL_PATH in this script
    echo.
    pause
    exit /b 1
)

echo Creating database...
"%PSQL_PATH%" -U postgres -c "CREATE DATABASE ai_code_review;"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Database created successfully!
) else (
    echo.
    echo ⚠️  Database might already exist or there was an error
    echo This is OK if the database already exists
)

echo.
echo Verifying database...
"%PSQL_PATH%" -U postgres -c "\l" | find "ai_code_review"

echo.
echo ========================================
echo   Done!
echo ========================================
pause
