# Structured Logging Implementation

## Overview

This document describes the structured logging implementation for the AI Code Review Platform backend, completed as part of Task 2.5 in the Production Environment Migration specification.

## Requirements Validated

- **Requirement 7.1**: Structured logging using JSON format for easy log aggregation and analysis
- **Requirement 7.2**: Log all API requests including request path, method, response status, and response time
- **Requirement 7.6**: Configure log rotation, retaining logs for the last 30 days

## Implementation Details

### 1. JSON Structured Logging (Requirement 7.1)

**File**: `backend/app/core/logging_config.py`

The logging system uses `pythonjsonlogger` to output structured JSON logs with the following fields:

- `timestamp`: ISO 8601 UTC timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger`: Logger name
- `message`: Log message
- `service_name`: Service identifier (configurable via environment)
- `request_id`: Unique request identifier (UUID)
- `user_id`: Authenticated user ID (if available)
- `correlation_id`: Distributed tracing correlation ID
- Additional context fields (method, url, status_code, duration_ms, client_ip, etc.)

**Example JSON log entry**:
```json
{
  "timestamp": "2026-03-03T05:02:32.411158+00:00",
  "level": "INFO",
  "logger": "app.api",
  "message": "Request completed",
  "service_name": "backend-api",
  "request_id": "req-12345",
  "user_id": "user-67890",
  "correlation_id": "corr-abcde",
  "method": "GET",
  "url": "/api/v1/projects",
  "status_code": 200,
  "duration_ms": 123.45,
  "client_ip": "192.168.1.100"
}
```

### 2. Request Logging Middleware (Requirement 7.2)

**File**: `backend/app/core/logging_config.py` (function: `log_request`)
**Integration**: `backend/app/main.py` (line: `app.middleware("http")(log_request)`)

The request logging middleware automatically captures and logs:

- **Request ID**: Generated UUID or extracted from `X-Request-ID` header
- **Correlation ID**: Extracted from `X-Correlation-ID` header or generated
- **User ID**: Extracted from authenticated user (set by auth middleware)
- **HTTP Method**: GET, POST, PUT, DELETE, etc.
- **Request URL**: Full request URL
- **Client IP**: Client IP address
- **User Agent**: Browser/client user agent
- **Response Status Code**: HTTP status code (200, 404, 500, etc.)
- **Response Time**: Request duration in milliseconds

The middleware logs two events per request:
1. **Request started**: When the request is received
2. **Request completed**: When the response is sent (includes status code and duration)

### 3. Log Rotation with 30-Day Retention (Requirement 7.6)

**File**: `backend/app/core/logging_config.py` (function: `setup_logging`)

Log rotation is implemented using Python's `TimedRotatingFileHandler` with the following configuration:

- **Rotation Time**: Midnight (UTC)
- **Rotation Interval**: 1 day
- **Backup Count**: 30 days (automatically deletes logs older than 30 days)
- **Log File Location**: `logs/app.log` (configurable via `LOG_DIR` environment variable)
- **Rotated File Format**: `app.log.YYYY-MM-DD` (e.g., `app.log.2026-03-02`)

**Configuration**:
```python
file_handler = TimedRotatingFileHandler(
    filename=log_file_path,
    when='midnight',      # Rotate at midnight
    interval=1,           # Rotate every 1 day
    backupCount=30,       # Keep 30 days of logs
    encoding='utf-8',
    utc=True              # Use UTC for rotation timing
)
file_handler.suffix = "%Y-%m-%d"  # Date suffix for rotated files
```

### 4. CloudWatch Integration (Requirement 7.2, 7.10)

**File**: `backend/app/core/cloudwatch_handler.py`

The logging system includes optional CloudWatch Logs integration:

- **Log Group**: `/aws/application/{service_name}`
- **Log Stream**: `{environment}/{instance_id}`
- **Retention**: 30 days (configured automatically)
- **Graceful Fallback**: If CloudWatch is unavailable, logs continue to local files

CloudWatch integration is enabled by default but can be disabled via environment variables:
- `CLOUDWATCH_ENABLED=false` to disable
- Requires AWS credentials configured

## Log Handlers

The logging system configures three handlers:

1. **Console Handler**: Outputs to stdout (for container environments)
2. **File Handler**: Writes to local file with rotation (30-day retention)
3. **CloudWatch Handler**: Sends logs to AWS CloudWatch (optional, 30-day retention)

All handlers use the same JSON formatter for consistency.

## Request Context Management

The logging system uses Python's `contextvars` to maintain request context across async operations:

```python
from app.core.logging_config import set_request_context, clear_request_context

# Set context at request start
set_request_context(
    request_id="req-12345",
    user_id="user-67890",
    correlation_id="corr-abcde"
)

# All logs within this context will include these fields
logger.info("Processing request")  # Includes request_id, user_id, correlation_id

