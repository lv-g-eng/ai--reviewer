# 🚀 Backend Server Startup Guide

## Quick Start

### Option 1: Using the Batch Script (Easiest)
```cmd
start-backend-local.bat
```

### Option 2: Manual Start
```cmd
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Docker (Recommended for Production)
```cmd
docker-compose up backend
```

## Prerequisites

Before starting the backend, ensure these services are running:

### Check Services
```cmd
docker ps
```

You should see:
- ✅ postgres (port 5432)
- ✅ redis (port 6379)
- ✅ neo4j (ports 7474, 7687)

### Start Services if Not Running
```cmd
docker-compose up -d postgres redis neo4j
```

## Troubleshooting

### Error: "Module not found"
```cmd
cd backend
pip install -r requirements.txt
```

### Error: "Connection refused" to database
```cmd
# Check if databases are running
docker ps

# Start databases
docker-compose up -d postgres redis neo4j

# Wait 10 seconds for databases to initialize
timeout /t 10
```

### Error: "Port 8000 already in use"
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Error: "Python not found"
```cmd
# Check Python installation
python --version

# If not installed, download from python.org
# Recommended: Python 3.11 or 3.12
```

## Verify Backend is Running

### 1. Check Health Endpoint
Open browser: http://localhost:8000/health

Or use curl:
```cmd
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ai-code-review-api",
  "version": "1.0.0"
}
```

### 2. Check API Documentation
Open browser: http://localhost:8000/docs

You should see the Swagger UI with all API endpoints.

### 3. Check Root Endpoint
```cmd
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "AI Code Review Platform API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## Environment Configuration

The backend uses `backend/.env` for configuration. Key settings:

```env
# Database connections
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_code_review
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=password

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Security
JWT_SECRET=your-secret-key-here

# LLM (Optional)
MODELS_DIR=models
LLM_ENABLED=true
LLM_GPU_LAYERS=35
```

## Common Issues

### Issue: Backend starts but frontend can't connect

**Solution 1: Check CORS settings**
In `backend/app/core/config.py`, ensure:
```python
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:3001",
]
```

**Solution 2: Check frontend API URL**
In `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Issue: Database connection errors

**Check database status:**
```cmd
docker ps | findstr postgres
docker ps | findstr redis
docker ps | findstr neo4j
```

**Restart databases:**
```cmd
docker-compose restart postgres redis neo4j
```

**Check database logs:**
```cmd
docker logs ai-based-quality-check-on-project-code-and-architecture-postgres-1
```

### Issue: Import errors

**Reinstall dependencies:**
```cmd
cd backend
pip install --upgrade -r requirements.txt
```

**Check Python version:**
```cmd
python --version
```
Should be Python 3.11 or 3.12

## Development Tips

### Auto-reload on Code Changes
The `--reload` flag enables auto-reload:
```cmd
python -m uvicorn app.main:app --reload
```

### Debug Mode
Set environment variable:
```cmd
set LOG_LEVEL=DEBUG
python -m uvicorn app.main:app --reload
```

### Run Tests
```cmd
cd backend
pytest
```

### Check Code Quality
```cmd
cd backend
pylint app/
black app/
mypy app/
```

## Next Steps

Once the backend is running:

1. ✅ Verify health: http://localhost:8000/health
2. ✅ Check API docs: http://localhost:8000/docs
3. ✅ Test authentication: http://localhost:8000/api/v1/auth/register
4. ✅ Start frontend: `cd frontend && npm run dev`
5. ✅ Access app: http://localhost:3000

## Need Help?

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Logs**: Check terminal output
- **Database Status**: `docker ps`
- **Project Guide**: See `PROJECT_GUIDE.md`

## Quick Commands Reference

```cmd
# Start backend
cd backend && python -m uvicorn app.main:app --reload

# Start with specific port
cd backend && python -m uvicorn app.main:app --port 8000

# Start databases
docker-compose up -d postgres redis neo4j

# Check services
docker ps

# View logs
docker logs <container-name>

# Stop backend
Ctrl+C (in terminal)

# Stop databases
docker-compose down
```

---

**Status**: Backend should now be accessible at http://localhost:8000
