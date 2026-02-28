# OWASP ZAP Security Scan Runner Script (PowerShell)
# This script simplifies running security scans against the application

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('baseline', 'api', 'full')]
    [string]$ScanType = 'baseline',
    
    [Parameter(Mandatory=$false)]
    [string]$BackendUrl = 'http://localhost:8000',
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDir = '',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipChecks = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help = $false
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

if ($OutputDir -eq '') {
    $OutputDir = Join-Path $ScriptDir 'zap_reports'
}

# Functions
function Write-Header {
    param([string]$Message)
    Write-Host "========================================" -ForegroundColor Green
    Write-Host $Message -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Docker {
    try {
        $null = docker --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Docker is not installed or not in PATH"
            exit 1
        }
        
        $null = docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Docker daemon is not running"
            exit 1
        }
        
        Write-Info "Docker is available"
        return $true
    }
    catch {
        Write-ErrorMsg "Docker check failed: $_"
        exit 1
    }
}

function Test-Backend {
    Write-Info "Checking if backend is accessible at $BackendUrl..."
    
    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/v1/health" -Method Get -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Info "Backend is accessible"
            return $true
        }
    }
    catch {
        try {
            $response = Invoke-WebRequest -Uri $BackendUrl -Method Get -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Warning "Backend is accessible but health endpoint not found"
                return $true
            }
        }
        catch {
            Write-Warning "Backend may not be accessible at $BackendUrl"
            Write-Warning "Make sure the backend is running before scanning"
            
            $continue = Read-Host "Continue anyway? (y/N)"
            if ($continue -ne 'y' -and $continue -ne 'Y') {
                exit 1
            }
        }
    }
}

function Get-ZapImage {
    Write-Info "Pulling latest OWASP ZAP Docker image..."
    docker pull owasp/zap2docker-stable
}

function Invoke-BaselineScan {
    Write-Header "Running ZAP Baseline Scan"
    
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    
    docker run --rm `
        --network host `
        -v "${OutputDir}:/zap/wrk:rw" `
        owasp/zap2docker-stable `
        zap-baseline.py `
        -t $BackendUrl `
        -r baseline_report.html `
        -J baseline_report.json `
        -w baseline_report.md `
        -I
    
    Write-Info "Baseline scan complete"
    Write-Info "Reports saved to: $OutputDir"
}

function Invoke-ApiScan {
    Write-Header "Running ZAP API Scan"
    
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    
    $apiSpec = "$BackendUrl/api/v1/openapi.json"
    Write-Info "Using API spec: $apiSpec"
    
    docker run --rm `
        --network host `
        -v "${OutputDir}:/zap/wrk:rw" `
        owasp/zap2docker-stable `
        zap-api-scan.py `
        -t $apiSpec `
        -f openapi `
        -r api_report.html `
        -J api_report.json `
        -w api_report.md `
        -I
    
    Write-Info "API scan complete"
    Write-Info "Reports saved to: $OutputDir"
}

function Invoke-FullScan {
    Write-Header "Running ZAP Full Scan"
    Write-Warning "Full scan may take significant time and generate load on the application"
    
    $continue = Read-Host "Continue with full scan? (y/N)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Info "Full scan cancelled"
        exit 0
    }
    
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    
    docker run --rm `
        --network host `
        -v "${OutputDir}:/zap/wrk:rw" `
        owasp/zap2docker-stable `
        zap-full-scan.py `
        -t $BackendUrl `
        -r full_report.html `
        -J full_report.json `
        -w full_report.md `
        -I
    
    Write-Info "Full scan complete"
    Write-Info "Reports saved to: $OutputDir"
}

