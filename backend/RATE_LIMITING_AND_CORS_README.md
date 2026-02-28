# Rate Limiting and CORS Configuration

This document describes the rate limiting and CORS (Cross-Origin Resource Sharing) implementation for the AI Code Review Platform backend.

## Overview

The backend implements comprehensive security controls including:
- **Rate Limiting**: Protects against abuse by limiting requests per user (Requirement 8.6)
- **CORS Policies**: Restricts cross-origin requests to approved domains (Requirement 8.8)

## Rate Limiting

### Implementation

Rate limiting is implemented using the `slowapi` library with Redis as the distributed storage backend. This ensures rate limits are enforced consistently across multiple backend instances.

**Key Features:**
- **100 requests per minute per user** (configurable via `RATE_LIMIT_PER_MINUTE`)
- **Per-user tracking**: Authenticated users are tracked by user ID, unauthenticated by IP address
- **Distributed**: Uses Redis for shared state across multiple instances
- **429 responses**: Returns HTTP 429 Too Many Requests when limit exceeded
- **Rate limit headers**: Includes `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers
- **Health check exemption**: Health check endpoints are not rate limited

### Configuration

Rate limiting is configured in `backend/app/core/config.py`:

```python
# Rate Limiting (Requirement 8.6)
RATE_LIMIT_PER_MINUTE: int = 100  # 100 requests per minute per user
```

Environment variable:
```bash
RATE_LIMIT_PER_MINUTE=100
```

### Usage

#### Global Rate Limiting

Rate limiting is automatically applied to all endpoints via middleware:

```python
from app.middleware.rate_limiting import configure_rate_limiting

app = FastAPI()
configure_rate_limiting(app)
```

#### Custom Rate Limits for Specific Endpoints

You can apply custom rate limits to specific endpoints:

```python
from fastapi import FastAPI, Request
from app.middleware.rate_limiting import custom_limiter

app = FastAPI()

@app.get("/expensive-operation")
@custom_limiter.limit("10/minute")  # Only 10 requests per minute
async def expensive_operation(request: Request):
    return {"status": "ok"}
```

### User Identification

The rate limiter identifies users using the following priority:

1. **Authenticated users**: Uses user ID from JWT token (`user:123`)
2. **Unauthenticated users**: Uses IP address (`ip:192.168.1.100`)

This is handled by the `get_user_identifier()` function in `backend/app/middleware/rate_limiting.py`.

### Response Format

When rate limit is exceeded, the API returns:

**Status Code:** 429 Too Many Requests

**Response Body:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

**Headers:**
```
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
```

### Redis Configuration

Rate limiting requires Redis for distributed storage:

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
```

The rate limiter automatically uses the Redis URL from settings.

## CORS Configuration

### Implementation

CORS is implemented using FastAPI's built-in `CORSMiddleware` with strict configuration to only allow approved origins.

**Key Features:**
- **Restricted origins**: Only specific approved domains can make cross-origin requests
- **Configured methods**: Only specific HTTP methods are allowed
- **Configured headers**: Only specific headers are allowed in requests
- **Exposed headers**: Rate limit headers are exposed to clients
- **Credentials support**: Allows cookies and authentication headers
- **Preflight caching**: OPTIONS requests are cached for 10 minutes

### Configuration

CORS is configured in `backend/app/core/config.py`:

```python
# CORS Configuration (Requirement 8.8)
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:8000", 
    "http://frontend:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS: bool = True
CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
CORS_ALLOW_HEADERS: List[str] = [
    "Accept",
    "Accept-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "X-CSRF-Token",
]
CORS_EXPOSE_HEADERS: List[str] = [
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "X-RateLimit-Reset",
    "Retry-After",
]
CORS_MAX_AGE: int = 600  # 10 minutes
```

### Environment Configuration

For development:
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

