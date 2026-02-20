"""
Enterprise RBAC Authentication Module for Backend.

This module provides role-based access control (RBAC) functionality including:
- User authentication and authorization
- JWT token management
- Session management
- Role-based permissions
- Project-level access control
- Audit logging
"""

from .models import (
    User,
    Session,
    Project,
    ProjectAccess,
    AuditLog,
    Role,
    Permission,
    ROLE_PERMISSIONS,
)

from .services import (
    AuthService,
    AuthResult,
    TokenPayload,
    RBACService,
    AuditService,
    AuditFilter,
)

from .middleware import (
    AuthMiddleware,
    security,
    get_current_user,
    require_role,
    require_permission,
    require_project_access,
)

from .config import auth_settings

__all__ = [
    # Models
    "User",
    "Session",
    "Project",
    "ProjectAccess",
    "AuditLog",
    "Role",
    "Permission",
    "ROLE_PERMISSIONS",
    # Services
    "AuthService",
    "AuthResult",
    "TokenPayload",
    "RBACService",
    "AuditService",
    "AuditFilter",
    # Middleware
    "AuthMiddleware",
    "security",
    "get_current_user",
    "require_role",
    "require_permission",
    "require_project_access",
    # Config
    "auth_settings",
]
