# OpenTelemetry Distributed Tracing Integration

This document describes the OpenTelemetry distributed tracing implementation for the AI Code Review Platform, configured to export traces to AWS X-Ray for visualization and analysis.

**Validates Requirement 18.1**: Distributed tracing using OpenTelemetry across all services

## Overview

OpenTelemetry provides distributed tracing capabilities that allow you to track requests as they flow through the system, from the initial API call through database queries, external API calls, and business logic operations.

### Key Features

- **Automatic Instrumentation**: FastAPI, HTTPX, Redis, and SQLAlchemy are automatically instrumented
- **Custom Spans**: Add custom spans for business logic operations
- **AWS X-Ray Integration**: Traces are exported to AWS X-Ray via OTLP protocol
- **Configurable Sampling**: Control trace sampling rate to manage costs
- **Rich Context**: Spans include attributes for debugging and analysis

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│  (Instrumented) │
└────────┬────────┘
         │
         ├─> HTTP Requests (HTTPX) ──> External APIs
         ├─> Database Queries (SQLAlchemy) ──> PostgreSQL
         ├─> Cache Operations (Redis) ──> Redis
         └─> Custom Business Logic ──> Custom Spans
                     │
                     ▼
         ┌───────────────────────┐
         │  OpenTelemetry SDK    │
         │  (Batch Processor)    │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   OTLP Exporter       │
         │  (gRPC Protocol)      │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  AWS X-Ray Collector  │
         │  (OTLP Endpoint)      │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │     AWS X-Ray         │
         │  (Trace Visualization)│
         └───────────────────────┘
```

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# OpenTelemetry Tracing Configuration
TRACING_ENABLED=true
OTLP_ENDPOINT=http://localhost:4317
TRACING_SAMPLE_RATE=1.0
TRACING_CONSOLE_EXPORT=false
```

### Configuration Options

| Variable | Description | Default | Valid Values |
|----------|-------------|---------|--------------|
| `TRACING_ENABLED` | Enable/disable tracing | `true` | `true`, `false` |
| `OTLP_ENDPOINT` | OTLP collector endpoint | `http://localhost:4317` | Any valid URL |
| `TRACING_SAMPLE_RATE` | Sampling rate (0.0-1.0) | `1.0` | `0.0` to `1.0` |
| `TRACING_CONSOLE_EXPORT` | Enable console export for debugging | `false` | `true`, `false` |

### Sampling Rates

- **Development**: `1.0` (100% - trace everything)
- **Staging**: `0.5` (50% - sample half of requests)
- **Production**: `0.1` to `0.3` (10-30% - balance cost and visibility)

## AWS X-Ray Setup

### 1. Install AWS X-Ray Daemon

The AWS X-Ray daemon receives traces via OTLP and forwards them to AWS X-Ray.

**On EC2 Instance:**

```bash
# Download and install X-Ray daemon
wget https://s3.us-east-2.amazonaws.com/aws-xray-assets.us-east-2/xray-daemon/aws-xray-daemon-linux-3.x.zip
unzip aws-xray-daemon-linux-3.x.zip
sudo cp xray -f /usr/bin/xray
sudo chmod +x /usr/bin/xray

# Create systemd service
sudo tee /etc/systemd/system/xray.service > /dev/null <<EOF
[Unit]
Description=AWS X-Ray Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/xray -o -n us-east-1
Restart=always
User=xray
Group=xray

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable xray
sudo systemctl start xray
```

**Using Docker:**

```bash
docker run --rm -d \
  --name xray-daemon \
  -p 2000:2000/udp \
  -p 4317:4317 \
  -e AWS_REGION=us-east-1 \
  amazon/aws-xray-daemon:latest \
  -o -n us-east-1
```

### 2. Configure IAM Permissions

The EC2 instance or ECS task needs these IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "xray:PutTraceSegments",
        "xray:PutTelemetryRecords"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Update Application Configuration

