# 🚀 Start Everything - Complete Guide

## Current Status

✅ **Databases Running** (via Docker)
- PostgreSQL on port 5432
- Redis on port 6379
- Neo4j on ports 7474, 7687

❌ **Backend Not Running** (needs to be started)
- Should run on port 8000

❌ **Frontend** (check if running)
- Should run on port 3000

## 🎯 Quick Start (3 Steps)

### Step 1: Start Backend (Port 8000)

**Option A: Double-click the batch file**
```
START_BACKEND_NOW.bat
```

**Option B: Manual command**
```cmd
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Password security configured: bcrypt with 12 rounds
✅ All database connections initialized
✅ LLM service initialized
INFO:     Application startup complete.
```

### Step 2: Verify Backend

Open browser: **http://localhost:8000/health**

Should see:
```json
{
  "status": "healthy",
  "service": "ai-code-review-api",
  "version": "1.0.0"
}
```

### Step 3: Start Frontend (if not running)

Open **new terminal**:
```cmd
cd frontend
npm run dev
```

Then open: **http://localhost:3000**

## ✅ Verification Checklist

### 1. Check All Services

```cmd
# Check Docker services
docker ps

# Should see:
# - postgres (5432)
# - redis (6379)
# - neo4j (7474, 7687)
# - api-gateway (3000)
# - auth-service (3001)
# - code-review-engine (3002)
# - architecture-analyzer (3003)
# - agentic-ai (3004)
# - project-manager (3005)
```

### 2. Test Backend Endpoints

```cmd
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# API documentation
# Open: http://localhost:8000/docs
```

### 3. Test Frontend

Open browser: **http://localhost:3000**

The "Backend Not Available" error should be **GONE** ✅

## 🔧 If Backend Won't Start

### Error: "Module not found"

```cmd
cd backend
pip install -r requirements.txt
```

### Error: "Connection refused" to database

```cmd
# Check if databases are running
docker ps | findstr postgres

# If not running, start them
docker-compose up -d postgres redis neo4j

# Wait 15 seconds
timeout /t 15
```

### Error: "Port 8000 already in use"

```cmd
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual ID)
taskkill /PID <PID> /F
```

### Error: "Python not found"

Install Python 3.11 or 3.12 from: https://www.python.org/downloads/

## 📊 Service Architecture

```
Frontend (Next.js)          → http://localhost:3000
    ↓
Backend (FastAPI)           → http://localhost:8000
    ↓
Databases:
    - PostgreSQL            → localhost:5432
    - Redis                 → localhost:6379
    - Neo4j                 → localhost:7474, 7687

Microservices:
    - API Gateway           → localhost:3000 (Docker)
    - Auth Service          → localhost:3001 (Docker)
    - Code Review Engine    → localhost:3002 (Docker)
    - Architecture Analyzer → localhost:3003 (Docker)
    - Agentic AI            → localhost:3004 (Docker)
    - Project Manager       → localhost:3005 (Docker)
```

## 🎯 Complete Startup Sequence

### Terminal 1: Databases (Already Running ✅)
```cmd
docker-compose up -d
```

### Terminal 2: Backend
```cmd
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 3: Frontend (if needed)
```cmd
cd frontend
npm run dev
```

## 🔍 Troubleshooting

### Frontend shows "Backend Not Available"

**Check 1: Is backend running?**
```cmd
curl http://localhost:8000/health
```

**Check 2: Is backend on correct port?**
Backend should be on port 8000, not 3000

**Check 3: Frontend configuration**
Check `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend starts but crashes immediately

**Check logs in terminal where backend is running**

Common issues:
1. Database connection failed → Check if Docker containers are running
2. Import error → Run `pip install -r requirements.txt`
3. Port in use → Kill process on port 8000

### Can't access http://localhost:8000

**Check if backend is actually running:**
```cmd
# Windows
netstat -ano | findstr :8000

# Should show LISTENING on port 8000
```

**Check firewall:**
Windows Firewall might be blocking port 8000

## 📝 Quick Commands Reference

```cmd
# Start databases
docker-compose up -d

# Start backend
cd backend && python -m uvicorn app.main:app --reload

# Start frontend
cd frontend && npm run dev

# Check what's running
docker ps
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Stop backend
Ctrl+C (in backend terminal)

# Stop databases
docker-compose down

# Restart everything
docker-compose restart
```

## ✅ Success Indicators

When everything is working:

1. ✅ Backend terminal shows: `Application startup complete`
2. ✅ http://localhost:8000/health returns JSON
3. ✅ http://localhost:8000/docs shows Swagger UI
4. ✅ Frontend loads without "Backend Not Available" error
5. ✅ Can register/login on frontend
6. ✅ Dashboard shows data

## 🎉 You're Ready!

Once you see:
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ No "Backend Not Available" error

Your application is fully operational!

## 📚 Additional Resources

- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health
- **Neo4j Browser**: http://localhost:7474
- **Project Guide**: `PROJECT_GUIDE.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`

---

**Quick Start Command:**
```cmd
START_BACKEND_NOW.bat
```

Then open: http://localhost:3000
