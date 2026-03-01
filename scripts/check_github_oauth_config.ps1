# GitHub OAuth Configuration Check Script (PowerShell)

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "GitHub OAuth Configuration Check" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

function Check-Pass {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Check-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Check-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

# Initialize variables
$clientId = ""
$clientSecret = ""
$frontendClientId = ""
$backendUrl = ""

# 1. Check root .env file
Write-Host "1. Checking root .env configuration..." -ForegroundColor White
if (Test-Path ".env") {
    Check-Pass ".env file exists"
    
    $envLines = Get-Content ".env"
    foreach ($line in $envLines) {
        if ($line -match "^GITHUB_CLIENT_ID=(.*)$") {
            $clientId = $matches[1].Trim()
            if ($clientId) {
                Check-Pass "GITHUB_CLIENT_ID configured: $clientId"
            } else {
                Check-Fail "GITHUB_CLIENT_ID is empty"
            }
        }
        if ($line -match "^GITHUB_CLIENT_SECRET=(.*)$") {
            $clientSecret = $matches[1].Trim()
            if ($clientSecret) {
                Check-Pass "GITHUB_CLIENT_SECRET configured (length: $($clientSecret.Length))"
            } else {
                Check-Fail "GITHUB_CLIENT_SECRET is empty"
            }
        }
    }
} else {
    Check-Fail ".env file not found"
}

Write-Host ""

# 2. Check frontend .env.local file
Write-Host "2. Checking frontend .env.local configuration..." -ForegroundColor White
if (Test-Path "frontend/.env.local") {
    Check-Pass "frontend/.env.local file exists"
    
    $frontendEnvLines = Get-Content "frontend/.env.local"
    foreach ($line in $frontendEnvLines) {
        if ($line -match "^NEXT_PUBLIC_GITHUB_CLIENT_ID=(.*)$") {
            $frontendClientId = $matches[1].Trim()
            if ($frontendClientId) {
                Check-Pass "NEXT_PUBLIC_GITHUB_CLIENT_ID configured: $frontendClientId"
                
                if ($clientId -eq $frontendClientId) {
                    Check-Pass "Frontend and backend Client IDs match"
                } else {
                    Check-Warn "Frontend and backend Client IDs do not match!"
                    Write-Host "  Backend: $clientId" -ForegroundColor Yellow
                    Write-Host "  Frontend: $frontendClientId" -ForegroundColor Yellow
                }
            } else {
                Check-Fail "NEXT_PUBLIC_GITHUB_CLIENT_ID is empty"
            }
        }
        if ($line -match "^NEXT_PUBLIC_BACKEND_URL=(.*)$") {
            $backendUrl = $matches[1].Trim()
            Check-Pass "NEXT_PUBLIC_BACKEND_URL: $backendUrl"
        }
    }
} else {
    Check-Fail "frontend/.env.local file not found"
    Write-Host "  Please copy from frontend/.env.example and configure" -ForegroundColor Yellow
}

Write-Host ""

# 3. Configuration recommendations
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Configuration Recommendations" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

if ($clientId) {
    Write-Host "Your GitHub OAuth App Configuration:" -ForegroundColor White
    Write-Host ""
    Write-Host "Client ID: $clientId" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Required callback URLs in GitHub OAuth App:" -ForegroundColor White
    Write-Host ""
    Write-Host "  Development:" -ForegroundColor Cyan
    Write-Host "    http://localhost:3000/api/github/callback" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Production (adjust domain):" -ForegroundColor Cyan
    Write-Host "    https://your-domain.com/api/github/callback" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuration Steps:" -ForegroundColor White
    Write-Host "  1. Visit: https://github.com/settings/developers" -ForegroundColor Gray
    Write-Host "  2. Find app with Client ID: $clientId" -ForegroundColor Gray
    Write-Host "  3. Add callback URL in 'Authorization callback URL'" -ForegroundColor Gray
    Write-Host "  4. Save changes" -ForegroundColor Gray
    Write-Host ""
}

# 4. Check service status
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Service Status Check" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

try {
    $frontend = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
    if ($frontend) {
        Check-Pass "Frontend service running on port 3000"
    } else {
        Check-Warn "Frontend service not running on port 3000"
    }
} catch {
    Check-Warn "Cannot check port 3000 status"
}

try {
    $backend = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if ($backend) {
        Check-Pass "Backend service running on port 8000"
    } else {
        Check-Warn "Backend service not running on port 8000"
    }
} catch {
    Check-Warn "Cannot check port 8000 status"
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Check Complete" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed documentation, see:" -ForegroundColor White
Write-Host "  docs/GITHUB_OAUTH_SETUP.md" -ForegroundColor Yellow
Write-Host ""

# Quick fix suggestions
if (-not $clientSecret) {
    Write-Host "Quick Fix Suggestions:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Get Client Secret from GitHub OAuth app settings" -ForegroundColor White
    Write-Host "   https://github.com/settings/developers" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Update GITHUB_CLIENT_SECRET in .env file" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Restart services" -ForegroundColor White
    Write-Host "   docker-compose restart" -ForegroundColor Cyan
    Write-Host ""
}
