# 🔧 Backend Startup - Quick Fix

## The Issue

The backend server needs to connect to PostgreSQL, Redis, and Neo4j databases. The connection is failing because of password mismatch.

## ✅ Quick Fix (2 Minutes)

### Step 1: Update Backend Environment

The `backend/.env` file has been updated with the correct passwords:
- PostgreSQL password: `postgres` (not `password`)
- Redis password: `` (empty, no password)

### Step 2: Start Backend Server

Open a **new terminal** and run:

```cmd
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
✅ All database connections initialized
✅ LLM service initialized
```

### Step 3: Verify It's Working

Open browser: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "service": "ai-code-review-api",
  "version": "1.0.0"
}
```

## Alternative: Use the Batch Script

Double-click: `start-backend-local.bat`

Or run from command line:
```cmd
start-backend-local.bat
```

## If You Still Get Errors

### Error: "Connection refused" to PostgreSQL

**Check if PostgreSQL is running:**
```cmd
docker ps | findstr postgres
```

**If not running, start it:**
```cmd
docker-compose up -d postgres
```

**Wait 10 seconds for it to initialize:**
```cmd
timeout /t 10
```

### Error: "Connection refused" to Redis

**Start Redis:**
```cmd
docker-compose up -d redis
```

### Error: "Connection refused" to Neo4j

**Start Neo4j:**
```cmd
docker-compose up -d neo4j
```

**Wait 30 seconds for Neo4j to initialize:**
```cmd
timeout /t 30
```

### Error: "Module not found"

**Install dependencies:**
```cmd
cd backend
pip install -r requirements.txt
```

## Verify All Services Are Running

```cmd
docker ps
```

You should see:
- ✅ postgres (port 5432)
- ✅ redis (port 6379)
- ✅ neo4j (ports 7474, 7687)

## Test Backend Endpoints

### 1. Health Check
```cmd
curl http://localhost:8000/health
```

### 2. Root Endpoint
```cmd
curl http://localhost:8000/
```

### 3. API Documentation
Open browser: http://localhost:8000/docs

## Frontend Connection

Once the backend is running, your frontend will automatically connect.

The frontend is configured to use: `http://localhost:8000`

Check `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Complete Startup Sequence

```cmd
# 1. Start databases (if not running)
docker-compose up -d postgres redis neo4j

# 2. Wait for databases to initialize
timeout /t 15

# 3. Start backend (in new terminal)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Verify backend is running
curl http://localhost:8000/health

# 5. Start frontend (in another new terminal)
cd frontend
npm run dev

# 6. Access application
# Open browser: http://localhost:3000
```

## Troubleshooting Commands

```cmd
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process on port 8000 (if needed)
# Replace <PID> with actual process ID from above command
taskkill /PID <PID> /F

# Check Docker containers
docker ps

# View backend logs (if running in Docker)
docker logs backend

# Restart databases
docker-compose restart postgres redis neo4j

# Check Python version
python --version

# Test database connection
docker exec -it ai-based-quality-check-on-project-code-and-architecture-postgres-1 psql -U postgres -d ai_code_review -c "SELECT 1;"
```

## Expected Output When Backend Starts

```
INFO:     Will watch for changes in these directories: ['D:\\Desktop\\AI-Based-Quality-Check-On-Project-Code-And-Architecture\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
✅ Password security configured: bcrypt with 12 rounds
⚠️  Security warnings:
   - No external API keys configured - limited functionality
✅ All database connections initialized
✅ LLM service initialized (models will load on first use)
INFO:     Application startup complete.
```

## Success Indicators

✅ Backend running on http://localhost:8000
✅ Health endpoint responds: http://localhost:8000/health
✅ API docs available: http://localhost:8000/docs
✅ Frontend can connect (no "Backend Not Available" error)

## Need More Help?

1. Check `START_BACKEND_GUIDE.md` for detailed instructions
2. Check `TROUBLESHOOTING.md` for common issues
3. View logs in the terminal where backend is running
4. Check Docker logs: `docker logs <container-name>`

---

**Quick Start Command:**
```cmd
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

That's it! Your backend should now be running and accessible.
