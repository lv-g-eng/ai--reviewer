# Database Optimization Implementation

This document describes the database optimization implementation for the AI-Based Reviewer platform.

## Overview

Database optimization has been implemented to meet performance requirements:
- **Requirement 10.1**: API responds within 500ms for P95 of requests
- **Requirement 10.5**: Database query optimization with proper indexes on all foreign keys
- **Requirement 10.6**: Connection pooling for PostgreSQL with pool size of 20 connections
- **Requirement 5.9**: Performance tests verifying API response time under 500ms for P95

## Implementation Components

### 1. Database Indexes (Migration 005)

**File**: `backend/alembic/versions/005_add_database_indexes.py`

#### Foreign Key Indexes

All foreign key columns now have indexes for efficient JOIN operations:

- `pull_requests.project_id` → `idx_pull_requests_project_id`
- `pull_requests.author_id` → `idx_pull_requests_author_id`
- `code_reviews.pull_request_id` → `idx_code_reviews_pull_request_id`
- `review_comments.review_id` → `idx_review_comments_review_id`
- `architecture_analyses.pull_request_id` → `idx_architecture_analyses_pull_request_id`
- `architecture_violations.analysis_id` → `idx_architecture_violations_analysis_id`
- `review_results.pull_request_id` → `idx_review_results_pull_request_id`
- `projects.owner_id` → `idx_projects_owner_id`
- `audit_logs.user_id` → `idx_audit_logs_user_id`
- `architectural_baselines.project_id` → `idx_architectural_baselines_project_id`
- `token_blacklist.user_id` → `idx_token_blacklist_user_id`

#### Composite Indexes for Common Query Patterns

Composite indexes optimize frequently used query combinations:

**Pull Requests**:
- `(project_id, status)` → Query PRs by project and status
- `(project_id, created_at)` → Query recent PRs for a project

**Code Reviews**:
- `(pull_request_id, status)` → Query reviews by PR and status

**Review Comments**:
- `(review_id, severity)` → Query comments by review and severity
- `file_path` → Query comments for specific files

**Architecture Analysis**:
- `(pull_request_id, status)` → Query analyses by PR and status
- `(analysis_id, severity)` → Query violations by analysis and severity
- `type` → Filter violations by type

**Projects**:
- `(owner_id, is_active)` → Query active projects for owner

**Audit Logs**:
- `(user_id, timestamp)` → User audit trails
- `(entity_type, entity_id)` → Entity-specific audit trails
- `(action, timestamp)` → Action-specific queries

**Sessions**:
- `(user_id, is_active)` → Query active user sessions
- `expires_at` → Cleanup expired sessions

**Code Entities**:
- `(project_id, entity_type)` → Query entities by project and type
- `pull_request_id` → Query PR-specific entities
- `file_path` → Query entities in specific files

**Libraries**:
- `(project_id, project_context)` → Query frontend/backend libraries
- `registry_type` → Query by package registry

#### Running the Migration

```bash
cd backend
alembic upgrade head
```

### 2. Connection Pooling Configuration

**File**: `backend/app/database/postgresql.py`

#### Configuration Parameters

```python
engine = create_async_engine(
    settings.postgres_url,
    pool_size=20,           # Core pool size (Requirement 10.6)
    max_overflow=10,        # Additional connections beyond pool_size
    pool_timeout=30,        # Timeout for getting connection (seconds)
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Verify connections before use
    pool_use_lifo=True,     # Use LIFO to reduce connection churn
)
```

#### Pool Behavior

- **Total Capacity**: 30 connections (20 core + 10 overflow)
- **Timeout**: 30 seconds to acquire connection from pool
- **Recycle**: Connections recycled after 1 hour to prevent stale connections
- **Pre-ping**: Connections verified before use to catch disconnects
- **LIFO**: Last-in-first-out reduces connection churn

### 3. Connection Pool Monitoring

**File**: `backend/app/database/pool_monitor.py`

#### Functions

- `get_pool_status(pool)`: Get current pool statistics
- `format_pool_status(status)`: Format status for logging
- `check_pool_health(pool)`: Check pool health and warnings
- `log_pool_status(engine)`: Log current pool status

#### Usage Example

```python
from app.database.postgresql import engine
from app.database.pool_monitor import log_pool_status, check_pool_health

# Log pool status
await log_pool_status(engine)

# Check pool health
health = check_pool_health(engine.pool)
if not health['healthy']:
    print(f"Warnings: {health['warnings']}")
```

### 4. Performance Tests

**File**: `backend/tests/test_database_performance.py`

#### Test Coverage

1. **Query PRs by Project**: Tests basic indexed query performance
2. **Query PRs by Status**: Tests composite index effectiveness
3. **Query Reviews with Comments**: Tests JOIN performance with foreign key indexes
4. **Query Comments by Severity**: Tests composite index for filtering
5. **Concurrent Query Performance**: Tests performance under concurrent load (50 queries)
6. **Complex Multi-Table Query**: Tests complex JOIN performance
7. **Connection Pool Under Load**: Tests pool behavior with 100 concurrent connections
8. **Index Effectiveness**: Verifies indexes are being used (EXPLAIN analysis)

