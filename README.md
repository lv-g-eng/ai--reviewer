# 🚀 AI-Powered Code Review Platform

> **Status**: Frontend 100% Complete | Backend 25% Complete | Production-Ready in 6-8 Weeks

A comprehensive microservices-based platform that provides automated code quality analysis, graph-based architecture visualization, and agentic AI reasoning for software development teams.

## 📊 Project Status

| Component | Status | Progress |
|-----------|--------|----------|
| Frontend (Next.js) | ✅ Complete | 100% |
| API Gateway | ✅ Complete | 100% |
| NextAuth Integration | ✅ Complete | 100% |
| Backend Services | 🟡 In Progress | 25% |
| Tests | ⚠️ Low Coverage | 20% |
| CI/CD | ⚠️ Not Setup | 0% |

## 🎯 Quick Start

**New to the project?** → Read **[PROJECT_GUIDE.md](PROJECT_GUIDE.md)** (5 minutes)

**Ready to code?** → See setup instructions below

## 🏗️ Architecture

### Microservices
- **api-gateway**: Entry point, routing, rate limiting (✅ Complete)
- **auth-service**: Authentication, authorization, RBAC (🟡 25% complete)
- **code-review-engine**: Code quality analysis (⏳ Not started)
- **architecture-analyzer**: Source code parsing, graph database (⏳ Not started)
- **agentic-ai**: AI reasoning, pattern recognition (⏳ Not started)
- **project-manager**: Project lifecycle management (⏳ Not started)

### Databases
- **PostgreSQL**: Relational data
- **Neo4j**: Architecture graph
- **Redis**: Caching & sessions

## 📖 Documentation

### Essential Reading
- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheat sheet
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues
- **[docs/](docs/)** - Complete documentation hub

### Key Guides
- **[docs/npm-management.md](docs/npm-management.md)** - NPM cache, audit, and updates
- **[docs/LLM_QUICK_START.md](docs/LLM_QUICK_START.md)** - Local LLM setup
- **[docs/SECURITY.md](docs/SECURITY.md)** - Security best practices
- **[docs/AI_PR_REVIEWER_GUIDE.md](docs/AI_PR_REVIEWER_GUIDE.md)** - AI code review

## 💻 Development Setup

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Docker (All Services)
```bash
docker-compose up -d
```

## 🏗️ Architecture

### Microservices
- **api-gateway**: Single entry point, routing, rate limiting
- **auth-service**: Authentication, authorization, RBAC
- **code-review-engine**: Code quality analysis
- **architecture-analyzer**: Source code parsing, graph database
- **agentic-ai**: AI reasoning, pattern recognition
- **project-manager**: Project lifecycle management

### Databases
- **PostgreSQL**: Relational data
- **Neo4j**: Architecture graph
- **Redis**: Caching & sessions

## 🧪 Testing

```bash
# API Gateway tests (409 tests, 95% coverage)
cd services/api-gateway
npm test

# NextAuth tests (64 tests, 100% coverage)
cd frontend
npm test -- auth

# Backend tests
cd backend
pytest

# All tests
npm test
```

## 🎯 Current Focus

### This Week
- Complete Backend Authentication Service (Task 2.2-2.4)
- API Gateway Integration (Task 3)
- Increase test coverage

### Next 2 Weeks
- Code Review Engine (Task 5)
- Architecture Analyzer (Task 6)
- Service Integration

See **[PROJECT_GUIDE.md](PROJECT_GUIDE.md)** for detailed roadmap.

---

**Ready to contribute?** Read [PROJECT_GUIDE.md](PROJECT_GUIDE.md) to get started!