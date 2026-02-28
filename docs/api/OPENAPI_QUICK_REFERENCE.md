# OpenAPI Specification Quick Reference

## Overview

The AI-Based Code Review Platform API is fully documented using OpenAPI 3.0 specification with:

- ✅ **75 API endpoints** across 18 categories
- ✅ **57 Pydantic schemas** for request/response validation
- ✅ **JWT Bearer authentication** with security schemes
- ✅ **Comprehensive error responses** (400, 401, 403, 404, 422, 429, 500, 503)
- ✅ **Interactive documentation** via Swagger UI and ReDoc

## Quick Access

### Interactive Documentation

| Interface | URL | Best For |
|-----------|-----|----------|
| **Swagger UI** | http://localhost:8000/docs | Testing APIs, trying requests |
| **ReDoc** | http://localhost:8000/redoc | Reading documentation |

### Specification Files

| Format | Location | Use Case |
|--------|----------|----------|
| **JSON** | `docs/api/openapi.json` | Import to Postman, API clients |
| **YAML** | `docs/api/openapi.yaml` | Human-readable, version control |

## API Categories

### 1. Health & Monitoring (3 endpoints)
- `GET /health` - Overall health status
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### 2. Authentication (6 endpoints)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT tokens
- `POST /api/v1/auth/logout` - Logout and invalidate token
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info
- `PATCH /api/v1/auth/password` - Change password

### 3. RBAC Authentication (4 endpoints)
- `POST /api/v1/rbac/auth/login` - RBAC login
- `POST /api/v1/rbac/auth/logout` - RBAC logout
- `POST /api/v1/rbac/auth/refresh` - Refresh RBAC token
- `GET /api/v1/rbac/auth/me` - Get current user info

### 4. Repository Management (5 endpoints)
- `GET /api/v1/repositories` - List repositories
- `POST /api/v1/repositories` - Create repository
- `GET /api/v1/repositories/{id}` - Get repository details
- `PUT /api/v1/repositories/{id}` - Update repository
- `DELETE /api/v1/repositories/{id}` - Delete repository

### 5. Architecture Analysis (3 endpoints)
- `POST /api/v1/analyze` - Analyze repository architecture
- `GET /api/v1/analysis/{id}` - Get analysis results
- `GET /api/v1/analysis/{id}/graph` - Get dependency graph

### 6. GitHub Integration (10+ endpoints)
- `POST /api/v1/webhooks/github` - GitHub webhook handler
- `GET /api/v1/github/repos` - List GitHub repositories
- `GET /api/v1/github/repos/{owner}/{repo}/pulls` - List pull requests
- And more...

### 7. Code Review (5+ endpoints)
- `POST /api/v1/code-review/analyze` - Trigger code review
- `GET /api/v1/code-review/results/{id}` - Get review results
- And more...

### 8. Audit Logs (5+ endpoints)
- `GET /api/v1/audit-logs` - Query audit logs
- `GET /api/v1/audit-logs/export` - Export audit logs
- And more...

### 9. User Data Management (2 endpoints)
- `GET /api/v1/users/{id}/export` - Export user data (GDPR)
- `DELETE /api/v1/users/{id}` - Delete user account (GDPR)

### 10. Metrics (1 endpoint)
- `GET /api/v1/metrics` - Prometheus metrics

## Authentication

### Security Scheme

```yaml
securitySchemes:
  HTTPBearer:
    type: http
    scheme: bearer
    bearerFormat: JWT
```

### Getting a Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Common Response Schemas

### Success Response (200)
```json
{
  "id": "123",
  "status": "success",
  "data": { ... }
}
```

### Error Response (4xx, 5xx)
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Validation Error (422)
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

## Request/Response Examples

### Example 1: Create Repository

**Request:**
```bash
POST /api/v1/repositories
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "my-project",
  "url": "https://github.com/user/my-project",
  "description": "My awesome project"
}
```

