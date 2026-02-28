# Data Lifecycle Management

This document describes the data lifecycle management implementation for the AI-Based Reviewer platform, including data retention policies, automated cleanup, and audit logging.

## Overview

The data lifecycle management system implements automated retention policies and cleanup operations to ensure:
- Compliance with data retention requirements
- Efficient use of storage resources
- Proper audit trail of all deletion operations
- Protection of critical audit logs

## Data Retention Policies

### Analysis Results
- **Retention Period**: 90 days
- **Cleanup Schedule**: Daily at 2:00 AM UTC
- **Rationale**: Analysis results become less relevant over time and can be safely deleted after 90 days
- **Validates Requirement**: 11.1

### Audit Logs
- **Retention Period**: 7 years (2,555 days)
- **Cleanup Schedule**: Never (audit logs are never automatically deleted)
- **Verification Schedule**: Weekly on Monday at 1:00 AM UTC
- **Rationale**: Compliance requirements mandate 7-year retention for audit logs
- **Validates Requirement**: 11.8

### Architectural Baselines
- **Retention Period**: 1 year (365 days)
- **Cleanup Schedule**: Weekly on Sunday at 3:00 AM UTC
- **Special Rule**: Baselines marked as "current" are never deleted
- **Rationale**: Historical baselines are useful for drift analysis but can be cleaned up after 1 year

### User Sessions
- **Retention Period**: 30 days
- **Cleanup Schedule**: Daily at 2:30 AM UTC
- **Rationale**: Expired sessions should be cleaned up to maintain database performance

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Celery Beat Scheduler                     │
│  (Triggers cleanup tasks on schedule)                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─── Daily 2:00 AM ──────────────────────┐
                 ├─── Daily 2:30 AM ──────────────────┐   │
                 ├─── Weekly Sunday 3:00 AM ──────┐   │   │
                 └─── Weekly Monday 1:00 AM ──┐   │   │   │
                                              │   │   │   │
┌────────────────────────────────────────────▼───▼───▼───▼───┐
│                    Celery Workers                            │
│  (Execute cleanup tasks)                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              DataLifecycleService                            │
│  - cleanup_old_analysis_results()                            │
│  - cleanup_old_architectural_baselines()                     │
│  - cleanup_expired_sessions()                                │
│  - verify_audit_log_retention()                              │
│  - get_cleanup_statistics()                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─── Delete old data ────────────────────┐
                 └─── Log to audit ───────────────────┐   │
                                                      │   │
┌─────────────────────────────────────────────────┐ │   │
│           AuditLoggingService                   │◄┘   │
│  (Records all deletion operations)              │     │
└─────────────────────────────────────────────────┘     │
                                                        │
┌───────────────────────────────────────────────────────▼─────┐
│                    PostgreSQL Database                       │
│  - analysis_results (90-day retention)                       │
│  - architectural_baselines (1-year retention)                │
│  - sessions (30-day retention)                               │
│  - audit_log_entries (7-year retention, never deleted)       │
└──────────────────────────────────────────────────────────────┘
```

### Service Layer

**DataLifecycleService** (`app/services/data_lifecycle_service.py`)
- Implements all cleanup operations
- Enforces retention policies
- Logs all deletions to audit log
- Provides statistics and verification

**DataRetentionPolicy** (Configuration class)
- Defines retention periods for each data type
- Centralized configuration for easy updates

### Task Layer

**Celery Tasks** (`app/tasks/data_cleanup.py`)
- `cleanup_old_analysis_results`: Daily cleanup of analysis results
- `cleanup_old_architectural_baselines`: Weekly cleanup of baselines
- `cleanup_expired_sessions`: Daily cleanup of expired sessions
- `verify_audit_log_retention`: Weekly verification of audit log retention
- `get_cleanup_statistics`: On-demand statistics generation

## Usage

### Scheduled Cleanup (Automatic)

Cleanup tasks run automatically according to the schedule defined in `celery_config.py`:

```python
# Daily at 2:00 AM UTC
'cleanup-old-analysis-results': {
    'task': 'app.tasks.data_cleanup.cleanup_old_analysis_results',
    'schedule': crontab(hour=2, minute=0),
    'kwargs': {'dry_run': False}
}
```

### Manual Cleanup (On-Demand)

You can trigger cleanup tasks manually using Celery:

```python
from app.tasks.data_cleanup import cleanup_old_analysis_results

# Run cleanup immediately
result = cleanup_old_analysis_results.delay(dry_run=False)

# Dry run (preview what would be deleted)
result = cleanup_old_analysis_results.delay(dry_run=True)
```

### Using the Service Directly

```python
from app.services.data_lifecycle_service import DataLifecycleService
from app.database.database import get_async_session

async def cleanup_example():
    async for session in get_async_session():
        service = DataLifecycleService(session)
        
        # Cleanup analysis results
        result = await service.cleanup_old_analysis_results(
            retention_days=90,
            dry_run=False
        )
        print(f"Deleted {result['deleted_count']} analysis results")
        
        # Get statistics
        stats = await service.get_cleanup_statistics()
        print(f"Total analysis results: {stats['analysis_results']['total']}")
        print(f"Expired: {stats['analysis_results']['expired']}")