For production:
```bash
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Security Validation

The configuration includes validation to detect security issues:

```python
# Validate CORS configuration
warnings = settings.validate_cors_config()
```

**Checks:**
- Wildcard origins (`*`) are flagged as security risk
- Localhost origins in production are flagged
- Credentials with wildcard origin are flagged (not allowed by browsers)

### Usage

CORS is automatically configured in `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=settings.CORS_EXPOSE_HEADERS,
    max_age=settings.CORS_MAX_AGE,
)
```

### CORS Headers

**Request Headers (from client):**
- `Origin`: The origin making the request
- `Access-Control-Request-Method`: Method for preflight
- `Access-Control-Request-Headers`: Headers for preflight

**Response Headers (from server):**
- `Access-Control-Allow-Origin`: Allowed origin
- `Access-Control-Allow-Methods`: Allowed methods
- `Access-Control-Allow-Headers`: Allowed headers
- `Access-Control-Allow-Credentials`: Whether credentials are allowed
- `Access-Control-Expose-Headers`: Headers exposed to client
- `Access-Control-Max-Age`: Preflight cache duration

## Testing

### Rate Limiting Tests

Run rate limiting tests:
```bash
pytest backend/tests/test_rate_limiting.py -v
```

**Test Coverage:**
- User identifier extraction (authenticated and unauthenticated)
- Health endpoint exemption
- Custom rate limits
- Redis backend configuration
- 429 response format
- Edge cases (missing user, proxy headers)

### CORS Tests

Run CORS tests:
```bash
pytest backend/tests/test_cors_config.py -v
```

**Test Coverage:**
- Allowed origins
- Preflight requests
- Credentials support
- Allowed methods and headers
- Exposed headers
- Security validation
- Edge cases (disallowed origins, methods, headers)

### Run All Tests

```bash
pytest backend/tests/test_rate_limiting.py backend/tests/test_cors_config.py -v
```

## Production Deployment

### Rate Limiting

1. **Set appropriate rate limit:**
   ```bash
   RATE_LIMIT_PER_MINUTE=100
   ```

2. **Ensure Redis is available:**
   - Use AWS ElastiCache Redis in Multi-AZ configuration
   - Configure connection pooling
   - Enable persistence for rate limit data

3. **Monitor rate limiting:**
   - Track 429 responses in logs
   - Alert on high rate limit violations
   - Analyze patterns to detect abuse

### CORS

1. **Configure production origins:**
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```

2. **Remove development origins:**
   - Remove `localhost` and `127.0.0.1` origins
   - Remove `http://` origins (use HTTPS only)

3. **Validate configuration:**
   ```python
   warnings = settings.validate_cors_config()
   if warnings:
       logger.warning(f"CORS configuration warnings: {warnings}")
   ```

4. **Test CORS in production:**
   - Verify allowed origins work
   - Verify disallowed origins are blocked
   - Test preflight requests
   - Verify credentials work

## Troubleshooting

### Rate Limiting Issues

**Problem:** Rate limiting not working
- **Check:** Redis connection is available
- **Check:** `RATE_LIMIT_PER_MINUTE` is set correctly
- **Check:** Middleware is configured in `main.py`

**Problem:** Users getting rate limited too quickly
- **Solution:** Increase `RATE_LIMIT_PER_MINUTE`
- **Solution:** Check if multiple users share same IP (NAT)

**Problem:** Rate limits not shared across instances
- **Check:** All instances use same Redis
- **Check:** Redis is accessible from all instances

### CORS Issues

**Problem:** CORS errors in browser
- **Check:** Origin is in `ALLOWED_ORIGINS`
- **Check:** Method is in `CORS_ALLOW_METHODS`
- **Check:** Headers are in `CORS_ALLOW_HEADERS`

**Problem:** Credentials not working
- **Check:** `CORS_ALLOW_CREDENTIALS` is `True`
- **Check:** Origin is specific (not wildcard)
- **Check:** Frontend sends `credentials: 'include'`

**Problem:** Preflight requests failing
- **Check:** OPTIONS method is allowed
- **Check:** Requested headers are in allowed list
- **Check:** Requested method is in allowed list

## Requirements Validation

### Requirement 8.6: Rate Limiting
✅ **Implemented**: 100 requests per minute per user
✅ **Redis backend**: Distributed rate limiting
✅ **429 responses**: Proper error responses
✅ **Per-user tracking**: User ID or IP address

### Requirement 8.8: CORS Policies
✅ **Restricted origins**: Only approved domains
✅ **Configured methods**: Specific HTTP methods
✅ **Configured headers**: Specific request headers
✅ **Security validation**: Detects misconfigurations

## References

- **Rate Limiting Library**: [slowapi](https://github.com/laurentS/slowapi)
- **CORS Middleware**: [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- **Requirements**: See `.kiro/specs/project-code-improvements/requirements.md`
- **Design**: See `.kiro/specs/project-code-improvements/design.md`

## Files

- `backend/app/middleware/rate_limiting.py` - Rate limiting middleware
- `backend/app/core/config.py` - Configuration settings
- `backend/app/main.py` - Middleware registration
- `backend/tests/test_rate_limiting.py` - Rate limiting tests
- `backend/tests/test_cors_config.py` - CORS tests
- `backend/.env.example` - Environment variable examples
