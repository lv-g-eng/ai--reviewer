# 📚 Quick Reference Guide

**Last Updated**: February 4, 2026

> **Quick access to all essential commands and configurations**

---

## 📍 Essential Links

- **[README.md](README.md)** - Project overview
- **[QUICK_START.md](QUICK_START.md)** - Complete setup guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues
- **[docs/README.md](docs/README.md)** - Documentation hub

---

## ⚡ Quick Start Commands

### Start Services

**Fast Start (3 commands)**:
```bash
docker-compose up -d postgres redis neo4j
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd frontend && npm run dev
```

**Windows Batch Scripts**:
```cmd
START_ALL_SERVICES.bat  # Start all infrastructure
START_NEO4J.bat         # Start Neo4j only
START_REDIS.bat         # Start Redis only
STOP_ALL_SERVICES.bat   # Stop all services
```

**Individual Services**:
```bash
# Infrastructure
docker-compose up -d postgres redis neo4j

# Backend (new terminal)
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd frontend
npm run dev
```

**Access**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop Services
```bash
# Stop backend/frontend: Ctrl+C in terminals

# Stop infrastructure
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 🧪 Testing Commands

```bash
# Run all tests
npm test  # Root: runs all service tests

# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && pytest

# Backend with coverage
cd backend && pytest --cov=app --cov-report=html

# API Gateway tests (409 tests, 95% coverage)
cd services/api-gateway && npm test

# Run specific test file
cd backend && pytest tests/test_auth_endpoints.py

# Run with verbose output
cd backend && pytest -v
```

---

## 🐳 Docker Commands

```bash
# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f postgres
docker-compose logs -f backend

# Check service status
docker-compose ps

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Remove orphan containers
docker-compose down --remove-orphans
```

---

## 🔑 Environment Variables

### Frontend (.env.local)
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=dev-secret-key-change-in-production-min-32-chars-required
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_URL=http://localhost:8000
```

### Backend (.env)
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_code_review
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET=test_secret_key_for_development_only
```

---

## 🚨 Common Issues

### Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Verify environment variables
cat frontend/.env.local
```

### Database connection failed
```bash
# Check services
docker-compose ps

# Restart services
docker-compose restart
```

### Tests failing
```bash
# Frontend
cd frontend
rm -rf node_modules .next
npm install

# Backend
cd backend
pip install -r requirements.txt
pytest --cache-clear
```

---

## 🔐 Security Commands

### Secret Management
```bash
# Create environment file from template
cp .env.example .env

# Clean secrets from git history (use with caution!)
bash scripts/remove_git_secrets.sh

# Verify no secrets in codebase
trufflehog filesystem . --json
```

### Security Scanning
```bash
# Python security
bandit -r backend/app -ll
safety check

# JavaScript security
cd frontend
npm audit
npm run lint

# Container security
docker build -t backend-test backend/
trivy image backend-test
```

---

## 🛠️ Maintenance Commands

### NPM Cache Management
```bash
# Windows
scripts\clean-npm-cache.bat
scripts\verify-path-clean.bat

# Linux/Mac
./scripts/clean-npm-cache.sh
./scripts/verify-path-clean.sh
```

### Database Management
```bash
# Create database
CREATE_DATABASE.bat

# Reset database
docker-compose down -v
docker-compose up -d
```

### LLM Setup
```bash
# Windows
scripts\setup-llm.bat

# Linux/Mac
./scripts/setup-llm.sh
```

---

## 🗄️ Database Commands

```bash
# Run migrations
cd backend && alembic upgrade head

# Create new migration
cd backend && alembic revision -m "description"

# Rollback migration
cd backend && alembic downgrade -1

# View migration history
cd backend && alembic history

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d postgres
cd backend && alembic upgrade head
```

---

## 🔧 Development Commands

```bash
# Code formatting
npm run format  # Format all services
cd backend && black app/  # Format Python code
cd frontend && npm run format  # Format TypeScript

# Linting
npm run lint  # Lint all services
cd backend && pylint app/  # Lint Python
cd frontend && npm run lint  # Lint TypeScript

# Type checking
cd frontend && npm run type-check
cd backend && mypy app/

# Build for production
cd frontend && npm run build
cd backend && docker build -t backend:latest .
```

---

## 🛠️ Maintenance Commands

### NPM Cache Management
```bash
# Windows
scripts\clean-npm-cache.bat

# Linux/Mac
./scripts/clean-npm-cache.sh

# Manual cleanup
npm cache clean --force
```

### Python Environment
```bash
# Create new virtual environment
python -m venv venv

# Activate
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Deactivate
deactivate

# Update dependencies
pip install --upgrade -r requirements.txt
```

### LLM Setup
```bash
# Windows
scripts\setup-llm.bat

# Linux/Mac
./scripts/setup-llm.sh
```

---

## 🔐 Security Commands

### Generate Secrets
```bash
# JWT Secret (32 characters)
openssl rand -hex 32

# NextAuth Secret (base64)
openssl rand -base64 32

# GitHub Webhook Secret
openssl rand -hex 20
```

### Security Scanning
```bash
# Python security
cd backend
bandit -r app/ -ll
safety check

# JavaScript security
cd frontend
npm audit
npm audit fix

# Check for secrets in code
trufflehog filesystem . --json
```

---

## 📊 Quick Status Check

```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check database connection
docker-compose exec postgres psql -U postgres -d ai_code_review -c "SELECT 1"

# Check Redis
docker-compose exec redis redis-cli ping

# Check Neo4j
curl http://localhost:7474
```

---

## 🚀 Production Commands

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production services
docker-compose -f docker-compose.prod.yml down
```

---

## 📞 Getting Help

1. **Common issues**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Setup guide**: [QUICK_START.md](QUICK_START.md)
3. **Full documentation**: [docs/README.md](docs/README.md)
4. **API reference**: http://localhost:8000/docs
5. **Create issue**: GitHub Issues

---

**💡 Pro Tip**: Use `Ctrl+F` to quickly find commands on this page!
