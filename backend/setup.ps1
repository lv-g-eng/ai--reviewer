# Backend Development Environment Setup Script (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Backend Development Environment Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found $pythonVersion" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install -r requirements-test.txt

# Install development tools
Write-Host "Installing development tools..." -ForegroundColor Yellow
pip install black isort ruff mypy

# Create .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host ".env file created. Please update it with your configuration." -ForegroundColor Green
} else {
    Write-Host ".env file already exists." -ForegroundColor Green
}

# Run database migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
try {
    alembic upgrade head
} catch {
    Write-Host "Migrations failed or not configured yet." -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "To activate the virtual environment, run:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To start the development server, run:" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "To run tests, run:" -ForegroundColor Yellow
Write-Host "  pytest" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
