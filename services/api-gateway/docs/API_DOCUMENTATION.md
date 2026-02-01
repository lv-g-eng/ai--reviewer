# API Gateway - API Documentation

> **Version**: 1.0.0 | **Base URL**: `http://localhost:3000/api/v1` | **Auth**: JWT Bearer Token

## 📋 Documentation Overview

This document provides a quick reference for the API Gateway endpoints. For complete API documentation with request/response schemas, examples, and interactive testing, see:

- **[OpenAPI/Swagger Specification](./openapi.yaml)** - Complete API specification
- **[Interactive API Explorer](https://editor.swagger.io/)** - Load the OpenAPI spec for interactive testing

---

## Quick Reference

### Authentication
```http
Authorization: Bearer <your-jwt-token>
```

### Rate Limits
- General API: 100 req/15min per IP
- Auth endpoints: 5 req/15min per IP

### Common Response Codes
- `200` OK - Success
- `201` Created - Resource created
- `400` Bad Request - Validation error
- `401` Unauthorized - Auth required
- `403` Forbidden - Insufficient permissions
- `404` Not Found - Resource not found
- `429` Too Many Requests - Rate limit exceeded
- `500` Internal Server Error - Server error
- `503` Service Unavailable - Circuit breaker open

### Response Headers
All responses include:
- `X-Correlation-ID` - Unique request identifier
- `X-RateLimit-Limit` - Rate limit maximum
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Rate limit reset time

---

## Health Check

### GET /health
Check API Gateway and backend services health (no auth required).

**Response 200**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-24T10:00:00.000Z",
  "uptime": 123.456,
  "services": {
    "auth": "healthy",
    "code-review": "healthy",
    "architecture": "healthy",
    "ai-service": "healthy",
    "project-manager": "healthy"
  },
  "redis": "connected"
}
```

---

## Projects API

### GET /api/v1/projects
List all projects with pagination and filtering.

**Query Parameters**:
- `page` (number, optional): Page number (default: 1)
- `limit` (number, optional): Items per page (default: 10, max: 100)
- `status` (string, optional): Filter by status (`active`, `inactive`, `archived`)
- `search` (string, optional): Search by name

**Response 200**:
```json
{
  "data": [
    {
      "id": "proj-123",
      "name": "My Project",
      "description": "Project description",
      "repositoryUrl": "https://github.com/user/repo",
      "status": "active",
      "createdAt": "2026-01-20T10:00:00.000Z",
      "updatedAt": "2026-01-24T10:00:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 50,
    "totalPages": 5
  }
}
```

### POST /api/v1/projects
Create a new project.

**Request Body**:
```json
{
  "name": "My Project",
  "description": "Project description",
  "repositoryUrl": "https://github.com/user/repo",
  "settings": {
    "autoReview": true,
    "reviewThreshold": "medium"
  }
}
```

**Response 201**:
```json
{
  "id": "proj-123",
  "name": "My Project",
  "description": "Project description",
  "repositoryUrl": "https://github.com/user/repo",
  "status": "active",
  "createdAt": "2026-01-24T10:00:00.000Z"
}
```

### GET /api/v1/projects/:id
Get project details by ID.

### PUT /api/v1/projects/:id
Update project.

### DELETE /api/v1/projects/:id
Delete project.

### GET /api/v1/projects/:id/stats
Get project statistics.

**Response 200**:
```json
{
  "totalReviews": 45,
  "completedReviews": 42,
  "pendingReviews": 3,
  "averageReviewTime": 15.5,
  "issuesFound": {
    "critical": 2,
    "high": 8,
    "medium": 15,
    "low": 23
  }
}
```

---

## Reviews API

### GET /api/v1/reviews
List all code reviews.

**Query Parameters**:
- `page`, `limit`: Pagination
- `projectId`: Filter by project
- `status`: `pending`, `in_progress`, `completed`, `failed`
- `severity`: `low`, `medium`, `high`, `critical`

### POST /api/v1/reviews
Create a new code review.

**Request Body**:
```json
{
  "projectId": "proj-123",
  "commitHash": "abc123def456",
  "branch": "main",
  "files": ["src/index.ts", "src/utils.ts"]
}
```

### GET /api/v1/reviews/:id
Get review details including issues and suggestions.

**Response 200**:
```json
{
  "id": "review-123",
  "projectId": "proj-123",
  "status": "completed",
  "issues": [
    {
      "id": "issue-1",
      "file": "src/index.ts",
      "line": 42,
      "severity": "high",
      "type": "security",
      "message": "Potential SQL injection vulnerability",
      "suggestion": "Use parameterized queries"
    }
  ],
  "suggestions": [
    {
      "id": "suggestion-1",
      "file": "src/utils.ts",
      "line": 15,
      "type": "performance",
      "description": "Consider using Map instead of Object for better performance",
      "code": "const cache = new Map();"
    }
  ]
}
```

### PUT /api/v1/reviews/:id
Update review status or notes.

### DELETE /api/v1/reviews/:id
Delete review.

### POST /api/v1/reviews/:id/comments
Add comment to review.

**Request Body**:
```json
{
  "content": "This looks good, but consider adding error handling."
}
```

---

## Architecture API

### GET /api/v1/architecture/:projectId
Get architecture overview for a project.

**Response 200**:
```json
{
  "projectId": "proj-123",
  "components": [
    {
      "id": "comp-1",
      "name": "UserService",
      "type": "service",
      "path": "src/services/user.ts",
      "size": 1250,
      "complexity": 8.5
    }
  ],
  "dependencies": [
    {
      "from": "UserService",
      "to": "DatabaseService",
      "type": "dependency",
      "weight": 0.8
    }
  ],
  "metrics": {
    "totalComponents": 15,
    "totalDependencies": 23,
    "cyclomaticComplexity": 12.5,
    "maintainabilityIndex": 78.2
  }
}
```

### POST /api/v1/architecture/:projectId/scan
Trigger architecture analysis scan.

**Request Body**:
```json
{
  "commitHash": "abc123",
  "deep": true
}
```

**Response 202**:
```json
{
  "scanId": "scan-123",
  "status": "initiated",
  "estimatedDuration": 120
}
```

### GET /api/v1/architecture/:projectId/graph
Get architecture graph data for visualization.

**Query Parameters**:
- `format`: `json`, `dot`, `mermaid`
- `depth`: Graph depth level

### GET /api/v1/architecture/:projectId/drift
Get architecture drift analysis.

---

## Queue API

### GET /api/v1/queue
List queue items.

**Query Parameters**:
- `page`, `limit`: Pagination
- `status`: `pending`, `processing`, `completed`, `failed`

**Response 200**:
```json
{
  "data": [
    {
      "id": "queue-123",
      "type": "code-review",
      "status": "processing",
      "progress": 65,
      "createdAt": "2026-01-24T10:00:00.000Z",
      "startedAt": "2026-01-24T10:01:00.000Z"
    }
  ]
}
```

### GET /api/v1/queue/:id
Get queue item status and progress.

### POST /api/v1/queue/:id/retry
Retry a failed queue item.

### DELETE /api/v1/queue/:id
Cancel a queue item.

---

## Admin API (Admin Role Required)

### GET /api/v1/admin/users
List all users.

**Response 200**:
```json
{
  "data": [
    {
      "id": "user-123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "status": "active",
      "createdAt": "2026-01-20T10:00:00.000Z",
      "lastLoginAt": "2026-01-24T09:30:00.000Z"
    }
  ]
}
```

### GET /api/v1/admin/audit-logs
Get audit logs.

### GET /api/v1/admin/settings
Get system settings.

### PUT /api/v1/admin/settings
Update system settings.

---

## Webhooks

### POST /api/webhooks/github
GitHub webhook handler (no auth, uses webhook secret).

**Headers**:
- `X-GitHub-Event`: Event type
- `X-Hub-Signature-256`: Webhook signature

### POST /api/webhooks/gitlab
GitLab webhook handler.

---

## Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": ["Additional error details"],
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-01-24T10:00:00.000Z"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Request validation failed
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVICE_UNAVAILABLE`: Backend service unavailable
- `CIRCUIT_BREAKER_OPEN`: Circuit breaker triggered
- `INTERNAL_SERVER_ERROR`: Server error

---

## Example Requests

### Using cURL

#### Get Projects
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/v1/projects?page=1&limit=10"
```

#### Create Project
```bash
curl -X POST http://localhost:3000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Project description",
    "repositoryUrl": "https://github.com/user/repo"
  }'
