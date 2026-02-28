# API Documentation

## Overview

The AI-Based Code Review and Architecture Analysis Platform provides a comprehensive REST API for automated code review, architectural analysis, and repository management.

## OpenAPI Specification

The API is fully documented using OpenAPI 3.0 specification. The specification is automatically generated from the FastAPI application and includes:

- **All API endpoints** with request/response schemas
- **Authentication requirements** for each endpoint
- **Error responses** with standardized formats
- **Request validation** rules and constraints
- **Example requests and responses**

## Accessing the Documentation

### Interactive Documentation

The API provides two interactive documentation interfaces:

1. **Swagger UI** (recommended for testing):
   - URL: `http://localhost:8000/docs`
   - Features: Interactive API testing, request/response examples, authentication support

2. **ReDoc** (recommended for reading):
   - URL: `http://localhost:8000/redoc`
   - Features: Clean layout, search functionality, detailed schemas

### OpenAPI Specification Files

The OpenAPI specification is available in two formats:

- **JSON**: `docs/api/openapi.json`
- **YAML**: `docs/api/openapi.yaml`

These files can be imported into API clients like Postman, Insomnia, or used with code generators.

## Generating the Specification

To regenerate the OpenAPI specification:

```bash
# From the backend directory
cd backend

# Generate with validation
python scripts/generate_openapi_spec.py --validate --summary

# Specify custom output directory
python scripts/generate_openapi_spec.py --output-dir ../docs/api
```

## Authentication

Most API endpoints require authentication using JWT (JSON Web Tokens).

### Getting a Token

**Option 1: Standard Authentication**

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Option 2: RBAC Authentication**

```bash
POST /api/v1/rbac/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Both endpoints return:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the access token in the Authorization header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration

- **Access tokens** expire after 24 hours
- **Refresh tokens** expire after 7 days

Use the refresh endpoint to get a new access token:

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

## API Endpoints

### Health & Monitoring

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Overall health status |
| `/health/ready` | GET | No | Readiness probe (Kubernetes) |
| `/health/live` | GET | No | Liveness probe (Kubernetes) |
| `/api/v1/metrics` | GET | No | Prometheus metrics |

### Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/register` | POST | No | Register new user |
| `/api/v1/auth/login` | POST | No | Login and get tokens |
| `/api/v1/auth/logout` | POST | Yes | Logout and invalidate token |
| `/api/v1/auth/refresh` | POST | No | Refresh access token |
| `/api/v1/auth/me` | GET | Yes | Get current user info |
| `/api/v1/auth/password` | PATCH | Yes | Change password |

### RBAC Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/rbac/auth/login` | POST | No | RBAC login |
| `/api/v1/rbac/auth/logout` | POST | Yes | RBAC logout |
| `/api/v1/rbac/auth/refresh` | POST | No | Refresh RBAC token |
| `/api/v1/rbac/auth/me` | GET | Yes | Get current user info |

### Repository Management

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/repositories` | GET | Yes | List repositories |
| `/api/v1/repositories` | POST | Yes | Create repository |
| `/api/v1/repositories/{id}` | GET | Yes | Get repository details |
| `/api/v1/repositories/{id}` | PUT | Yes | Update repository |
| `/api/v1/repositories/{id}` | DELETE | Yes | Delete repository |

### Architecture Analysis

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/analyze` | POST | Yes | Analyze repository architecture |
| `/api/v1/analysis/{id}` | GET | Yes | Get analysis results |
| `/api/v1/analysis/{id}/graph` | GET | Yes | Get dependency graph |

### GitHub Integration

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/webhooks/github` | POST | No* | GitHub webhook handler |
| `/api/v1/github/repos` | GET | Yes | List GitHub repositories |
| `/api/v1/github/repos/{owner}/{repo}/pulls` | GET | Yes | List pull requests |

*Webhook endpoints use HMAC signature verification instead of JWT

### Code Review

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/code-review/analyze` | POST | Yes | Trigger code review |
| `/api/v1/code-review/results/{id}` | GET | Yes | Get review results |

