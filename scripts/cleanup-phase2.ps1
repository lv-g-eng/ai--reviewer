# Phase 2 Cleanup Script (PowerShell)
# This script helps with the remaining cleanup tasks

Write-Host "🧹 Project Cleanup - Phase 2" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Function to ask for confirmation
function Confirm-Action {
    param([string]$Message)
    $response = Read-Host "$Message (y/n)"
    return $response -eq 'y' -or $response -eq 'Y'
}

# 1. Check for test backup files
Write-Host "📋 Checking for test backup files..." -ForegroundColor Yellow
$testBackups = Get-ChildItem -Path . -Recurse -Include "*_backup.py", "*_simple.py", "*_standalone.py" -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch "node_modules|venv|\.venv" }

if ($testBackups) {
    Write-Host "Found test backup files:" -ForegroundColor Yellow
    $testBackups | ForEach-Object { Write-Host "  $_" }
    if (Confirm-Action "Delete these test backup files?") {
        $testBackups | Remove-Item -Force
        Write-Host "✅ Deleted test backup files" -ForegroundColor Green
    }
} else {
    Write-Host "✅ No test backup files found" -ForegroundColor Green
}
Write-Host ""

# 2. Check enterprise_rbac_auth requirements
Write-Host "📋 Checking enterprise_rbac_auth/requirements.txt..." -ForegroundColor Yellow
if (Test-Path "enterprise_rbac_auth/requirements.txt") {
    Write-Host "Found: enterprise_rbac_auth/requirements.txt" -ForegroundColor Yellow
    Write-Host "This may be redundant after RBAC integration."
    if (Confirm-Action "Delete enterprise_rbac_auth/requirements.txt?") {
        Remove-Item "enterprise_rbac_auth/requirements.txt" -Force
        Write-Host "✅ Deleted enterprise_rbac_auth/requirements.txt" -ForegroundColor Green
    }
} else {
    Write-Host "✅ File not found or already deleted" -ForegroundColor Green
}
Write-Host ""

# 3. Check for empty test-results.json
Write-Host "📋 Checking for empty test-results.json..." -ForegroundColor Yellow
if (Test-Path "test-results.json") {
    $size = (Get-Item "test-results.json").Length
    if ($size -lt 10) {
        Write-Host "Found empty test-results.json" -ForegroundColor Yellow
        if (Confirm-Action "Delete empty test-results.json?") {
            Remove-Item "test-results.json" -Force
            Write-Host "✅ Deleted test-results.json" -ForegroundColor Green
        }
    }
} else {
    Write-Host "✅ File not found or already deleted" -ForegroundColor Green
}
Write-Host ""

# 4. Archive consolidation
Write-Host "📋 Checking archive directories..." -ForegroundColor Yellow
Write-Host "Current archive structure:"
$archiveCount = (Get-ChildItem -Path "archive/2026-01-21" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
$docsArchiveCount = (Get-ChildItem -Path "docs/archive" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "  - archive/2026-01-21/ ($archiveCount files)"
Write-Host "  - docs/archive/ ($docsArchiveCount files)"
Write-Host ""
Write-Host "Recommendation: Consider consolidating archives into a single directory" -ForegroundColor Cyan
Write-Host "Manual action required - review archive contents before moving"
Write-Host ""

# 5. Requirements files check
Write-Host "📋 Checking requirements files..." -ForegroundColor Yellow
Write-Host "Found requirements files:"
Get-ChildItem -Path "backend" -Filter "requirements*" -File -ErrorAction SilentlyContinue | 
    ForEach-Object { 
        $size = [math]::Round($_.Length / 1KB, 2)
        Write-Host "  $($_.Name) ($size KB)"
    }
Write-Host ""
Write-Host "Recommendation: Review and consolidate requirements files" -ForegroundColor Cyan
Write-Host "Manual action required - check differences between files"
Write-Host ""

# 6. Environment files check
Write-Host "📋 Checking environment configuration files..." -ForegroundColor Yellow
Write-Host "Root directory:"
Get-ChildItem -Path "." -Filter ".env*" -File -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.Name)" }
Write-Host "Backend:"
Get-ChildItem -Path "backend" -Filter ".env*" -File -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.Name)" }
Write-Host "Frontend:"
Get-ChildItem -Path "frontend" -Filter ".env*" -File -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.Name)" }
Write-Host ""
Write-Host "Recommendation: Review and remove redundant .env files" -ForegroundColor Cyan
Write-Host "Manual action required - ensure no production secrets are lost"
Write-Host ""

# Summary
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "✅ Phase 2 cleanup check complete" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review CLEANUP_SUMMARY.md for detailed recommendations"
Write-Host "2. Manually review requirements files for consolidation"
Write-Host "3. Manually review environment files"
Write-Host "4. Consider consolidating archive directories"
Write-Host "5. Review and merge quick start guides"
Write-Host ""
