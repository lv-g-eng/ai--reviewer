# Celery Configuration with Redis Backend

## Overview

This document describes the Celery configuration for asynchronous task processing in the AI Code Review Platform. Celery is configured with Redis as both the message broker and result backend, providing reliable task queuing, execution, and result tracking.

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│  (Task Creator) │
└────────┬────────┘
         │ Sends tasks
         ▼
┌─────────────────┐
│  Redis Broker   │
│  (Message Queue)│
└────────┬────────┘
         │ Distributes tasks
         ▼
┌─────────────────┐
│ Celery Workers  │
│ (Task Executors)│
└────────┬────────┘
         │ Stores results
         ▼
┌─────────────────┐
│ Redis Backend   │
│ (Result Storage)│
└─────────────────┘
```

## Configuration Components

### 1. Redis Broker Configuration

**Purpose**: Message broker for task queuing and distribution

**Settings**:
- `broker_url`: Redis connection URL from settings
- `broker_connection_retry_on_startup`: Retry connection on startup
- `broker_connection_max_retries`: Maximum 10 connection retries

**Environment Variables**:
```bash
CELERY_BROKER_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # Optional
```

### 2. Result Backend Configuration

**Purpose**: Store task results and track task status

**Settings**:
- `result_backend`: Redis connection URL (separate DB from broker)
- `result_expires`: Results expire after 1 hour (3600 seconds)
- `result_persistent`: Persist results to disk
- `result_compression`: Compress results with gzip
- `result_extended`: Store additional task metadata

**Features**:
- **Persistence**: Results survive Redis restarts
- **Compression**: Reduces memory usage for large results
- **Expiration**: Automatic cleanup of old results
- **Extended metadata**: Track task execution details

**Environment Variables**:
```bash
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 3. Task Routing and Priority Queues

**Purpose**: Route tasks to appropriate queues based on priority

**Queue Structure**:

| Queue | Priority | Use Case | Examples |
|-------|----------|----------|----------|
| `high_priority` | 10 | Urgent tasks requiring immediate processing | PR analysis, webhook responses |
| `default` | 5 | Normal tasks | AST parsing, graph building, LLM analysis |
| `low_priority` | 1 | Background tasks | Drift detection, cleanup, documentation |

**Task Routing Rules**:

```python
# High Priority (Priority 10)
- analyze_pull_request
- parse_pull_request_files
- post_review_comments

# Default Priority (Priority 5)
- AST parsing tasks
- Graph building tasks
- LLM analysis tasks

# Low Priority (Priority 1-2)
- Architectural drift detection
- Circular dependency detection
- Layer violation detection
- Data cleanup
- Documentation generation
```

**Configuration**:
```python
task_queues=(
    Queue('high_priority', priority=10, queue_arguments={'x-max-priority': 10}),
    Queue('default', priority=5, queue_arguments={'x-max-priority': 10}),
    Queue('low_priority', priority=1, queue_arguments={'x-max-priority': 10}),
)
```

### 4. Task Execution Settings

**Purpose**: Control task execution behavior and reliability

**Settings**:

| Setting | Value | Purpose |
|---------|-------|---------|
| `task_acks_late` | True | Acknowledge after execution (not before) |
| `task_reject_on_worker_lost` | True | Requeue tasks if worker crashes |
| `task_track_started` | True | Track when tasks start execution |
| `task_time_limit` | 3600s | Hard time limit (1 hour) |
| `task_soft_time_limit` | 3300s | Soft time limit (55 minutes) |
| `task_ignore_result` | False | Store task results |

**Reliability Features**:
- **Late acknowledgment**: Tasks are requeued if worker crashes before completion
- **Time limits**: Prevent runaway tasks from consuming resources
- **Result tracking**: Monitor task progress and retrieve results

### 5. Retry Configuration

**Purpose**: Automatically retry failed tasks with exponential backoff

**Settings**:

| Setting | Value | Purpose |
|---------|-------|---------|
| `task_default_retry_delay` | 60s | Initial retry delay |
| `task_max_retries` | 3 | Maximum retry attempts |
| `task_autoretry_for` | (Exception,) | Auto-retry on any exception |
| `task_retry_backoff` | True | Use exponential backoff |
| `task_retry_backoff_max` | 600s | Maximum 10 minutes backoff |
| `task_retry_jitter` | True | Add random jitter |

**Retry Behavior**:
1. **First retry**: After 60 seconds
2. **Second retry**: After ~120 seconds (exponential backoff)
3. **Third retry**: After ~240 seconds (exponential backoff)
4. **Jitter**: Random delay added to prevent thundering herd

