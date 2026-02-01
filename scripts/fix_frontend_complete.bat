@echo off
echo ========================================
echo Complete Frontend Fix Script
echo ========================================

cd frontend

echo.
echo [1/5] Stopping any running dev servers...
taskkill /F /IM node.exe 2>nul

echo.
echo [2/5] Cleaning all build artifacts...
if exist .next rmdir /s /q .next
if exist dist rmdir /s /q dist
if exist node_modules\.cache rmdir /s /q node_modules\.cache

echo.
echo [3/5] Clearing npm cache...
npm cache clean --force

echo.
echo [4/5] Reinstalling dependencies...
del package-lock.json 2>nul
npm install

echo.
echo [5/5] Building project...
npm run build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Build successful! Starting dev server...
    echo ========================================
    npm run dev
) else (
    echo.
    echo ========================================
    echo Build failed. Check errors above.
    echo ========================================
    pause
)
