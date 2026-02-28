#!/bin/bash

# Script to run end-to-end tests in staging environment
# This script sets up the staging environment and runs e2e tests

set -e  # Exit on error

echo "=========================================="
echo "Running End-to-End Tests in Staging"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in staging environment
if [ "$ENVIRONMENT" != "staging" ]; then
    echo -e "${YELLOW}Warning: ENVIRONMENT is not set to 'staging'${NC}"
    echo "Setting ENVIRONMENT=staging"
    export ENVIRONMENT=staging
fi

# Load staging environment variables
if [ -f ".env.staging" ]; then
    echo "Loading staging environment variables..."
    export $(cat .env.staging | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env.staging file not found${NC}"
    exit 1
fi

# Check required services
echo ""
echo "Checking required services..."

# Check PostgreSQL
if ! pg_isready -h ${DATABASE_HOST:-localhost} -p ${DATABASE_PORT:-5432} > /dev/null 2>&1; then
    echo -e "${RED}Error: PostgreSQL is not running${NC}"
    echo "Start with: docker-compose -f docker-compose.staging.yml up -d postgres"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"

# Check Neo4j
if ! nc -z ${NEO4J_HOST:-localhost} ${NEO4J_PORT:-7687} > /dev/null 2>&1; then
    echo -e "${RED}Error: Neo4j is not running${NC}"
    echo "Start with: docker-compose -f docker-compose.staging.yml up -d neo4j"
    exit 1
fi
echo -e "${GREEN}✓ Neo4j is running${NC}"

# Check Redis
if ! redis-cli -h ${REDIS_HOST:-localhost} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; then
    echo -e "${RED}Error: Redis is not running${NC}"
    echo "Start with: docker-compose -f docker-compose.staging.yml up -d redis"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}"

# Run database migrations
echo ""
echo "Running database migrations..."
cd backend
alembic upgrade head
cd ..

# Clean up old test data
echo ""
echo "Cleaning up old test data..."
python backend/scripts/cleanup_test_data.py || echo "No cleanup script found, skipping..."

# Run e2e tests
echo ""
echo "=========================================="
echo "Running E2E Tests"
echo "=========================================="

# Parse command line arguments
VERBOSE=""
COVERAGE=""
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=app --cov-report=html --cov-report=term"
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-v|--verbose] [-c|--coverage] [-t|--test TEST_NAME]"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest backend/tests/e2e/ -m e2e $VERBOSE $COVERAGE"

if [ -n "$SPECIFIC_TEST" ]; then
    PYTEST_CMD="pytest backend/tests/e2e/$SPECIFIC_TEST -m e2e $VERBOSE $COVERAGE"
fi

# Run tests
echo "Running: $PYTEST_CMD"
echo ""

if $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✓ All E2E Tests Passed!"
    echo -e "==========================================${NC}"
    
    # Show coverage report if generated
    if [ -n "$COVERAGE" ]; then
        echo ""
        echo "Coverage report generated at: htmlcov/index.html"
        echo "Open with: open htmlcov/index.html (macOS) or xdg-open htmlcov/index.html (Linux)"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}=========================================="
    echo "✗ E2E Tests Failed"
    echo -e "==========================================${NC}"
    
    # Show logs for debugging
    echo ""
    echo "Check logs for more details:"
    echo "  - Application logs: logs/app.log"
    echo "  - Database logs: docker logs <postgres_container>"
    echo "  - Neo4j logs: docker logs <neo4j_container>"
    
    exit 1
fi
