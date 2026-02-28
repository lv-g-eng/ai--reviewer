# Structured Error Logging

This document describes the structured error logging system implemented for the AI Code Review Platform.

## Overview

The structured error logging system provides comprehensive error tracking and debugging capabilities by:
- Logging all exceptions with full stack traces
- Including detailed request context in error logs
- Using JSON format for easy parsing by log aggregation tools
- Integrating seamlessly with the exception handlers

**Validates Requirements:** 12.2

## Features

### 1. JSON Logging Format

All error logs are output in JSON format using the `CustomJsonFormatter` from `app.core.logging_config`. This enables:
- Easy parsing by log aggregation tools (CloudWatch, ELK, Splunk)
- Structured querying and filtering
- Automated alerting based on log fields
- Integration with monitoring dashboards

Example JSON log output:
```json
{
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "level": "ERROR",
  "logger": "app.api.exception_handlers",
  "message": "Service exception: DatabaseException: Connection failed",
  "exception_type": "DatabaseException",
  "exception_module": "app.shared.exceptions",
  "error_code": "DB_CONNECTION_ERROR",
  "error_message": "Connection failed",
  "status_code": 500,
  "request_context": {
    "method": "POST",
    "path": "/api/v1/projects",
    "request_id": "abc123-def456",
    "user_id": "user_789",
    "client_host": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "url": "https://api.example.com/api/v1/projects",
    "scheme": "https",
    "host": "api.example.com"
  },
  "stack_trace": "Traceback (most recent call last):\n  File..."
}
```

### 2. Comprehensive Request Context

Every error log includes detailed request context:

| Field | Description | Example |
|-------|-------------|---------|
| `method` | HTTP method | `"POST"` |
| `path` | Request path | `"/api/v1/projects"` |
| `request_id` | Unique request identifier | `"abc123-def456"` |
| `user_id` | Authenticated user ID | `"user_789"` |
| `client_host` | Client IP address | `"192.168.1.100"` |
| `user_agent` | Client user agent | `"Mozilla/5.0..."` |
| `query_params` | Query parameters | `{"page": "1", "limit": "10"}` |
| `headers` | Safe request headers | `{"content-type": "application/json"}` |
| `url` | Full request URL | `"https://api.example.com/api/v1/projects"` |
| `scheme` | URL scheme | `"https"` |
| `host` | Request hostname | `"api.example.com"` |

**Security Note:** Sensitive headers (Authorization, API keys) are excluded from logs.

### 3. Full Stack Traces

All exceptions are logged with complete stack traces using Python's `traceback.format_exc()` and `exc_info=True`. This provides:
- Complete call stack at the point of exception
- File names and line numbers
- Local variable values (when available)
- Nested exception chains

### 4. Exception-Specific Context

Different exception types include additional context:

#### LLMProviderException
```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4"
}
```

#### CircuitBreakerException
```json
{
  "service_name": "github_api",
  "failure_count": 5
}
```

#### DatabaseException
```json
{
  "database": "postgresql",
  "operation": "insert"
}
```

#### AuthorizationException
```json
{
  "resource": "project",
  "action": "delete"
}
```

#### ExternalServiceException
```json
{
  "service_name": "github",
  "service_status_code": 503
}
```

#### TimeoutException
```json
{
  "operation": "llm_analysis",
  "timeout_seconds": 30.0
}
```

## Usage

### Automatic Logging

Error logging is automatic for all exceptions. The exception handlers in `app.api.exception_handlers` automatically log:

1. **Service Exceptions** - Custom application exceptions
2. **Validation Errors** - Pydantic/FastAPI validation failures
3. **Unhandled Exceptions** - Any unexpected errors

No additional code is required in your endpoints.

### Request ID Tracking

To enable request ID tracking across your application:

```python
from fastapi import Request

async def my_endpoint(request: Request):
    # Request ID is automatically available
    request_id = request.state.request_id
    
    # Use it in your logs
    logger.info("Processing request", extra={"request_id": request_id})
```

The request ID is automatically added by the `log_request` middleware in `app.core.logging_config`.

### User ID Tracking

For authenticated endpoints, user ID is automatically extracted from:
- `request.state.user_id`
- `request.state.user.id`
- `request.state.user["id"]`

To ensure user ID is logged, set it in your authentication middleware:

```python
async def auth_middleware(request: Request, call_next):
    # Authenticate user
    user = await authenticate(request)
    
    # Set user ID for logging
    request.state.user_id = user.id
    
    response = await call_next(request)
    return response
```

## Log Aggregation

### CloudWatch Integration

Logs are automatically sent to CloudWatch when configured in `app.core.logging_config`. The JSON format enables:

