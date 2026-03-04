# Security Update Script for Requirements (PowerShell)
# Updates requirements.in with security fixes from requirements-fixed.txt

Write-Host "🔒 Requirements Security Update Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend/requirements.in")) {
    Write-Host "❌ Error: backend/requirements.in not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory"
    exit 1
}

# Backup current requirements.in
Write-Host "📦 Creating backup..." -ForegroundColor Yellow
Copy-Item "backend/requirements.in" "backend/requirements.in.backup"
Write-Host "✅ Backup created: backend/requirements.in.backup" -ForegroundColor Green
Write-Host ""

# Security updates to apply
Write-Host "🔍 Security updates to apply:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Package              Current    → Fixed      CVE/Issue"
Write-Host "─────────────────────────────────────────────────────────────"
Write-Host "python-multipart     0.0.12     → 0.0.18     CVE-2024-53981"
Write-Host "python-jose          3.3.0      → 3.5.0      PYSEC-2024-232, PYSEC-2024-233"
Write-Host "cryptography         43.0.3     → 46.0.5     CVE-2024-12797"
Write-Host "aiohttp              3.11.7     → 3.13.3     Multiple CVEs"
Write-Host "requests             2.32.3     → 2.32.4     CVE-2024-47081"
Write-Host ""

# Ask for confirmation
$response = Read-Host "Apply these security updates? (y/n)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "❌ Update cancelled" -ForegroundColor Red
    Remove-Item "backend/requirements.in.backup"
    exit 0
}

Write-Host ""
Write-Host "📝 Updating requirements.in..." -ForegroundColor Yellow

# Read the file
$content = Get-Content "backend/requirements.in" -Raw

# Apply updates
$content = $content -replace 'python-multipart==0\.0\.12', 'python-multipart==0.0.18  # Security: CVE-2024-53981'
$content = $content -replace 'python-jose\[cryptography\]==3\.3\.0', 'python-jose[cryptography]==3.5.0  # Security: PYSEC-2024-232, PYSEC-2024-233'
$content = $content -replace 'cryptography==43\.0\.3', 'cryptography==46.0.5  # Security: CVE-2024-12797'
$content = $content -replace 'aiohttp==3\.11\.7', 'aiohttp==3.13.3  # Security: Multiple CVEs'
$content = $content -replace 'requests==2\.32\.3', 'requests==2.32.4  # Security: CVE-2024-47081'

# Write back
Set-Content "backend/requirements.in" $content

Write-Host "✅ requirements.in updated" -ForegroundColor Green
Write-Host ""

# Recompile
Write-Host "🔨 Recompiling requirements.txt..." -ForegroundColor Yellow
Push-Location backend
try {
    if (Get-Command pip-compile -ErrorAction SilentlyContinue) {
        pip-compile requirements.in
        Write-Host "✅ requirements.txt recompiled" -ForegroundColor Green
    } else {
        Write-Host "⚠️  pip-compile not found. Install with: pip install pip-tools" -ForegroundColor Yellow
        Write-Host "Then run: cd backend; pip-compile requirements.in"
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Review the changes: git diff backend/requirements.in backend/requirements.txt"
Write-Host "2. Test the new requirements: pip install -r backend/requirements.txt"
Write-Host "3. Run tests: pytest backend/tests/"
Write-Host "4. If all tests pass, delete requirements-fixed.txt"
Write-Host "5. Commit the changes"
Write-Host ""
Write-Host "To restore backup: Move-Item backend/requirements.in.backup backend/requirements.in -Force"
Write-Host ""
Write-Host "✅ Security update complete!" -ForegroundColor Green
