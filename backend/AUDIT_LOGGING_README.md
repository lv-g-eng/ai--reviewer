# Audit Logging System

## Overview

The Audit Logging System provides comprehensive, immutable audit trails for all security-relevant actions in the application. This implementation satisfies Requirements 1.10, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, and 15.7.

## Features

### 1. Comprehensive Event Logging

The system logs all security-relevant events including:

- **Authentication Events** (Req 15.1)
  - Successful and failed login attempts
  - Logout events
  - Token refresh operations
  - Password changes and resets
  - Includes: timestamp, IP address, user agent

- **Authorization Failures** (Req 15.2)
  - Access denied events
  - Permission denied events
  - Role insufficient events
  - Includes: user, resource, attempted action, reason

- **Data Modifications** (Req 15.3)
  - Create, update, and delete operations
  - Before and after state tracking
  - Automatic change computation for updates
  - Includes: full context with previous/new states

- **Administrative Actions** (Req 15.4)
  - User management (create, update, delete, role changes)
  - System configuration changes
  - Project management
  - Includes: full administrative context

### 2. Immutability (Req 15.5)

The audit log is designed to be immutable:

- **Append-Only Table**: PostgreSQL triggers prevent UPDATE and DELETE operations
- **Hash Chain**: Each entry contains a cryptographic hash linking to the previous entry
- **Tamper Detection**: Any modification breaks the hash chain and can be detected
- **Database Permissions**: UPDATE and DELETE permissions revoked at database level

### 3. Query and Export (Req 15.6, 15.7)

Powerful querying and export capabilities:

- **Filtering**: By user, action, date range, event type, resource, IP address, success status
- **Pagination**: Efficient pagination for large result sets
- **Export Formats**: JSON and CSV export for compliance reporting
- **Statistics**: Aggregate statistics for compliance dashboards

## Architecture

### Database Schema

```sql
CREATE TABLE audit_log_entries (
    id UUID PRIMARY KEY,
    previous_hash VARCHAR(64),
    current_hash VARCHAR(64) NOT NULL UNIQUE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    resource_name VARCHAR(500),
    user_id UUID,
    user_email VARCHAR(255),
    user_role VARCHAR(50),
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    request_method VARCHAR(10),
    request_path VARCHAR(1000),
    action VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    previous_state JSONB,
    new_state JSONB,
    changes JSONB,
    event_metadata JSONB,
    compliance_frameworks JSONB,
    retention_until TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Immutability trigger
CREATE TRIGGER prevent_audit_log_modification_trigger
BEFORE UPDATE OR DELETE ON audit_log_entries
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_log_modification();
```

### Hash Chain

Each audit log entry contains:
- `current_hash`: SHA-256 hash of the entry's critical fields
- `previous_hash`: Hash of the previous entry (creates chain)

This creates an immutable chain where any tampering can be detected by verifying:
1. Each entry's hash matches its computed hash
2. Each entry's previous_hash matches the previous entry's current_hash

## Usage

### Service Initialization

```python
from app.services.audit_logging_service import AuditLoggingService
from app.database.postgresql import get_db

async with get_db() as db:
    audit_service = AuditLoggingService(db)
```

### Logging Authentication Attempts

```python
# Successful login
await audit_service.log_authentication_attempt(
    user_email="user@example.com",
    success=True,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    user_id=user_id,
)

# Failed login
await audit_service.log_authentication_attempt(
    user_email="user@example.com",
    success=False,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    error_message="Invalid password",
)
```

### Logging Authorization Failures

```python
await audit_service.log_authorization_failure(
    user_id=user_id,
    user_email="user@example.com",
    user_role="developer",
    resource_type="project",
    resource_id="proj-123",
    attempted_action="delete",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    reason="Insufficient permissions",
)
```

### Logging Data Modifications

```python
# Create
await audit_service.log_data_modification(
    user_id=user_id,
    user_email="user@example.com",
    user_role="developer",
    operation="create",
    resource_type="project",
    resource_id="proj-456",
    resource_name="New Project",
    previous_state=None,
    new_state={"name": "New Project", "status": "active"},
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
)

# Update
await audit_service.log_data_modification(
    user_id=user_id,
    user_email="user@example.com",
    user_role="developer",
    operation="update",
    resource_type="project",
    resource_id="proj-456",
    resource_name="Project",
    previous_state={"name": "Old Name", "status": "active"},
    new_state={"name": "New Name", "status": "active"},
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
)

# Delete
await audit_service.log_data_modification(
    user_id=user_id,
    user_email="user@example.com",
    user_role="developer",
    operation="delete",
    resource_type="project",
    resource_id="proj-456",
    resource_name="Project",
    previous_state={"name": "Project", "status": "active"},
    new_state=None,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
)
```