### Audit Logs

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/audit-logs` | GET | Yes | Query audit logs |
| `/api/v1/audit-logs/export` | GET | Yes | Export audit logs |

### User Data Management (GDPR)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/users/{id}/export` | GET | Yes | Export user data |
| `/api/v1/users/{id}` | DELETE | Yes | Delete user account |

## Error Responses

All endpoints return standardized error responses:

### 400 Bad Request

```json
{
  "detail": "Invalid input parameters",
  "error_code": "INVALID_INPUT",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden

```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 429 Too Many Requests

```json
{
  "detail": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error",
  "error_id": "err_abc123xyz"
}
```

### 503 Service Unavailable

```json
{
  "detail": "Service temporarily unavailable",
  "retry_after": 300
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Default limit**: 100 requests per minute per user
- **Login endpoint**: 5 requests per minute per IP address
- **Webhook endpoints**: 1000 requests per hour per repository

When rate limit is exceeded, the API returns HTTP 429 with a `retry_after` header indicating when to retry.

## Pagination

List endpoints support pagination using query parameters:

```bash
GET /api/v1/repositories?page=1&page_size=20
```

Response includes pagination metadata:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

## Filtering and Sorting

Many list endpoints support filtering and sorting:

```bash
# Filter by status
GET /api/v1/analysis?status=completed

# Sort by creation date
GET /api/v1/repositories?sort=-created_at

# Combine filters
GET /api/v1/audit-logs?user_id=123&action=login&start_date=2024-01-01
```

## Webhooks

### GitHub Webhook Configuration

To receive automated PR analysis:

1. Go to your GitHub repository settings
2. Navigate to Webhooks → Add webhook
3. Set Payload URL: `https://your-domain.com/api/v1/webhooks/github`
4. Set Content type: `application/json`
5. Set Secret: Your webhook secret (configured in environment variables)
6. Select events: Pull requests, Push

### Webhook Security

GitHub webhooks are verified using HMAC-SHA256 signatures. The signature is validated against the configured webhook secret.

## Best Practices

### 1. Always Use HTTPS

Never send authentication tokens over unencrypted connections in production.

### 2. Store Tokens Securely

- Store tokens in secure storage (e.g., httpOnly cookies, secure keychain)
- Never store tokens in localStorage or sessionStorage
- Never commit tokens to version control

### 3. Handle Token Expiration

Implement automatic token refresh logic:

```javascript
async function apiRequest(url, options) {
  let response = await fetch(url, options);
  
  if (response.status === 401) {
    // Token expired, refresh it
    await refreshToken();
    // Retry request with new token
    response = await fetch(url, options);
  }
  
  return response;
}
```

### 4. Implement Retry Logic

For transient errors (500, 503), implement exponential backoff:

```python
import time
import requests

def api_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code < 500:
                return response
        except requests.RequestException:
            pass
        
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    raise Exception("Max retries exceeded")
```

### 5. Respect Rate Limits

Monitor rate limit headers and implement backoff when approaching limits.

## Code Examples

### Python

```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={
        'email': 'user@example.com',
        'password': 'password123'
    }
)
tokens = response.json()

# Make authenticated request
headers = {
    'Authorization': f"Bearer {tokens['access_token']}"
}
response = requests.get(
    'http://localhost:8000/api/v1/repositories',
    headers=headers
)
repositories = response.json()
```

### JavaScript/TypeScript

```typescript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
  }),
});
const tokens = await loginResponse.json();

// Make authenticated request
const reposResponse = await fetch('http://localhost:8000/api/v1/repositories', {
  headers: {
    'Authorization': `Bearer ${tokens.access_token}`,
  },
});
const repositories = await reposResponse.json();
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Make authenticated request
curl -X GET http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Support

For API support and questions:

- **Documentation**: http://localhost:8000/docs
- **Email**: support@example.com
- **GitHub Issues**: https://github.com/your-org/your-repo/issues

## Changelog

### Version 1.0.0 (2024-01-15)

- Initial API release
- Complete OpenAPI 3.0 specification
- JWT authentication
- RBAC support
- GitHub webhook integration
- Architecture analysis endpoints
- Audit logging
- GDPR compliance endpoints
