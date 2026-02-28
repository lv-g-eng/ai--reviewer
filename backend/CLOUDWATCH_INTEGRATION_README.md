# CloudWatch Logs Integration

This document describes the CloudWatch Logs integration for centralized logging.

## Overview

The application integrates with AWS CloudWatch Logs to provide centralized log aggregation and management. This integration satisfies:

- **Requirement 7.2**: Aggregate logs in a centralized logging system (CloudWatch)
- **Requirement 7.10**: Retain logs for 30 days

## Features

### Centralized Logging (Requirement 7.2)

All application logs are automatically sent to CloudWatch Logs in addition to local console and file outputs. This enables:

- **Centralized log aggregation** across multiple instances
- **Searchable logs** using CloudWatch Logs Insights
- **Log streaming** for real-time monitoring
- **Integration** with CloudWatch alarms and metrics

### 30-Day Log Retention (Requirement 7.10)

Log retention is automatically configured to 30 days when log groups are created or updated. This ensures:

- **Compliance** with data retention policies
- **Cost optimization** by automatically deleting old logs
- **Consistent retention** across all log groups

### Graceful Fallback

The CloudWatch integration is designed to fail gracefully:

- If AWS credentials are not available, logging continues to console/file
- If CloudWatch API calls fail, the application continues running
- All errors are logged with appropriate warnings

## Configuration

### Environment Variables

Configure CloudWatch integration using environment variables:

```bash
# Enable/disable CloudWatch logging
CLOUDWATCH_ENABLED=true

# AWS region for CloudWatch Logs
AWS_REGION=us-east-1

# Service identification
SERVICE_NAME=backend-api
ENVIRONMENT=production
INSTANCE_ID=i-1234567890abcdef0
```

### AWS Credentials

CloudWatch integration requires AWS credentials with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:PutRetentionPolicy"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/application/*"
    }
  ]
}
```

Credentials can be provided via:
- IAM instance role (recommended for EC2)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- AWS credentials file (`~/.aws/credentials`)

### Log Group and Stream Naming

**Log Group**: `/aws/application/{SERVICE_NAME}`
- Example: `/aws/application/backend-api`

**Log Stream**: `{ENVIRONMENT}/{INSTANCE_ID}`
- Example: `production/i-1234567890abcdef0`

This naming convention enables:
- Grouping logs by service
- Filtering logs by environment
- Identifying logs by instance

## Usage

### Basic Setup

The CloudWatch handler is automatically configured when you call `setup_logging()`:

```python
from app.core.logging_config import setup_logging

# Enable CloudWatch logging (default)
setup_logging(
    level="INFO",
    enable_json=True,
    enable_cloudwatch=True
)
```

### Custom Configuration

For custom CloudWatch configuration:

```python
from app.core.logging_config import setup_logging
from app.core.cloudwatch_handler import CloudWatchConfig

# Create custom configuration
config = CloudWatchConfig(
    log_group="/custom/log-group",
    log_stream="custom-stream",
    region_name="us-west-2",
    retention_days=30,
    enabled=True
)

# Setup logging with custom config
setup_logging(
    level="INFO",
    enable_cloudwatch=True,
    cloudwatch_config=config
)
```

### Adding CloudWatch to Existing Logger

To add CloudWatch logging to an existing logger:

```python
from app.core.cloudwatch_handler import add_cloudwatch_handler_to_logger
import logging

logger = logging.getLogger('my_module')
success = add_cloudwatch_handler_to_logger(logger)

if success:
    logger.info("CloudWatch logging enabled")
else:
    logger.warning("CloudWatch logging unavailable")
```

### Checking CloudWatch Status

To check CloudWatch integration status:

```python
from app.core.cloudwatch_handler import get_cloudwatch_status

status = get_cloudwatch_status()

print(f"Enabled: {status['enabled']}")
print(f"Connected: {status['connected']}")
print(f"Log Group: {status['log_group']}")
print(f"Log Stream: {status['log_stream']}")
print(f"Region: {status['region']}")
print(f"Retention: {status['retention_days']} days")

if status['error']:
    print(f"Error: {status['error']}")
```

## Log Format

Logs sent to CloudWatch use structured JSON format with the following fields:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456+00:00",
  "level": "INFO",
  "logger": "app.services.analyzer",
  "message": "Analysis completed",
  "service_name": "backend-api",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "correlation_id": "abc-def-ghi",
  "duration_ms": 1234,
  "status_code": 200
}
```

This structured format enables:
- **Efficient searching** using CloudWatch Logs Insights
- **Filtering** by any field
- **Aggregation** and analysis
- **Correlation** across distributed services

## CloudWatch Logs Insights Queries

### Find Errors in Last Hour

```sql
fields @timestamp, level, message, error
| filter level = "ERROR"
| sort @timestamp desc
| limit 100
```

### Analyze API Response Times

```sql
fields @timestamp, message, duration_ms, status_code
| filter duration_ms > 1000
| stats avg(duration_ms), max(duration_ms), count() by status_code
```

### Track User Activity

```sql
fields @timestamp, user_id, message, method, url
| filter user_id = "user123"
| sort @timestamp desc
```

### Find Slow Requests

```sql
fields @timestamp, request_id, duration_ms, url
| filter duration_ms > 500
| sort duration_ms desc
| limit 50
```

### Error Rate by Service

```sql
fields @timestamp, service_name, level
| filter level = "ERROR"
| stats count() as error_count by service_name
| sort error_count desc
```

## Monitoring and Alerting

### CloudWatch Alarms

Create alarms based on log patterns:

