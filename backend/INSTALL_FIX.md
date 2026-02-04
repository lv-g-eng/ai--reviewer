# Backend Installation Fix

## Problem
`asyncpg==0.29.0` fails to build on Python 3.13 due to C extension compatibility issues.

## Solutions

### Option 1: Use Python 3.11 or 3.12 (Recommended)

```bash
# Check your Python version
python --version

# If you have Python 3.13, install Python 3.11 or 3.12
# Download from: https://www.python.org/downloads/
```

Then create a virtual environment with the correct Python version:

```bash
cd backend

# Create venv with Python 3.11/3.12
py -3.11 -m venv .venv
# or
py -3.12 -m venv .venv

# Activate
.venv\Scripts\activate

# Install dependencies
pip install --no-cache-dir -r requirements.txt
```

### Option 2: Use Pre-built Wheel (Quick Fix)

```bash
cd backend

# Install asyncpg from pre-built wheel first
pip install asyncpg --only-binary :all:

# Then install rest of requirements
pip install --no-cache-dir -r requirements.txt
```

### Option 3: Skip asyncpg (Temporary)

If you don't need PostgreSQL async features immediately:

```bash
cd backend

# Install everything except asyncpg
pip install --no-cache-dir -r requirements.txt --ignore-installed asyncpg || true

# Use psycopg instead (already in requirements)
# The app will work with psycopg[binary] which is already installed
```

### Option 4: Update asyncpg Version

Edit `backend/requirements.txt` and change:
```
asyncpg==0.29.0
```
to:
```
asyncpg>=0.30.0  # Newer version with Python 3.13 support
```

Then install:
```bash
pip install --no-cache-dir -r requirements.txt
```

## Recommended Approach

**For Development**: Use Python 3.11 or 3.12 (most stable)

```bash
# 1. Install Python 3.11 or 3.12
# 2. Create venv
py -3.11 -m venv backend/.venv

# 3. Activate
backend\.venv\Scripts\activate

# 4. Install
pip install --no-cache-dir -r backend/requirements.txt
```

**For Quick Testing**: Skip asyncpg, use psycopg

```bash
# The app already has psycopg[binary] which works fine
# Just start the backend without asyncpg
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Verification

After installation, verify:

```bash
python -c "import asyncpg; print('asyncpg OK')"
# or
python -c "import psycopg; print('psycopg OK')"
```

## Why This Happens

- Python 3.13 changed internal C API
- `asyncpg 0.29.0` was built for Python 3.12 and earlier
- C extensions need to be recompiled for Python 3.13
- Pre-built wheels may not be available yet

## Long-term Fix

Update `requirements.txt` to use Python 3.11 or 3.12 compatible versions, or wait for asyncpg to release Python 3.13 compatible version.