### Logging Administrative Actions

```python
await audit_service.log_administrative_action(
    user_id=admin_id,
    user_email="admin@example.com",
    user_role="admin",
    action="user.role.assign",
    description="Assigned admin role to user john@example.com",
    resource_type="user",
    resource_id="user-789",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    success=True,
    metadata={"target_user": "john@example.com", "new_role": "admin"},
)
```

### Querying Audit Logs

```python
# Query by user
result = await audit_service.query_logs(
    user_id=user_id,
    limit=100,
    offset=0,
)

# Query by date range
from datetime import datetime, timedelta
result = await audit_service.query_logs(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    limit=100,
)

# Query by action
result = await audit_service.query_logs(
    action="login",
    success=False,  # Failed logins only
    limit=100,
)

# Result structure
{
    "total": 150,
    "limit": 100,
    "offset": 0,
    "items": [
        {
            "id": "...",
            "timestamp": "2024-01-15T10:30:00Z",
            "event_type": "auth.login.failure",
            "user_email": "user@example.com",
            "ip_address": "192.168.1.100",
            "action": "login",
            "description": "...",
            "success": false,
            ...
        },
        ...
    ]
}
```

### Exporting Audit Logs

```python
# Export as JSON
json_data = await audit_service.export_logs(
    format="json",
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
)

# Export as CSV
csv_data = await audit_service.export_logs(
    format="csv",
    user_id=user_id,
)
```

### Verifying Integrity

```python
# Verify hash chain integrity
result = await audit_service.verify_chain_integrity()

# Result structure
{
    "total_logs": 1000,
    "verified": true,
    "integrity_status": "intact",
    "breaks": [],
    "verified_at": "2024-01-15T10:30:00Z"
}

# If tampering detected
{
    "total_logs": 1000,
    "verified": false,
    "integrity_status": "compromised",
    "breaks": [
        {
            "log_id": "...",
            "timestamp": "2024-01-15T10:30:00Z",
            "reason": "Hash mismatch - log may have been tampered with",
            "expected_hash": "...",
            "actual_hash": "..."
        }
    ],
    "verified_at": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

### Query Audit Logs

```
GET /api/v1/audit-logs/
```

Query parameters:
- `user_id`: Filter by user ID
- `user_email`: Filter by user email
- `event_type`: Filter by event type
- `event_category`: Filter by category (auth, authz, data, admin)
- `action`: Filter by action
- `resource_type`: Filter by resource type
- `resource_id`: Filter by resource ID
- `ip_address`: Filter by IP address
- `success`: Filter by success status
- `start_date`: Filter by start date (ISO 8601)
- `end_date`: Filter by end date (ISO 8601)
- `limit`: Maximum number of results (default: 100, max: 1000)
- `offset`: Offset for pagination (default: 0)

Authorization: Requires `admin` or `compliance_officer` role

### Export Audit Logs

```
POST /api/v1/audit-logs/export
```

Request body:
```json
{
    "format": "json",  // or "csv"
    "user_id": "...",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
}
```

Authorization: Requires `admin` or `compliance_officer` role

### Verify Integrity

```
GET /api/v1/audit-logs/verify-integrity
```

Authorization: Requires `admin` role

### Get Event Types

```
GET /api/v1/audit-logs/event-types
```

Returns list of all available event types.

### Get Statistics

```
GET /api/v1/audit-logs/statistics
```

Query parameters:
- `start_date`: Start date for statistics
- `end_date`: End date for statistics

Returns statistics including:
- Total number of logs
- Logs by event category
- Logs by success/failure
- Most active users
- Most common actions

Authorization: Requires `admin` or `compliance_officer` role

## Event Types

### Authentication Events
- `auth.login.success` - Successful login
- `auth.login.failure` - Failed login attempt
- `auth.logout` - User logout
- `auth.token.refresh` - Token refresh
- `auth.password.change` - Password change
- `auth.password.reset` - Password reset

### Authorization Events
- `authz.access.denied` - Access denied
- `authz.permission.denied` - Permission denied
- `authz.role.insufficient` - Insufficient role

### Data Events
- `data.create` - Data creation
- `data.update` - Data update
- `data.delete` - Data deletion
- `data.export` - Data export

### Administrative Events
- `admin.user.create` - User creation
- `admin.user.update` - User update
- `admin.user.delete` - User deletion
- `admin.role.assign` - Role assignment
- `admin.role.revoke` - Role revocation
- `admin.project.create` - Project creation
- `admin.project.delete` - Project deletion
- `admin.config.change` - Configuration change
- `admin.system.setting` - System setting change

## Database Migration

Run the migration to create the audit_log_entries table:

```bash
cd backend
alembic upgrade head
```

The migration (007_add_audit_log_entries.py) creates:
- The audit_log_entries table
- Comprehensive indexes for efficient querying
- Immutability trigger and function
- Database permission restrictions

## Testing

Run the audit logging tests:

```bash
cd backend
pytest tests/test_audit_logging_simple.py -v
```

Tests cover:
- Authentication logging
- Authorization failure logging
- Data modification logging
- Administrative action logging
- Immutability verification
- Query functionality
- Export functionality
- Hash chain integrity

## Compliance

The audit logging system supports compliance with:
- **PCI-DSS**: Comprehensive audit trails for all access and modifications
- **HIPAA**: Audit logs for PHI access and modifications
- **GDPR**: Audit trails for data processing activities
- **SOX**: Financial data access and modification tracking
- **ISO 27001**: Information security event logging

Default retention period: 7 years (2555 days)

## Performance Considerations

### Indexes

The system includes comprehensive indexes for efficient querying:
- Timestamp (descending) for recent logs
- User ID + timestamp for user activity
- Event type + timestamp for event filtering
- Resource type + resource ID for resource tracking
- IP address + timestamp for security analysis

### Pagination

Always use pagination when querying large result sets:
- Default limit: 100
- Maximum limit: 1000
- Use offset for pagination

### Retention

Audit logs are retained for 7 years by default. Implement a cleanup job to archive or delete logs past their retention period:

```python
from datetime import datetime, timezone

