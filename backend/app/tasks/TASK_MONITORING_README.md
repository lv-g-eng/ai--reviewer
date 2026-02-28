

# Task Monitoring for Celery Tasks

## Overview

This module provides comprehensive monitoring capabilities for Celery tasks, enabling visibility into task execution, progress tracking, failure handling, and timeout management. The monitoring system is designed to meet production requirements for observability and reliability.

## Features

### 1. Task Progress Tracking

Track the progress of long-running tasks with percentage completion, stage information, and status messages.

**Benefits:**
- Real-time visibility into task execution
- Better user experience with progress indicators
- Easier debugging of stuck or slow tasks

**Usage:**
```python
from app.tasks.task_monitoring import MonitoredTask, TaskProgressStage

@celery_app.task(base=MonitoredTask, bind=True)
def my_long_task(self, data):
    self.update_progress(25, "Processing data", TaskProgressStage.PARSING_FILES)
    # ... do work ...
    self.update_progress(50, "Building graph", TaskProgressStage.BUILDING_GRAPH)
    # ... do more work ...
    self.update_progress(100, "Complete", TaskProgressStage.COMPLETED)
    return result
```

### 2. Task Failure Handling

Automatic failure detection, logging, and retry management with exponential backoff.

**Features:**
- Structured error logging with full context
- Intelligent retry decisions based on error type
- Exponential backoff with jitter
- Failure state tracking

**Automatic Behavior:**
- Transient errors (ConnectionError, TimeoutError) → Retry
- Validation errors (ValueError, TypeError) → No retry
- All failures logged with full stack trace

### 3. Task Timeout Handling

Detect and handle both soft and hard timeouts to prevent runaway tasks.

**Timeout Types:**
- **Soft Timeout**: Task receives exception and can clean up (SoftTimeLimitExceeded)
- **Hard Timeout**: Task is killed immediately (TimeLimitExceeded)

**Configuration:**
```python
@celery_app.task(
    base=MonitoredTask,
    bind=True,
    time_limit=3600,      # Hard limit: 1 hour
    soft_time_limit=3300  # Soft limit: 55 minutes
)
def my_task(self):
    # Task logic
    pass
```

**Timeout Decorator:**
```python
from app.tasks.task_monitoring import with_timeout

@with_timeout(30)  # 30 second timeout
async def call_external_api():
    # API call here
    pass
```

### 4. Task Status API

REST API endpoints for querying task status, progress, and results.

**Endpoints:**
- `GET /api/v1/tasks/{task_id}/status` - Get detailed task status
- `GET /api/v1/tasks/{task_id}/progress` - Get task progress
- `GET /api/v1/tasks/{task_id}/result` - Get task result (blocking)
- `POST /api/v1/tasks/{task_id}/revoke` - Cancel a task
- `GET /api/v1/tasks/active` - List active tasks
- `GET /api/v1/tasks/scheduled` - List scheduled tasks
- `GET /api/v1/tasks/workers/stats` - Get worker statistics

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MonitoredTask Base Class                 │
│  - Automatic state tracking (STARTED, PROGRESS, SUCCESS)    │
│  - Failure detection and logging                            │
│  - Timeout detection (soft and hard)                        │
│  - Retry tracking                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Task Implementation                       │
│  - parse_pull_request_files                                 │
│  - build_dependency_graph                                   │
│  - analyze_with_llm                                         │
│  - post_review_comments                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Redis Result Backend                      │
│  - Stores task state and metadata                           │
│  - Persists progress updates                                │
│  - Stores results and errors                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Task Status API                         │
│  - Query task status and progress                           │
│  - Retrieve results                                         │
│  - Cancel tasks                                             │
│  - Monitor workers                                          │
└─────────────────────────────────────────────────────────────┘
```

## Task States

### Standard Celery States
- **PENDING**: Task is waiting to be executed
- **STARTED**: Task has started execution
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task failed permanently
- **RETRY**: Task is being retried
- **REVOKED**: Task was cancelled

### Custom States
- **PROGRESS**: Task is in progress (with progress updates)
- **TIMEOUT**: Task exceeded time limit

## Task Progress Stages

For PR analysis workflow:
- **initializing**: Task is starting up
- **parsing_files**: Parsing PR files with AST
- **building_graph**: Building dependency graph in Neo4j
- **analyzing_llm**: Analyzing code with LLM
- **posting_comments**: Posting review comments to GitHub
- **completed**: Task completed successfully
- **failed**: Task failed

## Usage Examples

### Creating a Monitored Task

```python
from app.tasks.task_monitoring import MonitoredTask, TaskProgressStage
from app.celery_config import celery_app

