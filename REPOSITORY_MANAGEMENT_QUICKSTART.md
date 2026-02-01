# Repository Management - Quick Start Guide

## Overview

The Repository Management System allows you to add and manage GitHub repository dependencies directly through the API. This feature supports automatic validation, dependency extraction, and version tracking.

## Quick Setup

### 1. Configure GitHub Token

```bash
# Generate a GitHub Personal Access Token at:
# https://github.com/settings/tokens

# Add to your .env file
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env
```

### 2. Run Database Migration

```bash
cd backend
alembic upgrade head
```

### 3. Start the Application

```bash
docker-compose up -d
```

## Basic Usage

### Add a Repository

```bash
# Using cURL
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/facebook/react.git",
    "branch": "main",
    "auto_update": false,
    "description": "React library"
  }'
```

### Validate Before Adding

```bash
curl -X GET "http://localhost:8000/api/v1/repositories/validate?repository_url=https://github.com/vuejs/vue.git" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### List Repositories

```bash
curl -X GET "http://localhost:8000/api/v1/repositories?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Supported URL Formats

### HTTPS Format
```
https://github.com/owner/repo.git
https://github.com/owner/repo
```

### SSH Format
```
git@github.com:owner/repo.git
git@github.com:owner/repo
```

## Features

✅ **Automatic Validation**
- Repository existence check
- Access permission verification
- Branch/tag detection

✅ **Dependency Extraction**
- npm (package.json)
- pip (requirements.txt)
- More package managers coming soon

✅ **Version Management**
- Branch tracking
- Tag/version pinning
- Auto-update support

✅ **Metadata Storage**
- Repository information
- Dependency counts
- Last sync timestamps

## Python Example

```python
import requests

API_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Add repository
response = requests.post(
    f"{API_URL}/repositories",
    headers=headers,
    json={
        "repository_url": "https://github.com/nodejs/node.git",
        "branch": "main",
        "auto_update": False
    }
)

if response.status_code == 201:
    repo = response.json()
    print(f"✅ Added: {repo['owner']}/{repo['name']}")
    print(f"   ID: {repo['id']}")
    print(f"   Status: {repo['status']}")
else:
    print(f"❌ Error: {response.json()['detail']}")
```

## JavaScript/TypeScript Example

```typescript
const API_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'your-jwt-token';

async function addRepository(url: string, branch: string = 'main') {
  const response = await fetch(`${API_URL}/repositories`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      repository_url: url,
      branch,
      auto_update: false
    })
  });

  if (response.ok) {
    const repo = await response.json();
    console.log(`✅ Added: ${repo.owner}/${repo.name}`);
    return repo;
  } else {
    const error = await response.json();
    console.error(`❌ Error: ${error.detail}`);
    throw new Error(error.detail);
  }
}

// Usage
addRepository('https://github.com/angular/angular.git')
  .then(repo => console.log('Repository added:', repo.id))
  .catch(err => console.error('Failed:', err));
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/repositories` | Add new repository |
| GET | `/api/v1/repositories/validate` | Validate repository URL |
| GET | `/api/v1/repositories` | List all repositories |
| GET | `/api/v1/repositories/{id}` | Get repository details |
| PATCH | `/api/v1/repositories/{id}` | Update repository |
| DELETE | `/api/v1/repositories/{id}` | Remove repository |
| POST | `/api/v1/repositories/{id}/sync` | Sync with remote |

## Common Issues

### Invalid URL Format
```json
{
  "detail": "Invalid GitHub URL format..."
}
```
**Solution:** Use correct format: `https://github.com/owner/repo.git`

### Repository Not Found
```json
{
  "detail": "Repository not found"
}
```
**Solution:** Check repository exists and is accessible

### Access Denied
```json
{
  "detail": "Access denied. Check GitHub token permissions."
}
```
**Solution:** Verify GitHub token has `repo` scope

## Next Steps

1. ✅ Clean up test data: `python scripts/cleanup_test_data.py`
2. ✅ Configure environment variables
3. ✅ Run database migrations
4. ✅ Add your first repository
5. 📖 Read full documentation: `docs/REPOSITORY_MANAGEMENT.md`

## Documentation

- **Full Guide:** [docs/REPOSITORY_MANAGEMENT.md](docs/REPOSITORY_MANAGEMENT.md)
- **Data Cleanup:** [docs/DATA_CLEANUP_GUIDE.md](docs/DATA_CLEANUP_GUIDE.md)
- **API Reference:** http://localhost:8000/docs (when running)

## Support

For issues or questions:
1. Check the documentation
2. Review error messages
3. Check logs: `docker-compose logs backend`
4. Create an issue with details