### 6. Rate Limiting

**Purpose**: Prevent overwhelming external APIs and services

**Default Rate Limit**: 10 tasks per minute

**Task-Specific Limits**:
```python
task_annotations={
    'analyze_pull_request': {'rate_limit': '5/m'},   # 5 per minute
    'llm_analysis.*': {'rate_limit': '10/m'},        # 10 per minute
    'architectural_drift.*': {'rate_limit': '2/m'},  # 2 per minute
}
```

**Rationale**:
- **PR analysis**: Limited to avoid GitHub API rate limits
- **LLM analysis**: Limited to respect OpenAI/Anthropic rate limits
- **Drift detection**: Low priority, no need for high throughput

### 7. Periodic Tasks (Celery Beat)

**Purpose**: Schedule recurring tasks for maintenance and monitoring

**Schedule**:

| Task | Schedule | Queue | Purpose |
|------|----------|-------|---------|
| `detect-drift-weekly` | Monday 2 AM UTC | low_priority | Weekly architectural drift detection |
| `detect-cycles-daily` | Daily 3 AM UTC | low_priority | Daily circular dependency detection |
| `detect-violations-twice-weekly` | Mon/Thu 4 AM UTC | low_priority | Layer violation checks |
| `cleanup-old-data` | Daily 1 AM UTC | low_priority | Delete old analysis results |
| `celery-health-check` | Every 5 minutes | default | Worker health monitoring |

**Configuration Example**:
```python
beat_schedule={
    'detect-drift-weekly': {
        'task': 'app.tasks.architectural_drift.detect_architectural_drift',
        'schedule': crontab(day_of_week='monday', hour=2, minute=0),
        'args': ('*',),
        'options': {'queue': 'low_priority', 'expires': 86400}
    },
}
```

### 8. Worker Configuration

**Purpose**: Control worker behavior and resource usage

**Settings**:

| Setting | Value | Purpose |
|---------|-------|---------|
| `worker_prefetch_multiplier` | 1 | Fetch one task at a time |
| `worker_max_tasks_per_child` | 1000 | Restart after 1000 tasks |
| `worker_send_task_events` | True | Send events for monitoring |

**Benefits**:
- **Fair distribution**: Workers fetch tasks one at a time
- **Memory leak prevention**: Workers restart periodically
- **Monitoring**: Task events enable real-time monitoring

## Usage

### Starting Celery Workers

**Development**:
```bash
# Start worker with all queues
celery -A app.celery_config worker --loglevel=info

# Start worker for specific queue
celery -A app.celery_config worker -Q high_priority --loglevel=info
```

**Production**:
```bash
# Start multiple workers for different queues
celery -A app.celery_config worker -Q high_priority --concurrency=4 --loglevel=info
celery -A app.celery_config worker -Q default --concurrency=8 --loglevel=info
celery -A app.celery_config worker -Q low_priority --concurrency=2 --loglevel=info
```

### Starting Celery Beat (Scheduler)

```bash
# Start beat scheduler for periodic tasks
celery -A app.celery_config beat --loglevel=info
```

### Monitoring Tasks

**Flower (Web-based monitoring)**:
```bash
# Install Flower
pip install flower

# Start Flower
celery -A app.celery_config flower --port=5555
```

Access at: http://localhost:5555

**Command-line monitoring**:
```bash
# List active tasks
celery -A app.celery_config inspect active

# List scheduled tasks
celery -A app.celery_config inspect scheduled

# List registered tasks
celery -A app.celery_config inspect registered

# Worker statistics
celery -A app.celery_config inspect stats
```

### Sending Tasks

**From FastAPI endpoints**:
```python
from app.celery_config import celery_app

# Send task to high priority queue
result = celery_app.send_task(
    'app.tasks.pull_request_analysis.analyze_pull_request',
    args=[pr_id],
    queue='high_priority',
    priority=10
)

# Get task result
task_result = result.get(timeout=60)
```

**Using task decorators**:
```python
from app.celery_config import celery_app

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue='high_priority'
)
def analyze_pull_request(self, pr_id: int):
    try:
        # Task logic here
        pass
    except Exception as exc:
        # Retry on failure
        raise self.retry(exc=exc)
```

## Performance Tuning

### Worker Concurrency

**CPU-bound tasks** (AST parsing):
```bash
celery -A app.celery_config worker --concurrency=4  # Number of CPU cores
```

**I/O-bound tasks** (LLM API calls):
```bash
celery -A app.celery_config worker --concurrency=20  # Higher concurrency
```

