#!/bin/bash
# Terraform Validation Script
# Validates Terraform configuration before deployment

set -e

echo "=========================================="
echo "Terraform Configuration Validation"
echo "=========================================="
echo ""

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Error: Terraform is not installed"
    echo "   Install from: https://www.terraform.io/downloads"
    exit 1
fi

echo "✓ Terraform is installed"
terraform version
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI is not installed"
    echo "   Install from: https://aws.amazon.com/cli/"
    exit 1
fi

echo "✓ AWS CLI is installed"
aws --version
echo ""

# Check AWS credentials
echo "Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✓ AWS credentials are configured"
    aws sts get-caller-identity
else
    echo "❌ Error: AWS credentials are not configured"
    echo "   Run: aws configure"
    exit 1
fi
echo ""

# Initialize Terraform
echo "Initializing Terraform..."
if terraform init -backend=false > /dev/null 2>&1; then
    echo "✓ Terraform initialized successfully"
else
    echo "❌ Error: Terraform initialization failed"
    terraform init -backend=false
    exit 1
fi
echo ""

# Validate Terraform configuration
echo "Validating Terraform configuration..."
if terraform validate; then
    echo "✓ Terraform configuration is valid"
else
    echo "❌ Error: Terraform configuration is invalid"
    exit 1
fi
echo ""

# Format check
echo "Checking Terraform formatting..."
if terraform fmt -check -recursive; then
    echo "✓ Terraform files are properly formatted"
else
    echo "⚠ Warning: Some files need formatting"
    echo "   Run: terraform fmt -recursive"
fi
echo ""

# Check for terraform.tfvars
if [ -f "terraform.tfvars" ]; then
    echo "✓ terraform.tfvars file exists"
else
    echo "⚠ Warning: terraform.tfvars file not found"
    echo "   Copy terraform.tfvars.example to terraform.tfvars and configure"
fi
echo ""

# Check for required variables
echo "Checking for required sensitive variables..."
REQUIRED_VARS=("db_password" "neo4j_password" "neo4j_connection_uri")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -f "terraform.tfvars" ]; then
        if grep -q "^${var}" terraform.tfvars; then
            echo "✓ ${var} is configured"
        else
            echo "⚠ Warning: ${var} is not configured in terraform.tfvars"
            MISSING_VARS+=("$var")
        fi
    fi
done
echo ""

# Security checks
echo "Running security checks..."

# Check for hardcoded secrets
echo "Checking for hardcoded secrets..."
if grep -r "password.*=.*\".*\"" *.tf 2>/dev/null | grep -v "variable\|description\|sensitive"; then
    echo "⚠ Warning: Possible hardcoded passwords found in .tf files"
else
    echo "✓ No hardcoded passwords found in .tf files"
fi
echo ""

# Check if tfsec is installed
if command -v tfsec &> /dev/null; then
    echo "Running tfsec security scan..."
    if tfsec . --soft-fail; then
        echo "✓ Security scan completed"
    else
        echo "⚠ Warning: Security issues found (see above)"
    fi
else
    echo "⚠ tfsec not installed - skipping security scan"
    echo "   Install from: https://github.com/aquasecurity/tfsec"
fi
echo ""

# Summary
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo ""

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo "✓ All checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Review terraform.tfvars configuration"
    echo "2. Run: terraform plan -var-file=\"environments/dev/terraform.tfvars\""
    echo "3. Run: terraform apply -var-file=\"environments/dev/terraform.tfvars\""
    exit 0
else
    echo "⚠ Configuration incomplete"
    echo ""
    echo "Missing variables in terraform.tfvars:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - ${var}"
    done
    echo ""
    echo "Please configure these variables before deployment"
    exit 1
fi