# Clear context at request end
clear_request_context()
```

## Configuration

### Environment Variables

- `LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: INFO
- `LOG_DIR`: Directory for log files - default: logs
- `SERVICE_NAME`: Service identifier for multi-service deployments - default: backend-api
- `ENVIRONMENT`: Environment name (development, staging, production) - default: development
- `CLOUDWATCH_ENABLED`: Enable CloudWatch integration - default: true
- `AWS_REGION`: AWS region for CloudWatch - default: us-east-1

### Example Configuration

```bash
# .env.production
LOG_LEVEL=INFO
LOG_DIR=/var/log/backend
SERVICE_NAME=backend-api
ENVIRONMENT=production
CLOUDWATCH_ENABLED=true
AWS_REGION=us-east-1
```

## Testing

### Unit Tests

**File**: `backend/tests/test_json_logging.py`

The test suite includes:

1. **JSON Formatter Tests**: Verify all required fields are included
2. **Request Context Tests**: Verify context variables work correctly
3. **Log Rotation Tests**: Verify rotation configuration (30-day retention)
4. **Exception Logging Tests**: Verify exceptions are logged with context

### Running Tests

```bash
cd backend
python -m pytest tests/test_json_logging.py -v
```

## Verification

To verify the implementation:

```bash
cd backend
python -c "from app.core.logging_config import setup_logging; from logging.handlers import TimedRotatingFileHandler; import logging; setup_logging(level='INFO', enable_json=True); handlers = [h for h in logging.getLogger().handlers if isinstance(h, TimedRotatingFileHandler)]; h = handlers[0] if handlers else None; print(f'Rotation: when={h.when}, interval={h.interval}, backupCount={h.backupCount}') if h else print('No rotating handler')"
```

Expected output:
```
Rotation: when=MIDNIGHT, interval=86400, backupCount=30
```

## Integration with Main Application

The logging system is initialized in `backend/app/main.py` during application startup:

```python
from app.core.logging_config import setup_logging, log_request

# Initialize logging
setup_logging(level=settings.LOG_LEVEL, enable_json=True)

# Add request logging middleware
app.middleware("http")(log_request)
```

## Log File Management

### Local Development

In local development, logs are written to `logs/app.log` with daily rotation:

```
logs/
├── app.log              # Current log file
├── app.log.2026-03-02   # Yesterday's logs
├── app.log.2026-03-01   # 2 days ago
└── ...                  # Up to 30 days
```

### Production Environment

In production, logs are:
1. Written to local files with rotation (backup/debugging)
2. Sent to CloudWatch Logs (centralized monitoring)
3. Both retain logs for 30 days

### Log Cleanup

Old log files are automatically deleted by the `TimedRotatingFileHandler`:
- Files older than 30 days are removed during rotation
- No manual cleanup required

## Monitoring and Alerting

The structured JSON format enables:

1. **Log Aggregation**: Easy parsing by log aggregation tools (CloudWatch, ELK, Splunk)
2. **Metrics Extraction**: Extract metrics from log fields (response time, error rate)
3. **Alerting**: Set up alerts based on log patterns (error rate > 5%, response time > 500ms)
4. **Distributed Tracing**: Use correlation_id to trace requests across services

## Best Practices

1. **Use Structured Fields**: Add context as extra fields, not in the message
   ```python
   # Good
   logger.info("User login", extra={'user_id': user_id, 'ip': ip_address})
   
   # Bad
   logger.info(f"User {user_id} logged in from {ip_address}")
   ```

2. **Set Request Context**: Always set request context in middleware
   ```python
   set_request_context(request_id=request_id, user_id=user_id)
   ```

3. **Log Exceptions with Context**: Use `log_exception` for structured exception logging
   ```python
   from app.core.logging_config import log_exception
   
   try:
       # ... code ...
   except Exception as e:
       log_exception(e, context={'user_id': user_id, 'operation': 'create_project'})
   ```

4. **Mask Sensitive Data**: Use `mask_sensitive_in_logs` for sensitive information
   ```python
   from app.core.logging_config import mask_sensitive_in_logs
   
   safe_message = mask_sensitive_in_logs(error_message)
   logger.error(safe_message)
   ```

## Troubleshooting

### Issue: Logs not rotating

**Solution**: Check that the log directory is writable and the application has permission to create/delete files.

### Issue: CloudWatch logs not appearing

**Solution**: 
1. Verify AWS credentials are configured
2. Check `CLOUDWATCH_ENABLED` environment variable
3. Verify IAM permissions for CloudWatch Logs

### Issue: Log file growing too large

**Solution**: The rotation should handle this automatically. If not:
1. Check `backupCount` is set to 30
2. Verify rotation is happening at midnight
3. Check disk space

## Summary

The structured logging implementation provides:

✅ **JSON structured logging** for easy aggregation and analysis (Requirement 7.1)
✅ **Request logging middleware** capturing all API requests with required fields (Requirement 7.2)
✅ **Log rotation** with 30-day retention for compliance (Requirement 7.6)
✅ **CloudWatch integration** for centralized monitoring (optional)
✅ **Request context tracking** for distributed tracing
✅ **Sensitive data masking** for security
✅ **Comprehensive test coverage** for reliability

All requirements have been validated and the implementation is production-ready.
