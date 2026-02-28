# Terraform Validation Script (PowerShell)
# Validates Terraform configuration before deployment

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Terraform Configuration Validation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Terraform is installed
Write-Host "Checking Terraform installation..." -ForegroundColor Yellow
try {
    $tfVersion = terraform version
    Write-Host "✓ Terraform is installed" -ForegroundColor Green
    Write-Host $tfVersion
} catch {
    Write-Host "❌ Error: Terraform is not installed" -ForegroundColor Red
    Write-Host "   Install from: https://www.terraform.io/downloads" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if AWS CLI is installed
Write-Host "Checking AWS CLI installation..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version
    Write-Host "✓ AWS CLI is installed" -ForegroundColor Green
    Write-Host $awsVersion
} catch {
    Write-Host "❌ Error: AWS CLI is not installed" -ForegroundColor Red
    Write-Host "   Install from: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check AWS credentials
Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ AWS credentials are configured" -ForegroundColor Green
        Write-Host $identity
    } else {
        throw "AWS credentials not configured"
    }
} catch {
    Write-Host "❌ Error: AWS credentials are not configured" -ForegroundColor Red
    Write-Host "   Run: aws configure" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Initialize Terraform
Write-Host "Initializing Terraform..." -ForegroundColor Yellow
try {
    terraform init -backend=false | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Terraform initialized successfully" -ForegroundColor Green
    } else {
        throw "Terraform initialization failed"
    }
} catch {
    Write-Host "❌ Error: Terraform initialization failed" -ForegroundColor Red
    terraform init -backend=false
    exit 1
}
Write-Host ""

# Validate Terraform configuration
Write-Host "Validating Terraform configuration..." -ForegroundColor Yellow
try {
    terraform validate
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Terraform configuration is valid" -ForegroundColor Green
    } else {
        throw "Terraform validation failed"
    }
} catch {
    Write-Host "❌ Error: Terraform configuration is invalid" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Format check
Write-Host "Checking Terraform formatting..." -ForegroundColor Yellow
terraform fmt -check -recursive | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Terraform files are properly formatted" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Some files need formatting" -ForegroundColor Yellow
    Write-Host "   Run: terraform fmt -recursive" -ForegroundColor Yellow
}
Write-Host ""

# Check for terraform.tfvars
Write-Host "Checking configuration files..." -ForegroundColor Yellow
if (Test-Path "terraform.tfvars") {
    Write-Host "✓ terraform.tfvars file exists" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: terraform.tfvars file not found" -ForegroundColor Yellow
    Write-Host "   Copy terraform.tfvars.example to terraform.tfvars and configure" -ForegroundColor Yellow
}
Write-Host ""

# Check for required variables
Write-Host "Checking for required sensitive variables..." -ForegroundColor Yellow
$requiredVars = @("db_password", "neo4j_password", "neo4j_connection_uri")
$missingVars = @()

if (Test-Path "terraform.tfvars") {
    $tfvarsContent = Get-Content "terraform.tfvars" -Raw
    foreach ($var in $requiredVars) {
        if ($tfvarsContent -match "^$var\s*=") {
            Write-Host "✓ $var is configured" -ForegroundColor Green
        } else {
            Write-Host "⚠ Warning: $var is not configured in terraform.tfvars" -ForegroundColor Yellow
            $missingVars += $var
        }
    }
}
Write-Host ""

# Security checks
Write-Host "Running security checks..." -ForegroundColor Yellow

# Check for hardcoded secrets in .tf files
Write-Host "Checking for hardcoded secrets..." -ForegroundColor Yellow
$tfFiles = Get-ChildItem -Path . -Filter "*.tf" -Recurse
$foundSecrets = $false
foreach ($file in $tfFiles) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match 'password\s*=\s*"[^"]*"' -and $content -notmatch 'variable|description|sensitive') {
        Write-Host "⚠ Warning: Possible hardcoded password in $($file.Name)" -ForegroundColor Yellow
        $foundSecrets = $true
    }
}
if (-not $foundSecrets) {
    Write-Host "✓ No hardcoded passwords found in .tf files" -ForegroundColor Green
}
Write-Host ""

# Check if tfsec is installed
Write-Host "Checking for tfsec..." -ForegroundColor Yellow
try {
    tfsec --version | Out-Null
    Write-Host "Running tfsec security scan..." -ForegroundColor Yellow
    tfsec . --soft-fail
    Write-Host "✓ Security scan completed" -ForegroundColor Green
} catch {
    Write-Host "⚠ tfsec not installed - skipping security scan" -ForegroundColor Yellow
    Write-Host "   Install from: https://github.com/aquasecurity/tfsec" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($missingVars.Count -eq 0) {
    Write-Host "✓ All checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Review terraform.tfvars configuration"
    Write-Host "2. Run: terraform plan -var-file=`"environments/dev/terraform.tfvars`""
    Write-Host "3. Run: terraform apply -var-file=`"environments/dev/terraform.tfvars`""
    exit 0
} else {
    Write-Host "⚠ Configuration incomplete" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Missing variables in terraform.tfvars:" -ForegroundColor Yellow
    foreach ($var in $missingVars) {
        Write-Host "  - $var" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Please configure these variables before deployment" -ForegroundColor Yellow
    exit 1
}
