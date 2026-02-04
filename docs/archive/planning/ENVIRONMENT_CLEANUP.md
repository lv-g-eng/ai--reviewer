# Virtual Environment Cleanup Guide

## Current Situation

Your project has **3 virtual environments**:

1. **`venv/`** (root) - Python 3.13.9 from Anaconda (~1GB)
2. **`.venv/`** (root) - Python 3.13.5 from system Python (~870MB)
3. **`backend/venv/`** - Python 3.13.9 from Anaconda (~665MB)

## Recommendation: Keep Only `backend/venv/`

### Why?

1. **Backend is the only Python component**
   - Main application is in `backend/` directory
   - All Python dependencies are for backend
   - Frontend uses Node.js/npm, not Python

2. **Root virtual environments are redundant**
   - No Python code at root level
   - Scripts in `scripts/` can use backend/venv
   - Duplicate dependencies waste disk space

3. **Docker is the deployment method**
   - Production uses Docker containers
   - Virtual environments only needed for local development
   - One venv is sufficient

## Cleanup Steps

### Option 1: Automated Cleanup (Windows)

```cmd
cleanup_environments.bat
```

### Option 2: Manual Cleanup

#### Windows (PowerShell)
```powershell
# Remove root venv
Remove-Item -Recurse -Force venv

# Remove root .venv
Remove-Item -Recurse -Force .venv

# Keep backend/venv
# (no action needed)
```

#### Linux/Mac
```bash
# Remove root venv
rm -rf venv

# Remove root .venv
rm -rf .venv

# Keep backend/venv
# (no action needed)
```

## After Cleanup

### Using Backend Virtual Environment

```cmd
# Activate backend environment
cd backend
venv\Scripts\activate

# Install/update dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn app.main:app --reload
```

### Using Docker (Recommended)

```cmd
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Disk Space Saved

After cleanup, you'll free up approximately:
- `venv/`: ~1,000 MB
- `.venv/`: ~870 MB
- **Total saved: ~1.87 GB**

Remaining:
- `backend/venv/`: ~665 MB (kept for development)

## Project Structure After Cleanup

```
project/
├── backend/
│   ├── venv/              ← KEEP (Python environment)
│   ├── app/
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── node_modules/      ← Node.js dependencies
│   ├── package.json
│   └── ...
├── scripts/               ← Use backend/venv when needed
├── docker-compose.yml     ← Production deployment
└── ...
```

## Updating .gitignore

The `.gitignore` has been updated to exclude root-level virtual environments:

```gitignore
# Python virtual environments
venv/
.venv/
env/
.env/
ENV/
env.bak/
venv.bak/
```

Note: `backend/venv/` should also be in .gitignore (already excluded by pattern).

## Best Practices

### For Development

1. **Use backend/venv for Python work**
   ```cmd
   cd backend
   venv\Scripts\activate
   ```

2. **Use Docker for full stack**
   ```cmd
   docker-compose up -d
   ```

3. **Use npm for frontend**
   ```cmd
   cd frontend
   npm install
   npm run dev
   ```

### For New Team Members

1. Clone repository
2. Create backend environment:
   ```cmd
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Or use Docker:
   ```cmd
   docker-compose up -d
   ```

## Verification

After cleanup, verify:

```cmd
# Should NOT exist
dir venv
dir .venv

# Should exist
dir backend\venv

# Test backend environment
cd backend
venv\Scripts\activate
python --version
# Should show: Python 3.13.9

pip list
# Should show all backend dependencies
```

## Troubleshooting

### If you accidentally delete backend/venv

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### If scripts fail after cleanup

Update script paths to use backend/venv:

```python
# In scripts, use:
import sys
sys.path.insert(0, '../backend')
```

Or run from backend directory:

```cmd
cd backend
venv\Scripts\activate
python ../scripts/your_script.py
```

## Summary

✅ **Keep:** `backend/venv/` (665 MB)
❌ **Remove:** `venv/` (1,000 MB)
❌ **Remove:** `.venv/` (870 MB)

**Total space saved:** ~1.87 GB

**Recommended approach:** Use Docker for development and deployment, keep backend/venv only for quick Python testing.
