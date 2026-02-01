@echo off
echo Fixing all unused variables in frontend...

cd frontend\src

REM Fix reviews/[id]/page.tsx
powershell -Command "(Get-Content 'app\reviews\[id]\page.tsx') -replace 'const \[isLoading, setIsLoading\] = useState\(false\);', 'const [isLoading] = useState(false);' | Set-Content 'app\reviews\[id]\page.tsx'"

echo Done! Now run: npm run build
cd ..\..