Set the OTLP endpoint to point to the X-Ray daemon:

```bash
OTLP_ENDPOINT=http://localhost:4317
```

## Usage

### Automatic Instrumentation

The following components are automatically instrumented:

#### FastAPI Routes

All FastAPI routes are automatically traced:

```python
@app.get("/api/v1/projects")
async def list_projects():
    # This endpoint is automatically traced
    return {"projects": []}
```

#### HTTP Requests (HTTPX)

All HTTPX requests are automatically traced:

```python
import httpx

async with httpx.AsyncClient() as client:
    # This request is automatically traced
    response = await client.get("https://api.github.com/repos/user/repo")
```

#### Database Queries (SQLAlchemy)

All SQLAlchemy queries are automatically traced:

```python
from app.database.postgresql import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    # This query is automatically traced
    result = await session.execute("SELECT * FROM projects")
```

#### Redis Operations

All Redis operations are automatically traced:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379)
# This operation is automatically traced
redis_client.set('key', 'value')
```

### Custom Spans

Add custom spans for business logic:

```python
from app.core.tracing import get_tracer
from opentelemetry.trace import Status, StatusCode

tracer = get_tracer(__name__)

async def analyze_code(code: str):
    """Analyze code with custom tracing"""
    
    # Create a custom span
    with tracer.start_as_current_span("analyze_code") as span:
        # Add attributes for context
        span.set_attribute("code.length", len(code))
        span.set_attribute("code.language", "python")
        
        try:
            # Step 1: Parse code
            with tracer.start_as_current_span("parse_code") as parse_span:
                ast_tree = parse_code(code)
                parse_span.set_attribute("ast.nodes", len(ast_tree))
            
            # Step 2: Analyze complexity
            with tracer.start_as_current_span("analyze_complexity") as complexity_span:
                complexity = calculate_complexity(ast_tree)
                complexity_span.set_attribute("complexity.score", complexity)
            
            # Mark span as successful
            span.set_status(Status(StatusCode.OK))
            span.set_attribute("analysis.status", "success")
            
            return {"complexity": complexity}
            
        except Exception as e:
            # Record exception in span
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.set_attribute("analysis.status", "failed")
            raise
```

### Span Attributes

Add meaningful attributes to spans for better observability:

```python
# User context
span.set_attribute("user.id", user_id)
span.set_attribute("user.role", user_role)

# Request context
span.set_attribute("request.method", "POST")
span.set_attribute("request.path", "/api/v1/analyze")

# Business metrics
span.set_attribute("files.count", file_count)
span.set_attribute("issues.found", issue_count)
span.set_attribute("analysis.duration_ms", duration)

# Error context
span.set_attribute("error.type", "ValidationError")
span.set_attribute("error.message", str(error))
```

## Viewing Traces in AWS X-Ray

### 1. Access AWS X-Ray Console

Navigate to: https://console.aws.amazon.com/xray/

### 2. Service Map

The service map shows:
- All services in your application
- Request flow between services
- Response times and error rates
- Dependencies on external services

### 3. Trace List

View individual traces:
- Filter by response time, status code, or custom attributes
- Sort by duration or timestamp
- Search by trace ID

### 4. Trace Details

Each trace shows:
- Complete request timeline
- All spans with durations
- Span attributes and metadata
- Exceptions and errors
- Database queries and external API calls

### 5. Analytics

Use X-Ray analytics to:
- Identify slow endpoints
- Find error patterns
- Analyze performance trends
- Compare time periods

## Best Practices

### 1. Span Naming

Use descriptive, hierarchical span names:

```python
# Good
"analyze_repository"
"analyze_repository.clone"
"analyze_repository.parse_files"
"analyze_repository.build_graph"

# Bad
"operation1"
"do_stuff"
"process"
```

### 2. Attribute Naming

Follow OpenTelemetry semantic conventions:

```python
# Standard attributes
span.set_attribute("http.method", "GET")
span.set_attribute("http.status_code", 200)
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.statement", "SELECT * FROM users")

