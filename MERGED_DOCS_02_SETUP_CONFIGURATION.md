# Project Documentation - Setup & Configuration

**Document Type:** Merged Documentation
**Last Updated:** 2026-01-21
**Merged From:** SETUP_GUIDE.md, ENVIRONMENT_CLEANUP.md, QUICK_ACTIONS.md, docs/INSTALLATION.md, docs/DEVELOPMENT.md

---

## Table of Contents

1. [Complete Setup Guide](#1-complete-setup-guide)
2. [Environment Configuration](#2-environment-configuration)
3. [Virtual Environment Cleanup](#3-virtual-environment-cleanup)
4. [Quick Actions Reference](#4-quick-actions-reference)
5. [Development Setup](#5-development-setup)

---

## 1. Complete Setup Guide

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Git
- PostgreSQL client (optional)

### Step-by-Step Setup

#### Step 1: Clean Up Test Data

```bash
# Run the automated cleanup script
python scripts/cleanup_test_data.py
```

This will:
- Remove test users from database
- Clear test data from Redis
- Clean Neo4j test nodes
- Sanitize environment files
- Delete standalone test scripts

#### Step 2: Configure Environment Variables

**Generate Secure Keys:**

```bash
# JWT Secret (32 bytes hex)
openssl rand -hex 32

# NextAuth Secret (base64)
openssl rand -base64 32

# Webhook Secret
openssl rand -hex 20
```

**Update .env (Root Directory):**

```bash
# Database Configuration
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=ai_code_review
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://your_db_user:your_secure_password_here@postgres:5432/ai_code_review

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_URL=redis://:your_redis_password_here@redis:6379

# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
NEO4J_DATABASE=neo4j

# Security - Use generated keys from above
JWT_SECRET=your_generated_jwt_secret_here
SECRET_KEY=your_generated_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# GitHub Integration
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# LLM API Keys (Optional)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4

# Celery Configuration
CELERY_BROKER_URL=redis://:your_redis_password_here@redis:6379/0
CELERY_RESULT_BACKEND=redis://:your_redis_password_here@redis:6379/1

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Update backend/.env:**

```bash
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_code_review
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password_here

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
NEO4J_DATABASE=neo4j

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_DB=0

JWT_SECRET=your_generated_jwt_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

GITHUB_TOKEN=ghp_your_github_token_here
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

CELERY_BROKER_URL=redis://:your_redis_password_here@localhost:6379/1
CELERY_RESULT_BACKEND=redis://:your_redis_password_here@localhost:6379/2

RATE_LIMIT_PER_MINUTE=60
```

**Update frontend/.env.local:**

```bash
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_generated_nextauth_secret_here

# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_URL=http://localhost:8000

# Application Environment
NEXT_PUBLIC_APP_ENV=development
NODE_ENV=development
```

#### Step 3: Get GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `read:org` - Read organization data
4. Generate and copy the token
5. Add to `.env` files as `GITHUB_TOKEN`

#### Step 4: Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Step 5: Run Database Migrations

```bash
# Navigate to backend
cd backend

# Run migrations
alembic upgrade head

# Verify tables created
docker-compose exec postgres psql -U your_db_user -d ai_code_review -c "\dt"
```

Expected tables:
- users
- roles
- permissions
- user_roles
- role_permissions
- projects
- analysis_results
- analysis_tasks
- user_preferences
- project_metrics
- audit_logs
- repositories

#### Step 6: Create First User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "SecurePassword123!",
    "full_name": "Admin User"
  }'
```

#### Step 7: Test Repository Management

```bash
# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "SecurePassword123!"
  }' | jq -r '.access_token')

# Validate a repository
curl -X GET "http://localhost:8000/api/v1/repositories/validate?repository_url=https://github.com/facebook/react.git" \
  -H "Authorization: Bearer $TOKEN"

# Add a repository
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/facebook/react.git",
    "branch": "main",
    "auto_update": false,
    "description": "React library"
  }'
```

#### Step 8: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs

# Check frontend (if running)
open http://localhost:3000

# Check database connections
python backend/check-services.py
```

### Verification Checklist

- [ ] All services running (postgres, redis, neo4j, backend)
- [ ] Database migrations completed
- [ ] No test data in databases
- [ ] Environment variables configured
- [ ] GitHub token working
- [ ] User registration successful
- [ ] User login successful
- [ ] Repository validation working
- [ ] Repository addition working
- [ ] API documentation accessible

---

## 2. Environment Configuration

### Environment Files Structure

```
project/
├── .env                    # Root environment (Docker services)
├── .env.example            # Template for .env
├── backend/.env            # Backend-specific variables
└── frontend/.env.local     # Frontend-specific variables
```

### Required Variables

**Database:**
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_DB` - Database name
- `DATABASE_URL` - Full connection string

**Redis:**
- `REDIS_HOST` - Redis hostname
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_PASSWORD` - Redis password
- `REDIS_URL` - Full connection string

**Neo4j:**
- `NEO4J_URI` - Neo4j connection URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `NEO4J_DATABASE` - Database name

**Security:**
- `JWT_SECRET` - JWT signing key (32+ characters)
- `SECRET_KEY` - Application secret key
- `NEXTAUTH_SECRET` - NextAuth secret

**GitHub:**
- `GITHUB_TOKEN` - GitHub personal access token
- `GITHUB_WEBHOOK_SECRET` - Webhook secret

### Optional Variables

**LLM Integration:**
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `DEFAULT_LLM_PROVIDER` - Default provider (openai/anthropic)
- `DEFAULT_LLM_MODEL` - Default model name

**Application:**
- `ENVIRONMENT` - Environment (development/production)
- `DEBUG` - Debug mode (true/false)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING)

### Security Best Practices

1. **Never commit .env files**
   - Already in .gitignore
   - Use .env.example as template

2. **Generate strong secrets**
   ```bash
   # 32-byte hex string
   openssl rand -hex 32
   
   # Base64 encoded
   openssl rand -base64 32
   ```

3. **Rotate secrets regularly**
   - Change JWT secrets every 90 days
   - Rotate API keys quarterly
   - Update passwords monthly

4. **Use different secrets per environment**
   - Development secrets
   - Staging secrets
   - Production secrets

---

## 3. Virtual Environment Cleanup

### Current Situation

Your project may have multiple virtual environments:

1. **`venv/`** (root) - Python 3.13.9 from Anaconda (~1GB)
2. **`.venv/`** (root) - Python 3.13.5 from system Python (~870MB)
3. **`backend/venv/`** - Python 3.13.9 from Anaconda (~665MB)

### Recommendation: Keep Only `backend/venv/`

**Why?**

1. **Backend is the only Python component**
   - Main application is in `backend/` directory
   - All Python dependencies are for backend
   - Frontend uses Node.js/npm, not Python

2. **Root virtual environments are redundant**
   - No Python code at root level
   - Scripts in `scripts/` can use backend/venv
   - Duplicate dependencies waste disk space

3. **Docker is the deployment method**
   - Production uses Docker containers
   - Virtual environments only needed for local development
   - One venv is sufficient

### Cleanup Steps

#### Automated Cleanup (Windows)

```cmd
cleanup_environments.bat
```

#### Manual Cleanup

**Windows (PowerShell):**
```powershell
# Remove root venv
Remove-Item -Recurse -Force venv

# Remove root .venv
Remove-Item -Recurse -Force .venv

# Keep backend/venv
```

**Linux/Mac:**
```bash
# Remove root venv
rm -rf venv

# Remove root .venv
rm -rf .venv

# Keep backend/venv
```

### After Cleanup

**Using Backend Virtual Environment:**

```cmd
# Activate backend environment
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install/update dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn app.main:app --reload
```

**Using Docker (Recommended):**

```cmd
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Disk Space Saved

After cleanup:
- `venv/`: ~1,000 MB (removed)
- `.venv/`: ~870 MB (removed)
- **Total saved: ~1.87 GB**

Remaining:
- `backend/venv/`: ~665 MB (kept for development)

---

## 4. Quick Actions Reference

### Immediate Actions (5 minutes)

#### 1. Clean Up Virtual Environments
```cmd
cleanup_environments.bat
```
**Result:** Frees up ~1.87 GB

#### 2. Generate Secure Keys
```cmd
# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Bash
openssl rand -hex 32
```

#### 3. Update .env File
```bash
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET=generated_secret
GITHUB_TOKEN=ghp_your_token
```

### Start the System (2 minutes)

```cmd
# Start all services
docker-compose up -d

# Run migration
cd backend && alembic upgrade head
```

### Verify Everything Works (3 minutes)

```cmd
# Check services
docker-compose ps

# Check API health
curl http://localhost:8000/health

# View API docs
start http://localhost:8000/docs
```

### Test Repository Management (5 minutes)

```cmd
# Create user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePass123!","full_name":"Admin"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePass123!"}'

# Validate repository
curl -X GET "http://localhost:8000/api/v1/repositories/validate?repository_url=https://github.com/facebook/react.git" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Add repository
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repository_url":"https://github.com/facebook/react.git","branch":"main"}'
```

---

## 5. Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Create migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Lint code
npm run lint

# Format code
npm run format

# Build for production
npm run build

# Start production server
npm start
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild service
docker-compose up -d --build backend

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres
```

### Database Operations

```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d ai_code_review

# List tables
\dt

# Describe table
\d users

# Run query
SELECT * FROM users;

# Exit
\q

# Backup database
pg_dump -U postgres ai_code_review > backup.sql

# Restore database
psql -U postgres ai_code_review < backup.sql
```

```bash
# Redis
docker-compose exec redis redis-cli

# Test connection
PING

# List keys
KEYS *

# Get value
GET key_name

# Delete key
DEL key_name

# Flush database
FLUSHDB
```

```bash
# Neo4j
# Access browser at http://localhost:7474

# Or use cypher-shell
docker-compose exec neo4j cypher-shell -u neo4j -p your_password

# List nodes
MATCH (n) RETURN n LIMIT 10;

# Delete all nodes
MATCH (n) DETACH DELETE n;
```

---

## Modification History

### 2026-01-21
- Merged SETUP_GUIDE.md, ENVIRONMENT_CLEANUP.md, QUICK_ACTIONS.md, docs/INSTALLATION.md, docs/DEVELOPMENT.md
- Consolidated setup instructions
- Added environment configuration details
- Included virtual environment cleanup guide
- Added quick actions reference
- Compiled development setup procedures

---

## Related Documents

- **Overview:** MERGED_DOCS_01_PROJECT_OVERVIEW.md
- **Features:** MERGED_DOCS_03_FEATURES_GUIDES.md
- **Technical:** MERGED_DOCS_04_TECHNICAL_REFERENCE.md
- **Troubleshooting:** MERGED_DOCS_05_TROUBLESHOOTING_MAINTENANCE.md
