# Repository Management System

## Overview

The Repository Management System allows you to add, manage, and track GitHub repository dependencies in your AI Code Review Platform. It supports automatic validation, dependency extraction, and version management.

## Features

### 1. GitHub Repository Integration
- Support for HTTPS and SSH URL formats
- Automatic repository validation
- Branch and tag detection
- Dependency extraction (npm, pip)

### 2. URL Format Support

#### HTTPS Format
```
https://github.com/{owner}/{repo}.git
https://github.com/{owner}/{repo}
```

#### SSH Format
```
git@github.com:{owner}/{repo}.git
git@github.com:{owner}/{repo}
```

### 3. Automatic Validation
- Repository existence check
- Access permission verification
- Branch/tag availability
- Dependency file detection

### 4. Dependency Management
- Automatic dependency extraction
- Support for multiple package managers:
  - npm (package.json)
  - pip (requirements.txt)
- Version tracking
- Auto-update capabilities

## API Endpoints

### Add Repository
```http
POST /api/v1/repositories
Content-Type: application/json

{
  "repository_url": "https://github.com/owner/repo.git",
  "branch": "main",
  "version": "v1.0.0",
  "auto_update": false,
  "description": "Optional description"
}
```

**Response:**
```json
{
  "id": "uuid",
  "repository_url": "https://github.com/owner/repo.git",
  "owner": "owner",
  "name": "repo",
  "branch": "main",
  "version": "v1.0.0",
  "status": "active",
  "description": "Optional description",
  "auto_update": false,
  "last_synced": "2026-01-21T10:00:00Z",
  "created_at": "2026-01-21T10:00:00Z",
  "updated_at": "2026-01-21T10:00:00Z",
  "metadata": {
    "url_format": "https",
    "clone_url": "https://github.com/owner/repo.git",
    "default_branch": "main",
    "available_branches": ["main", "develop"],
    "available_tags": ["v1.0.0", "v0.9.0"],
    "dependencies": {
      "package_manager": "npm",
      "count": 25
    }
  }
}
```

### Validate Repository
```http
GET /api/v1/repositories/validate?repository_url=https://github.com/owner/repo.git&branch=main
```

**Response:**
```json
{
  "is_valid": true,
  "is_accessible": true,
  "exists": true,
  "default_branch": "main",
  "available_branches": ["main", "develop", "feature/new"],
  "available_tags": ["v1.0.0", "v0.9.0"],
  "error_message": null
}
```

### List Repositories
```http
GET /api/v1/repositories?page=1&page_size=20&status=active
```

### Get Repository Details
```http
GET /api/v1/repositories/{repository_id}
```

### Update Repository
```http
PATCH /api/v1/repositories/{repository_id}
Content-Type: application/json

{
  "branch": "develop",
  "auto_update": true,
  "description": "Updated description"
}
```

### Sync Repository
```http
POST /api/v1/repositories/{repository_id}/sync
```

### Delete Repository
```http
DELETE /api/v1/repositories/{repository_id}
```

## Usage Examples

### Python Client
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
        "repository_url": "https://github.com/facebook/react.git",
        "branch": "main",
        "auto_update": False,
        "description": "React library for UI"
    }
)

repository = response.json()
print(f"Added repository: {repository['id']}")

# Validate before adding
response = requests.get(
    f"{API_URL}/repositories/validate",
    headers=headers,
    params={
        "repository_url": "https://github.com/vuejs/vue.git",
        "branch": "main"
    }
)

validation = response.json()
if validation["is_valid"]:
    print("Repository is valid and accessible")
else:
    print(f"Validation failed: {validation['error_message']}")
```

### JavaScript/TypeScript Client
```typescript
const API_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'your-jwt-token';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json'
};

// Add repository
async function addRepository() {
  const response = await fetch(`${API_URL}/repositories`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      repository_url: 'https://github.com/angular/angular.git',
      branch: 'main',
      auto_update: false,
      description: 'Angular framework'
    })
  });
  
  const repository = await response.json();
  console.log('Added repository:', repository.id);
}

