# FastAPI Exception Handlers

## Overview

This module provides comprehensive exception handling for the FastAPI application with standardized error responses, full stack trace logging, and appropriate HTTP status code mapping.

**Validates Requirements:** 2.5, 12.1, 12.2, 12.3

## Features

### 1. Custom Exception Classes

Located in `backend/app/shared/exceptions.py`:

- **ServiceException** - Base exception for all service errors
- **AuthenticationException** - Authentication failures (401)
- **AuthorizationException** - Authorization/permission failures (403)
- **NotFoundException** - Resource not found errors (404)
- **ConflictException** - Resource conflict errors (409)
- **ValidationException** - Input validation errors (422)
- **RateLimitException** - Rate limiting errors (429)
- **TimeoutException** - Operation timeout errors (504)
- **DatabaseException** - Database operation errors (500)
- **LLMProviderException** - LLM API errors (500)
- **CircuitBreakerException** - Circuit breaker open errors (503)
- **CacheException** - Cache operation errors (500)
- **ExternalServiceException** - External service errors (502)

### 2. Exception Handlers

Located in `backend/app/api/exception_handlers.py`:

#### Service Exception Handler
Handles all custom service exceptions with:
- Automatic HTTP status code mapping
- Full stack trace logging with request context
- Standardized error response format
- Special handling for rate limit exceptions (Retry-After header)

#### Validation Exception Handler
Handles FastAPI/Pydantic validation errors with:
- Detailed field-level error information
- Standardized error response format
- Request context logging

#### Global Exception Handler
Catches all unhandled exceptions with:
- Full stack trace logging
- Generic error message (security-conscious)
- Request context capture
- HTTP 500 status code

### 3. Standardized Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "message": "Human-readable error message",
    "code": "MACHINE_READABLE_ERROR_CODE",
    "status": 400,
    "details": {
      "additional": "context"
    },
    "request_id": "optional-request-id"
  }
}
```

## Usage

### Raising Custom Exceptions

```python
from app.shared.exceptions import (
    AuthenticationException,
    NotFoundException,
    ValidationException,
)

# Authentication error
raise AuthenticationException("Invalid credentials")

# Resource not found
raise NotFoundException(
    "Project not found",
    resource_type="project",
    resource_id="123"
)

# Validation error with details
raise ValidationException(
    "Invalid email format",
    field="email",
    value="invalid-email",
    details={"expected": "user@example.com"}
)
```

### HTTP Status Code Mapping

| Exception Type | HTTP Status | Status Code |
|---------------|-------------|-------------|
| AuthenticationException | 401 | Unauthorized |
| AuthorizationException | 403 | Forbidden |
| NotFoundException | 404 | Not Found |
| ConflictException | 409 | Conflict |
| ValidationException | 422 | Unprocessable Entity |
| RateLimitException | 429 | Too Many Requests |
| TimeoutException | 504 | Gateway Timeout |
| DatabaseException | 500 | Internal Server Error |
| LLMProviderException | 500 | Internal Server Error |
| CircuitBreakerException | 503 | Service Unavailable |
| CacheException | 500 | Internal Server Error |
| ExternalServiceException | 502 | Bad Gateway |
| ServiceException (base) | 400 | Bad Request |
| Unhandled Exception | 500 | Internal Server Error |

## Logging

### Request Context

All exceptions are logged with request context including:
- HTTP method
- Request path
- Query parameters
- Client IP address
- User agent

### Stack Traces

Full stack traces are logged for:
- All service exceptions (Requirement 12.2)
- All unhandled exceptions (Requirement 12.2)

### Log Format

```python
logger.error(
    f"Service exception: {exc.__class__.__name__}",
    extra={
        "exception_type": "AuthenticationException",
        "error_code": "AUTH_FAILED",
        "error_message": "Invalid credentials",
        "error_details": {},
        "request_context": {
            "method": "POST",
            "path": "/api/auth/login",
            "query_params": {},
            "client_host": "127.0.0.1",
            "user_agent": "Mozilla/5.0..."
        }
    },
    exc_info=True  # Includes full stack trace
)
```

## Security Considerations

1. **Generic Error Messages**: Unhandled exceptions return generic messages to avoid exposing internal implementation details
2. **Conditional Details**: Exception details are only included in debug mode for unhandled exceptions
3. **Request Context**: Sensitive data is not logged (passwords, tokens, etc.)
4. **Stack Traces**: Full stack traces are logged server-side but never exposed to clients

## Testing

Comprehensive tests are located in `backend/tests/test_exception_handlers.py`:

- Exception handler behavior tests
- HTTP status code mapping tests
- Error response format tests
- Request context extraction tests
- Custom exception class tests

Run tests:
```bash
pytest backend/tests/test_exception_handlers.py -v
```

## Integration

Exception handlers are automatically registered in `backend/app/main.py`:

```python
from app.api.exception_handlers import register_exception_handlers

app = FastAPI(...)
register_exception_handlers(app)
```

## Requirements Validation

- **Requirement 2.5**: Unhandled exceptions log full stack trace and return standardized error response with HTTP 500 ✓
- **Requirement 12.1**: Global exception handler catches all unhandled exceptions ✓
- **Requirement 12.2**: Exceptions are logged with full stack trace and request context ✓
- **Requirement 12.3**: Standardized error responses with error code and message ✓

## Examples

### Example 1: Authentication Error

Request:
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "wrong-password"
}
```

Response:
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": {
    "message": "Invalid credentials",
    "code": "AUTH_FAILED",
    "status": 401
  }
}
```

### Example 2: Validation Error

Request:
```http
POST /api/projects
Content-Type: application/json

{
  "name": "",
  "repository_url": "not-a-url"
}
```

Response:
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION_ERROR",
    "status": 422,
    "details": {
      "errors": [
        {
          "field": "body.name",
          "message": "ensure this value has at least 1 characters",
          "type": "value_error.any_str.min_length"
        },
        {
          "field": "body.repository_url",
          "message": "invalid or missing URL scheme",
          "type": "value_error.url.scheme"
        }
      ]
    }
  }
}
```

### Example 3: Rate Limit Error

Request:
```http
GET /api/projects
```

Response:
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json

{
  "error": {
    "message": "Rate limit exceeded",
    "code": "RATE_LIMIT_EXCEEDED",
    "status": 429
  }
}
```

### Example 4: Unhandled Error

Request:
```http
GET /api/projects/123
```

Response:
```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": {
    "message": "An internal server error occurred",
    "code": "INTERNAL_SERVER_ERROR",
    "status": 500
  }
}
```

Server logs:
```
ERROR app.api.exception_handlers:exception_handlers.py:222 Unhandled exception: ValueError
Traceback (most recent call last):
  File "app/api/v1/endpoints/projects.py", line 45, in get_project
    result = some_function()
ValueError: Unexpected error
```

## Future Enhancements

1. **Request ID Tracking**: Add request ID to all error responses for tracing
2. **Error Metrics**: Track error rates by type for monitoring
3. **Custom Error Pages**: Provide HTML error pages for browser requests
4. **Localization**: Support multiple languages for error messages
5. **Error Recovery**: Implement automatic retry logic for transient errors
