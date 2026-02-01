@echo off
echo ========================================
echo Frontend Build Fix Script
echo ========================================

cd frontend

echo.
echo [1/4] Cleaning build artifacts...
if exist .next rmdir /s /q .next
if exist dist rmdir /s /q dist

echo.
echo [2/4] Installing dependencies...
call npm install

echo.
echo [3/4] Running linter...
call npm run lint -- --fix

echo.
echo [4/4] Building project...
call npm run build

echo.
echo ========================================
echo Build complete!
echo ========================================
pause
