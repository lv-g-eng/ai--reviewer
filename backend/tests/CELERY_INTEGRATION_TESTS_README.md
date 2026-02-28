# Celery Integration Tests

This document describes the integration tests for Celery task execution, chaining, failure handling, and retry logic.

## Overview

The integration tests in `test_celery_integration.py` verify the complete Celery workflow with real workers and Redis backend. These tests validate:

1. **Task Execution**: Basic task execution with various argument types
2. **Task Chaining**: Sequential task execution with data passing
3. **Failure Handling**: Task failure detection and error propagation
4. **Retry Logic**: Automatic retry with exponential backoff
5. **Task Monitoring**: Progress tracking and status queries
6. **Task Revocation**: Canceling running or pending tasks
7. **Parallel Execution**: Running tasks in parallel using groups
8. **Redis Integration**: Result storage and retrieval from Redis backend

## Requirements

**Validates Requirements:**
- **13.5**: Redis caching and queuing integration tests
- **10.7**: Asynchronous task processing using Celery
- **12.7**: Timeout handling for all external API calls

## Prerequisites

### Required Services

1. **Redis Server**: Must be running on `localhost:6379`
   ```bash
   # Start Redis with Docker
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Or install locally
   # Windows: Download from https://github.com/microsoftarchive/redis/releases
   # Linux: sudo apt-get install redis-server
   # macOS: brew install redis
   ```

2. **Celery Worker**: Tests use pytest-celery plugin which starts workers automatically

### Python Dependencies

```bash
pip install pytest pytest-celery pytest-asyncio celery redis
```

## Running the Tests

### Run All Integration Tests

```bash
# From backend directory
pytest tests/test_celery_integration.py -v
```

### Run Specific Test Classes

```bash
# Test task execution
pytest tests/test_celery_integration.py::TestSimpleTaskExecution -v

# Test task chaining
pytest tests/test_celery_integration.py::TestTaskChaining -v

# Test failure and retry
pytest tests/test_celery_integration.py::TestTaskFailureAndRetry -v

# Test monitoring
pytest tests/test_celery_integration.py::TestTaskMonitoring -v
```

### Run with Output

```bash
# Show print statements and detailed output
pytest tests/test_celery_integration.py -v -s
```

### Run with Coverage

```bash
pytest tests/test_celery_integration.py --cov=app.tasks --cov-report=html
```

## Test Structure

### 1. Simple Task Execution Tests

**Class**: `TestSimpleTaskExecution`

Tests basic task execution with different argument types:
- Simple arithmetic tasks
- Tasks with keyword arguments
- Tasks returning complex data structures

**Example**:
```python
def test_simple_task_execution(self, celery_app, celery_worker):
    @celery_app.task(name='test_simple_task')
    def simple_task(x, y):
        return x + y
    
    result = simple_task.apply_async(args=[2, 3])
    output = result.get(timeout=10)
    
    assert output == 5
    assert result.successful()
```

### 2. Task Chaining Tests

**Class**: `TestTaskChaining`

Tests sequential task execution where output of one task becomes input to the next:
- Simple 2-task chains
- Multi-step chains (3+ tasks)
- Chains passing dictionaries between tasks

**Example**:
```python
def test_simple_chain(self, celery_app, celery_worker):
    workflow = chain(
        add.s(2, 3),      # Returns 5
        multiply.s(4)     # Returns 5 * 4 = 20
    )
    
    result = workflow.apply_async()
    output = result.get(timeout=10)
    
    assert output == 20
```

### 3. Failure and Retry Tests

**Class**: `TestTaskFailureAndRetry`

Tests task failure handling and automatic retry logic:
- Tasks that fail without retry
- Tasks that retry and eventually succeed
- Tasks that exceed max retries
- Conditional retry logic

**Example**:
```python
def test_task_retry_on_failure(self, celery_app, celery_worker):
    @celery_app.task(bind=True, max_retries=3, default_retry_delay=1)
    def retry_task(self):
        if attempt_count < 3:
            raise self.retry(exc=ValueError("Temporary failure"), countdown=1)
        return {'status': 'success'}
    
    result = retry_task.apply_async()
    output = result.get(timeout=15)
    
    assert output['status'] == 'success'
```