```

### Dry Run Mode

All cleanup operations support dry run mode for testing:

```python
# Preview what would be deleted without actually deleting
result = await service.cleanup_old_analysis_results(dry_run=True)
print(f"Would delete {result['would_delete_count']} records")
```

## Monitoring

### Cleanup Statistics

Get current statistics about data eligible for cleanup:

```python
from app.tasks.data_cleanup import get_cleanup_statistics

stats = get_cleanup_statistics.delay()
print(stats.get())
```

Example output:
```json
{
  "analysis_results": {
    "total": 1500,
    "expired": 200,
    "oldest": "2023-01-15T10:30:00Z",
    "newest": "2024-01-15T10:30:00Z",
    "retention_days": 90
  },
  "audit_logs": {
    "total": 50000,
    "oldest": "2020-01-01T00:00:00Z",
    "newest": "2024-01-15T10:30:00Z",
    "retention_days": 2555,
    "note": "Audit logs are never automatically deleted"
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Audit Trail

All cleanup operations are logged to the audit log:

```sql
SELECT 
    timestamp,
    action,
    description,
    event_metadata->>'deleted_count' as deleted_count
FROM audit_log_entries
WHERE action LIKE 'cleanup_%'
ORDER BY timestamp DESC;
```

### Celery Monitoring

Monitor cleanup task execution using Celery Flower or logs:

```bash
# View task history
celery -A app.celery_config inspect active

# View scheduled tasks
celery -A app.celery_config inspect scheduled
```

## Configuration

### Retention Periods

Retention periods are defined in `DataRetentionPolicy`:

```python
class DataRetentionPolicy:
    ANALYSIS_RESULTS_RETENTION_DAYS = 90
    AUDIT_LOGS_RETENTION_DAYS = 2555  # 7 years
    ARCHITECTURAL_BASELINES_RETENTION_DAYS = 365
    USER_SESSIONS_RETENTION_DAYS = 30
```

To change retention periods, update these constants and redeploy.

### Cleanup Schedule

Cleanup schedules are defined in `celery_config.py`:

```python
beat_schedule = {
    'cleanup-old-analysis-results': {
        'task': 'app.tasks.data_cleanup.cleanup_old_analysis_results',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM UTC
        'kwargs': {'dry_run': False}
    }
}
```

### Task Retry Configuration

Cleanup tasks automatically retry on failure:

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def cleanup_old_analysis_results(self, dry_run=False):
    # Task implementation
    pass
```

## Testing

### Unit Tests

Run unit tests for data lifecycle service:

```bash
pytest backend/tests/test_data_lifecycle.py -v
```

### Integration Tests

Run integration tests for Celery tasks:

```bash
pytest backend/tests/test_data_cleanup_tasks.py -v
```

### Test Coverage

The test suite covers:
- Cleanup operations with various retention periods
- Dry run mode
- Audit logging of cleanup operations
- Edge cases (no data, zero retention, etc.)
- Task retry behavior
- Error handling

## Security Considerations

### Audit Log Protection

- Audit logs are **never** automatically deleted
- Retention verification runs weekly to ensure compliance
- Any attempt to delete audit logs is logged itself

### Deletion Audit Trail

- All cleanup operations are logged with:
  - Number of records deleted
  - Cutoff date used
  - Sample of deleted records (first 10)
  - Timestamp and system user

### Access Control

- Cleanup tasks run as system user
- Manual cleanup requires admin privileges
- Dry run mode available for testing

## Troubleshooting

### Cleanup Not Running

Check Celery Beat is running:
```bash
celery -A app.celery_config beat --loglevel=info
```

Check Celery workers are running:
```bash
celery -A app.celery_config worker --loglevel=info
```

### Cleanup Failing

Check task logs:
```bash
tail -f logs/celery.log | grep cleanup
```

Run dry run to test:
```python
from app.tasks.data_cleanup import cleanup_old_analysis_results
result = cleanup_old_analysis_results.delay(dry_run=True)
print(result.get())
```

### Audit Log Retention Issues

Run verification task:
```python
from app.tasks.data_cleanup import verify_audit_log_retention
result = verify_audit_log_retention.delay()
print(result.get())
```

## Compliance

### Requirements Validation

- **Requirement 11.1**: Analysis results older than 90 days are automatically deleted
- **Requirement 11.8**: Audit logs are retained for 7 years and never automatically deleted

### Audit Evidence

All cleanup operations provide audit evidence:
1. Audit log entries for each cleanup operation
2. Statistics showing before/after counts
3. Sample records included in audit metadata
4. Timestamps and retention periods recorded

## Future Enhancements

Potential improvements for future releases:

1. **Configurable Retention Policies**: Allow per-project retention policies
2. **Backup Before Delete**: Automatically backup data before deletion
3. **Selective Cleanup**: Allow cleanup of specific projects or date ranges
4. **Cleanup Notifications**: Send notifications when large cleanups occur
5. **Data Archival**: Archive old data to cold storage instead of deleting
6. **Compliance Reports**: Generate compliance reports showing retention adherence

## References

- [Celery Beat Documentation](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html)
- [PostgreSQL Data Retention Best Practices](https://www.postgresql.org/docs/current/sql-delete.html)
- [Audit Log Retention Requirements](https://www.iso.org/standard/64120.html)
