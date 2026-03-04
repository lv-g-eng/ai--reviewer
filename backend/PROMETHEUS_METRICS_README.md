# Prometheus Metrics Integration

This document describes the Prometheus metrics implementation for monitoring API performance and business metrics.

**Implements Requirement 7.3**: Collect metrics for API response times, error rates, and throughput.

## Overview

The application exposes Prometheus metrics at the `/api/v1/metrics` endpoint for scraping. Metrics are automatically collected for all HTTP requests via middleware, and custom business metrics can be recorded throughout the application.

## Architecture

### Components

1. **Metrics Module** (`app/core/prometheus_metrics.py`)
   - Defines all Prometheus metrics (counters, histograms, gauges)
   - Provides helper functions for recording metrics
   - Uses a custom registry for isolation

2. **Middleware** (`app/middleware/prometheus_middleware.py`)
   - Automatically collects HTTP request metrics
   - Tracks request duration, count, and in-progress requests
   - Normalizes URL paths to reduce cardinality

3. **Metrics Endpoint** (`app/api/v1/endpoints/metrics.py`)
   - Exposes `/api/v1/metrics` endpoint for Prometheus scraping
   - Returns metrics in Prometheus text format

## Available Metrics

### HTTP Metrics (Automatic)

These metrics are automatically collected by the middleware for all HTTP requests:

- **`http_request_duration_seconds`** (Histogram)
  - HTTP request duration in seconds
  - Labels: `method`, `endpoint`, `status_code`
  - Buckets: 5ms to 10s

- **`http_requests_total`** (Counter)
  - Total HTTP requests
  - Labels: `method`, `endpoint`, `status_code`

- **`http_requests_in_progress`** (Gauge)
  - Number of HTTP requests currently being processed
  - Labels: `method`, `endpoint`

- **`http_errors_total`** (Counter)
  - Total HTTP errors
  - Labels: `method`, `endpoint`, `status_code`, `error_type`

- **`exception_count`** (Counter)
  - Total exceptions raised
  - Labels: `exception_type`, `endpoint`

### Database Metrics

- **`database_query_duration_seconds`** (Histogram)
  - Database query duration in seconds
  - Labels: `database`, `operation`

- **`database_connections_active`** (Gauge)
  - Number of active database connections
  - Labels: `database`

- **`database_operations_total`** (Counter)
  - Total database operations
  - Labels: `database`, `operation`, `status`

### Application Metrics

- **`app_info`** (Info)
  - Application information including version and environment
  - Labels: `version`, `environment`

- **`health_check_duration_seconds`** (Histogram)
  - Duration of health checks in seconds
  - Labels: `check_type` (health, readiness, liveness, dependency)

- **`dependency_status`** (Gauge)
  - Status of each dependency (1=healthy, 0=unhealthy)
  - Labels: `dependency_name` (PostgreSQL, Neo4j, Redis, Celery, LLM)

### Code Analysis Metrics

- **`code_analysis_duration_seconds`** (Histogram)
  - Code analysis duration in seconds
  - Labels: `analysis_type`

- **`code_analysis_total`** (Counter)
  - Total code analyses performed
  - Labels: `analysis_type`, `status`

- **`code_entities_processed`** (Counter)
  - Total code entities processed
  - Labels: `entity_type`

- **`circular_dependencies_detected`** (Counter)
  - Total circular dependencies detected
  - Labels: `severity`

### LLM Metrics

- **`llm_requests_total`** (Counter)
  - Total LLM API requests
  - Labels: `provider`, `model`, `status`

- **`llm_request_duration_seconds`** (Histogram)
  - LLM API request duration in seconds
  - Labels: `provider`, `model`

- **`llm_tokens_used`** (Counter)
  - Total LLM tokens used
  - Labels: `provider`, `model`, `token_type`

- **`llm_circuit_breaker_state`** (Gauge)
  - LLM circuit breaker state (0=closed, 1=open, 2=half-open)
  - Labels: `provider`

### Cache Metrics

- **`cache_operations_total`** (Counter)
  - Total cache operations
  - Labels: `operation`, `status`

- **`cache_hit_ratio`** (Gauge)
  - Cache hit ratio (0-1)

### Task Queue Metrics

- **`celery_tasks_total`** (Counter)
  - Total Celery tasks
  - Labels: `task_name`, `status`

- **`celery_task_duration_seconds`** (Histogram)
  - Celery task duration in seconds
  - Labels: `task_name`