**Response (201):**
```json
{
  "id": "repo_123",
  "name": "my-project",
  "url": "https://github.com/user/my-project",
  "description": "My awesome project",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Example 2: Analyze Repository

**Request:**
```bash
POST /api/v1/analyze
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "repositoryUrl": "https://github.com/user/my-project",
  "includeArchitectureAnalysis": true,
  "includeComplexityMetrics": true,
  "includeDependencyAnalysis": true
}
```

**Response (200):**
```json
{
  "repositoryUrl": "https://github.com/user/my-project",
  "analysisId": "analysis_456",
  "status": "completed",
  "architectureSummary": {
    "totalFiles": 150,
    "totalClasses": 45,
    "totalFunctions": 230,
    "architecturalPurpose": "Web application with MVC architecture",
    "detectedPatterns": ["MVC", "Repository Pattern", "Dependency Injection"]
  },
  "metrics": {
    "cyclomaticComplexity": 5.2,
    "coupling": 35.5,
    "cohesion": 64.5,
    "codeSmells": 12
  }
}
```

## Regenerating the Specification

To regenerate the OpenAPI specification after code changes:

```bash
cd backend

# Generate with validation
python scripts/generate_openapi_spec.py --validate

# Generate with detailed summary
python scripts/generate_openapi_spec.py --validate --summary

# Specify custom output directory
python scripts/generate_openapi_spec.py --output-dir ../docs/api
```

## Validation Results

Current specification status:

- ✅ **75 endpoints** documented
- ✅ **67 unique paths**
- ✅ **57 schemas** defined
- ✅ **18 tags** for organization
- ✅ **JWT Bearer** security scheme
- ⚠️ **9 endpoints** need authentication documentation
- ⚠️ **22 endpoints** need more response documentation

## Integration with Tools

### Postman

1. Open Postman
2. Click Import → Upload Files
3. Select `docs/api/openapi.json`
4. All endpoints will be imported with schemas

### Insomnia

1. Open Insomnia
2. Click Import/Export → Import Data
3. Select `docs/api/openapi.yaml`
4. Collection will be created automatically

### Code Generation

Generate client SDKs using OpenAPI Generator:

```bash
# Python client
openapi-generator-cli generate \
  -i docs/api/openapi.json \
  -g python \
  -o clients/python

# TypeScript client
openapi-generator-cli generate \
  -i docs/api/openapi.json \
  -g typescript-axios \
  -o clients/typescript
```

## Best Practices

### 1. Keep Documentation Updated

Run the generation script after:
- Adding new endpoints
- Modifying request/response schemas
- Changing authentication requirements
- Updating error responses

### 2. Use Pydantic Models

All request/response models should use Pydantic for:
- Automatic schema generation
- Request validation
- Response serialization
- Documentation examples

### 3. Document Error Responses

Include all possible error responses:
```python
@router.get(
    "/endpoint",
    responses={
        200: {"model": SuccessResponse},
        401: {"model": UnauthorizedResponse},
        404: {"model": NotFoundResponse},
        500: {"model": InternalServerErrorResponse}
    }
)
```

### 4. Add Examples

Use Pydantic's `Config.json_schema_extra` for examples:
```python
class MyModel(BaseModel):
    field: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "example value"
            }
        }
```

### 5. Tag Endpoints

Organize endpoints with tags:
```python
@router.get("/endpoint", tags=["Category Name"])
```

## Troubleshooting

### Issue: Specification not updating

**Solution:** Restart the FastAPI server and regenerate:
```bash
# Stop server
# Restart server
python scripts/generate_openapi_spec.py --validate
```

### Issue: Missing schemas

**Solution:** Ensure all models are imported in `app/schemas/__init__.py`

### Issue: Authentication not showing

**Solution:** Add security decorator to endpoints:
```python
from app.api.dependencies import get_current_user

@router.get("/endpoint", dependencies=[Depends(get_current_user)])
```

## Support

- **Documentation**: http://localhost:8000/docs
- **Specification**: `docs/api/openapi.json`
- **Full Guide**: `docs/api/API_DOCUMENTATION.md`

## Changelog

### 2024-01-15 - Initial Release
- Generated comprehensive OpenAPI 3.0 specification
- 75 endpoints across 18 categories
- 57 Pydantic schemas
- JWT Bearer authentication
- Standardized error responses
- Interactive documentation (Swagger UI + ReDoc)