// List repositories
async function listRepositories() {
  const response = await fetch(
    `${API_URL}/repositories?page=1&page_size=20`,
    { headers }
  );
  
  const data = await response.json();
  console.log(`Found ${data.total} repositories`);
  data.repositories.forEach(repo => {
    console.log(`- ${repo.owner}/${repo.name} (${repo.status})`);
  });
}
```

### cURL Examples
```bash
# Add repository
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/nodejs/node.git",
    "branch": "main",
    "auto_update": false
  }'

# Validate repository
curl -X GET "http://localhost:8000/api/v1/repositories/validate?repository_url=https://github.com/python/cpython.git" \
  -H "Authorization: Bearer $TOKEN"

# List repositories
curl -X GET "http://localhost:8000/api/v1/repositories?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"

# Sync repository
curl -X POST http://localhost:8000/api/v1/repositories/{repo_id}/sync \
  -H "Authorization: Bearer $TOKEN"
```

## Configuration

### GitHub Token
Set your GitHub personal access token in the environment:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Or in `.env`:
```
GITHUB_TOKEN=ghp_your_token_here
```

### Token Permissions
Required GitHub token scopes:
- `repo` - Full control of private repositories
- `read:org` - Read organization data (if accessing org repos)

## Repository Status Flow

```
PENDING → VALIDATING → CLONING → ANALYZING → ACTIVE
                ↓           ↓          ↓
              FAILED     FAILED    FAILED
                ↓
            ARCHIVED
```

- **PENDING**: Repository added, awaiting validation
- **VALIDATING**: Checking repository accessibility
- **CLONING**: Cloning repository content
- **ANALYZING**: Extracting dependencies and metadata
- **ACTIVE**: Repository ready for use
- **FAILED**: Error occurred during processing
- **ARCHIVED**: Repository archived/disabled

## Error Handling

### Common Errors

#### Invalid URL Format
```json
{
  "detail": "Invalid GitHub URL format. Expected formats:\n  - HTTPS: https://github.com/owner/repo.git\n  - SSH: git@github.com:owner/repo.git"
}
```

#### Repository Not Found
```json
{
  "detail": "Repository not found"
}
```

#### Access Denied
```json
{
  "detail": "Access denied. Check GitHub token permissions."
}
```

#### Branch Not Found
```json
{
  "detail": "Branch 'feature/xyz' not found"
}
```

## Best Practices

1. **Always validate before adding**: Use the validation endpoint to check repository accessibility
2. **Use specific branches**: Specify branch names instead of relying on defaults
3. **Enable auto-update carefully**: Only enable for stable dependencies
4. **Monitor sync status**: Regularly check repository sync status
5. **Use version tags**: Pin to specific versions for production dependencies

## Database Schema

```sql
CREATE TABLE repositories (
    id UUID PRIMARY KEY,
    repository_url VARCHAR(500) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    branch VARCHAR(255) NOT NULL DEFAULT 'main',
    version VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    description VARCHAR(500),
    auto_update BOOLEAN DEFAULT false,
    last_synced TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    metadata JSONB DEFAULT '{}'
);
```

## Troubleshooting

### Repository validation fails
- Check GitHub token is valid and has correct permissions
- Verify repository URL format
- Ensure repository is accessible (not private without token)

### Dependencies not detected
- Ensure repository has package.json (npm) or requirements.txt (pip)
- Check file is in repository root
- Verify branch name is correct

### Sync fails
- Check network connectivity
- Verify GitHub API rate limits
- Ensure repository still exists and is accessible

## Future Enhancements

- [ ] Support for more package managers (Maven, Gradle, Cargo)
- [ ] Webhook integration for automatic updates
- [ ] Dependency vulnerability scanning
- [ ] License compliance checking
- [ ] Automated dependency updates
- [ ] Repository mirroring
- [ ] Multi-repository dependency graphs