- **`celery_queue_length`** (Gauge)
  - Number of tasks in Celery queue
  - Labels: `queue_name`

### Authentication Metrics

- **`auth_attempts_total`** (Counter)
  - Total authentication attempts
  - Labels: `method`, `status`

- **`active_sessions`** (Gauge)
  - Number of active user sessions

### GitHub Integration Metrics

- **`github_webhook_events_total`** (Counter)
  - Total GitHub webhook events received
  - Labels: `event_type`, `status`

- **`github_api_requests_total`** (Counter)
  - Total GitHub API requests
  - Labels: `operation`, `status`

- **`github_api_rate_limit_remaining`** (Gauge)
  - GitHub API rate limit remaining

## Usage

### Automatic HTTP Metrics

HTTP metrics are automatically collected by the middleware. No code changes are required.

```python
# Metrics are automatically recorded for all requests
@app.get("/api/v1/users")
async def get_users():
    return {"users": []}
```

### Recording Custom Metrics

Use the helper functions to record custom business metrics:

```python
from app.core.prometheus_metrics import (
    record_database_operation,
    record_code_analysis,
    record_llm_request,
    record_cache_operation,
    record_celery_task,
)

# Record database operation
async def query_users():
    start_time = time.time()
    try:
        result = await db.execute(query)
        duration = time.time() - start_time
        record_database_operation('postgresql', 'query', duration, 'success')
        return result
    except Exception as e:
        duration = time.time() - start_time
        record_database_operation('postgresql', 'query', duration, 'error')
        raise

# Record code analysis
async def analyze_code(code: str):
    start_time = time.time()
    try:
        result = await parser.parse(code)
        duration = time.time() - start_time
        record_code_analysis('ast_parsing', duration, 'success')
        return result
    except Exception as e:
        duration = time.time() - start_time
        record_code_analysis('ast_parsing', duration, 'error')
        raise

# Record LLM request
async def call_llm(prompt: str):
    start_time = time.time()
    try:
        response = await llm_client.complete(prompt)
        duration = time.time() - start_time
        record_llm_request(
            provider='openai',
            model='gpt-4',
            duration=duration,
            status='success',
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens
        )
        return response
    except Exception as e:
        duration = time.time() - start_time
        record_llm_request('openai', 'gpt-4', duration, 'error')
        raise

# Record cache operation
def get_from_cache(key: str):
    value = cache.get(key)
    if value:
        record_cache_operation('get', 'hit')
    else:
        record_cache_operation('get', 'miss')
    return value

# Record Celery task
@celery_app.task
def process_data(data):
    start_time = time.time()
    try:
        result = do_processing(data)
        duration = time.time() - start_time
        record_celery_task('process_data', duration, 'success')
        return result
    except Exception as e:
        duration = time.time() - start_time
        record_celery_task('process_data', duration, 'failure')
        raise
```

### Using MetricsTimer Context Manager

For timing operations, use the `MetricsTimer` context manager:

```python
from app.core.prometheus_metrics import MetricsTimer, code_analysis_duration_seconds

async def analyze_repository(repo_url: str):
    with MetricsTimer(code_analysis_duration_seconds, analysis_type='full_repo'):
        # ... perform analysis ...
        result = await perform_analysis(repo_url)
    return result
```

### Recording Application Metrics

Application metrics are automatically recorded by the health service:

```python
from app.core.prometheus_metrics import (
    set_app_info,
    record_health_check,
    set_dependency_status
)

# Set application info (called once at startup)
set_app_info(version='1.0.0', environment='production')

# Record health check duration (automatically done by health service)
async def check_health():
    start_time = time.time()
    # ... perform health checks ...
    duration = time.time() - start_time
    record_health_check('health', duration)

# Set dependency status (automatically done by health service)
set_dependency_status('PostgreSQL', is_healthy=True)
set_dependency_status('Neo4j', is_healthy=False)
```

## Prometheus Configuration

### Scrape Configuration

Add the following to your Prometheus configuration (`prometheus.yml`):

```yaml
scrape_configs:
  - job_name: 'fastapi-app'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
```

### Example Queries

#### API Performance

```promql
# P95 response time by endpoint
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# Request rate by endpoint
rate(http_requests_total[5m])

# Error rate
rate(http_errors_total[5m]) / rate(http_requests_total[5m])
```

#### Database Performance

```promql
# Average query duration by database
rate(database_query_duration_seconds_sum[5m]) / 
rate(database_query_duration_seconds_count[5m])

# Database operations per second
rate(database_operations_total[5m])
```