```
# Query all errors for a specific user
fields @timestamp, message, error_code, request_context.path
| filter request_context.user_id = "user_789"
| filter level = "ERROR"
| sort @timestamp desc

# Query errors by endpoint
fields @timestamp, message, exception_type, status_code
| filter request_context.path = "/api/v1/projects"
| filter level = "ERROR"
| stats count() by exception_type

# Query errors with high response times
fields @timestamp, message, request_context.duration_ms
| filter level = "ERROR"
| filter request_context.duration_ms > 1000
```

### ELK Stack Integration

For Elasticsearch/Logstash/Kibana:

1. **Logstash Configuration:**
```ruby
input {
  file {
    path => "/var/log/app/*.log"
    codec => json
  }
}

filter {
  # Logs are already in JSON format
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

2. **Kibana Queries:**
- Filter by `exception_type`
- Group by `request_context.path`
- Visualize error rates over time
- Create alerts for specific error codes

## Monitoring and Alerting

### Recommended Alerts

1. **High Error Rate**
   - Condition: Error count > 10 per minute
   - Action: Send to on-call engineer

2. **Critical Exceptions**
   - Condition: `exception_type` in [DatabaseException, CircuitBreakerException]
   - Action: Page on-call team

3. **Specific User Errors**
   - Condition: Same `user_id` with > 5 errors in 1 minute
   - Action: Investigate potential abuse or bug

4. **Endpoint Failures**
   - Condition: Specific `request_context.path` with > 50% error rate
   - Action: Disable endpoint or rollback deployment

### Metrics to Track

- Error rate by endpoint
- Error rate by exception type
- Error rate by user
- Average error response time
- Stack trace frequency (identify common issues)

## Best Practices

### 1. Use Appropriate Exception Types

Always use the most specific exception type:

```python
# Good
raise DatabaseException(
    message="Failed to connect to PostgreSQL",
    database="postgresql",
    operation="connect"
)

# Bad
raise Exception("Database error")
```

### 2. Include Contextual Details

Provide helpful details in exception messages:

```python
# Good
raise NotFoundException(
    message=f"Project with ID {project_id} not found",
    resource_type="project",
    resource_id=project_id
)

# Bad
raise NotFoundException(message="Not found")
```

### 3. Don't Log Sensitive Data

Never include sensitive data in exception messages or details:

```python
# Bad - exposes password
raise AuthenticationException(
    message=f"Invalid password: {password}"
)

# Good
raise AuthenticationException(
    message="Invalid credentials"
)
```

### 4. Use Error Codes

Always provide error codes for programmatic error handling:

```python
raise ValidationException(
    message="Email format is invalid",
    field="email",
    error_code="INVALID_EMAIL_FORMAT"
)
```

## Testing

### Unit Tests

Test error logging in `backend/tests/test_exception_handlers.py`:

```python
def test_error_logging_includes_request_context(client, caplog):
    """Test that errors include full request context"""
    response = client.post("/api/v1/invalid")
    
    # Check log contains request context
    assert "request_context" in caplog.records[0].extra
    assert "request_id" in caplog.records[0].extra["request_context"]
    assert "method" in caplog.records[0].extra["request_context"]
```

### Integration Tests

Test end-to-end error logging:

```python
async def test_error_logging_with_authentication(client, auth_token):
    """Test that errors include user ID for authenticated requests"""
    response = await client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"invalid": "data"}
    )
    
    # Verify user ID is in logs
    # Check log aggregation system
```

## Troubleshooting

### Logs Not in JSON Format

**Problem:** Logs are plain text instead of JSON

**Solution:** Ensure `setup_logging(enable_json=True)` is called in `app.main.py`

### Missing Request Context

**Problem:** Request context fields are missing from logs

**Solution:** Ensure `log_request` middleware is registered before exception handlers

### Missing User ID

**Problem:** User ID not appearing in logs for authenticated requests

**Solution:** Set `request.state.user_id` in your authentication middleware

### Stack Traces Too Large

**Problem:** Stack traces consuming too much log storage

**Solution:** Configure log retention policies in CloudWatch or your log aggregation tool

## Related Documentation

- [Exception Handlers](./EXCEPTION_HANDLERS_README.md) - Exception handling system
- [Logging Configuration](../core/logging_config.py) - JSON logging setup
- [Custom Exceptions](../shared/exceptions.py) - Exception hierarchy

## Requirements Validation

This implementation validates the following requirements:

- **Requirement 12.2:** Log exceptions with full stack traces and request context
- **Requirement 7.1:** Use structured JSON format for log aggregation
- **Requirement 7.2:** Aggregate logs in centralized logging system

## Future Enhancements

1. **Distributed Tracing:** Integrate with OpenTelemetry for cross-service tracing
2. **Log Sampling:** Sample high-volume logs to reduce costs
3. **Anomaly Detection:** Use ML to detect unusual error patterns
4. **Error Grouping:** Automatically group similar errors for easier triage
