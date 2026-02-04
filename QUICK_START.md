# 🚀 Quick Start Guide

**Time to Running**: 5-10 minutes  
**Prerequisites**: Node.js 18+, Python 3.11/3.12, Docker Desktop

---

## ⚡ Fast Start (3 Commands)

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis neo4j

# 2. Start backend (new terminal)
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Start frontend (new terminal)
cd frontend && npm run dev
```

**Access**: 
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📋 Detailed Setup

### Prerequisites

**Python Version**: Use Python 3.11 or 3.12 (Python 3.13 has compatibility issues with asyncpg)

```bash
# Check your Python version
python --version

# If you have Python 3.13, install Python 3.11 or 3.12
# Download from: https://www.python.org/downloads/
```

### Step 1: Start Infrastructure (30 seconds)

```bash
# Start databases
docker-compose up -d postgres redis neo4j

# Wait for services to be ready (~15 seconds)
docker-compose ps
```

### Step 2: Setup Backend (2 minutes)

```bash
cd backend

# Create virtual environment with Python 3.11 or 3.12
py -3.11 -m venv venv
# or: py -3.12 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your values (see Environment Variables section)

# Run database migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Note**: If you get `asyncpg` build errors, see [backend/INSTALL_FIX.md](backend/INSTALL_FIX.md) for solutions.

### Step 3: Setup Frontend (2 minutes)

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your values (see Environment Variables section)

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

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

**Production**: Generate secure secrets:
```bash
# JWT Secret (32 characters)
openssl rand -hex 32

# NextAuth Secret (base64)
openssl rand -base64 32
```

---

## ✅ Verify Installation

```bash
# Check services are running
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs  # or visit in browser

# Check frontend
open http://localhost:3000  # or visit in browser
```

---

## 🛑 Stop Services

```bash
# Stop backend/frontend: Ctrl+C in their terminals

# Stop infrastructure
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 🚨 Troubleshooting

### Python 3.13 Compatibility Issue

**Error**: `asyncpg` fails to build with compilation errors

**Solution**: Use Python 3.11 or 3.12

```bash
# Install Python 3.11 or 3.12 from python.org
# Then create venv with correct version:
py -3.11 -m venv backend/venv
backend\venv\Scripts\activate
pip install --no-cache-dir -r backend/requirements.txt
```

See [backend/INSTALL_FIX.md](backend/INSTALL_FIX.md) for detailed solutions.

### Backend Won't Start

```bash
# Check port 8000 is not in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Check logs
cd backend
tail -f app.log

# Verify database connection
docker-compose ps postgres
```

### Frontend Can't Connect to Backend

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check environment variables
cat frontend/.env.local

# Check CORS settings in backend
```

### Database Connection Failed

```bash
# Check services are running
docker-compose ps

# Restart services
docker-compose restart postgres redis neo4j

# Check logs
docker-compose logs postgres
```

### Tests Failing

```bash
# Frontend
cd frontend
rm -rf node_modules .next
npm install
npm test

# Backend
cd backend
pip install -r requirements.txt
pytest --cache-clear
```

### Clean Orphan Containers

If you see warnings about orphan containers:
```bash
docker-compose down --remove-orphans
docker-compose up -d postgres redis neo4j
```

---

## 📚 Next Steps

### For Developers
1. **Read the docs**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
2. **Explore the API**: http://localhost:8000/docs
3. **Run tests**: `npm test` (frontend) or `pytest` (backend)
4. **Check code quality**: `npm run lint`

### For Project Managers
1. **Review architecture**: [README.md](README.md#architecture)
2. **Check project status**: [README.md](README.md#project-status)
3. **View documentation**: [docs/README.md](docs/README.md)

### Common Tasks
- **Add a feature**: See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **Run tests**: See [Testing](#testing) section
- **Deploy**: See [README.md](README.md#deployment)
- **Troubleshoot**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📞 Getting Help

1. **Check documentation**: [docs/README.md](docs/README.md)
2. **Common issues**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Quick reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. **Create an issue**: GitHub Issues

---

## ⏱️ Performance Notes

- Infrastructure starts in ~15 seconds
- Backend starts in ~15-20 seconds
- Frontend starts in ~10-15 seconds
- **Total time to running**: ~45-60 seconds

**Optimization Tips**:
- Use `--workers 1` for faster backend startup (increase for production)
- Use `--log-level warning` to reduce startup overhead
- Keep Docker Desktop running for faster container starts

---

**🎉 You're all set! Happy coding!**
