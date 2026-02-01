# Project File Index

**Generated**: January 21, 2026  
**Status**: Organized and Updated

---

## 📚 Documentation

### Root Level (Essential)
- [README.md](README.md) - Project overview and quick links
- [QUICK_START.md](QUICK_START.md) - Fast setup guide (5 minutes)
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command cheat sheet
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving guide

### Documentation Hub
- [docs/README.md](docs/README.md) - **Complete documentation index**

### Key Documentation Files
- [docs/npm-management.md](docs/npm-management.md) - NPM cache, audit, updates
- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Detailed installation
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - Development setup
- [docs/SECURITY.md](docs/SECURITY.md) - Security best practices
- [docs/AI_PR_REVIEWER_GUIDE.md](docs/AI_PR_REVIEWER_GUIDE.md) - AI code review
- [docs/AI_SELF_HEALING_GUIDE.md](docs/AI_SELF_HEALING_GUIDE.md) - Self-healing system
- [docs/LLM_INTEGRATION_GUIDE.md](docs/LLM_INTEGRATION_GUIDE.md) - LLM integration
- [docs/LLM_QUICK_START.md](docs/LLM_QUICK_START.md) - Fast LLM setup

---

## 🔧 Scripts

### Startup Scripts (Root Level)
- `START_ALL_SERVICES.bat` - Start all infrastructure services
- `STOP_ALL_SERVICES.bat` - Stop all services
- `START_NEO4J.bat` - Start Neo4j database
- `START_REDIS.bat` - Start Redis cache
- `CREATE_DATABASE.bat` - Initialize database

### Setup Scripts (scripts/)
- `setup-llm.bat` / `setup-llm.sh` - LLM environment setup
- `setup-dev.sh` - Development environment setup

### Maintenance Scripts (scripts/)
- `clean-npm-cache.bat` / `clean-npm-cache.sh` - Clean npm cache
- `verify-path-clean.bat` / `verify-path-clean.sh` - Verify clean paths
- `organize_project.py` - Project file organization
- `consolidate_docs.py` - Documentation consolidation

### Security Scripts (scripts/)
- `remove_git_secrets.sh` - Remove secrets from git history
- `security_compliance_report.py` - Generate security reports

### Utility Scripts (scripts/)
- `ai_self_healing.py` - AI-powered error fixing
- `detect_code_duplication.py` - Find duplicate code
- `fix_frontend_build.bat` - Fix frontend build issues
- `generate_requirements.py` - Generate Python requirements
- `scan_file_paths.py` - Scan for path issues
- `test-llm-integration.py` - Test LLM integration
- `validate_optimization.py` - Validate optimizations
- `verify-frontend-env.sh` / `verify-frontend-env-enhanced.sh` - Verify frontend env

---

## 🏗️ Services

### Frontend
- **Location**: `frontend/`
- **Tech**: Next.js 14, React 18, TypeScript
- **Docs**: `frontend/README.md`
- **Status**: ✅ Complete (100%)

### Backend
- **Location**: `backend/`
- **Tech**: FastAPI, Python 3.11+
- **Docs**: `backend/README.md`
- **Status**: 🟡 In Progress (25%)

### Microservices

#### API Gateway
- **Location**: `services/api-gateway/`
- **Tech**: Node.js, Express
- **Docs**: `services/api-gateway/README.md`
- **Status**: ✅ Complete (100%)

#### LLM Service
- **Location**: `services/llm-service/`
- **Tech**: Python, LLaMA.cpp
- **Docs**: `services/llm-service/README.md`
- **Status**: ✅ Complete

#### Other Services
- `services/agentic-ai/` - AI reasoning service
- `services/architecture-analyzer/` - Code analysis
- `services/auth-service/` - Authentication
- `services/code-review-engine/` - Code review
- `services/project-manager/` - Project management

---

## 📦 Configuration Files

### Root Level
- `docker-compose.yml` - Development services
- `docker-compose.prod.yml` - Production services
- `.env.example` - Environment template
- `package.json` - Root package config
- `tsconfig.json` - TypeScript config
- `.eslintrc.js` - ESLint config
- `.prettierrc` - Prettier config
- `.gitignore` - Git ignore rules