#### LLM Usage

```promql
# LLM requests per minute
rate(llm_requests_total[1m]) * 60

# Average LLM response time
rate(llm_request_duration_seconds_sum[5m]) / 
rate(llm_request_duration_seconds_count[5m])

# Total tokens used per hour
increase(llm_tokens_used[1h])
```

#### Cache Performance

```promql
# Cache hit ratio
cache_hit_ratio

# Cache operations per second
rate(cache_operations_total[5m])
```

#### Health and Dependencies

```promql
# Dependency health status (1=healthy, 0=unhealthy)
dependency_status

# Health check duration
histogram_quantile(0.95, rate(health_check_duration_seconds_bucket[5m]))

# Number of unhealthy dependencies
count(dependency_status == 0)

# Application info
app_info
```

### Alerting Rules

Example alerting rules (`alerts.yml`):

```yaml
groups:
  - name: api_alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      # Slow response time
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API response time"
          description: "P95 response time is {{ $value }}s"
      
      # LLM circuit breaker open
      - alert: LLMCircuitBreakerOpen
        expr: llm_circuit_breaker_state > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "LLM circuit breaker is open"
          description: "Circuit breaker for {{ $labels.provider }} is open"
      
      # Dependency unhealthy
      - alert: DependencyUnhealthy
        expr: dependency_status == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Dependency is unhealthy"
          description: "{{ $labels.dependency_name }} is unhealthy"
      
      # Slow health checks
      - alert: SlowHealthCheck
        expr: histogram_quantile(0.95, rate(health_check_duration_seconds_bucket[5m])) > 5.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Health checks are slow"
          description: "P95 health check duration is {{ $value }}s for {{ $labels.check_type }}"
```

## Grafana Dashboards

### Example Dashboard Panels

1. **API Overview**
   - Request rate (requests/sec)
   - Error rate (%)
   - P50, P95, P99 response times
   - Requests in progress

2. **Database Performance**
   - Query duration by database
   - Operations per second
   - Active connections

3. **LLM Usage**
   - Requests per minute
   - Average response time
   - Tokens used per hour
   - Circuit breaker state

4. **Cache Performance**
   - Hit ratio
   - Operations per second
   - Hit/miss breakdown

5. **Health and Dependencies**
   - Dependency status by name
   - Health check duration
   - Number of unhealthy dependencies
   - Application version and environment

6. **Task Queue**
   - Tasks per minute
   - Average task duration
   - Queue length
   - Success/failure rate

## Testing

Run the metrics tests:

```bash
# Run all metrics tests
pytest backend/tests/test_prometheus_metrics.py -v

# Run middleware tests
pytest backend/tests/test_prometheus_middleware.py -v

# Run with coverage
pytest backend/tests/test_prometheus_*.py --cov=app.core.prometheus_metrics --cov=app.middleware.prometheus_middleware
```

## Best Practices

1. **Label Cardinality**: Keep label cardinality low to avoid performance issues
   - Use normalized paths (e.g., `/users/{id}` instead of `/users/123`)
   - Avoid user-specific labels
   - Limit the number of unique label values

2. **Metric Naming**: Follow Prometheus naming conventions
   - Use `_total` suffix for counters
   - Use `_seconds` suffix for durations
   - Use descriptive names

3. **Recording Metrics**: Record metrics at appropriate points
   - Record HTTP metrics automatically via middleware
   - Record business metrics at service boundaries
   - Use context managers for timing operations

4. **Performance**: Minimize overhead
   - Metrics collection is fast but not free
   - Avoid recording metrics in tight loops
   - Use sampling for high-frequency events if needed

## Troubleshooting

### Metrics Not Appearing

1. Check that the middleware is configured:
   ```python
   from app.middleware.prometheus_middleware import configure_prometheus_middleware
   configure_prometheus_middleware(app)
   ```

2. Verify the metrics endpoint is accessible:
   ```bash
   curl http://localhost:8000/api/v1/metrics
   ```

3. Check Prometheus scrape configuration and targets

### High Cardinality Issues

If you see performance issues or high memory usage:

1. Check label cardinality:
   ```promql
   count by(__name__) ({__name__=~".+"})
   ```

2. Review path normalization in middleware
3. Reduce the number of unique label values

### Missing Custom Metrics

1. Verify metrics are being recorded:
   ```python
   from app.core.prometheus_metrics import get_metrics
   print(get_metrics().decode('utf-8'))
   ```

2. Check that helper functions are called correctly
3. Verify labels match the metric definition

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