@celery_app.task(
    base=MonitoredTask,
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue='high_priority'
)
def analyze_code(self, code_id: str):
    """Analyze code with progress tracking"""
    
    # Update progress at each stage
    self.update_progress(10, "Fetching code", TaskProgressStage.INITIALIZING)
    code = fetch_code(code_id)
    
    self.update_progress(30, "Parsing code", TaskProgressStage.PARSING_FILES)
    parsed = parse_code(code)
    
    self.update_progress(60, "Analyzing", TaskProgressStage.ANALYZING_LLM)
    analysis = analyze(parsed)
    
    self.update_progress(90, "Saving results", TaskProgressStage.POSTING_COMMENTS)
    save_results(analysis)
    
    self.update_progress(100, "Complete", TaskProgressStage.COMPLETED)
    return analysis
```

### Querying Task Status

```python
from app.tasks.task_monitoring import get_task_status, get_task_progress

# Get full status
status = get_task_status(task_id)
print(f"State: {status['state']}")
print(f"Progress: {status.get('progress', 0)}%")
print(f"Message: {status.get('message', '')}")

# Get just progress
progress = get_task_progress(task_id)
print(f"Progress: {progress['progress']}%")
print(f"Stage: {progress['stage']}")
```

### Canceling a Task

```python
from app.tasks.task_monitoring import revoke_task

# Graceful cancellation (let task finish current operation)
result = revoke_task(task_id, terminate=False)

# Immediate termination (SIGKILL)
result = revoke_task(task_id, terminate=True)
```

### Using Timeout Decorator

```python
from app.tasks.task_monitoring import with_timeout, TaskTimeoutError

@with_timeout(30)  # 30 second timeout
async def call_github_api():
    try:
        response = await github_client.get_pr_files(repo, pr_number)
        return response
    except TaskTimeoutError:
        logger.error("GitHub API call timed out")
        raise
```

### Custom Retry Logic

```python
from app.tasks.task_monitoring import TaskFailureHandler

handler = TaskFailureHandler()

try:
    result = risky_operation()
except Exception as e:
    # Decide if we should retry
    should_retry = handler.should_retry(e, retry_count, max_retries)
    
    if should_retry:
        # Calculate delay with exponential backoff
        delay = handler.get_retry_delay(retry_count)
        
        # Log failure
        handler.log_failure(
            task_name='my_task',
            task_id=task_id,
            exc=e,
            args=args,
            kwargs=kwargs,
            retry_count=retry_count
        )
        
        # Retry
        raise self.retry(exc=e, countdown=delay)
    else:
        # Don't retry
        raise
```

## API Usage

### Get Task Status

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}/status
```

Response:
```json
{
  "task_id": "abc-123-def-456",
  "state": "PROGRESS",
  "ready": false,
  "successful": null,
  "failed": null,
  "progress": 50,
  "stage": "analyzing_llm",
  "message": "Analyzing code with LLM...",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Get Task Progress

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}/progress
```

Response:
```json
{
  "task_id": "abc-123-def-456",
  "state": "PROGRESS",
  "progress": 75,
  "stage": "posting_comments",
  "message": "Posted 5/10 comments",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

### Cancel Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks/{task_id}/revoke \
  -H "Content-Type: application/json" \
  -d '{"terminate": false}'
```

Response:
```json
{
  "task_id": "abc-123-def-456",
  "revoked": true,
  "terminated": false,
  "message": "Task revoked successfully"
}
```

### List Active Tasks

```bash
curl http://localhost:8000/api/v1/tasks/active
```

Response:
```json
[
  {
    "task_id": "task-1",
    "task_name": "app.tasks.pull_request_analysis.analyze_pull_request",
    "worker": "worker1@hostname",
    "args": "[\"pr-123\"]",
    "kwargs": "{}",
    "time_start": 1234567890.0
  }
]
```

### Get Worker Statistics

```bash
curl http://localhost:8000/api/v1/tasks/workers/stats
```

Response:
```json
{
  "workers": [
    {
      "name": "worker1@hostname",
      "pool": "prefork",
      "max_concurrency": 4,
      "total_tasks": {"completed": 100, "failed": 5},
      "rusage": {"utime": 150.5, "stime": 50.2}
    }
  ],
  "total_workers": 1
}
```

## Monitoring and Debugging

### View Task Logs

All task events are logged with structured information:

```python
import logging
logger = logging.getLogger(__name__)

# Logs include:
# - task_id
# - task_name
# - progress
# - stage
# - error information
# - retry count
# - execution time
```

### Monitor with Flower

```bash
# Install Flower
pip install flower

# Start Flower
celery -A app.celery_config flower --port=5555

# Access at http://localhost:5555
```

### Check Task Status in Redis

```bash
# Connect to Redis
redis-cli

# Get task result
GET celery-task-meta-{task_id}

# List all task keys
KEYS celery-task-meta-*
```

## Performance Considerations

### Progress Update Frequency

