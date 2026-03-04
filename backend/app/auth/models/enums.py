"""
Enums for the Enterprise RBAC Authentication System.
"""
from enum import Enum


class Role(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    PROGRAMMER = "developer"
    VISITOR = "reviewer"


class Permission(str, Enum):
    """Permissions that can be granted to roles."""
    CREATE_USER = "CREATE_USER"
    DELETE_USER = "DELETE_USER"
    UPDATE_USER = "UPDATE_USER"
    VIEW_USER = "VIEW_USER"
    CREATE_PROJECT = "CREATE_PROJECT"
    DELETE_PROJECT = "DELETE_PROJECT"
    UPDATE_PROJECT = "UPDATE_PROJECT"
    VIEW_PROJECT = "VIEW_PROJECT"
    MODIFY_CONFIG = "MODIFY_CONFIG"
    VIEW_CONFIG = "VIEW_CONFIG"
    EXPORT_REPORT = "EXPORT_REPORT"


# Role-Permission Mapping
ROLE_PERMISSIONS: dict[Role, list[Permission]] = {
    Role.ADMIN: [
        Permission.CREATE_USER,
        Permission.DELETE_USER,
        Permission.UPDATE_USER,
        Permission.VIEW_USER,
        Permission.CREATE_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.UPDATE_PROJECT,
        Permission.VIEW_PROJECT,
        Permission.MODIFY_CONFIG,
        Permission.VIEW_CONFIG,
        Permission.EXPORT_REPORT,
    ],
    Role.PROGRAMMER: [
        Permission.CREATE_PROJECT,
        Permission.UPDATE_PROJECT,
        Permission.VIEW_PROJECT,
        Permission.VIEW_CONFIG,
        Permission.EXPORT_REPORT,
    ],
    Role.VISITOR: [
        Permission.VIEW_PROJECT,
    ],
}
