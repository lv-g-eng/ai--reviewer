# Quick Start Guide

## Prerequisites Setup

You have the following installed:
- ✅ PostgreSQL at `D:\PostgreSQL\`
- ✅ Redis at `D:\redis-5.0.4\`
- ✅ Neo4j at `D:\neo4j-community-2025.12.1-windows\`
- ✅ Python (Anaconda)
- ✅ Node.js

## Step 1: Configure Database Credentials

### PostgreSQL
1. Open `backend\.env`
2. Update the PostgreSQL password:
   ```
   POSTGRES_PASSWORD=your_actual_password
   ```

### Neo4j
1. First time setup - set Neo4j password:
   ```cmd
   cd D:\neo4j-community-2025.12.1-windows\neo4j-community-2025.12.1\bin
   neo4j-admin set-initial-password your_password
   ```
2. Update `backend\.env`:
   ```
   NEO4J_PASSWORD=your_password
   ```

## Step 2: Create Database

1. Open pgAdmin or use psql:
   ```sql
   CREATE DATABASE ai_code_review;
   ```

## Step 3: Start Everything

### Option A: Start All at Once (Recommended)
```cmd
START_ALL_SERVICES.bat
```

This will:
- Start PostgreSQL (if not running)
- Start Redis
- Start Neo4j
- Wait for services to initialize
- Start the backend server

### Option B: Start Services Individually

**Terminal 1 - Redis:**
```cmd
START_REDIS.bat
```

**Terminal 2 - Neo4j:**
```cmd
START_NEO4J.bat
```

**Terminal 3 - Backend:**
```cmd
START_BACKEND_SIMPLE.bat
```

**Terminal 4 - Frontend:**
```cmd
cd frontend
npm run dev
```

## Step 4: Verify Services

Open these URLs in your browser:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health
- **Neo4j Browser:** http://localhost:7474

## Step 5: Stop Services

```cmd
STOP_ALL_SERVICES.bat
```

Or press `Ctrl+C` in each terminal window.

## Troubleshooting

### Backend won't start
- Check if databases are running
- Verify credentials in `backend\.env`
- Check logs for specific errors

### PostgreSQL connection failed
- Verify PostgreSQL is running
- Check password in `backend\.env`
- Ensure database `ai_code_review` exists

### Neo4j connection failed
- Run initial password setup command
- Update password in `backend\.env`
- Check Neo4j is running at http://localhost:7474

### Redis connection failed
- Check if Redis is running: `tasklist | find "redis"`
- Restart Redis: `START_REDIS.bat`

## Quick Commands

**Check if services are running:**
```cmd
tasklist | find "postgres"
tasklist | find "redis"
tasklist | find "java"
```

**Backend only (no databases):**
```cmd
START_BACKEND_SIMPLE.bat
```

**Full stack:**
```cmd
START_ALL_SERVICES.bat
```

## Next Steps

1. Create a user account at http://localhost:3000/register
2. Explore the API docs at http://localhost:8000/docs
3. Check the project dashboard