```

#### Trigger Architecture Scan
```bash
curl -X POST http://localhost:3000/api/v1/architecture/proj-123/scan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "deep": true,
    "commitHash": "abc123"
  }'
```

### Using JavaScript/Fetch

```javascript
// Get projects
const response = await fetch('/api/v1/projects', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const projects = await response.json();

// Create project
const newProject = await fetch('/api/v1/projects', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'My Project',
    repositoryUrl: 'https://github.com/user/repo'
  })
});
```

---

## Rate Limiting Details

### Headers
All responses include rate limiting headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### Limits
- **General API**: 100 requests per 15 minutes per IP
- **Authentication**: 5 requests per 15 minutes per IP
- **Admin endpoints**: Same as general API but requires admin role

### Rate Limit Response
When rate limit is exceeded:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests from this IP, please try again later",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-01-24T10:00:00.000Z"
  }
}
```

---

## Testing the API

### Postman Collection
Import the OpenAPI specification into Postman for interactive testing:
1. Open Postman
2. Import → Link → Paste OpenAPI spec URL
3. Configure environment variables (base URL, token)

### Swagger UI
Use Swagger UI for interactive API exploration:
1. Go to [Swagger Editor](https://editor.swagger.io/)
2. Load the [OpenAPI specification](./openapi.yaml)
3. Try out endpoints directly in the browser

### Authentication Testing
```bash
# Get token from auth service
TOKEN=$(curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.token')

# Use token in requests
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/v1/projects
```

---

For complete API documentation with detailed schemas, examples, and interactive testing, see the **[OpenAPI Specification](./openapi.yaml)**.

---

**Last Updated**: January 24, 2026  
**Version**: 1.0.0
