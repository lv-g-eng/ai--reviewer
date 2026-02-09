# 🚀 AI-Powered Code Review Platform

> **Status**: Active Development | Frontend Complete | Backend In Progress

A comprehensive microservices-based platform that provides automated code quality analysis, graph-based architecture visualization, and agentic AI reasoning for software development teams.

## 📊 Project Status

| Component | Status | Progress |
|-----------|--------|----------|
| Frontend (Next.js) | ✅ Complete | 100% |
| API Gateway | ✅ Complete | 100% |
| NextAuth Integration | ✅ Complete | 100% |
| Backend Services | 🟡 In Progress | 40% |
| Tests | 🟡 Improving | 35% |
| CI/CD | ⏳ Planned | 0% |

## 🎯 Quick Start

### Prerequisites
- Node.js 18+, Python 3.11+, Docker Desktop
- PostgreSQL, Redis, Neo4j (via Docker)

### Start in 3 Steps

```bash
# 1. Start infrastructure services
docker-compose up -d postgres redis neo4j

# 2. Start backend (new terminal)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Start frontend (new terminal)
cd frontend
npm run dev
```

**Access**: 
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Need help?** → See [QUICK_START.md](QUICK_START.md) for detailed setup | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for issues

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│ API Gateway  │────▶│   Backend   │
│  (Next.js)  │     │  (Node.js)   │     │  (FastAPI)  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  PostgreSQL  │     │   Neo4j     │
                    │    Redis     │     │   Celery    │
                    └──────────────┘     └─────────────┘
```

### Core Services
- **Frontend**: Next.js 14, React 18, TailwindCSS (✅ Complete)
- **API Gateway**: Routing, rate limiting, circuit breaker (✅ Complete)
- **Backend**: FastAPI, SQLAlchemy, async operations (🟡 40% complete)
- **Databases**: PostgreSQL (relational), Neo4j (graph), Redis (cache)

## 📖 Documentation

### Getting Started
- **[QUICK_START.md](QUICK_START.md)** - Complete setup guide (5 minutes)
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheat sheet
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues

### Documentation Hub
- **[docs/architecture/URS.md](docs/architecture/URS.md)** - User Requirement Specification
- **[docs/architecture/SRS.md](docs/architecture/SRS.md)** - Software Requirement Specification
- **[docs/README.md](docs/README.md)** - Complete documentation index
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development guide
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Detailed installation

### Feature Guides
- **[docs/AI_PR_REVIEWER_GUIDE.md](docs/AI_PR_REVIEWER_GUIDE.md)** - AI code review
- **[docs/LLM_QUICK_START.md](docs/LLM_QUICK_START.md)** - Local LLM setup
- **[docs/SECURITY.md](docs/SECURITY.md)** - Security best practices

## 💻 Development

### Environment Setup
```bash
# Frontend
cd frontend && npm install && cp .env.example .env.local

# Backend
cd backend && python -m venv venv && pip install -r requirements.txt && cp .env.example .env

# Infrastructure
docker-compose up -d
```

### Development Workflow
```bash
# Run tests
npm test                    # Frontend tests
cd backend && pytest        # Backend tests

# Code quality
npm run lint                # Lint all services
npm run format              # Format code

# Database migrations
cd backend && alembic upgrade head
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
# Run all tests
npm test                              # Root: runs all service tests

# Specific test suites
cd services/api-gateway && npm test   # API Gateway (409 tests, 95% coverage)
cd frontend && npm test               # Frontend (64 tests, 100% coverage)
cd backend && pytest                  # Backend (growing coverage)

# With coverage
cd backend && pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### Production Checklist
- [ ] Update environment variables in `.env`
- [ ] Set strong `JWT_SECRET` and `NEXTAUTH_SECRET`
- [ ] Configure production databases
- [ ] Enable HTTPS
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure backups

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

**Development Guidelines**: See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## 📞 Support

- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: Create a GitHub issue
- **Security**: See [docs/SECURITY.md](docs/SECURITY.md)

---

**Version**: 1.0.0 | **License**: MIT | **Last Updated**: February 2026