- Update progress at meaningful milestones (not too frequently)
- Recommended: 5-10 updates per task
- Each update writes to Redis (network overhead)

**Good:**
```python
self.update_progress(25, "Step 1 complete")
self.update_progress(50, "Step 2 complete")
self.update_progress(75, "Step 3 complete")
self.update_progress(100, "All steps complete")
```

**Bad:**
```python
for i in range(100):
    self.update_progress(i, f"Processing item {i}")  # Too many updates!
```

### Result Backend Storage

- Results expire after 1 hour (configurable in celery_config.py)
- Results are compressed with gzip
- Large results consume Redis memory

**Best Practices:**
- Store only essential data in task results
- Use database for large datasets
- Clean up old results regularly

### Timeout Configuration

- Set appropriate timeouts based on expected task duration
- Soft timeout should be slightly less than hard timeout
- Allow time for cleanup in soft timeout handler

**Example:**
```python
@celery_app.task(
    time_limit=3600,      # 1 hour hard limit
    soft_time_limit=3300  # 55 minutes soft limit (5 min cleanup time)
)
```

## Error Handling

### Transient Errors (Retry)

These errors are automatically retried:
- `ConnectionError` - Network issues
- `TimeoutError` - Operation timeout
- `TaskTimeoutError` - Custom timeout

### Permanent Errors (No Retry)

These errors are not retried:
- `ValueError` - Invalid input
- `TypeError` - Type mismatch
- `KeyError` - Missing key

### Custom Error Handling

```python
@celery_app.task(base=MonitoredTask, bind=True)
def my_task(self):
    try:
        result = risky_operation()
        return result
    except SpecificError as e:
        # Handle specific error
        logger.error(f"Specific error: {e}")
        # Don't retry
        raise
    except Exception as e:
        # Let MonitoredTask handle retry logic
        raise
```

## Testing

### Unit Tests

```python
from app.tasks.task_monitoring import MonitoredTask

def test_task_progress():
    @celery_app.task(base=MonitoredTask, bind=True)
    def test_task(self):
        self.update_progress(50, "Halfway")
        return "done"
    
    with patch.object(test_task, 'update_state') as mock_update:
        test_task()
        # Verify progress was updated
        assert any(
            call[1]['meta']['progress'] == 50
            for call in mock_update.call_args_list
        )
```

### Integration Tests

```python
def test_task_workflow():
    # Queue task
    result = my_task.apply_async(args=['test'])
    
    # Poll for completion
    while not result.ready():
        status = get_task_status(result.id)
        print(f"Progress: {status.get('progress', 0)}%")
        time.sleep(1)
    
    # Get result
    assert result.successful()
    assert result.result == expected_result
```

## Troubleshooting

### Task Stuck in PENDING

**Symptoms:** Task never starts executing

**Causes:**
- No workers running
- Workers not consuming from correct queue
- Task routing misconfigured

**Solutions:**
```bash
# Check if workers are running
celery -A app.celery_config inspect active

# Check worker queues
celery -A app.celery_config inspect active_queues

# Start worker for specific queue
celery -A app.celery_config worker -Q high_priority
```

### Task Timing Out

**Symptoms:** Task fails with SoftTimeLimitExceeded or TimeLimitExceeded

**Causes:**
- Task takes longer than configured timeout
- External API calls are slow
- Database queries are slow

**Solutions:**
- Increase timeout limits
- Optimize slow operations
- Add timeout to external calls
- Break task into smaller subtasks

### Progress Not Updating

**Symptoms:** Progress stays at 0% or doesn't change

**Causes:**
- update_progress() not being called
- Redis connection issues
- Result backend not configured

**Solutions:**
```python
# Verify update_progress is called
self.update_progress(50, "Test")

# Check Redis connection
redis-cli ping

# Verify result backend in celery_config.py
result_backend='redis://localhost:6379/1'
```

### High Memory Usage

**Symptoms:** Workers consuming excessive memory

**Causes:**
- Large task results stored in Redis
- Memory leaks in task code
- Too many concurrent tasks

**Solutions:**
```python
# Limit result size
result_expires=3600  # 1 hour

# Restart workers periodically
worker_max_tasks_per_child=1000

# Reduce concurrency
celery worker --concurrency=2
```

## Validates Requirements

- **Requirement 12.7**: Implement timeout handling for all external API calls
  - ✅ Soft and hard timeout detection
  - ✅ Timeout decorator for external calls
  - ✅ Timeout state tracking
  - ✅ Graceful timeout handling with cleanup

## References

- [Celery Task Documentation](https://docs.celeryproject.org/en/stable/userguide/tasks.html)
- [Celery Monitoring](https://docs.celeryproject.org/en/stable/userguide/monitoring.html)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html#best-practices)
- [Redis Result Backend](https://docs.celeryproject.org/en/stable/userguide/configuration.html#redis-backend-settings)

