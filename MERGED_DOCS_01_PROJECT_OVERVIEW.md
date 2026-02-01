# Project Documentation - Overview & Getting Started

**Document Type:** Merged Documentation
**Last Updated:** 2026-01-21
**Merged From:** README.md, PROJECT_GUIDE.md, PROJECT_INDEX.md, MASTER_GUIDE.md, QUICK_START.md

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Quick Start Guide](#2-quick-start-guide)
3. [Project Structure](#3-project-structure)
4. [Master Guide](#4-master-guide)
5. [Project Index](#5-project-index)

---

## 1. Project Overview

### AI-Based Code Quality Check Platform

An AI-powered platform for automated code review, architecture analysis, and quality assessment.

### Key Features

- **Automated Code Review**: AI-driven analysis of pull requests
- **Architecture Analysis**: Dependency graph visualization and analysis
- **GitHub Integration**: Seamless integration with GitHub repositories
- **Repository Management**: Add and manage GitHub dependencies
- **LLM Integration**: Support for local and cloud-based LLMs
- **Real-time Analysis**: Instant feedback on code quality

### Technology Stack

**Backend:**
- Python 3.11+ with FastAPI
- PostgreSQL for relational data
- Neo4j for graph data
- Redis for caching
- Celery for async tasks

**Frontend:**
- Next.js 14 with TypeScript
- React 18
- Tailwind CSS
- NextAuth for authentication

**Infrastructure:**
- Docker & Docker Compose
- Nginx for reverse proxy
- Prometheus & Grafana for monitoring

---

## 2. Quick Start Guide

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Quick Setup (15 minutes)

#### Step 1: Clone Repository
```bash
git clone <repository-url>
cd ai-code-review-platform
```

#### Step 2: Clean Up Test Data
```bash
python scripts/cleanup_test_data.py
```

#### Step 3: Configure Environment

Generate secure keys:
```bash
# JWT Secret
openssl rand -hex 32

# NextAuth Secret
openssl rand -base64 32
```

Update `.env`:
```bash
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET=generated_jwt_secret
GITHUB_TOKEN=ghp_your_github_token
```

#### Step 4: Start Services
```bash
docker-compose up -d
```

#### Step 5: Run Migrations
```bash
cd backend
alembic upgrade head
```

#### Step 6: Verify Installation
```bash
# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

### First Steps

1. **Create User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePass123!","full_name":"Admin"}'
```

2. **Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePass123!"}'
```

3. **Add Repository**
```bash
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repository_url":"https://github.com/facebook/react.git","branch":"main"}'
```

---

## 3. Project Structure

```
ai-code-review-platform/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core configuration
│   │   ├── database/          # Database connections
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── tasks/             # Celery tasks
│   │   └── utils/             # Utilities
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js app router
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilities
│   │   └── types/             # TypeScript types
│   └── package.json           # Node dependencies
│
├── services/                   # Microservices
│   ├── api-gateway/           # API Gateway service
│   ├── auth-service/          # Authentication service
│   ├── llm-service/           # LLM inference service
│   └── ...
│
├── scripts/                    # Utility scripts
│   ├── cleanup_test_data.py   # Data cleanup
│   ├── setup-dev.sh           # Development setup
│   └── ...
│
├── docs/                       # Documentation
│   ├── REPOSITORY_MANAGEMENT.md
│   ├── DATA_CLEANUP_GUIDE.md
│   └── ...
│
├── monitoring/                 # Monitoring configuration
│   ├── prometheus/
│   └── grafana/
│
├── docker-compose.yml          # Docker services
└── .env                        # Environment variables
```

---

## 4. Master Guide

### Development Workflow

#### Backend Development

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Create migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head
```

#### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Start production server
npm start
```

#### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Stop all services
docker-compose down

# Rebuild service
docker-compose up -d --build backend
```

### Common Tasks

#### Adding a New API Endpoint

1. Create schema in `backend/app/schemas/`
2. Create endpoint in `backend/app/api/v1/endpoints/`
3. Register in `backend/app/api/v1/router.py`
4. Add tests in `backend/tests/`

#### Adding a New Database Model

1. Create model in `backend/app/models/`
2. Create migration: `alembic revision -m "add_table"`
3. Edit migration file
4. Apply: `alembic upgrade head`

#### Adding a New Frontend Component

1. Create component in `frontend/src/components/`
2. Add TypeScript types in `frontend/src/types/`
3. Add tests in `frontend/src/__tests__/`
4. Import and use in pages

### Best Practices

1. **Code Quality**
   - Follow PEP 8 for Python
   - Use ESLint for JavaScript/TypeScript
   - Write tests for new features
   - Document complex logic

2. **Git Workflow**
   - Create feature branches
   - Write descriptive commit messages
   - Submit pull requests for review
   - Keep commits atomic

3. **Security**
   - Never commit secrets
   - Use environment variables
   - Validate all inputs
   - Sanitize outputs

4. **Performance**
   - Use database indexes
   - Implement caching
   - Optimize queries
   - Monitor performance

---

## 5. Project Index

### Documentation Files

**Setup & Configuration:**
- SETUP_GUIDE.md - Complete setup instructions
- ENVIRONMENT_CLEANUP.md - Virtual environment cleanup
- QUICK_ACTIONS.md - Quick reference for common tasks

**Feature Guides:**
- docs/REPOSITORY_MANAGEMENT.md - Repository management system
- docs/DATA_CLEANUP_GUIDE.md - Data cleanup procedures
- docs/LLM_INTEGRATION_GUIDE.md - LLM integration guide
- docs/AI_PR_REVIEWER_GUIDE.md - AI PR reviewer usage

**Technical Documentation:**
- IMPLEMENTATION_SUMMARY.md - Technical implementation details
- CHANGES.md - Change log
- TROUBLESHOOTING.md - Common issues and solutions

**API Documentation:**
- services/api-gateway/docs/ - API Gateway documentation
- http://localhost:8000/docs - Interactive API documentation

### Script Files

**Setup Scripts:**
- scripts/setup-dev.sh - Development environment setup
- scripts/setup-llm.sh - LLM service setup
- cleanup_environments.bat - Virtual environment cleanup

**Maintenance Scripts:**
- scripts/cleanup_test_data.py - Remove test data
- scripts/clean-npm-cache.sh - Clean npm cache
- scripts/verify-path-clean.sh - Verify file paths

**Service Scripts:**
- START_ALL_SERVICES.bat - Start all services
- STOP_ALL_SERVICES.bat - Stop all services
- backend/start_worker.sh - Start Celery worker

### Key Endpoints

**Authentication:**
- POST /api/v1/auth/register - Register user
- POST /api/v1/auth/login - Login
- GET /api/v1/auth/me - Get current user

**Repository Management:**
- POST /api/v1/repositories - Add repository
- GET /api/v1/repositories/validate - Validate URL
- GET /api/v1/repositories - List repositories

**Analysis:**
- POST /api/v1/analysis/projects/{id}/analyze - Analyze project
- GET /api/v1/analysis/results/{id} - Get results

**Health:**
- GET /health - Health check
- GET /api/v1/health - Detailed health

### Environment Variables

**Required:**
- POSTGRES_PASSWORD - Database password
- JWT_SECRET - JWT signing key
- GITHUB_TOKEN - GitHub API token

**Optional:**
- OPENAI_API_KEY - OpenAI API key
- ANTHROPIC_API_KEY - Anthropic API key
- REDIS_PASSWORD - Redis password

### Ports

- 3000 - Frontend (Next.js)
- 8000 - Backend API (FastAPI)
- 5432 - PostgreSQL
- 6379 - Redis
- 7474 - Neo4j Browser
- 7687 - Neo4j Bolt
- 9090 - Prometheus
- 3001 - Grafana

---

## Modification History

### 2026-01-21
- Merged README.md, PROJECT_GUIDE.md, PROJECT_INDEX.md, MASTER_GUIDE.md, QUICK_START.md
- Added comprehensive project overview
- Consolidated quick start instructions
- Unified project structure documentation
- Created master development guide
- Compiled complete project index

---

## Related Documents

- **Setup:** MERGED_DOCS_02_SETUP_CONFIGURATION.md
- **Features:** MERGED_DOCS_03_FEATURES_GUIDES.md
- **Technical:** MERGED_DOCS_04_TECHNICAL_REFERENCE.md
- **Troubleshooting:** MERGED_DOCS_05_TROUBLESHOOTING_MAINTENANCE.md
