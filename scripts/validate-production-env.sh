#!/bin/bash
# ============================================================================
# Production Environment Validation Script
# ============================================================================
# This script validates that all required environment variables are set
# and properly configured for production deployment.
# ============================================================================

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
CHECKS=0

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((ERRORS++))
}

# Load environment variables
if [ -f ".env.production" ]; then
    log_info "Loading .env.production file..."
    export $(grep -v '^#' .env.production | grep -v '^$' | xargs)
    log_success ".env.production file loaded"
else
    log_error ".env.production file not found"
    exit 1
fi

echo ""
echo "========================================="
echo "Production Environment Validation"
echo "========================================="
echo ""

# ============================================================================
# 1. Check Required Environment Variables
# ============================================================================
log_info "Checking required environment variables..."

required_vars=(
    "ENVIRONMENT"
    "POSTGRES_HOST"
    "POSTGRES_PORT"
    "POSTGRES_USER"
    "POSTGRES_PASSWORD"
    "POSTGRES_DB"
    "NEO4J_URI"
    "NEO4J_USER"
    "NEO4J_PASSWORD"
    "REDIS_HOST"
    "REDIS_PORT"
    "REDIS_PASSWORD"
    "JWT_SECRET"
    "SECRET_KEY"
    "SESSION_SECRET"
    "NEXT_PUBLIC_API_URL"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log_error "Missing required environment variable: $var"
    else
        log_success "Environment variable set: $var"
    fi
done

echo ""

# ============================================================================
# 2. Validate Environment Setting
# ============================================================================
log_info "Validating environment setting..."

if [ "$ENVIRONMENT" = "production" ]; then
    log_success "Environment is set to production"
else
    log_error "Environment is not set to production (current: $ENVIRONMENT)"
fi

if [ "$DEBUG" = "false" ]; then
    log_success "Debug mode is disabled"
else
    log_warning "Debug mode is enabled (should be false in production)"
fi

echo ""

# ============================================================================
# 3. Validate Secret Keys
# ============================================================================
log_info "Validating secret keys..."

# Check JWT_SECRET length
if [ -n "$JWT_SECRET" ]; then
    jwt_length=${#JWT_SECRET}
    if [ $jwt_length -ge 32 ]; then
        log_success "JWT_SECRET length is sufficient ($jwt_length characters)"
    else
        log_error "JWT_SECRET is too short ($jwt_length characters, minimum 32 required)"
    fi
    
    # Check if it's still the placeholder
    if [[ "$JWT_SECRET" == *"CHANGE_ME"* ]]; then
        log_error "JWT_SECRET still contains placeholder value - must be changed"
    fi
fi

# Check SECRET_KEY length
if [ -n "$SECRET_KEY" ]; then
    secret_length=${#SECRET_KEY}
    if [ $secret_length -ge 32 ]; then
        log_success "SECRET_KEY length is sufficient ($secret_length characters)"
    else
        log_error "SECRET_KEY is too short ($secret_length characters, minimum 32 required)"
    fi
    
    if [[ "$SECRET_KEY" == *"CHANGE_ME"* ]]; then
        log_error "SECRET_KEY still contains placeholder value - must be changed"
    fi
fi

# Check SESSION_SECRET length
if [ -n "$SESSION_SECRET" ]; then
    session_length=${#SESSION_SECRET}
    if [ $session_length -ge 32 ]; then
        log_success "SESSION_SECRET length is sufficient ($session_length characters)"
    else
        log_error "SESSION_SECRET is too short ($session_length characters, minimum 32 required)"
    fi
    
    if [[ "$SESSION_SECRET" == *"CHANGE_ME"* ]]; then
        log_error "SESSION_SECRET still contains placeholder value - must be changed"
    fi
fi

echo ""

# ============================================================================
# 4. Validate Database Passwords
# ============================================================================
log_info "Validating database passwords..."

# Check PostgreSQL password
if [ -n "$POSTGRES_PASSWORD" ]; then
    postgres_pwd_length=${#POSTGRES_PASSWORD}
    if [ $postgres_pwd_length -ge 32 ]; then
        log_success "POSTGRES_PASSWORD length is sufficient ($postgres_pwd_length characters)"
    else
        log_warning "POSTGRES_PASSWORD is shorter than recommended (current: $postgres_pwd_length, recommended: 32+)"
    fi
    
    if [[ "$POSTGRES_PASSWORD" == *"CHANGE_ME"* ]]; then
        log_error "POSTGRES_PASSWORD still contains placeholder value - must be changed"
    fi
fi

# Check Neo4j password
if [ -n "$NEO4J_PASSWORD" ]; then
    neo4j_pwd_length=${#NEO4J_PASSWORD}
    if [ $neo4j_pwd_length -ge 32 ]; then
        log_success "NEO4J_PASSWORD length is sufficient ($neo4j_pwd_length characters)"
    else
        log_warning "NEO4J_PASSWORD is shorter than recommended (current: $neo4j_pwd_length, recommended: 32+)"
    fi
    
    if [[ "$NEO4J_PASSWORD" == *"CHANGE_ME"* ]]; then
        log_error "NEO4J_PASSWORD still contains placeholder value - must be changed"
    fi
fi

# Check Redis password
if [ -n "$REDIS_PASSWORD" ]; then
    redis_pwd_length=${#REDIS_PASSWORD}
    if [ $redis_pwd_length -ge 32 ]; then
        log_success "REDIS_PASSWORD length is sufficient ($redis_pwd_length characters)"
    else
        log_warning "REDIS_PASSWORD is shorter than recommended (current: $redis_pwd_length, recommended: 32+)"
    fi
    
    if [[ "$REDIS_PASSWORD" == *"CHANGE_ME"* ]]; then
        log_error "REDIS_PASSWORD still contains placeholder value - must be changed"
    fi
fi

echo ""

# ============================================================================
# 5. Validate API URL Configuration
# ============================================================================
log_info "Validating API URL configuration..."

if [ -n "$NEXT_PUBLIC_API_URL" ]; then
    if [[ "$NEXT_PUBLIC_API_URL" == https://* ]]; then
        log_success "NEXT_PUBLIC_API_URL uses HTTPS"
    else
        log_error "NEXT_PUBLIC_API_URL must use HTTPS in production"
    fi
    
    if [[ "$NEXT_PUBLIC_API_URL" == *"your-domain.com"* ]]; then
        log_error "NEXT_PUBLIC_API_URL still contains placeholder domain - must be changed"
    fi
fi

echo ""

# ============================================================================
# 6. Validate CORS Configuration
# ============================================================================
log_info "Validating CORS configuration..."

if [ -n "$CORS_ALLOWED_ORIGINS" ]; then
    if [[ "$CORS_ALLOWED_ORIGINS" == *"your-domain.com"* ]]; then
        log_error "CORS_ALLOWED_ORIGINS still contains placeholder domain - must be changed"
    else
        log_success "CORS_ALLOWED_ORIGINS is configured"
    fi
fi

echo ""

# ============================================================================
# 7. Validate Rate Limiting Configuration
# ============================================================================
log_info "Validating rate limiting configuration..."

if [ "$ENABLE_RATE_LIMITING" = "true" ]; then
    log_success "Rate limiting is enabled"
    
    if [ -n "$RATE_LIMIT_PER_MINUTE" ] && [ "$RATE_LIMIT_PER_MINUTE" -le 100 ]; then
        log_success "Rate limit per minute is set to $RATE_LIMIT_PER_MINUTE"
    else
        log_warning "Rate limit per minute is not set or exceeds recommended value"
    fi
    
    if [ -n "$RATE_LIMIT_PER_HOUR" ] && [ "$RATE_LIMIT_PER_HOUR" -le 5000 ]; then
        log_success "Rate limit per hour is set to $RATE_LIMIT_PER_HOUR"
    else
        log_warning "Rate limit per hour is not set or exceeds recommended value"
    fi
else
    log_warning "Rate limiting is disabled (should be enabled in production)"
fi

echo ""

# ============================================================================
# 8. Validate Security Headers
# ============================================================================
log_info "Validating security headers configuration..."

if [ "$ENABLE_HSTS" = "true" ]; then
    log_success "HSTS is enabled"
else
    log_warning "HSTS is disabled (should be enabled in production)"
fi

if [ "$ENABLE_CSP" = "true" ]; then
    log_success "Content Security Policy is enabled"
else
    log_warning "CSP is disabled (should be enabled in production)"
fi

echo ""

# ============================================================================
# 9. Test Database Connections
# ============================================================================
log_info "Testing database connections..."

if command -v python3 &> /dev/null; then
    if [ -f "scripts/test_db_connections.py" ]; then
        log_info "Running database connection tests..."
        python3 scripts/test_db_connections.py
        if [ $? -eq 0 ]; then
            log_success "Database connection tests passed"
        else
            log_error "Database connection tests failed"
        fi
    else
        log_warning "Database connection test script not found (scripts/test_db_connections.py)"
    fi
else
    log_warning "Python3 not found, skipping database connection tests"
fi

echo ""

# ============================================================================
# 10. Validate SSL Certificates
# ============================================================================
log_info "Validating SSL certificates..."

if [ -d "certs" ]; then
    if [ -f "certs/fullchain.pem" ] && [ -f "certs/privkey.pem" ]; then
        log_success "SSL certificate files found"
        
        # Check certificate expiration
        if command -v openssl &> /dev/null; then
            expiry_date=$(openssl x509 -enddate -noout -in certs/fullchain.pem | cut -d= -f2)
            expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$expiry_date" +%s 2>/dev/null)
            current_epoch=$(date +%s)
            days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))
            
            if [ $days_until_expiry -gt 30 ]; then
                log_success "SSL certificate is valid for $days_until_expiry more days"
            elif [ $days_until_expiry -gt 0 ]; then
                log_warning "SSL certificate expires in $days_until_expiry days - renewal recommended"
            else
                log_error "SSL certificate has expired"
            fi
        fi
    else
        log_error "SSL certificate files not found in certs/ directory"
        log_info "Expected files: certs/fullchain.pem, certs/privkey.pem"
    fi
else
    log_error "certs/ directory not found"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo -e "${GREEN}Successful checks: $CHECKS${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Errors: $ERRORS${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ All validation checks passed!${NC}"
        echo "Production environment is ready for deployment."
        exit 0
    else
        echo -e "${YELLOW}⚠ Validation passed with warnings.${NC}"
        echo "Please review the warnings above before deploying to production."
        exit 0
    fi
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s).${NC}"
    echo "Please fix the errors above before deploying to production."
    exit 1
fi