### 4. Task Monitoring Tests

**Class**: `TestTaskMonitoring`

Tests progress tracking and status queries using `MonitoredTask` base class:
- Progress updates during execution
- Failure tracking with error details
- Status queries (pending, running, success, failure)

**Example**:
```python
def test_monitored_task_progress(self, celery_app, celery_worker):
    @celery_app.task(bind=True, base=MonitoredTask)
    def monitored_task(self):
        self.update_progress(25, "Step 1", TaskProgressStage.PARSING_FILES)
        self.update_progress(50, "Step 2", TaskProgressStage.BUILDING_GRAPH)
        return "completed"
    
    result = monitored_task.apply_async()
    
    # Poll for progress
    progress = get_task_progress(result.id)
    assert progress['progress'] >= 0
```

### 5. Task Revocation Tests

**Class**: `TestTaskRevocation`

Tests canceling running or pending tasks:
- Revoking pending tasks
- Terminating running tasks

**Example**:
```python
def test_revoke_pending_task(self, celery_app, celery_worker):
    result = long_task.apply_async()
    revoke_result = revoke_task(result.id, terminate=False)
    
    assert revoke_result['revoked'] is True
```

### 6. Chain Failure Handling Tests

**Class**: `TestChainFailureHandling`

Tests how chains handle failures in the middle:
- Chain stops on failure
- Chain continues after retry
- Error propagation through chain

**Example**:
```python
def test_chain_stops_on_failure(self, celery_app, celery_worker):
    workflow = chain(
        step1.s(),
        step2.s(),  # This fails
        step3.s()   # This should not execute
    )
    
    result = workflow.apply_async()
    
    with pytest.raises(ValueError):
        result.get(timeout=10)
```

### 7. Parallel Execution Tests

**Class**: `TestParallelExecution`

Tests running multiple tasks in parallel using groups:
- Group execution
- Collecting results from parallel tasks

**Example**:
```python
def test_group_execution(self, celery_app, celery_worker):
    job = group(
        parallel_task.s(1),
        parallel_task.s(2),
        parallel_task.s(3)
    )
    
    result = job.apply_async()
    outputs = result.get(timeout=10)
    
    assert outputs == [2, 4, 6]
```

### 8. Redis Backend Integration Tests

**Class**: `TestRedisBackendIntegration`

Tests Celery integration with Redis:
- Results stored in Redis
- Result retrieval
- Result expiration

**Example**:
```python
def test_result_stored_in_redis(self, celery_app, celery_worker):
    result = redis_task.apply_async()
    output = result.get(timeout=10)
    
    # Verify result is retrievable
    result2 = AsyncResult(result.id, app=celery_app)
    assert result2.result == output
```

### 9. Error Scenarios Tests

**Class**: `TestErrorScenarios`

Tests various error conditions:
- Invalid arguments
- Exceptions in chains
- Unexpected errors

### 10. Task Timeout Tests

**Class**: `TestTaskTimeout`

Tests timeout handling:
- Soft timeout (raises exception)
- Hard timeout (kills task)

## Test Configuration

### Celery Configuration for Tests

```python
@pytest.fixture(scope="module")
def celery_config():
    return {
        'broker_url': 'redis://localhost:6379/1',  # Use test database
        'result_backend': 'redis://localhost:6379/1',
        'task_always_eager': False,  # Run tasks asynchronously
        'task_eager_propagates': True,
        'task_track_started': True,
        'result_expires': 300,  # 5 minutes
    }
```

### Worker Configuration

```python
@pytest.fixture(scope="module")
def celery_worker_parameters():
    return {
        'perform_ping_check': False,
        'shutdown_timeout': 5,
    }
```

## Common Issues and Solutions

### Issue: Redis Connection Refused

**Error**: `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.`