### Memory Management

**Limit memory per worker**:
```bash
celery -A app.celery_config worker --max-memory-per-child=500000  # 500MB
```

**Restart workers periodically**:
```python
worker_max_tasks_per_child=1000  # Restart after 1000 tasks
```

### Queue Optimization

**Separate workers for different queues**:
```bash
# High priority worker (more resources)
celery -A app.celery_config worker -Q high_priority --concurrency=8

# Low priority worker (fewer resources)
celery -A app.celery_config worker -Q low_priority --concurrency=2
```

## Troubleshooting

### Common Issues

**1. Tasks not executing**:
```bash
# Check if workers are running
celery -A app.celery_config inspect active

# Check if Redis is accessible
redis-cli ping

# Check worker logs
celery -A app.celery_config worker --loglevel=debug
```

**2. Tasks timing out**:
```python
# Increase time limits in celery_config.py
task_time_limit=7200  # 2 hours
task_soft_time_limit=6600  # 1 hour 50 minutes
```

**3. Memory issues**:
```bash
# Reduce worker concurrency
celery -A app.celery_config worker --concurrency=2

# Restart workers more frequently
worker_max_tasks_per_child=500
```

**4. Redis connection errors**:
```bash
# Check Redis connection
redis-cli -h localhost -p 6379 ping

# Increase connection retries
broker_connection_max_retries=20
```

### Monitoring and Debugging

**Enable debug logging**:
```bash
celery -A app.celery_config worker --loglevel=debug
```

**Check task status**:
```python
from app.celery_config import celery_app

result = celery_app.AsyncResult(task_id)
print(f"Status: {result.status}")
print(f"Result: {result.result}")
print(f"Traceback: {result.traceback}")
```

**Monitor queue lengths**:
```bash
# Check queue lengths in Redis
redis-cli llen celery

# Or use Flower web interface
celery -A app.celery_config flower
```

## Production Deployment

### Docker Compose

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  celery_worker:
    build: .
    command: celery -A app.celery_config worker --loglevel=info --concurrency=4
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1

  celery_beat:
    build: .
    command: celery -A app.celery_config beat --loglevel=info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1

volumes:
  redis_data:
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: celery-worker
        image: ai-code-review:latest
        command: ["celery", "-A", "app.celery_config", "worker", "--loglevel=info"]
        env:
        - name: CELERY_BROKER_URL
          value: "redis://redis-service:6379/0"
        - name: CELERY_RESULT_BACKEND
          value: "redis://redis-service:6379/1"
```

### AWS Deployment

**ElastiCache Redis**:
```bash
# Use ElastiCache Redis endpoint
CELERY_BROKER_URL=redis://my-cluster.abc123.0001.use1.cache.amazonaws.com:6379/0
CELERY_RESULT_BACKEND=redis://my-cluster.abc123.0001.use1.cache.amazonaws.com:6379/1
```

**ECS Task Definition**:
```json
{
  "family": "celery-worker",
  "containerDefinitions": [
    {
      "name": "celery-worker",
      "image": "ai-code-review:latest",
      "command": ["celery", "-A", "app.celery_config", "worker", "--loglevel=info"],
      "environment": [
        {"name": "CELERY_BROKER_URL", "value": "redis://..."},
        {"name": "CELERY_RESULT_BACKEND", "value": "redis://..."}
      ]
    }
  ]
}
```

## Security Considerations

### Redis Authentication

```bash
# Use password-protected Redis
CELERY_BROKER_URL=redis://:password@localhost:6379/0
CELERY_RESULT_BACKEND=redis://:password@localhost:6379/1
```

### TLS/SSL Encryption

```python
# Enable SSL for Redis connections
broker_use_ssl = {
    'ssl_cert_reqs': ssl.CERT_REQUIRED,
    'ssl_ca_certs': '/path/to/ca-cert',
    'ssl_certfile': '/path/to/client-cert',
    'ssl_keyfile': '/path/to/client-key',
}
```

### Task Serialization

```python
# Use JSON serialization (not pickle) for security
task_serializer='json'
accept_content=['json']
result_serializer='json'
```

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html#best-practices)
- [Flower Monitoring](https://flower.readthedocs.io/)

## Validates Requirements

- **Requirement 10.7**: Implement asynchronous task processing using Celery for long-running operations
  - ✅ Redis broker for task queuing
  - ✅ Task routing for different task types
  - ✅ Priority queues for urgent tasks
  - ✅ Result backend for tracking task completion
  - ✅ Configuration for development and production environments
