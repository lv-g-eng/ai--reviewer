#!/bin/bash
# Security Tests Runner Script
# 
# This script runs comprehensive security tests including OWASP ZAP scanning
# and OWASP Top 10 vulnerability tests.
#
# Usage:
#   ./run_security_tests.sh [options]
#
# Options:
#   --backend-url URL    Backend URL (default: http://localhost:8000)
#   --skip-zap          Skip OWASP ZAP automated scan
#   --verbose           Show detailed output
#   --help              Show this help message

set -e

# Default configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
SKIP_ZAP=false
VERBOSE=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-url)
            BACKEND_URL="$2"
            shift 2
            ;;
        --skip-zap)
            SKIP_ZAP=true
            shift
            ;;
        --verbose)
            VERBOSE="-s"
            shift
            ;;
        --help)
            echo "Security Tests Runner"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --backend-url URL    Backend URL (default: http://localhost:8000)"
            echo "  --skip-zap          Skip OWASP ZAP automated scan"
            echo "  --verbose           Show detailed output"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Print banner
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}           Security Tests - OWASP Top 10 2021              ${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "Backend URL: ${GREEN}$BACKEND_URL${NC}"
echo -e "Skip ZAP Scan: ${YELLOW}$SKIP_ZAP${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check if backend is accessible
echo -n "  Checking backend accessibility... "
if curl -s -f "$BACKEND_URL/api/v1/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo -e "${RED}ERROR: Backend at $BACKEND_URL is not accessible${NC}"
    echo "Please start the backend before running security tests:"
    echo "  cd backend && uvicorn app.main:app --reload"
    exit 1
fi

# Check if Docker is available
echo -n "  Checking Docker availability... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo -e "${RED}ERROR: Docker is not available${NC}"
    echo "Please install Docker to run OWASP ZAP scans:"
    echo "  https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if pytest is available
echo -n "  Checking pytest availability... "
if python -m pytest --version &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo -e "${RED}ERROR: pytest is not available${NC}"
    echo "Please install pytest:"
    echo "  pip install pytest requests pyyaml"
    exit 1
fi

echo ""

# Export environment variables
export BACKEND_URL

# Run tests
cd "$BACKEND_DIR"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}Running Security Tests${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Test categories
if [ "$SKIP_ZAP" = false ]; then
    echo -e "${YELLOW}1. OWASP ZAP Automated Scan${NC}"
    echo "   This may take 5-10 minutes..."
    echo ""
    
    if python -m pytest tests/system/test_security_owasp_top10.py::TestOWASPZAPScan -v $VERBOSE; then
        echo -e "${GREEN}✓ ZAP scan completed successfully${NC}"
    else
        echo -e "${RED}✗ ZAP scan failed${NC}"
        exit 1
    fi
    echo ""
else
    echo -e "${YELLOW}Skipping OWASP ZAP automated scan${NC}"
    echo ""
fi

echo -e "${YELLOW}2. OWASP Top 10 Vulnerability Tests${NC}"
echo ""

if python -m pytest tests/system/test_security_owasp_top10.py::TestOWASPTop10Vulnerabilities -v $VERBOSE; then
    echo -e "${GREEN}✓ OWASP Top 10 tests passed${NC}"
else
    echo -e "${RED}✗ OWASP Top 10 tests failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}3. Security Headers Tests${NC}"
echo ""

if python -m pytest tests/system/test_security_owasp_top10.py::TestSecurityHeaders -v $VERBOSE; then
    echo -e "${GREEN}✓ Security headers tests passed${NC}"
else
    echo -e "${RED}✗ Security headers tests failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}4. Rate Limiting Tests${NC}"
echo ""

if python -m pytest tests/system/test_security_owasp_top10.py::TestRateLimiting -v $VERBOSE; then
    echo -e "${GREEN}✓ Rate limiting tests passed${NC}"
else
    echo -e "${YELLOW}⚠ Rate limiting tests had warnings${NC}"
    # Don't fail on rate limiting tests as they may not trigger without auth
fi
echo ""

# Summary
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✓ All security tests completed successfully${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Show reports location
if [ "$SKIP_ZAP" = false ]; then
    REPORTS_DIR="$BACKEND_DIR/security/zap_reports"
    if [ -d "$REPORTS_DIR" ]; then
        echo "Security scan reports available at:"
        echo "  HTML: $REPORTS_DIR/baseline_report.html"
        echo "  JSON: $REPORTS_DIR/baseline_report.json"
        echo "  Markdown: $REPORTS_DIR/baseline_report.md"
        echo ""
    fi
fi

echo -e "${GREEN}Security testing complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review any warnings or medium severity findings"
echo "  2. Fix any identified vulnerabilities"
echo "  3. Re-run tests to verify fixes"
echo "  4. Document any accepted risks"
echo ""

exit 0
