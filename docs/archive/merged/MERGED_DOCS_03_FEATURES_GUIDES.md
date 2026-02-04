# Project Documentation - Features & Guides

**Document Type:** Merged Documentation
**Last Updated:** 2026-01-21
**Merged From:** docs/REPOSITORY_MANAGEMENT.md, REPOSITORY_MANAGEMENT_QUICKSTART.md, docs/LLM_INTEGRATION_GUIDE.md, docs/AI_PR_REVIEWER_GUIDE.md, docs/DATA_CLEANUP_GUIDE.md

---

## Table of Contents

1. [Repository Management System](#1-repository-management-system)
2. [LLM Integration](#2-llm-integration)
3. [AI PR Reviewer](#3-ai-pr-reviewer)
4. [Data Cleanup Procedures](#4-data-cleanup-procedures)

---

## 1. Repository Management System

### Overview

The Repository Management System allows you to add, manage, and track GitHub repository dependencies. It supports automatic validation, dependency extraction, and version management.

### Features

- **GitHub Repository Integration**
  - Support for HTTPS and SSH URL formats
  - Automatic repository validation
  - Branch and tag detection
  - Dependency extraction (npm, pip)

- **URL Format Support**
  - HTTPS: `https://github.com/{owner}/{repo}.git`
  - SSH: `git@github.com:{owner}/{repo}.git`

- **Automatic Validation**
  - Repository existence check
  - Access permission verification
  - Branch/tag availability
  - Dependency file detection

- **Dependency Management**
  - Automatic dependency extraction
  - Support for npm (package.json)
  - Support for pip (requirements.txt)
  - Version tracking
  - Auto-update capabilities

### Quick Start

#### Setup

```bash
# Configure GitHub token
echo "GITHUB_TOKEN=ghp_your_token" >> .env

# Run migration
cd backend && alembic upgrade head

# Start services
docker-compose up -d
```

#### Add Repository

```bash
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

#### Validate Before Adding

```bash
curl -X GET "http://localhost:8000/api/v1/repositories/validate?repository_url=https://github.com/vuejs/vue.git" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### List Repositories

```bash
curl -X GET "http://localhost:8000/api/v1/repositories?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/repositories` | Add new repository |
| GET | `/api/v1/repositories/validate` | Validate repository URL |
| GET | `/api/v1/repositories` | List all repositories |
| GET | `/api/v1/repositories/{id}` | Get repository details |
| PATCH | `/api/v1/repositories/{id}` | Update repository |
| DELETE | `/api/v1/repositories/{id}` | Remove repository |
| POST | `/api/v1/repositories/{id}/sync` | Sync with remote |

### Usage Examples

#### Python

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
else:
    print(f"❌ Error: {response.json()['detail']}")
```

#### JavaScript/TypeScript

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
    throw new Error(error.detail);
  }
}
```

### Repository Status Flow

```
PENDING → VALIDATING → CLONING → ANALYZING → ACTIVE
              ↓            ↓          ↓
           FAILED      FAILED    FAILED
              ↓
          ARCHIVED
```

### Common Issues

**Invalid URL Format:**
```json
{
  "detail": "Invalid GitHub URL format..."
}
```
**Solution:** Use correct format: `https://github.com/owner/repo.git`

**Repository Not Found:**
```json
{
  "detail": "Repository not found"
}
```
**Solution:** Check repository exists and is accessible

**Access Denied:**
```json
{
  "detail": "Access denied. Check GitHub token permissions."
}
```
**Solution:** Verify GitHub token has `repo` scope

---

## 2. LLM Integration

### Overview

The platform supports both local and cloud-based LLM providers for code analysis and review.

### Supported Providers

**Cloud Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)

**Local Providers:**
- llama.cpp (GGUF models)
- Custom models

### Configuration

#### OpenAI

```bash
# .env
OPENAI_API_KEY=sk-your-openai-key
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4
```

#### Anthropic

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_LLM_MODEL=claude-3-opus-20240229
```

#### Local LLM

```bash
# .env
LLM_ENABLED=true
LLM_MODEL_PATH=./models/your-model.gguf
LLM_CONTEXT_SIZE=4096
LLM_GPU_LAYERS=35
```

### Usage

#### Code Analysis

```python
from app.services.llm_service import llm_service

# Analyze code
result = await llm_service.analyze_code(
    code=code_content,
    language="python",
    context="Review for security issues"
)

print(result.analysis)
print(result.suggestions)
```

#### PR Review

```python
from app.services.ai_pr_reviewer import AIPRReviewer

reviewer = AIPRReviewer()

# Review PR
review = await reviewer.review_pull_request(
    pr_id="123",
    repository="owner/repo",
    files_changed=changed_files
)

print(review.summary)
print(review.issues)
print(review.recommendations)
```

### API Endpoints

**LLM Service:**
- POST `/api/v1/llm/analyze` - Analyze code
- POST `/api/v1/llm/chat` - Chat with LLM
- GET `/api/v1/llm/models` - List available models

**PR Review:**
- POST `/api/v1/analysis/pr/review` - Review PR
- GET `/api/v1/analysis/pr/{id}/results` - Get review results

### Best Practices

1. **Choose appropriate model**
   - GPT-4 for complex analysis
   - GPT-3.5 for quick reviews
   - Local models for privacy

2. **Optimize context**
   - Include relevant code only
   - Provide clear instructions
   - Limit context size

3. **Handle rate limits**
   - Implement retry logic
   - Use exponential backoff
   - Cache results

4. **Monitor costs**
   - Track API usage
   - Set usage limits
   - Use local models when possible

---

## 3. AI PR Reviewer

### Overview

Automated pull request review using AI to identify issues, suggest improvements, and ensure code quality.

### Features

- **Automated Code Review**
  - Syntax and style checking
  - Security vulnerability detection
  - Performance optimization suggestions
  - Best practice recommendations

- **Multi-Language Support**
  - Python
  - JavaScript/TypeScript
  - Java
  - C#
  - Go

- **Integration**
  - GitHub webhooks
  - Manual triggers
  - Scheduled reviews

### Setup

#### Configure GitHub Webhook

1. Go to repository settings
2. Add webhook: `https://your-domain.com/api/v1/github/webhook`
3. Select events: Pull requests
4. Add webhook secret to `.env`

#### Enable Auto-Review

```bash
# .env
AI_PR_REVIEW_ENABLED=true
AI_PR_REVIEW_AUTO=true
AI_PR_REVIEW_PROVIDER=openai
```

### Usage

#### Manual Review

```bash
curl -X POST http://localhost:8000/api/v1/analysis/pr/review \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "owner/repo",
    "pr_number": 123
  }'
```

#### Get Review Results

```bash
curl -X GET http://localhost:8000/api/v1/analysis/pr/123/results \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Review Output

```json
{
  "pr_id": "123",
  "repository": "owner/repo",
  "status": "completed",
  "summary": {
    "total_files": 15,
    "issues_found": 8,
    "critical": 2,
    "warnings": 6,
    "suggestions": 12
  },
  "issues": [
    {
      "file": "src/auth.py",
      "line": 45,
      "severity": "critical",
      "type": "security",
      "message": "SQL injection vulnerability",
      "suggestion": "Use parameterized queries"
    }
  ],
  "recommendations": [
    "Add input validation",
    "Implement error handling",
    "Add unit tests"
  ]
}
```

### Configuration Options

```python
# Review settings
AI_PR_REVIEW_CONFIG = {
    "check_security": True,
    "check_performance": True,
    "check_style": True,
    "check_tests": True,
    "min_test_coverage": 80,
    "max_complexity": 10,
    "auto_comment": True,
    "auto_approve": False
}
```

---

## 4. Data Cleanup Procedures

### Overview

Procedures for cleaning up test data, placeholder content, and false information from the project.

### Automated Cleanup Script

#### Running the Script

```bash
# From project root
python scripts/cleanup_test_data.py
```

#### What Gets Cleaned

**Database Cleanup (PostgreSQL):**
- Removes test users (emails containing 'test' or 'example.com')
- Removes orphaned user roles
- Removes orphaned projects
- Removes orphaned analysis results

**Redis Cleanup:**
- Removes all keys containing 'test'
- Clears test JWT tokens
- Clears test session data

**Neo4j Cleanup:**
- Removes nodes with test project IDs
- Removes test relationships
- Clears test graph data

**Environment Files:**
- Clears sensitive data from `.env` files
- Replaces with template values
- Preserves structure

**Test Files:**
- Removes standalone test scripts
- Preserves test suite files

### Manual Cleanup Steps

#### 1. Environment Configuration

After running cleanup, update environment files:

```bash
# Generate secure keys
openssl rand -hex 32  # JWT_SECRET
openssl rand -base64 32  # NEXTAUTH_SECRET

# Update .env
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET=generated_secret
GITHUB_TOKEN=ghp_your_token
```

#### 2. Database Reset (Optional)

```bash
# PostgreSQL
docker-compose down -v
docker-compose up -d postgres
cd backend && alembic upgrade head

# Neo4j
docker-compose down -v
docker-compose up -d neo4j

# Redis
docker-compose down -v
docker-compose up -d redis
```

#### 3. Verify Cleanup

```bash
# Check for remaining test data
grep -r "test@example.com" backend/
grep -r "changeme" .env*

# Check database
psql -U postgres -d ai_code_review -c "SELECT email FROM users WHERE email LIKE '%test%';"
```

### What NOT to Clean

**Preserve:**
- `backend/tests/` - Unit and integration tests
- `frontend/src/__tests__/` - Frontend tests
- Test configuration files
- Documentation
- Configuration templates

### Post-Cleanup Checklist

- [ ] All `.env` files updated with real values
- [ ] Secure keys generated and configured
- [ ] Database connections tested
- [ ] No test users in database
- [ ] No placeholder passwords
- [ ] GitHub token configured
- [ ] LLM API keys configured (if using)
- [ ] Application starts successfully
- [ ] Health check returns healthy status

### Verification Commands

```bash
# Test database connections
python backend/check-services.py

# Test API health
curl http://localhost:8000/health

# Test authentication (should fail without valid user)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
# Expected: 401 Unauthorized
```

### Troubleshooting

**Cleanup Script Fails:**
```bash
# Ensure databases are running
docker-compose up -d postgres redis neo4j

# Wait for databases
sleep 10

# Run cleanup again
python scripts/cleanup_test_data.py
```

**Test Data Remains:**
```bash
# Manual database cleanup
psql -U postgres -d ai_code_review << EOF
DELETE FROM users WHERE email LIKE '%test%' OR email LIKE '%example.com%';
DELETE FROM user_roles WHERE user_id NOT IN (SELECT id FROM users);
EOF

# Manual Redis cleanup
redis-cli FLUSHDB

# Manual Neo4j cleanup
cypher-shell -u neo4j -p password "MATCH (n) WHERE n.projectId CONTAINS 'test' DETACH DELETE n"
```

---

## Modification History

### 2026-01-21
- Merged docs/REPOSITORY_MANAGEMENT.md, REPOSITORY_MANAGEMENT_QUICKSTART.md, docs/LLM_INTEGRATION_GUIDE.md, docs/AI_PR_REVIEWER_GUIDE.md, docs/DATA_CLEANUP_GUIDE.md
- Consolidated repository management documentation
- Added LLM integration guide
- Included AI PR reviewer documentation
- Added data cleanup procedures

---

## Related Documents

- **Overview:** MERGED_DOCS_01_PROJECT_OVERVIEW.md
- **Setup:** MERGED_DOCS_02_SETUP_CONFIGURATION.md
- **Technical:** MERGED_DOCS_04_TECHNICAL_REFERENCE.md
- **Troubleshooting:** MERGED_DOCS_05_TROUBLESHOOTING_MAINTENANCE.md
