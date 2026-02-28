# PowerShell script to run end-to-end tests in staging environment
# This script sets up the staging environment and runs e2e tests

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running End-to-End Tests in Staging" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if running in staging environment
if ($env:ENVIRONMENT -ne "staging") {
    Write-Host "Warning: ENVIRONMENT is not set to 'staging'" -ForegroundColor Yellow
    Write-Host "Setting ENVIRONMENT=staging"
    $env:ENVIRONMENT = "staging"
}

# Load staging environment variables
if (Test-Path ".env.staging") {
    Write-Host "Loading staging environment variables..."
    Get-Content ".env.staging" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            Set-Item -Path "env:$name" -Value $value
        }
    }
} else {
    Write-Host "Error: .env.staging file not found" -ForegroundColor Red
    exit 1
}

# Check required services
Write-Host ""
Write-Host "Checking required services..."

# Check PostgreSQL
$dbHost = if ($env:DATABASE_HOST) { $env:DATABASE_HOST } else { "localhost" }
$dbPort = if ($env:DATABASE_PORT) { $env:DATABASE_PORT } else { "5432" }

try {
    $connection = New-Object System.Net.Sockets.TcpClient($dbHost, $dbPort)
    $connection.Close()
    Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
} catch {
    Write-Host "Error: PostgreSQL is not running" -ForegroundColor Red
    Write-Host "Start with: docker-compose -f docker-compose.staging.yml up -d postgres"
    exit 1
}

# Check Neo4j
$neo4jHost = if ($env:NEO4J_HOST) { $env:NEO4J_HOST } else { "localhost" }
$neo4jPort = if ($env:NEO4J_PORT) { $env:NEO4J_PORT } else { "7687" }

try {
    $connection = New-Object System.Net.Sockets.TcpClient($neo4jHost, $neo4jPort)
    $connection.Close()
    Write-Host "✓ Neo4j is running" -ForegroundColor Green
} catch {
    Write-Host "Error: Neo4j is not running" -ForegroundColor Red
    Write-Host "Start with: docker-compose -f docker-compose.staging.yml up -d neo4j"
    exit 1
}

# Check Redis
$redisHost = if ($env:REDIS_HOST) { $env:REDIS_HOST } else { "localhost" }
$redisPort = if ($env:REDIS_PORT) { $env:REDIS_PORT } else { "6379" }

try {
    $connection = New-Object System.Net.Sockets.TcpClient($redisHost, $redisPort)
    $connection.Close()
    Write-Host "✓ Redis is running" -ForegroundColor Green
} catch {
    Write-Host "Error: Redis is not running" -ForegroundColor Red
    Write-Host "Start with: docker-compose -f docker-compose.staging.yml up -d redis"
    exit 1
}

# Run database migrations
Write-Host ""
Write-Host "Running database migrations..."
Push-Location backend
alembic upgrade head
Pop-Location

# Clean up old test data
Write-Host ""
Write-Host "Cleaning up old test data..."
try {
    python backend/scripts/cleanup_test_data.py
} catch {
    Write-Host "No cleanup script found, skipping..."
}

# Run e2e tests
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running E2E Tests" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Parse command line arguments
param(
    [switch]$Verbose,
    [switch]$Coverage,
    [string]$Test
)

$pytestArgs = @("backend/tests/e2e/", "-m", "e2e")

if ($Verbose) {
    $pytestArgs += "-v"
}

if ($Coverage) {
    $pytestArgs += @("--cov=app", "--cov-report=html", "--cov-report=term")
}

if ($Test) {
    $pytestArgs[0] = "backend/tests/e2e/$Test"
}

# Run tests
Write-Host "Running: pytest $($pytestArgs -join ' ')"
Write-Host ""

$testResult = & pytest @pytestArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✓ All E2E Tests Passed!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    
    # Show coverage report if generated
    if ($Coverage) {
        Write-Host ""
        Write-Host "Coverage report generated at: htmlcov/index.html"
        Write-Host "Open with: Start-Process htmlcov/index.html"
    }
    
    exit 0
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "✗ E2E Tests Failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    
    # Show logs for debugging
    Write-Host ""
    Write-Host "Check logs for more details:"
    Write-Host "  - Application logs: logs/app.log"
    Write-Host "  - Database logs: docker logs <postgres_container>"
    Write-Host "  - Neo4j logs: docker logs <neo4j_container>"
    
    exit 1
}
