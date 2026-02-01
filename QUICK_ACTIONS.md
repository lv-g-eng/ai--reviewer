# Quick Actions - What to Do Next

## 🎯 Immediate Actions (5 minutes)

### 1. Clean Up Virtual Environments (Recommended)
```cmd
cleanup_environments.bat
```
**Result:** Frees up ~1.87 GB of disk space

### 2. Generate Secure Keys
```cmd
# Open PowerShell and run:
# For JWT Secret
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# For NextAuth Secret
$bytes = New-Object byte[] 32
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

### 3. Update .env File
Open `.env` and update these values:
```bash
POSTGRES_PASSWORD=your_secure_password_here
JWT_SECRET=paste_generated_jwt_secret_here
GITHUB_TOKEN=ghp_your_github_token_here
```

## 🚀 Start the System (2 minutes)

```cmd
# Start all services
docker-compose up -d

# Wait 30 seconds for services to start

# Run database migration
cd backend
alembic upgrade head
cd ..
```

## ✅ Verify Everything Works (3 minutes)

```cmd
# Check services are running
docker-compose ps

# Check API health
curl http://localhost:8000/health

# View API documentation
start http://localhost:8000/docs
```

## 🧪 Test Repository Management (5 minutes)

### Step 1: Create a User
```cmd
curl -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@yourdomain.com\",\"password\":\"SecurePass123!\",\"full_name\":\"Admin User\"}"
```

### Step 2: Login and Get Token
```cmd
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@yourdomain.com\",\"password\":\"SecurePass123!\"}"
```
**Copy the `access_token` from the response**

### Step 3: Validate a Repository
```cmd
curl -X GET "http://localhost:8000/api/v1/repositories/validate?repository_url=https://github.com/facebook/react.git" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Step 4: Add a Repository
```cmd
curl -X POST http://localhost:8000/api/v1/repositories ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -H "Content-Type: application/json" ^
  -d "{\"repository_url\":\"https://github.com/facebook/react.git\",\"branch\":\"main\",\"description\":\"React library\"}"
```

## 📚 Documentation

| Document | Purpose | Time to Read |
|----------|---------|--------------|
| [FINAL_SUMMARY.md](FINAL_SUMMARY.md) | Complete overview | 5 min |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Detailed setup | 15 min |
| [QUICK_REFERENCE_REPOSITORY.md](QUICK_REFERENCE_REPOSITORY.md) | Command reference | 2 min |
| [docs/REPOSITORY_MANAGEMENT.md](docs/REPOSITORY_MANAGEMENT.md) | Full guide | 30 min |

## 🔧 Troubleshooting

### Services Won't Start
```cmd
# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

### Migration Fails
```cmd
# Check database is running
docker-compose ps postgres

# Try again
cd backend
alembic upgrade head
```

### Can't Connect to API
```cmd
# Check if backend is running
docker-compose ps backend

# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

## 📞 Quick Help

**Problem:** Environment cleanup failed
**Solution:** Run manually: `rmdir /s /q venv` and `rmdir /s /q .venv`

**Problem:** GitHub token not working
**Solution:** Get new token at https://github.com/settings/tokens with `repo` scope

**Problem:** Database connection failed
**Solution:** Check `.env` has correct `POSTGRES_PASSWORD`

**Problem:** API returns 401 Unauthorized
**Solution:** Login again to get a fresh JWT token

## ✨ You're Done!

After completing these steps, you'll have:
- ✅ Clean project (no test data)
- ✅ Optimized disk space (~1.87 GB freed)
- ✅ Working repository management system
- ✅ All services running
- ✅ Database migrated
- ✅ System tested and verified

**Total time: ~15 minutes**

---

**Next:** Start building your features on top of the repository management system!
