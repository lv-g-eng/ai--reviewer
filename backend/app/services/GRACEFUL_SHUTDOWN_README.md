# Graceful Shutdown Implementation

## Overview

The graceful shutdown service ensures that the application shuts down cleanly when receiving termination signals (SIGTERM, SIGINT), completing in-flight requests and closing database connections properly.

**Validates Requirements:** 12.10

## Features

### Signal Handling
- **SIGTERM**: Sent by Kubernetes, Docker, systemd during pod termination
- **SIGINT**: Sent by Ctrl+C during local development
- Prevents abrupt termination that could corrupt data or leave connections open

### Shutdown Sequence

1. **Signal Reception**: Catches SIGTERM/SIGINT signals
2. **Stop New Requests**: Prevents new requests from being accepted
3. **Complete In-Flight Requests**: Waits for active requests to finish (with timeout)
4. **Execute Callbacks**: Runs registered shutdown callbacks in order
5. **Close Connections**: Cleanly closes PostgreSQL, Neo4j, and Redis connections
6. **Exit**: Terminates the application process

### Configurable Timeout

Default: 30 seconds

The shutdown timeout ensures the application doesn't hang indefinitely:
- If shutdown completes within timeout: Clean exit
- If timeout is reached: Forced exit to prevent hanging

## Usage

### Basic Setup

The graceful shutdown handler is automatically initialized in `main.py` and `main_optimized.py`:

```python
from app.services.graceful_shutdown import setup_graceful_shutdown

# During application startup
shutdown_handler = setup_graceful_shutdown(shutdown_timeout=30)
```

### Registering Shutdown Callbacks

You can register custom cleanup functions to run during shutdown:

```python
from app.services.graceful_shutdown import get_shutdown_handler

shutdown_handler = get_shutdown_handler()

async def cleanup_background_tasks():
    """Stop background tasks"""
    # Your cleanup code here
    pass

# Register the callback
shutdown_handler.register_shutdown_callback(cleanup_background_tasks)
```

### Checking Shutdown Status

```python
from app.services.graceful_shutdown import get_shutdown_handler

shutdown_handler = get_shutdown_handler()

if shutdown_handler.is_shutdown_in_progress():
    # Reject new requests or operations
    raise HTTPException(status_code=503, detail="Server is shutting down")
```

## Implementation Details

### Database Connection Cleanup

The shutdown handler automatically closes all database connections:

```python
async def _close_database_connections(self):
    """Close all database connections cleanly"""
    await asyncio.gather(
        self._safe_close(close_postgres, "PostgreSQL"),
        self._safe_close(close_neo4j, "Neo4j"),
        self._safe_close(close_redis, "Redis"),
        return_exceptions=True
    )
```

### Error Handling

- Each shutdown callback is executed with its own timeout
- Errors in callbacks don't prevent other callbacks from running
- Database connection errors are logged but don't block shutdown
- Shutdown always completes within the configured timeout

## Testing Graceful Shutdown

### Local Testing

```bash
# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal, send SIGTERM
kill -TERM <pid>

# Or use Ctrl+C (SIGINT)
```

### Docker Testing

```bash
# Start container
docker run -d --name backend backend:latest

# Send SIGTERM (Docker stop sends SIGTERM)
docker stop backend

# Check logs
docker logs backend
```

### Kubernetes Testing

```bash
# Delete pod (sends SIGTERM)
kubectl delete pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

## Expected Log Output

```
INFO: Received SIGTERM signal, initiating graceful shutdown...
INFO: ======================================================================
INFO: GRACEFUL SHUTDOWN INITIATED
INFO: ======================================================================
INFO: Executing 3 shutdown callbacks...
INFO: [1/3] Executing: cleanup_background_tasks
INFO: [1/3] Completed: cleanup_background_tasks
INFO: [2/3] Executing: flush_metrics
INFO: [2/3] Completed: flush_metrics
INFO: [3/3] Executing: close_file_handles
INFO: [3/3] Completed: close_file_handles
INFO: Closing database connections...
INFO: PostgreSQL connection closed
INFO: Neo4j connection closed
INFO: Redis connection closed
INFO: All database connections closed
INFO: ======================================================================
INFO: GRACEFUL SHUTDOWN COMPLETED (2.34s)
INFO: ======================================================================
```

## Best Practices

### 1. Keep Shutdown Fast
- Aim for shutdown to complete in < 10 seconds
- Use timeouts for all cleanup operations
- Don't perform heavy operations during shutdown

### 2. Register Critical Cleanup Only
- Only register callbacks for critical cleanup
- Don't register callbacks for operations that can be safely interrupted

### 3. Handle Errors Gracefully
- All shutdown callbacks should handle their own errors
- Don't raise exceptions from shutdown callbacks
- Log errors but continue shutdown

### 4. Test Shutdown Regularly
- Include shutdown testing in CI/CD pipeline
- Test with various workloads (idle, busy, error states)
- Verify no data corruption or connection leaks

## Kubernetes Integration

### Pod Termination Grace Period

Kubernetes sends SIGTERM and waits for the grace period before sending SIGKILL:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: backend
spec:
  terminationGracePeriodSeconds: 30  # Must be >= shutdown_timeout
  containers:
  - name: backend
    image: backend:latest
```

### Readiness Probe

During shutdown, the readiness probe should fail to stop new traffic:

```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Troubleshooting

### Shutdown Takes Too Long

**Symptom**: Shutdown exceeds timeout, forced termination

**Solutions**:
- Increase `shutdown_timeout` parameter
- Optimize shutdown callbacks
- Check for blocking operations in callbacks

### Connections Not Closing

**Symptom**: Database connections remain open after shutdown

**Solutions**:
- Verify database close functions are being called
- Check for connection leaks in application code
- Ensure connection pools are properly configured

### SIGTERM Not Handled

**Symptom**: Application terminates immediately without cleanup

**Solutions**:
- Verify signal handlers are registered during startup
- Check that `setup_graceful_shutdown()` is called
- Ensure application is running in foreground (not daemonized)

## Related Requirements

- **Requirement 12.10**: THE System SHALL implement graceful shutdown procedures completing in-flight requests before terminating
- **Requirement 12.8**: THE Backend_Service SHALL implement health check endpoints monitoring database connectivity

## Related Files

- `backend/app/services/graceful_shutdown.py` - Main implementation
- `backend/app/main.py` - Integration in main application
- `backend/app/main_optimized.py` - Integration in optimized application
- `backend/tests/test_graceful_shutdown.py` - Test suite
