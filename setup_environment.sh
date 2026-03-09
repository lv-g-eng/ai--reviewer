#!/bin/bash
# =============================================================================
# AI Code Review Platform - Environment Setup Script
# =============================================================================
# This script automatically fixes common setup issues
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Environment Setup & Fix Script${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Step 1: Create .env file if not exists
echo -e "${YELLOW}Step 1: Setting up environment file${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo -e "${GREEN}✓ Created .env from template${NC}"
    else
        echo -e "${RED}✗ .env.template not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

# Step 2: Generate secure secrets
echo ""
echo -e "${YELLOW}Step 2: Generating secure secrets${NC}"

# Function to generate random secret
generate_secret() {
    python3 -c "import secrets; print(secrets.token_hex(32))"
}

# Update .env with generated secrets
update_env_var() {
    local var_name=$1
    local var_value=$2
    
    if grep -q "^${var_name}=" .env; then
        # Update existing variable
        sed -i "s|^${var_name}=.*|${var_name}=${var_value}|" .env
    else
        # Add new variable
        echo "${var_name}=${var_value}" >> .env
    fi
}

# Generate and set secrets
JWT_SECRET=$(generate_secret)
SECRET_KEY=$(generate_secret)
SESSION_SECRET=$(generate_secret)

update_env_var "JWT_SECRET" "$JWT_SECRET"
update_env_var "SECRET_KEY" "$SECRET_KEY"
update_env_var "SESSION_SECRET" "$SESSION_SECRET"

echo -e "${GREEN}✓ Generated secure secrets${NC}"

# Step 3: Set database passwords (for development only)
echo ""
echo -e "${YELLOW}Step 3: Setting database credentials${NC}"

# For development, use simple passwords
update_env_var "POSTGRES_PASSWORD" "dev_password_123"
update_env_var "NEO4J_PASSWORD" "dev_password_123"
update_env_var "REDIS_PASSWORD" "dev_password_123"

echo -e "${GREEN}✓ Set development database passwords${NC}"
echo -e "${YELLOW}  Note: Change these for production!${NC}"

# Step 4: Install Python dependencies
echo ""
echo -e "${YELLOW}Step 4: Installing Python dependencies${NC}"

if [ -f "backend/requirements.txt" ]; then
    cd backend
    pip install --break-system-packages -q -r requirements.txt 2>&1 | grep -v "Requirement already satisfied" || true
    cd ..
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}✗ backend/requirements.txt not found${NC}"
fi

# Step 5: Check Docker (optional)
echo ""
echo -e "${YELLOW}Step 5: Checking Docker${NC}"

if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        echo -e "${GREEN}✓ Docker is running${NC}"
        
        # Start Docker services if docker-compose exists
        if [ -f "docker-compose.yml" ]; then
            echo -e "${BLUE}  Starting Docker services...${NC}"
            docker-compose up -d postgres redis neo4j 2>&1 || {
                echo -e "${YELLOW}  ⚠ Some Docker services may have failed to start${NC}"
                echo -e "${YELLOW}  This is OK if you're using local databases${NC}"
            }
        fi
    else
        echo -e "${YELLOW}⚠ Docker is installed but not running${NC}"
        echo -e "${YELLOW}  Start Docker Desktop or Docker daemon to use containerized databases${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Docker not installed${NC}"
    echo -e "${YELLOW}  You'll need local PostgreSQL, Redis, and Neo4j installations${NC}"
fi

# Step 6: Install frontend dependencies
echo ""
echo -e "${YELLOW}Step 6: Installing frontend dependencies${NC}"

if [ -d "frontend" ]; then
    cd frontend
    
    if command -v npm &> /dev/null; then
        if [ ! -d "node_modules" ]; then
            echo -e "${BLUE}  Installing npm packages...${NC}"
            npm install --silent 2>&1 | tail -5
            echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
        else
            echo -e "${GREEN}✓ node_modules already exists${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ npm not found, skipping frontend setup${NC}"
    fi
    
    cd ..
else
    echo -e "${YELLOW}⚠ frontend directory not found${NC}"
fi

# Step 7: Run quick health check again
echo ""
echo -e "${YELLOW}Step 7: Verifying setup${NC}"

if [ -f "quick_health_check.py" ]; then
    python3 quick_health_check.py
else
    echo -e "${YELLOW}⚠ quick_health_check.py not found${NC}"
fi

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Setup Complete${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${GREEN}✅ Environment setup finished!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review and update .env with your specific settings"
echo "2. Start databases (Docker or local installation)"
echo "3. Run backend: cd backend && uvicorn app.main:app --reload"
echo "4. Run frontend: cd frontend && npm run dev"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "- Change default passwords before production deployment"
echo "- Configure API keys (GITHUB_TOKEN, OPENAI_API_KEY, etc.) if needed"
echo ""
