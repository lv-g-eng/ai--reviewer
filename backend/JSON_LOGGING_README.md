# JSON Logging Configuration

## Overview

This document describes the structured JSON logging implementation for the AI Code Review Platform backend services. The logging system is designed for production environments with centralized log aggregation systems like CloudWatch Logs or ELK stack.

**Validates Requirement 7.1**: THE Monitoring_System SHALL collect application logs from all services using structured JSON format

## Features

### Structured JSON Format

All logs are output in structured JSON format with the following standard fields:

- **timestamp**: ISO 8601 UTC timestamp
- **level**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **message**: Log message
- **logger**: Logger name (module path)
- **service_name**: Service identifier (default: "backend-api")
- **request_id**: Unique request identifier (UUID)
- **user_id**: Authenticated user ID (if available)
- **correlation_id**: Distributed tracing correlation ID

### Request Context Tracking

The logging system automatically captures request context through middleware:

- **Request ID**: Generated UUID for each request or extracted from `X-Request-ID` header
- **User ID**: Extracted from authenticated user in request state
- **Correlation ID**: Extracted from `X-Correlation-ID` header or generated UUID

These context fields are automatically included in all log messages within a request.

### Sensitive Data Masking

The logging system masks sensitive data in log messages:

- Passwords in connection strings
- API keys and tokens
- JWT tokens
- Database credentials
- Webhook secrets

## Configuration

### Basic Setup

```python
from app.core.logging_config import setup_logging

# Configure JSON logging
setup_logging(
    level="INFO",              # Log level
    enable_json=True,          # Enable JSON format
    service_name="backend-api" # Service identifier
)
```

### Environment Variables

- `LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `SERVICE_NAME`: Service identifier for multi-service deployments

### Log Levels

The system supports standard Python log levels:

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious errors

## Usage

### Basic Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log messages with automatic context
logger.info("User logged in")
logger.warning("Slow query detected", extra={'duration': 1500})
logger.error("Database connection failed", extra={'database': 'postgresql'})
```

### Request Context

The request context is automatically set by the middleware, but you can also set it manually:

```python
from app.core.logging_config import set_request_context, clear_request_context

# Set request context
set_request_context(
    request_id="req-123",
    user_id="user-456",
    correlation_id="corr-789"
)

# All logs will include these context fields
logger.info("Processing request")

# Clear context after request
clear_request_context()
```

### Exception Logging

```python
from app.core.logging_config import log_exception

try:
    # Some operation
    process_data()
except Exception as e:
    # Log exception with context
    log_exception(e, context={
        'operation': 'process_data',
        'input_size': 1000
    })
```

### Extra Fields

Add custom fields to log messages using the `extra` parameter:

```python
logger.info(
    "Request completed",
    extra={
        'method': 'GET',
        'url': '/api/users',
        'status_code': 200,
        'duration': 123.45
    }
)
```

## Log Output Format

### Example JSON Log Entry

```json
{
  "timestamp": "2024-02-23T10:30:45.123456+00:00",
  "level": "INFO",
  "logger": "app.api.v1.endpoints.users",
  "message": "Request completed",
  "service_name": "backend-api",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "correlation_id": "corr-456",
  "method": "GET",
  "url": "/api/v1/users",
  "status_code": 200,
  "duration_ms": 123.45
}
```

## Integration with Centralized Logging

### CloudWatch Logs

The JSON format is compatible with CloudWatch Logs Insights queries:

```sql
fields @timestamp, level, message, request_id, user_id, duration_ms
| filter level = "ERROR"
| sort @timestamp desc
| limit 100
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

The JSON format can be directly ingested by Logstash:

```ruby
input {
  file {
    path => "/var/log/app/*.log"
    codec => json
  }
}

