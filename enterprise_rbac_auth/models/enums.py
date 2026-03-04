"""
Enums for the Enterprise RBAC Authentication System.
"""
from enum import Enum


class Role(str, Enum):
    """User roles in the system."""
    ADMIN = "ADMIN"           # Full system control
    MANAGER = "MANAGER"       # Project oversight & ROI
    REVIEWER = "REVIEWER"     # Read/Write analysis
    PROGRAMMER = "PROGRAMMER" # CRUD own branch
    VISITOR = "VISITOR"       # Read-only grants


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
    # ADMIN: Full system control - all permissions
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
    # MANAGER: Project oversight & ROI - can manage projects and view reports
    Role.MANAGER: [
        Permission.VIEW_USER,
        Permission.CREATE_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.UPDATE_PROJECT,
        Permission.VIEW_PROJECT,
        Permission.VIEW_CONFIG,
        Permission.EXPORT_REPORT,
    ],
    # REVIEWER: Read/Write analysis - can update projects and export reports
    Role.REVIEWER: [
        Permission.UPDATE_PROJECT,
        Permission.VIEW_PROJECT,
        Permission.VIEW_CONFIG,
        Permission.EXPORT_REPORT,
    ],
    # PROGRAMMER: CRUD own branch - can create and manage own projects
    Role.PROGRAMMER: [
        Permission.CREATE_PROJECT,
        Permission.UPDATE_PROJECT,
        Permission.VIEW_PROJECT,
        Permission.VIEW_CONFIG,
        Permission.EXPORT_REPORT,
    ],
    # VISITOR: Read-only grants - can only view projects
    Role.VISITOR: [
        Permission.VIEW_PROJECT,
    ],
}