### Frontend
- `frontend/.env.example` - Frontend env template
- `frontend/package.json` - Frontend dependencies
- `frontend/tsconfig.json` - Frontend TypeScript
- `frontend/next.config.mjs` - Next.js config
- `frontend/tailwind.config.ts` - Tailwind config

### Backend
- `backend/.env` - Backend environment
- `backend/requirements.txt` - Python dependencies
- `backend/pyproject.toml` - Python project config
- `backend/alembic.ini` - Database migrations

---

## 🗂️ Directory Structure

```
├── README.md                       # Main entry point
├── QUICK_START.md                  # Fast setup
├── QUICK_REFERENCE.md              # Command reference
├── TROUBLESHOOTING.md              # Problem solving
│
├── docs/                           # Documentation hub
│   ├── README.md                   # Documentation index
│   ├── npm-management.md           # NPM guide (NEW)
│   ├── INSTALLATION.md
│   ├── DEVELOPMENT.md
│   ├── SECURITY.md
│   ├── AI_PR_REVIEWER_GUIDE.md
│   ├── AI_SELF_HEALING_GUIDE.md
│   ├── LLM_INTEGRATION_GUIDE.md
│   ├── LLM_QUICK_START.md
│   └── archive/                    # Archived docs
│
├── scripts/                        # Utility scripts
│   ├── setup-llm.*
│   ├── clean-npm-cache.*
│   ├── verify-path-clean.*
│   ├── organize_project.py
│   └── ...
│
├── frontend/                       # Next.js frontend
├── backend/                        # FastAPI backend
├── services/                       # Microservices
│   ├── api-gateway/
│   ├── llm-service/
│   └── ...
│
├── monitoring/                     # Prometheus, Grafana
├── k8s/                           # Kubernetes configs
├── nginx/                         # Nginx configs
├── models/                        # LLM models
└── archive/                       # Archived files
    └── 2026-01-21/
```

---

## 🗄️ Archived Files

Archived files are stored in `archive/` with date stamps:

### archive/2026-01-21/
- **documentation/** - Temporary/outdated docs
- **scripts/** - Old/duplicate scripts
- **config/** - Old configuration files

### docs/archive/
- **operations/** - Old NPM guides (replaced by npm-management.md)
- **security-reports/** - Historical security reports

See `archive/*/INDEX.md` for details on archived content.

---

## 📊 Project Statistics

**Documentation:**
- Root level: 4 essential files
- docs/: 15+ organized guides
- Service-specific: Multiple READMEs

**Scripts:**
- Startup: 5 batch files
- Utility: 15+ scripts
- Well-organized by purpose

**Services:**
- Frontend: 100% complete
- Backend: 25% complete
- Microservices: 2/6 complete

---

## 🔍 Quick Find

### By Purpose

**Setup & Installation:**
- QUICK_START.md
- docs/INSTALLATION.md
- docs/DEVELOPMENT.md

**Daily Development:**
- QUICK_REFERENCE.md
- docs/npm-management.md
- TROUBLESHOOTING.md

**Features:**
- docs/AI_PR_REVIEWER_GUIDE.md
- docs/AI_SELF_HEALING_GUIDE.md
- docs/LLM_QUICK_START.md

**Security:**
- docs/SECURITY.md
- docs/SECRETS_MIGRATION_GUIDE.md
- docs/SECURITY_COMPLIANCE_IMPLEMENTATION.md

**Operations:**
- docs/npm-management.md
- docs/PHASE_3_IMPLEMENTATION.md

---

## 📞 Navigation Tips

1. **Start with README.md** - Main project overview
2. **Use docs/README.md** - Complete documentation index
3. **Check QUICK_REFERENCE.md** - Common commands
4. **Search PROJECT_INDEX.md** - Find specific files (this file)

---

**Last Updated**: January 21, 2026  
**Maintained By**: Project Team  
**Status**: ✅ Organized and Current