function Get-ScanResults {
    Write-Header "Parsing Scan Results"
    
    $jsonReport = switch ($ScanType) {
        'baseline' { Join-Path $OutputDir 'baseline_report.json' }
        'api' { Join-Path $OutputDir 'api_report.json' }
        'full' { Join-Path $OutputDir 'full_report.json' }
    }
    
    if (-not (Test-Path $jsonReport)) {
        Write-Warning "JSON report not found: $jsonReport"
        return $false
    }
    
    try {
        $report = Get-Content $jsonReport -Raw | ConvertFrom-Json
        $alerts = $report.site[0].alerts
        
        $high = ($alerts | Where-Object { $_.riskdesc -like 'High*' }).Count
        $medium = ($alerts | Where-Object { $_.riskdesc -like 'Medium*' }).Count
        $low = ($alerts | Where-Object { $_.riskdesc -like 'Low*' }).Count
        $info = ($alerts | Where-Object { $_.riskdesc -like 'Informational*' }).Count
        
        Write-Host ""
        Write-Info "Scan Results Summary:"
        Write-Host "  High Risk:          $high"
        Write-Host "  Medium Risk:        $medium"
        Write-Host "  Low Risk:           $low"
        Write-Host "  Informational:      $info"
        Write-Host ""
        
        # Check compliance (requirement: zero critical and high severity)
        if ($high -eq 0) {
            Write-Info "✅ PASS: Zero high severity vulnerabilities found"
            return $true
        }
        else {
            Write-ErrorMsg "❌ FAIL: $high high severity vulnerabilities found (requirement: 0)"
            return $false
        }
    }
    catch {
        Write-Warning "Failed to parse results: $_"
        return $false
    }
}

function Show-Usage {
    @"
OWASP ZAP Security Scanner

USAGE:
    .\run_security_scan.ps1 [OPTIONS]

OPTIONS:
    -ScanType <type>       Scan type: baseline, api, or full (default: baseline)
    -BackendUrl <url>      Backend URL (default: http://localhost:8000)
    -OutputDir <dir>       Output directory for reports (default: .\zap_reports)
    -SkipChecks            Skip pre-flight checks
    -Help                  Show this help message

EXAMPLES:
    # Run baseline scan
    .\run_security_scan.ps1 -ScanType baseline

    # Run API scan against custom URL
    .\run_security_scan.ps1 -ScanType api -BackendUrl http://localhost:8000

    # Run full scan with custom output directory
    .\run_security_scan.ps1 -ScanType full -OutputDir C:\temp\zap_reports

REQUIREMENTS:
    - Docker Desktop installed and running
    - Backend application running and accessible
    - Network connectivity to backend

COMPLIANCE:
    This scan verifies compliance with requirement 8.10:
    "THE System SHALL pass OWASP ZAP security scan with zero critical 
    and zero high severity vulnerabilities"
"@
}

# Main execution
function Main {
    if ($Help) {
        Show-Usage
        exit 0
    }
    
    Write-Header "OWASP ZAP Security Scanner"
    
    Write-Host "Configuration:"
    Write-Host "  Backend URL:    $BackendUrl"
    Write-Host "  Scan Type:      $ScanType"
    Write-Host "  Output Dir:     $OutputDir"
    Write-Host ""
    
    # Pre-flight checks
    if (-not $SkipChecks) {
        Test-Docker
        Test-Backend
        Get-ZapImage
    }
    
    # Run appropriate scan
    switch ($ScanType) {
        'baseline' { Invoke-BaselineScan }
        'api' { Invoke-ApiScan }
        'full' { Invoke-FullScan }
        default {
            Write-ErrorMsg "Invalid scan type: $ScanType"
            Write-ErrorMsg "Valid types: baseline, api, full"
            exit 1
        }
    }
    
    # Parse and display results
    $passed = Get-ScanResults
    
    Write-Host ""
    Write-Header "Scan Complete"
    Write-Info "View detailed reports in: $OutputDir"
    
    if ($passed) {
        Write-Info "✅ Security scan PASSED"
        exit 0
    }
    else {
        Write-ErrorMsg "❌ Security scan FAILED"
        Write-ErrorMsg "Review the reports and fix identified vulnerabilities"
        exit 1
    }
}

# Run main function
Main