filter {
  # Add any additional processing
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

### Splunk

The JSON format is compatible with Splunk HTTP Event Collector (HEC):

```python
# Configure Splunk handler
import logging
from splunk_handler import SplunkHandler

splunk_handler = SplunkHandler(
    host='splunk.example.com',
    port=8088,
    token='your-hec-token',
    index='app-logs'
)
logging.getLogger().addHandler(splunk_handler)
```

## Middleware Integration

The logging middleware is automatically configured in `app/main.py`:

```python
from app.core.logging_config import log_request

# Request Logging Middleware
app.middleware("http")(log_request)
```

This middleware:
1. Generates or extracts request ID and correlation ID
2. Extracts user ID from authenticated user
3. Sets request context for all logs
4. Logs request start with method, URL, client IP
5. Logs request completion with status code and duration
6. Logs request failures with error details
7. Adds correlation headers to response
8. Clears request context after request

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information (disabled in production)
- **INFO**: Normal operational messages
- **WARNING**: Potentially problematic situations
- **ERROR**: Errors that need attention
- **CRITICAL**: Critical failures requiring immediate action

### 2. Include Relevant Context

Always include relevant context in log messages:

```python
# Good
logger.info("User created", extra={'user_id': user.id, 'email': user.email})

# Bad
logger.info("User created")
```

### 3. Avoid Logging Sensitive Data

Never log sensitive data directly:

```python
# Bad
logger.info(f"User password: {password}")

# Good
logger.info("User password updated", extra={'user_id': user.id})
```

### 4. Use Structured Fields

Use the `extra` parameter for structured data instead of string formatting:

```python
# Good
logger.info("Query executed", extra={'duration': 123.45, 'rows': 100})

# Bad
logger.info(f"Query executed in 123.45ms, returned 100 rows")
```

### 5. Log at Appropriate Points

- Log at service boundaries (API requests, database queries, external API calls)
- Log important business events (user registration, order placement)
- Log errors and exceptions with full context
- Avoid excessive logging in tight loops

## Testing

Run the JSON logging tests:

```bash
pytest tests/test_json_logging.py -v
```

The test suite validates:
- JSON formatter includes all required fields
- Timestamp format is ISO 8601
- Request context is properly tracked
- Extra fields are included in output
- Sensitive data is masked
- Exception logging includes context
- Integration with request middleware

## Troubleshooting

### Logs Not in JSON Format

Check that JSON logging is enabled:

```python
setup_logging(enable_json=True)
```

### Missing Request Context

Ensure the request middleware is configured:

```python
app.middleware("http")(log_request)
```

### Duplicate Log Entries

Clear existing handlers before setup:

```python
root_logger = logging.getLogger()
root_logger.handlers.clear()
```

### Performance Impact

JSON formatting has minimal performance impact. For high-throughput services:

1. Use appropriate log levels (INFO or WARNING in production)
2. Avoid logging in tight loops
3. Use asynchronous log handlers for high-volume logging

## Related Documentation

- [Monitoring and Observability](../docs/MONITORING.md)
- [CloudWatch Integration](../docs/CLOUDWATCH_INTEGRATION.md)
- [Error Handling](./app/api/EXCEPTION_HANDLERS_README.md)
- [Audit Logging](./AUDIT_LOGGING_README.md)

## Requirements Validation

This implementation validates:

- **Requirement 7.1**: THE Monitoring_System SHALL collect application logs from all services using structured JSON format
  - ✅ All logs output in structured JSON format
  - ✅ Includes timestamp, level, message, request_id, user_id, service_name
  - ✅ Request context automatically captured via middleware
  - ✅ Compatible with CloudWatch Logs and ELK stack
  - ✅ Sensitive data masking implemented
  - ✅ Comprehensive test coverage

## Future Enhancements

1. **Async Log Handlers**: Implement asynchronous log handlers for high-volume logging
2. **Log Sampling**: Add sampling for high-frequency log messages
3. **Structured Metrics**: Integrate with Prometheus for metrics collection
4. **Distributed Tracing**: Full OpenTelemetry integration for distributed tracing
5. **Log Aggregation**: Direct integration with CloudWatch Logs API