#### Running Performance Tests

```bash
cd backend
pytest tests/test_database_performance.py -v -s
```

#### Expected Results

All tests should pass with P95 response times < 500ms:

```
Query PRs by Project Performance:
  Average: ~50ms
  P50: ~40ms
  P95: < 500ms ✓
  P99: < 500ms

Concurrent Query Performance (50 concurrent queries):
  Average: ~80ms
  P50: ~60ms
  P95: < 500ms ✓
  P99: < 500ms
```

### 5. Query Performance Analysis

**File**: `backend/scripts/analyze_query_performance.py`

This script uses PostgreSQL's `EXPLAIN ANALYZE` to analyze query execution plans and verify index usage.

#### Running Analysis

```bash
cd backend
python scripts/analyze_query_performance.py
```

#### What to Look For

- ✅ **Index Scan** or **Index Only Scan**: Good - using indexes
- ✅ **Bitmap Index Scan**: Acceptable for multi-column queries
- ❌ **Seq Scan**: Bad - full table scan, missing index
- ✅ **Low execution times**: < 10ms for simple queries

### 6. Connection Pool Testing

**File**: `backend/scripts/test_connection_pool.py`

This script tests connection pool behavior under various load conditions.

#### Running Tests

```bash
cd backend
python scripts/test_connection_pool.py
```

#### Test Scenarios

1. **Pool Capacity Test**: 20 concurrent connections (pool size)
2. **Pool Overflow Test**: 30 concurrent connections (pool + overflow)
3. **Pool Timeout Test**: 35 concurrent connections (beyond capacity)
4. **Health Monitoring**: Monitor pool health at different utilization levels
5. **Pool Recycle**: Verify pool configuration

## Performance Benchmarks

### Query Performance Targets

| Query Type | P50 Target | P95 Target | P99 Target |
|------------|-----------|-----------|-----------|
| Simple SELECT | < 10ms | < 50ms | < 100ms |
| JOIN (2 tables) | < 20ms | < 100ms | < 200ms |
| Complex JOIN (3+ tables) | < 50ms | < 200ms | < 400ms |
| Concurrent (50 queries) | < 100ms | < 500ms | < 1000ms |

### Connection Pool Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Pool Size | 20 | 20 ✓ |
| Max Overflow | 10 | 10 ✓ |
| Pool Timeout | 30s | 30s ✓ |
| Pool Recycle | 1 hour | 3600s ✓ |

## Monitoring in Production

### Health Check Endpoint

Add pool monitoring to health check endpoint:

```python
from app.database.postgresql import engine
from app.database.pool_monitor import check_pool_health

@router.get("/health/database")
async def database_health():
    health = check_pool_health(engine.pool)
    return {
        "healthy": health['healthy'],
        "utilization": health['utilization_percent'],
        "warnings": health['warnings'],
        "status": health['status']
    }
```

### Metrics to Monitor

1. **Pool Utilization**: Should stay < 80% under normal load
2. **Overflow Usage**: Should be minimal (< 5 connections)
3. **Query Response Times**: P95 < 500ms
4. **Connection Timeouts**: Should be zero or near-zero

### Alerts

Configure alerts for:
- Pool utilization > 80%
- Overflow connections > 5
- P95 query time > 500ms
- Connection timeout errors

## Troubleshooting

### High Query Times

1. Check if indexes are being used: Run `analyze_query_performance.py`
2. Look for sequential scans in EXPLAIN output
3. Verify migration 005 has been applied
4. Check for missing indexes on new foreign keys

### Pool Exhaustion

1. Check pool status: `log_pool_status(engine)`
2. Look for connection leaks (not closing sessions)
3. Increase pool size if legitimate high load
4. Check for long-running queries blocking connections

### Connection Timeouts

1. Verify pool timeout is appropriate (30s default)
2. Check for database connectivity issues
3. Monitor pool utilization during timeouts
4. Consider increasing max_overflow if needed

## Maintenance

### Adding New Indexes

When adding new tables or foreign keys:

1. Create new migration: `alembic revision -m "add_new_indexes"`
2. Add foreign key indexes for all FK columns
3. Add composite indexes for common query patterns
4. Test with `analyze_query_performance.py`
5. Run performance tests to verify P95 < 500ms

### Monitoring Index Usage

Periodically check index usage:

```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;
```

Indexes with `idx_scan = 0` may be unused and can be removed.

## References

- **Requirements**: `.kiro/specs/project-code-improvements/requirements.md`
  - Requirement 10.1: API response time < 500ms (P95)
  - Requirement 10.5: Database query optimization with indexes
  - Requirement 10.6: Connection pooling (size 20)
  - Requirement 5.9: Performance tests

- **Design**: `.kiro/specs/project-code-improvements/design.md`
  - Database optimization strategy
  - Performance targets

- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/en/20/core/pooling.html
- **PostgreSQL Indexing**: https://www.postgresql.org/docs/current/indexes.html
