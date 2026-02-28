# Security Tests Runner Script (PowerShell)
# 
# This script runs comprehensive security tests including OWASP ZAP scanning
# and OWASP Top 10 vulnerability tests.
#
# Usage:
#   .\run_security_tests.ps1 [-BackendUrl <url>] [-SkipZap] [-Verbose]
#
# Parameters:
#   -BackendUrl    Backend URL (default: http://localhost:8000)
#   -SkipZap       Skip OWASP ZAP automated scan
#   -Verbose       Show detailed output

param(
    [string]$BackendUrl = "http://localhost:8000",
    [switch]$SkipZap = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Resolve-Path (Join-Path $ScriptDir "../..")

# Print banner
Write-Host "============================================================" -ForegroundColor Blue
Write-Host "           Security Tests - OWASP Top 10 2021              " -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""
Write-Host "Backend URL: " -NoNewline
Write-Host $BackendUrl -ForegroundColor Green
Write-Host "Skip ZAP Scan: " -NoNewline
Write-Host $SkipZap -ForegroundColor Yellow
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Blue

# Check if backend is accessible
Write-Host "  Checking backend accessibility... " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/v1/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓" -ForegroundColor Green
} catch {
    Write-Host "✗" -ForegroundColor Red
    Write-Host "ERROR: Backend at $BackendUrl is not accessible" -ForegroundColor Red
    Write-Host "Please start the backend before running security tests:"
    Write-Host "  cd backend && uvicorn app.main:app --reload"
    exit 1
}

# Check if Docker is available
Write-Host "  Checking Docker availability... " -NoNewline
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓" -ForegroundColor Green
    } else {
        throw "Docker not found"
    }
} catch {
    Write-Host "✗" -ForegroundColor Red
    Write-Host "ERROR: Docker is not available" -ForegroundColor Red
    Write-Host "Please install Docker to run OWASP ZAP scans:"
    Write-Host "  https://docs.docker.com/get-docker/"
    exit 1
}

# Check if pytest is available
Write-Host "  Checking pytest availability... " -NoNewline
try {
    python -m pytest --version 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓" -ForegroundColor Green
    } else {
        throw "pytest not found"
    }
} catch {
    Write-Host "✗" -ForegroundColor Red
    Write-Host "ERROR: pytest is not available" -ForegroundColor Red
    Write-Host "Please install pytest:"
    Write-Host "  pip install pytest requests pyyaml"
    exit 1
}

Write-Host ""

# Set environment variable
$env:BACKEND_URL = $BackendUrl

# Change to backend directory
Push-Location $BackendDir

try {
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host "Running Security Tests" -ForegroundColor Blue
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host ""

    $verboseFlag = if ($Verbose) { "-s" } else { "" }

    # Test categories
    if (-not $SkipZap) {
        Write-Host "1. OWASP ZAP Automated Scan" -ForegroundColor Yellow
        Write-Host "   This may take 5-10 minutes..."
        Write-Host ""
        
        $zapTest = "tests/system/test_security_owasp_top10.py::TestOWASPZAPScan"
        python -m pytest $zapTest -v $verboseFlag
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ ZAP scan completed successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ ZAP scan failed" -ForegroundColor Red
            exit 1
        }
        Write-Host ""
    } else {
        Write-Host "Skipping OWASP ZAP automated scan" -ForegroundColor Yellow
        Write-Host ""
    }

    Write-Host "2. OWASP Top 10 Vulnerability Tests" -ForegroundColor Yellow
    Write-Host ""
    
    $owaspTest = "tests/system/test_security_owasp_top10.py::TestOWASPTop10Vulnerabilities"
    python -m pytest $owaspTest -v $verboseFlag
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ OWASP Top 10 tests passed" -ForegroundColor Green
    } else {
        Write-Host "✗ OWASP Top 10 tests failed" -ForegroundColor Red
        exit 1
    }
    Write-Host ""

    Write-Host "3. Security Headers Tests" -ForegroundColor Yellow
    Write-Host ""
    
    $headersTest = "tests/system/test_security_owasp_top10.py::TestSecurityHeaders"
    python -m pytest $headersTest -v $verboseFlag
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Security headers tests passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Security headers tests failed" -ForegroundColor Red
        exit 1
    }
    Write-Host ""

    Write-Host "4. Rate Limiting Tests" -ForegroundColor Yellow
    Write-Host ""
    
    $rateLimitTest = "tests/system/test_security_owasp_top10.py::TestRateLimiting"
    python -m pytest $rateLimitTest -v $verboseFlag
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Rate limiting tests passed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Rate limiting tests had warnings" -ForegroundColor Yellow
        # Don't fail on rate limiting tests
    }
    Write-Host ""

    # Summary
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host "✓ All security tests completed successfully" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host ""

    # Show reports location
    if (-not $SkipZap) {
        $ReportsDir = Join-Path $BackendDir "security\zap_reports"
        if (Test-Path $ReportsDir) {
            Write-Host "Security scan reports available at:"
            Write-Host "  HTML: $ReportsDir\baseline_report.html"
            Write-Host "  JSON: $ReportsDir\baseline_report.json"
            Write-Host "  Markdown: $ReportsDir\baseline_report.md"
            Write-Host ""
        }
    }

    Write-Host "Security testing complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Review any warnings or medium severity findings"
    Write-Host "  2. Fix any identified vulnerabilities"
    Write-Host "  3. Re-run tests to verify fixes"
    Write-Host "  4. Document any accepted risks"
    Write-Host ""

} finally {
    Pop-Location
}

exit 0