```bash
# Alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name high-error-rate \
  --alarm-description "Alert when error rate exceeds 5%" \
  --metric-name ErrorCount \
  --namespace AWS/Logs \
  --statistic Sum \
  --period 300 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold
```

### Log Metric Filters

Create metric filters to track specific patterns:

```bash
# Track authentication failures
aws logs put-metric-filter \
  --log-group-name /aws/application/backend-api \
  --filter-name AuthFailures \
  --filter-pattern '[timestamp, level=ERROR, logger, message="Authentication failed*"]' \
  --metric-transformations \
    metricName=AuthFailureCount,metricNamespace=Application,metricValue=1
```

## Troubleshooting

### CloudWatch Handler Not Created

**Symptom**: Logs appear in console but not in CloudWatch

**Possible Causes**:
1. AWS credentials not configured
2. Insufficient IAM permissions
3. CloudWatch disabled via `CLOUDWATCH_ENABLED=false`
4. Network connectivity issues

**Solution**:
```python
from app.core.cloudwatch_handler import get_cloudwatch_status

status = get_cloudwatch_status()
print(f"Error: {status['error']}")
```

### Access Denied Errors

**Symptom**: `AccessDeniedException` in logs

**Solution**: Ensure IAM role/user has required permissions:
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`
- `logs:DescribeLogGroups`
- `logs:PutRetentionPolicy`

### Logs Not Appearing Immediately

**Symptom**: Logs appear in CloudWatch with delay

**Explanation**: Logs are batched and sent every 5 seconds for efficiency. This is normal behavior.

### High CloudWatch Costs

**Symptom**: Unexpected CloudWatch Logs costs

**Solutions**:
1. Reduce log verbosity (use INFO instead of DEBUG)
2. Filter out noisy logs
3. Verify 30-day retention is configured
4. Consider log sampling for high-volume logs

## Testing

### Unit Tests

Run CloudWatch integration tests:

```bash
cd backend
pytest tests/test_cloudwatch_integration.py -v
```

### Manual Testing

Test CloudWatch integration manually:

```python
import logging
from app.core.logging_config import setup_logging

# Setup logging with CloudWatch
setup_logging(level="INFO", enable_cloudwatch=True)

# Create test logger
logger = logging.getLogger(__name__)

# Send test logs
logger.info("Test log message", extra={'test_field': 'test_value'})
logger.warning("Test warning")
logger.error("Test error", extra={'error_code': 'TEST_ERROR'})

# Check CloudWatch Logs console after 5-10 seconds
```

### Verify in AWS Console

1. Open AWS CloudWatch Console
2. Navigate to Logs → Log groups
3. Find log group: `/aws/application/backend-api`
4. Click on log stream: `{environment}/{instance_id}`
5. Verify logs appear with JSON structure

## Best Practices

### 1. Use Structured Logging

Always use structured logging with extra fields:

```python
logger.info(
    "User action completed",
    extra={
        'user_id': user.id,
        'action': 'update_profile',
        'duration_ms': 123
    }
)
```

### 2. Include Request Context

Request context (request_id, user_id, correlation_id) is automatically included when using the logging middleware.

### 3. Mask Sensitive Data

Sensitive data is automatically masked by the logging configuration. Never log:
- Passwords
- API keys
- Tokens
- Credit card numbers
- Personal identification numbers

### 4. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious errors

### 5. Monitor CloudWatch Costs

- Use 30-day retention (configured automatically)
- Avoid excessive DEBUG logging in production
- Use log sampling for high-volume logs
- Monitor CloudWatch Logs costs in AWS Cost Explorer

## Integration with Other Services

### CloudWatch Metrics

Create custom metrics from logs:

```python
# Log with metric data
logger.info(
    "API request completed",
    extra={
        'metric_name': 'api_response_time',
        'metric_value': response_time_ms,
        'metric_unit': 'Milliseconds'
    }
)
```

### CloudWatch Alarms

Set up alarms based on log patterns or metrics derived from logs.

### AWS Lambda

CloudWatch Logs can trigger Lambda functions for automated responses to log events.

### Amazon SNS

Configure CloudWatch Logs to send notifications via SNS for critical errors.

## Performance Considerations

### Batching

Logs are batched and sent every 5 seconds to minimize API calls and improve performance.

### Async Processing

Log sending is asynchronous and doesn't block application threads.

### Error Handling

CloudWatch errors don't affect application functionality - logs continue to console/file.

### Network Overhead

CloudWatch integration adds minimal network overhead (~1-2ms per batch).

## Security

### IAM Permissions

Use least-privilege IAM policies. Only grant permissions to specific log groups.

### Encryption

CloudWatch Logs are encrypted at rest by default using AWS-managed keys.

### VPC Endpoints

For enhanced security, use VPC endpoints for CloudWatch Logs to keep traffic within AWS network.

### Audit Trail

CloudWatch Logs API calls are logged in AWS CloudTrail for audit purposes.

## Compliance

### Data Retention (Requirement 7.10)

- Logs are retained for 30 days
- Automatic deletion after retention period
- Configurable per log group

### Data Residency

- Logs stored in configured AWS region
- No cross-region replication by default

### Access Control

- IAM-based access control
- CloudTrail audit logging
- Encryption at rest and in transit

## References

- [AWS CloudWatch Logs Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)
- [Watchtower Documentation](https://github.com/kislyuk/watchtower)
- [CloudWatch Logs Insights Query Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)
- [CloudWatch Logs Pricing](https://aws.amazon.com/cloudwatch/pricing/)
