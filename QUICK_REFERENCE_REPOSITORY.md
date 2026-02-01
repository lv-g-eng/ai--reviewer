# Repository Management - Quick Reference

## 🚀 Quick Start

```bash
# 1. Clean up test data
python scripts/cleanup_test_data.py

# 2. Configure GitHub token
echo "GITHUB_TOKEN=ghp_your_token" >> .env

# 3. Run migration
cd backend && alembic upgrade head

# 4. Start services
docker-compose up -d
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/repositories` | Add repository |
| GET | `/api/v1/repositories/validate` | Validate URL |
| GET | `/api/v1/repositories` | List all |
| GET | `/api/v1/repositories/{id}` | Get details |
| PATCH | `/api/v1/repositories/{id}` | Update |
| DELETE | `/api/v1/repositories/{id}` | Remove |
| POST | `/api/v1/repositories/{id}/sync` | Sync |

## 🔗 URL Formats

```bash
# HTTPS
https://github.com/owner/repo.git
https://github.com/owner/repo

# SSH
git@github.com:owner/repo.git
git@github.com:owner/repo
```

## 💻 Code Examples

### Python

```python
import requests

API = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Add repository
response = requests.post(
    f"{API}/repositories",
    headers=headers,
    json={
        "repository_url": "https://github.com/facebook/react.git",
        "branch": "main"
    }
)
```

### JavaScript

```javascript
const API = 'http://localhost:8000/api/v1';
const TOKEN = 'your-jwt-token';

const response = await fetch(`${API}/repositories`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    repository_url: 'https://github.com/facebook/react.git',
    branch: 'main'
  })
});
```

### cURL

```bash
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/facebook/react.git",
    "branch": "main"
  }'
```

## 🔑 Environment Setup

```bash
# Generate secure keys
openssl rand -hex 32  # JWT_SECRET
openssl rand -base64 32  # NEXTAUTH_SECRET

# Required variables
GITHUB_TOKEN=ghp_your_token
POSTGRES_PASSWORD=secure_password
JWT_SECRET=generated_secret
```

## 🧪 Testing

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Validate repository
curl -X GET "http://localhost:8000/api/v1/repositories/validate?repository_url=https://github.com/facebook/react.git" \
  -H "Authorization: Bearer $TOKEN"

# Add repository
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repository_url":"https://github.com/facebook/react.git","branch":"main"}'
```

## 📦 Supported Package Managers

- ✅ npm (package.json)
- ✅ pip (requirements.txt)
- 🔜 Maven (pom.xml)
- 🔜 Gradle (build.gradle)
- 🔜 Cargo (Cargo.toml)

## 🔄 Repository Status

```
PENDING → VALIDATING → CLONING → ANALYZING → ACTIVE
              ↓            ↓          ↓
           FAILED      FAILED     FAILED
              ↓
          ARCHIVED
```

## ⚠️ Common Errors

| Error | Solution |
|-------|----------|
| Invalid URL format | Use: `https://github.com/owner/repo.git` |
| Repository not found | Check URL and repository exists |
| Access denied | Verify GitHub token has `repo` scope |
| Branch not found | Check branch name is correct |

## 🛠️ Troubleshooting

```bash
# Check services
docker-compose ps

# View logs
docker-compose logs backend

# Test database
psql -U postgres -d ai_code_review -c "SELECT * FROM repositories;"

# Check GitHub token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

## 📚 Documentation

- **Full Guide:** [docs/REPOSITORY_MANAGEMENT.md](docs/REPOSITORY_MANAGEMENT.md)
- **Setup:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Cleanup:** [docs/DATA_CLEANUP_GUIDE.md](docs/DATA_CLEANUP_GUIDE.md)
- **Changes:** [CHANGES.md](CHANGES.md)

## 🔗 Useful Links

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- GitHub Tokens: https://github.com/settings/tokens

## 📞 Quick Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f backend

# Migration
cd backend && alembic upgrade head

# Cleanup
python scripts/cleanup_test_data.py
```
