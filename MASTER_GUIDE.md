# AI-Based Quality Check Platform - Master Guide

> **Single Source of Truth** - Start here for everything about this project

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Node.js 18+, Python 3.11+, Docker Desktop
- PostgreSQL, Redis, Neo4j (via Docker or local)

### Start the Platform
```bash
# 1. Start databases
START_ALL_SERVICES.bat

# 2. Start backend (in new terminal)
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Start frontend (in new terminal)
cd frontend
npm run dev
```

Access: http://localhost:3000

## 📚 Documentation Hub

### Essential Guides
| Guide | Purpose | When to Use |
|-------|---------|-------------|
| [QUICK_START.md](QUICK_START.md) | Fast setup | First time setup |
| [PROJECT_GUIDE.md](PROJECT_GUIDE.md) | Complete overview | Understanding architecture |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Fix issues | When errors occur |
| [docs/](docs/) | All documentation | Detailed information |

### By Task
- **Setup & Installation** → [QUICK_START.md](QUICK_START.md)
- **Development** → [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **LLM Integration** → [docs/LLM_QUICK_START.md](docs/LLM_QUICK_START.md)
- **Security** → [docs/SECURITY.md](docs/SECURITY.md)
- **Deployment** → [PROJECT_GUIDE.md](PROJECT_GUIDE.md)

## 🏗️ Project Architecture

### Core Services
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

### Technology Stack
- **Frontend:** Next.js 14, React 18, TailwindCSS, NextAuth
- **Backend:** FastAPI, SQLAlchemy, Celery, Neo4j
- **Databases:** PostgreSQL, Redis, Neo4j
- **AI/ML:** LLaMA.cpp, Qwen models, Tree-sitter parsers

## 📂 Project Structure

```
├── frontend/              # Next.js frontend application
├── backend/              # FastAPI backend application
├── services/             # Microservices
│   ├── api-gateway/     # API Gateway service
│   ├── llm-service/     # LLM integration service
│   └── [others]/        # Additional services
├── docs/                # All documentation
├── scripts/             # Utility scripts
└── monitoring/          # Prometheus, Grafana configs
```

## 🔧 Common Tasks

### Development
```bash
# Backend development
cd backend
python -m uvicorn app.main:app --reload

# Frontend development
cd frontend
npm run dev

# Run tests
cd backend && pytest
cd frontend && npm test
```

### Database Management
```bash
# Start all databases
START_ALL_SERVICES.bat

# Stop all databases
STOP_ALL_SERVICES.bat

# Create database
CREATE_DATABASE.bat
```

### LLM Setup
```bash
# Windows
scripts\setup-llm.bat

# Linux/Mac
./scripts/setup-llm.sh
```

## 🐛 Troubleshooting

### Common Issues

**Frontend ChunkLoadError**
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

**Backend Won't Start**
- Check PostgreSQL is running: `psql -U postgres -h localhost`
- Check Redis: `redis-cli ping`
- Check Neo4j: Visit http://localhost:7474
- Review: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Database Connection Issues**
- Verify .env files in root and backend/
- Check database services are running
- Verify credentials match

## 📋 File Organization

### Documentation Files (.md)
- **Root Level:** Quick start, project guide, troubleshooting
- **docs/:** Detailed guides, implementation reports
- **Service-specific:** In respective service directories

### Configuration Files
- **.env:** Root and backend environment variables
- **docker-compose.yml:** Service orchestration
- **package.json:** Frontend dependencies
- **requirements.txt:** Backend dependencies

### Scripts (.bat, .sh)
- **scripts/:** Utility scripts (setup, cleanup, testing)
- **Root level:** Service startup scripts

## 🔐 Security

### Environment Variables
Never commit:
- `.env` files
- API keys
- Database passwords
- JWT secrets

### Security Guides
- [SECURITY.md](docs/SECURITY.md) - Security best practices
- [SECRETS_MIGRATION_GUIDE.md](docs/SECRETS_MIGRATION_GUIDE.md) - Secrets management

## 🚢 Deployment

### Production Checklist
- [ ] Update all .env files with production values
- [ ] Set strong NEXTAUTH_SECRET
- [ ] Configure production databases
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review security settings

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001
- **Neo4j Browser:** http://localhost:7474

## 🤝 Contributing

1. Follow existing code style
2. Write tests for new features
3. Update documentation
4. Test locally before committing
5. Never commit secrets

## 📞 Getting Help

1. **Check Documentation**
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - [docs/](docs/)
   - Service-specific READMEs

2. **Review Logs**
   - Backend: `backend/app.log`
   - Frontend: Browser console
   - Services: `services/*/logs/`

3. **Check Implementation Summaries**
   - `backend/TASK_*.md` files
   - Service documentation

## 📈 Project Status

- ✅ Core backend API
- ✅ Frontend UI
- ✅ Authentication (NextAuth + JWT)
- ✅ Database integration (PostgreSQL, Neo4j, Redis)
- ✅ API Gateway with circuit breaker
- ✅ LLM integration
- ✅ AI PR Reviewer
- 🟡 Production deployment (in progress)

## 🗂️ Archived Documentation

Older documentation has been consolidated. See:
- [DOCUMENTATION_CLEANUP_SUMMARY.md](DOCUMENTATION_CLEANUP_SUMMARY.md)
- Individual service docs in `services/*/docs/`

---

**Last Updated:** January 21, 2026
**Version:** 1.0.0

For detailed information, see [PROJECT_GUIDE.md](PROJECT_GUIDE.md) and [docs/](docs/)