# Custom attributes (use namespaces)
span.set_attribute("app.user.id", user_id)
span.set_attribute("app.analysis.type", "full")
span.set_attribute("app.repository.size", repo_size)
```

### 3. Error Handling

Always record exceptions in spans:

```python
try:
    result = await risky_operation()
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR, str(e)))
    raise
```

### 4. Sampling Strategy

Adjust sampling based on environment:

```python
# Development: Trace everything
TRACING_SAMPLE_RATE=1.0

# Staging: Sample 50%
TRACING_SAMPLE_RATE=0.5

# Production: Sample 10-30% based on traffic
TRACING_SAMPLE_RATE=0.1
```

### 5. Performance Considerations

- Use batch span processor (default) for better performance
- Avoid creating too many spans (keep it meaningful)
- Don't add sensitive data to span attributes
- Use sampling to control costs in high-traffic scenarios

## Troubleshooting

### Traces Not Appearing in X-Ray

1. **Check X-Ray daemon is running:**
   ```bash
   sudo systemctl status xray
   ```

2. **Verify OTLP endpoint is accessible:**
   ```bash
   telnet localhost 4317
   ```

3. **Check IAM permissions:**
   - Ensure EC2 instance role has `xray:PutTraceSegments` permission

4. **Enable console export for debugging:**
   ```bash
   TRACING_CONSOLE_EXPORT=true
   ```

### High Latency

1. **Check batch processor settings:**
   - Increase batch size
   - Increase export interval

2. **Reduce sampling rate:**
   ```bash
   TRACING_SAMPLE_RATE=0.1
   ```

3. **Optimize span creation:**
   - Remove unnecessary spans
   - Reduce span attributes

### Missing Spans

1. **Verify instrumentation is enabled:**
   ```python
   from app.core.tracing import get_tracing_config
   config = get_tracing_config()
   print(f"Tracing enabled: {config is not None}")
   ```

2. **Check for exceptions during instrumentation:**
   - Review application logs for tracing errors

3. **Ensure async context is propagated:**
   - Use `asyncio.create_task()` for background tasks
   - Pass context explicitly if needed

## Testing

### Unit Tests

Run tracing tests:

```bash
cd backend
pytest tests/test_tracing.py -v
```

### Integration Tests

Test with console exporter:

```bash
TRACING_ENABLED=true \
TRACING_CONSOLE_EXPORT=true \
python -m pytest tests/test_tracing.py -v -s
```

### Load Testing

Test tracing under load:

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

## Cost Optimization

### AWS X-Ray Pricing

- **Traces recorded**: $5.00 per 1 million traces
- **Traces retrieved**: $0.50 per 1 million traces
- **Traces scanned**: $0.50 per 1 million traces

### Cost Reduction Strategies

1. **Adjust sampling rate:**
   - Production: 10-30% sampling
   - Development: 100% sampling

2. **Filter noisy endpoints:**
   - Health checks
   - Static assets
   - Metrics endpoints

3. **Set trace retention:**
   - Default: 30 days
   - Reduce for cost savings

4. **Use trace groups:**
   - Group similar traces
   - Analyze patterns instead of individual traces

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [AWS X-Ray Documentation](https://docs.aws.amazon.com/xray/)
- [OpenTelemetry Python SDK](https://opentelemetry-python.readthedocs.io/)
- [OTLP Specification](https://opentelemetry.io/docs/reference/specification/protocol/otlp/)

## Support

For issues or questions:
1. Check application logs: `tail -f backend/logs/app.log`
2. Review X-Ray daemon logs: `sudo journalctl -u xray -f`
3. Enable debug logging: `LOG_LEVEL=DEBUG`
4. Contact the DevOps team

---

**Last Updated**: 2024-01-15
**Requirement**: 18.1 - Distributed tracing using OpenTelemetry