**Solution**: Start Redis server:
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### Issue: Tests Hang or Timeout

**Cause**: Celery worker not starting or tasks not being processed

**Solution**:
1. Check Redis is running: `redis-cli ping` (should return "PONG")
2. Verify pytest-celery is installed: `pip install pytest-celery`
3. Increase timeout in tests if needed

### Issue: Task Results Not Found

**Cause**: Results expired or Redis database cleared

**Solution**: Ensure `result_expires` is set high enough in test config (300 seconds)

### Issue: Worker Shutdown Warnings

**Warning**: `Worker shutdown timeout exceeded`

**Solution**: This is normal for tests. Workers are forcefully terminated after tests complete.

## Best Practices

### 1. Use Unique Task Names

Always use unique task names in tests to avoid conflicts:
```python
@celery_app.task(name='test_unique_name_123')
def my_test_task():
    pass
```

### 2. Set Appropriate Timeouts

Use reasonable timeouts for `result.get()`:
```python
result.get(timeout=10)  # 10 seconds is usually sufficient
```

### 3. Clean Up After Tests

Tests automatically clean up, but you can manually revoke tasks if needed:
```python
result.revoke(terminate=True)
```

### 4. Test Isolation

Each test should be independent. Don't rely on state from previous tests.

### 5. Mock External Services

For integration tests that call external APIs, use mocks:
```python
with patch('app.services.github_client.get_github_client') as mock_github:
    mock_github.return_value = mock_client
    # Test code here
```

## Performance Considerations

### Test Execution Time

- Simple task tests: ~1-2 seconds each
- Chain tests: ~2-5 seconds each
- Retry tests: ~5-15 seconds each (due to retry delays)
- Full suite: ~2-5 minutes

### Optimizing Test Speed

1. **Reduce retry delays**: Use `default_retry_delay=1` instead of 60
2. **Use shorter timeouts**: Set `soft_time_limit=2` for timeout tests
3. **Run tests in parallel**: Use `pytest-xdist` plugin
   ```bash
   pytest tests/test_celery_integration.py -n auto
   ```

## Debugging Tests

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Print Task State

```python
print(f"Task state: {result.state}")
print(f"Task info: {result.info}")
print(f"Task traceback: {result.traceback}")
```

### Check Redis Directly

```bash
redis-cli
> KEYS celery-task-meta-*
> GET celery-task-meta-<task-id>
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Celery Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-celery pytest-asyncio
      
      - name: Run integration tests
        run: |
          cd backend
          pytest tests/test_celery_integration.py -v
```

## Related Documentation

- [Celery Configuration](../app/CELERY_CONFIGURATION_README.md)
- [Task Monitoring](../app/tasks/TASK_MONITORING_README.md)
- [PR Analysis Workflow](../app/tasks/PR_ANALYSIS_WORKFLOW_README.md)
- [Celery Official Documentation](https://docs.celeryq.dev/)
- [pytest-celery Plugin](https://pytest-celery.readthedocs.io/)

## Troubleshooting

### Get Help

If you encounter issues:

1. Check Redis is running: `redis-cli ping`
2. Check Celery configuration: Review `app/celery_config.py`
3. Enable debug logging: Set `CELERY_LOG_LEVEL=DEBUG`
4. Check test output: Run with `-v -s` flags
5. Review task state: Use `get_task_status(task_id)`

### Common Test Failures

| Error | Cause | Solution |
|-------|-------|----------|
| `ConnectionError` | Redis not running | Start Redis server |
| `TimeoutError` | Task taking too long | Increase timeout or check worker |
| `TaskRevokedError` | Task was canceled | Check revocation logic |
| `MaxRetriesExceededError` | Too many retries | Check retry logic and limits |

## Contributing

When adding new integration tests:

1. Follow existing test structure
2. Use descriptive test names
3. Add docstrings explaining what is tested
4. Keep tests independent and isolated
5. Use appropriate timeouts
6. Update this README with new test descriptions

## License

These tests are part of the AI-Based Reviewer project and follow the same license.
