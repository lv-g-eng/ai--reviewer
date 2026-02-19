# Data Models Documentation

This directory contains all SQLAlchemy data models for the Enterprise RBAC Authentication System.

## Models Overview

### Core Models

1. **User** (`user.py`)
   - Represents authenticated users in the system
   - Fields: id, username, password_hash, role, created_at, updated_at, last_login, is_active
   - Relationships: owned_projects, sessions, audit_logs, project_accesses

2. **Project** (`project.py`)
   - Represents code assets or workspaces
   - Fields: id, name, description, owner_id, created_at, updated_at
   - Relationships: owner, access_grants

3. **ProjectAccess** (`project.py`)
   - Represents explicit access grants to projects
   - Fields: project_id, user_id, granted_at, granted_by
   - Composite primary key: (project_id, user_id)

4. **Session** (`session.py`)
   - Represents active user sessions
   - Fields: id, user_id, token, issued_at, expires_at, is_valid, device_info, ip_address
   - Relationships: user

5. **AuditLog** (`audit_log.py`)
   - Tracks user actions for compliance
   - Fields: id, timestamp, user_id, username, action, resource_type, resource_id, ip_address, user_agent, success, error_message
   - Relationships: user

### Enums

**Role** (`enums.py`)
- ADMIN: Full system privileges
- PROGRAMMER: Project creation and management
- VISITOR: Read-only access to assigned projects

**Permission** (`enums.py`)
- CREATE_USER, DELETE_USER, UPDATE_USER, VIEW_USER
- CREATE_PROJECT, DELETE_PROJECT, UPDATE_PROJECT, VIEW_PROJECT
- MODIFY_CONFIG, VIEW_CONFIG
- EXPORT_REPORT

### Role-Permission Mapping

The `ROLE_PERMISSIONS` dictionary defines which permissions each role has:

- **ADMIN**: All 11 permissions
- **PROGRAMMER**: CREATE_PROJECT, UPDATE_PROJECT, VIEW_PROJECT, VIEW_CONFIG, EXPORT_REPORT
- **VISITOR**: VIEW_PROJECT only

## Database Schema

### Entity Relationships

```
User (1) ----< (N) Project (owner)
User (1) ----< (N) Session
User (1) ----< (N) AuditLog
User (N) ----< (N) Project (via ProjectAccess)
```

### Key Constraints

- User.username: UNIQUE, NOT NULL
- Session.token: UNIQUE, NOT NULL
- ProjectAccess: Composite primary key (project_id, user_id)
- All foreign keys have proper indexes for query performance

## Usage Examples

### Creating a User

```python
from enterprise_rbac_auth.models import User, Role
import uuid

user = User(
    id=str(uuid.uuid4()),
    username="john_doe",
    password_hash="hashed_password_here",
    role=Role.PROGRAMMER,
    is_active=True
)
db.add(user)
db.commit()
```

### Creating a Project

```python
from enterprise_rbac_auth.models import Project
import uuid

project = Project(
    id=str(uuid.uuid4()),
    name="My Project",
    description="A sample project",
    owner_id=user.id
)
db.add(project)
db.commit()
```

### Granting Project Access

```python
from enterprise_rbac_auth.models import ProjectAccess

access = ProjectAccess(
    project_id=project.id,
    user_id=grantee_user.id,
    granted_by=admin_user.id
)
db.add(access)
db.commit()
```

### Creating a Session

```python
from enterprise_rbac_auth.models import Session
from datetime import datetime, timedelta
import uuid

session = Session(
    id=str(uuid.uuid4()),
    user_id=user.id,
    token="jwt_token_here",
    issued_at=datetime.utcnow(),
    expires_at=datetime.utcnow() + timedelta(hours=1),
    is_valid=True,
    ip_address="192.168.1.1"
)
db.add(session)
db.commit()
```

### Creating an Audit Log

```python
from enterprise_rbac_auth.models import AuditLog
from datetime import datetime
import uuid

log = AuditLog(
    id=str(uuid.uuid4()),
    timestamp=datetime.utcnow(),
    user_id=user.id,
    username=user.username,
    action="LOGIN",
    ip_address="192.168.1.1",
    success=True
)
db.add(log)
db.commit()
```

## Testing

Run the model tests:

```bash
pytest tests/test_models.py -v
```

All tests should pass, verifying:
- Enum values are correct
- Role-permission mapping is accurate
- Models can be created and persisted
- Relationships work correctly
- Constraints are enforced

## Database Initialization

Initialize the database with default admin user:

```bash
python -m enterprise_rbac_auth.init_db
```

Or use the management CLI:

```bash
python -m enterprise_rbac_auth.manage_db init
python -m enterprise_rbac_auth.manage_db reset  # WARNING: Deletes all data
python -m enterprise_rbac_auth.manage_db create-admin --username admin --password secret
```

## Notes

- All datetime fields use UTC timestamps
- Password hashes should be 60 characters (bcrypt format)
- UUIDs are stored as strings (36 characters with hyphens)
- The last Admin user cannot be deleted (enforced at service layer)
- Audit logs are immutable (enforced at service layer)
- Session tokens should be stored securely and never logged