# Find expired logs
expired_logs = await db.execute(
    select(AuditLogEntry).where(
        AuditLogEntry.retention_until < datetime.now(timezone.utc)
    )
)

# Archive to cold storage before deletion
# Then delete (if allowed by compliance requirements)
```

## Security Considerations

1. **Access Control**: Only admin and compliance_officer roles can query audit logs
2. **Immutability**: Database triggers prevent modification or deletion
3. **Hash Chain**: Cryptographic verification of log integrity
4. **Sensitive Data**: Avoid logging passwords, tokens, or other secrets
5. **PII Protection**: Consider data privacy regulations when logging user data

## Integration Examples

### Middleware Integration

```python
from fastapi import Request
from app.services.audit_logging_service import AuditLoggingService

async def audit_middleware(request: Request, call_next):
    # Get audit service
    audit_service = AuditLoggingService(request.state.db)
    
    # Process request
    response = await call_next(request)
    
    # Log if authentication failed
    if response.status_code == 401:
        await audit_service.log_authentication_attempt(
            user_email=request.state.user_email,
            success=False,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            error_message="Unauthorized",
        )
    
    return response
```

### Decorator Integration

```python
from functools import wraps
from app.services.audit_logging_service import AuditLoggingService

def audit_admin_action(action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Log admin action
            audit_service = AuditLoggingService(kwargs['db'])
            await audit_service.log_administrative_action(
                user_id=kwargs['current_user']['id'],
                user_email=kwargs['current_user']['email'],
                user_role=kwargs['current_user']['role'],
                action=action,
                description=f"Admin action: {action}",
                resource_type=None,
                resource_id=None,
                ip_address=kwargs['request'].client.host,
                user_agent=kwargs['request'].headers.get("user-agent"),
                success=True,
            )
            
            return result
        return wrapper
    return decorator

@audit_admin_action("user.delete")
async def delete_user(user_id: str, db: AsyncSession, current_user: dict, request: Request):
    # Delete user logic
    pass
```

## Troubleshooting

### Issue: Audit logs not being created

Check:
1. Database connection is working
2. Migration has been run
3. Service is initialized with valid session
4. No exceptions in logs

### Issue: Query performance is slow

Solutions:
1. Ensure indexes are created (check migration)
2. Use appropriate filters to reduce result set
3. Use pagination
4. Consider date range filters

### Issue: Hash chain verification fails

Possible causes:
1. Database corruption
2. Manual modification of logs (should be prevented by trigger)
3. Migration issue

Action: Investigate the specific breaks reported in verification result

## Future Enhancements

Potential improvements:
1. Real-time audit log streaming
2. Anomaly detection (unusual access patterns)
3. Automated compliance reports
4. Integration with SIEM systems
5. Audit log compression for long-term storage
6. Machine learning for security insights
