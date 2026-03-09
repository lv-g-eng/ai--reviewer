#!/bin/bash
# =============================================================================
# AI Code Review Platform - Smoke Test Runner
# =============================================================================
# This script runs minimal smoke tests to verify core functionality
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Smoke Test - Phase 2 Health Check${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found. Please run from project root.${NC}"
    exit 1
fi

# Function to check service health
check_service() {
    local service_name=$1
    local port=$2
    
    echo -e "${BLUE}Checking $service_name...${NC}"
    
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✓ $service_name is running on port $port${NC}"
        return 0
    else
        echo -e "${RED}✗ $service_name is NOT running on port $port${NC}"
        return 1
    fi
}

# Function to check Docker container
check_docker_container() {
    local container_name=$1
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        echo -e "${GREEN}✓ Docker container '$container_name' is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Docker container '$container_name' is NOT running${NC}"
        return 1
    fi
}

# Phase 1: Check if Docker services are running
echo -e "${YELLOW}Phase 1: Checking Docker Services${NC}"
echo "-----------------------------------"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker is not installed. Some tests may fail.${NC}"
else
    # Check Docker containers
    check_docker_container "ai_review_postgres" || echo -e "${YELLOW}  Tip: Run 'docker-compose up -d postgres'${NC}"
    check_docker_container "ai_review_redis" || echo -e "${YELLOW}  Tip: Run 'docker-compose up -d redis'${NC}"
    check_docker_container "ai_review_neo4j" || echo -e "${YELLOW}  Tip: Run 'docker-compose up -d neo4j'${NC}"
fi

echo ""

# Phase 2: Check if ports are accessible
echo -e "${YELLOW}Phase 2: Checking Network Ports${NC}"
echo "--------------------------------"

# Check if nc is available
if command -v nc &> /dev/null; then
    check_service "PostgreSQL" 5432 || true
    check_service "Redis" 6379 || true
    check_service "Neo4j HTTP" 7474 || true
    check_service "Neo4j Bolt" 7687 || true
else
    echo -e "${YELLOW}⚠ 'nc' command not found. Skipping port checks.${NC}"
fi

echo ""

# Phase 3: Check Python environment
echo -e "${YELLOW}Phase 3: Checking Python Environment${NC}"
echo "------------------------------------"

if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo -e "${GREEN}✓ Python: $python_version${NC}"
    
    # Check if pytest is installed
    if python3 -c "import pytest" 2>/dev/null; then
        echo -e "${GREEN}✓ pytest is installed${NC}"
    else
        echo -e "${YELLOW}⚠ pytest is not installed. Installing...${NC}"
        pip install --break-system-packages pytest pytest-asyncio
    fi
else
    echo -e "${RED}✗ Python3 is not installed${NC}"
    exit 1
fi

echo ""

# Phase 4: Check environment variables
echo -e "${YELLOW}Phase 4: Checking Environment Variables${NC}"
echo "--------------------------------------"

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
    
    # Check critical variables
    critical_vars=(
        "POSTGRES_DB"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "JWT_SECRET"
        "SECRET_KEY"
    )
    
    for var in "${critical_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            value=$(grep "^${var}=" .env | cut -d'=' -f2)
            if [ -n "$value" ] && [ "$value" != "your_${var,,}_here" ]; then
                echo -e "${GREEN}  ✓ $var is set${NC}"
            else
                echo -e "${YELLOW}  ⚠ $var has placeholder value${NC}"
            fi
        else
            echo -e "${RED}  ✗ $var is not set${NC}"
        fi
    done
else
    echo -e "${RED}✗ .env file not found. Please copy .env.template to .env${NC}"
    echo -e "${YELLOW}  Tip: cp .env.template .env${NC}"
fi

echo ""

# Phase 5: Run smoke tests
echo -e "${YELLOW}Phase 5: Running Smoke Tests${NC}"
echo "----------------------------"

cd backend

# Check if we can import the main app
echo -e "${BLUE}Testing basic imports...${NC}"
if python3 -c "from app.main import app; print('✓ Main app imports successfully')" 2>&1; then
    :
else
    echo -e "${RED}✗ Failed to import main app${NC}"
    echo -e "${YELLOW}  This might be due to missing dependencies. Installing...${NC}"
    pip install --break-system-packages -r requirements.txt
fi

echo ""

# Run the smoke tests
echo -e "${BLUE}Executing smoke tests...${NC}"
echo ""

if [ -f "tests/smoke_test_core.py" ]; then
    python3 -m pytest tests/smoke_test_core.py -v --tb=short 2>&1
    test_exit_code=$?
else
    echo -e "${YELLOW}⚠ Smoke test file not found at tests/smoke_test_core.py${NC}"
    echo -e "${YELLOW}  Running basic import tests instead...${NC}"
    
    python3 -c "
import sys
try:
    from app.main import app
    print('✅ App import: OK')
except Exception as e:
    print(f'❌ App import: FAILED - {e}')
    sys.exit(1)
" 2>&1
    
    test_exit_code=$?
fi

cd ..

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Smoke Test Complete${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Summary
if [ $test_exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ All smoke tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Review any warnings above"
    echo "2. Configure missing environment variables if needed"
    echo "3. Proceed to Phase 3: Fix broken functionality"
else
    echo -e "${RED}❌ Some smoke tests failed.${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting tips:${NC}"
    echo "1. Ensure Docker containers are running: docker-compose up -d"
    echo "2. Check .env file has correct values"
    echo "3. Install dependencies: cd backend && pip install -r requirements.txt"
    echo "4. Check logs: docker-compose logs"
fi

exit $test_exit_code
