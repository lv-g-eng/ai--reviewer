# 📚 Quick Reference Guide

**Last Updated**: January 21, 2026

---

## 📍 Essential Links

- **[README.md](README.md)** - Project overview
- **[QUICK_START.md](QUICK_START.md)** - Environment setup
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
- **[docs/](docs/)** - Complete documentation

---

## ⚡ Quick Commands

### Start Services
```bash
# Windows - Start all services
START_ALL_SERVICES.bat

# Or individually
START_NEO4J.bat
START_REDIS.bat

# Linux/Mac - Infrastructure
docker-compose up -d

# Frontend
cd frontend
npm install
npm run dev  # http://localhost:3000

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
```

### Testing
```bash
# API Gateway (409 tests, 95% coverage)
cd services/api-gateway
npm test

# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest
```

### Docker
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
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

## 📊 Project Status

| Component | Status | Progress |
|-----------|--------|----------|
| API Gateway | ✅ Complete | 100% |
| Frontend UI | ✅ Complete | 100% |
| NextAuth | ✅ Complete | 100% |
| Backend Auth | 🟡 In Progress | 25% |
| Other Services | ⏳ Not Started | 0% |

---

## 📞 Getting Help

1. Check **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
2. Review **[docs/README.md](docs/README.md)**
3. Search in relevant documentation
4. Create GitHub issue

---

**Quick Tip**: Bookmark this page for easy reference! 📌
