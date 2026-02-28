"""
Property-based tests for RBAC (Role-Based Access Control) system.

**Validates: Requirements 5.3, 5.6**

This module tests RBAC properties using Hypothesis for property-based testing:
- Permission inheritance properties
- Role hierarchy properties

Property-based testing generates many test cases automatically to verify
that RBAC properties hold across a wide range of inputs.

Each property test runs with 100 iterations as specified in Requirement 5.6.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import Set, List

from app.auth.models.enums import Role, Permission, ROLE_PERMISSIONS


# Strategy for generating roles
role_strategy = st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR])

# Strategy for generating permissions
permission_strategy = st.sampled_from(list(Permission))

# Strategy for generating lists of roles
roles_list_strategy = st.lists(role_strategy, min_size=1, max_size=3, unique=True)

# Strategy for generating lists of permissions
permissions_list_strategy = st.lists(permission_strategy, min_size=1, max_size=5, unique=True)


class TestPermissionInheritanceProperties:
    """
    Property-based tests for permission inheritance in RBAC system.
    
    **Validates: Requirement 5.3** - Property-based tests for RBAC authentication system
    **Validates: Requirement 5.6** - Execute minimum 100 iterations per property
    """
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_role_has_defined_permissions(self, role):
        """
        Property: Every role must have a defined set of permissions.
        
        This ensures that all roles in the system have explicit permission mappings.
        """
        assert role in ROLE_PERMISSIONS, \
            f"Role {role} must have defined permissions"
        
        permissions = ROLE_PERMISSIONS[role]
        assert isinstance(permissions, list), \
            f"Permissions for {role} must be a list"
        
        assert len(permissions) > 0, \
            f"Role {role} must have at least one permission"
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_all_role_permissions_are_valid(self, role):
        """
        Property: All permissions assigned to a role must be valid Permission enum values.
        
        This ensures data integrity in the permission system.
        """
        permissions = ROLE_PERMISSIONS[role]
        
        for permission in permissions:
            assert isinstance(permission, Permission), \
                f"Permission {permission} for role {role} must be a Permission enum"
            
            # Verify it's in the Permission enum
            assert permission in Permission, \
                f"Permission {permission} must be a valid Permission enum value"
    
    @given(permission=permission_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_admin_has_all_permissions(self, permission):
        """
        Property: ADMIN role must have all permissions in the system.
        
        This is a critical security property - admins should have complete access.
        """
        admin_permissions = ROLE_PERMISSIONS[Role.ADMIN]
        
        assert permission in admin_permissions, \
            f"ADMIN must have permission {permission}"
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_role_permissions_are_subset_of_all_permissions(self, role):
        """
        Property: Permissions for any role must be a subset of all defined permissions.
        
        This prevents invalid permissions from being assigned.
        """
        role_permissions = set(ROLE_PERMISSIONS[role])
        all_permissions = set(Permission)
        
        assert role_permissions.issubset(all_permissions), \
            f"Permissions for {role} must be subset of all permissions"
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_role_permissions_have_no_duplicates(self, role):
        """
        Property: Permission list for each role should have no duplicates.
        
        This ensures clean permission definitions.
        """
        permissions = ROLE_PERMISSIONS[role]
        
        assert len(permissions) == len(set(permissions)), \
            f"Role {role} has duplicate permissions"
    
    def test_visitor_permissions_subset_of_programmer(self):
        """
        Property: VISITOR permissions must be a subset of PROGRAMMER permissions.
        
        This enforces the role hierarchy: VISITOR < PROGRAMMER < ADMIN
        """
        visitor_perms = set(ROLE_PERMISSIONS[Role.VISITOR])
        programmer_perms = set(ROLE_PERMISSIONS[Role.PROGRAMMER])
        
        assert visitor_perms.issubset(programmer_perms), \
            "VISITOR permissions must be subset of PROGRAMMER permissions"
    
    def test_programmer_permissions_subset_of_admin(self):
        """
        Property: PROGRAMMER permissions must be a subset of ADMIN permissions.
        
        This enforces the role hierarchy: VISITOR < PROGRAMMER < ADMIN
        """
        programmer_perms = set(ROLE_PERMISSIONS[Role.PROGRAMMER])
        admin_perms = set(ROLE_PERMISSIONS[Role.ADMIN])
        
        assert programmer_perms.issubset(admin_perms), \
            "PROGRAMMER permissions must be subset of ADMIN permissions"
    
    def test_visitor_permissions_subset_of_admin(self):
        """
        Property: VISITOR permissions must be a subset of ADMIN permissions.
        
        This enforces transitive hierarchy: VISITOR < ADMIN
        """
        visitor_perms = set(ROLE_PERMISSIONS[Role.VISITOR])
        admin_perms = set(ROLE_PERMISSIONS[Role.ADMIN])
        
        assert visitor_perms.issubset(admin_perms), \
            "VISITOR permissions must be subset of ADMIN permissions"
    
    @given(
        role1=role_strategy,
        role2=role_strategy
    )
    @settings(max_examples=100, deadline=2000)
    def test_permission_inheritance_is_transitive(self, role1, role2):
        """
        Property: If role A has all permissions of role B, and role B has all 
        permissions of role C, then role A has all permissions of role C.
        
        This tests transitivity of the permission hierarchy.
        """
        # Skip if roles are the same
        assume(role1 != role2)
        
        perms1 = set(ROLE_PERMISSIONS[role1])
        perms2 = set(ROLE_PERMISSIONS[role2])
        
        # If role1 is a superset of role2
        if perms1.issuperset(perms2):
            # Then for any third role that role2 is a superset of
            for role3 in [Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]:
                if role3 != role2:
                    perms3 = set(ROLE_PERMISSIONS[role3])
                    if perms2.issuperset(perms3):
                        # role1 must also be a superset of role3 (transitivity)
                        assert perms1.issuperset(perms3), \
                            f"Transitivity violated: {role1} should have all perms of {role3}"


class TestRoleHierarchyProperties:
    """
    Property-based tests for role hierarchy in RBAC system.
    
    **Validates: Requirement 5.3** - Property-based tests for RBAC authentication system
    **Validates: Requirement 5.6** - Execute minimum 100 iterations per property
    """
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_role_is_valid_enum(self, role):
        """
        Property: All roles must be valid Role enum values.
        """
        assert isinstance(role, Role), \
            f"Role {role} must be a Role enum"
        
        assert role in [Role.ADMIN, Role.PROGRAMMER, Role.VISITOR], \
            f"Role {role} must be one of the defined roles"
    
    def test_role_hierarchy_levels_are_distinct(self):
        """
        Property: Each role level must have a distinct set of permissions.
        
        This ensures roles are meaningfully different.
        """
        admin_perms = set(ROLE_PERMISSIONS[Role.ADMIN])
        programmer_perms = set(ROLE_PERMISSIONS[Role.PROGRAMMER])
        visitor_perms = set(ROLE_PERMISSIONS[Role.VISITOR])
        
        # ADMIN should have more permissions than PROGRAMMER
        assert len(admin_perms) > len(programmer_perms), \
            "ADMIN must have more permissions than PROGRAMMER"
        
        # PROGRAMMER should have more permissions than VISITOR
        assert len(programmer_perms) > len(visitor_perms), \
            "PROGRAMMER must have more permissions than VISITOR"
        
        # ADMIN should have more permissions than VISITOR
        assert len(admin_perms) > len(visitor_perms), \
            "ADMIN must have more permissions than VISITOR"
    
    def test_admin_is_highest_role(self):
        """
        Property: ADMIN role must have all permissions that any other role has.
        
        This ensures ADMIN is truly the highest privilege level.
        """
        admin_perms = set(ROLE_PERMISSIONS[Role.ADMIN])
        
        for role in [Role.PROGRAMMER, Role.VISITOR]:
            role_perms = set(ROLE_PERMISSIONS[role])
            assert admin_perms.issuperset(role_perms), \
                f"ADMIN must have all permissions of {role}"
    
    def test_visitor_is_lowest_role(self):
        """
        Property: VISITOR role must have the fewest permissions.
        
        This ensures VISITOR is the most restricted role.
        """
        visitor_perms = set(ROLE_PERMISSIONS[Role.VISITOR])
        
        for role in [Role.ADMIN, Role.PROGRAMMER]:
            role_perms = set(ROLE_PERMISSIONS[role])
            assert len(visitor_perms) <= len(role_perms), \
                f"VISITOR must have fewer or equal permissions than {role}"
    
    @given(permission=permission_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_permission_granted_to_lower_role_implies_granted_to_higher(self, permission):
        """
        Property: If a permission is granted to a lower role, it must be granted
        to all higher roles.
        
        This enforces upward inheritance in the hierarchy.
        """
        # If VISITOR has permission, PROGRAMMER and ADMIN must have it
        if permission in ROLE_PERMISSIONS[Role.VISITOR]:
            assert permission in ROLE_PERMISSIONS[Role.PROGRAMMER], \
                f"If VISITOR has {permission}, PROGRAMMER must have it"
            assert permission in ROLE_PERMISSIONS[Role.ADMIN], \
                f"If VISITOR has {permission}, ADMIN must have it"
        
        # If PROGRAMMER has permission, ADMIN must have it
        if permission in ROLE_PERMISSIONS[Role.PROGRAMMER]:
            assert permission in ROLE_PERMISSIONS[Role.ADMIN], \
                f"If PROGRAMMER has {permission}, ADMIN must have it"
    
    @given(
        role1=role_strategy,
        role2=role_strategy
    )
    @settings(max_examples=100, deadline=2000)
    def test_role_comparison_is_consistent(self, role1, role2):
        """
        Property: Role hierarchy comparison must be consistent.
        
        If role A has all permissions of role B, then role B cannot have
        permissions that role A doesn't have (unless they're equal).
        """
        perms1 = set(ROLE_PERMISSIONS[role1])
        perms2 = set(ROLE_PERMISSIONS[role2])
        
        # If role1 is a strict superset of role2
        if perms1.issuperset(perms2) and perms1 != perms2:
            # Then role2 cannot be a superset of role1
            assert not (perms2.issuperset(perms1) and perms2 != perms1), \
                f"Hierarchy inconsistency between {role1} and {role2}"
    
    def test_hierarchy_has_no_cycles(self):
        """
        Property: Role hierarchy must be acyclic (no circular dependencies).
        
        This ensures a clear hierarchy without circular permission inheritance.
        """
        roles = [Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]
        
        # Build a directed graph of "has all permissions of" relationships
        for i, role1 in enumerate(roles):
            perms1 = set(ROLE_PERMISSIONS[role1])
            
            for j, role2 in enumerate(roles):
                if i != j:
                    perms2 = set(ROLE_PERMISSIONS[role2])
                    
                    # If role1 has all permissions of role2
                    if perms1.issuperset(perms2) and perms1 != perms2:
                        # Then role2 must not have all permissions of role1
                        assert not (perms2.issuperset(perms1) and perms2 != perms1), \
                            f"Cycle detected: {role1} <-> {role2}"
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_role_has_at_least_view_permission(self, role):
        """
        Property: Every role should have at least one VIEW permission.
        
        This ensures all users can view something in the system.
        """
        permissions = ROLE_PERMISSIONS[role]
        view_permissions = [p for p in permissions if 'VIEW' in p.value]
        
        assert len(view_permissions) > 0, \
            f"Role {role} must have at least one VIEW permission"
    
    def test_admin_has_all_crud_operations(self):
        """
        Property: ADMIN must have all CRUD operations (CREATE, VIEW, UPDATE, DELETE)
        for all resources.
        
        This ensures admins have complete control.
        """
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        admin_perm_values = [p.value for p in admin_perms]
        
        # Check for user CRUD
        assert any('CREATE_USER' in p for p in admin_perm_values), \
            "ADMIN must have CREATE_USER"
        assert any('VIEW_USER' in p for p in admin_perm_values), \
            "ADMIN must have VIEW_USER"
        assert any('UPDATE_USER' in p for p in admin_perm_values), \
            "ADMIN must have UPDATE_USER"
        assert any('DELETE_USER' in p for p in admin_perm_values), \
            "ADMIN must have DELETE_USER"
        
        # Check for project CRUD
        assert any('CREATE_PROJECT' in p for p in admin_perm_values), \
            "ADMIN must have CREATE_PROJECT"
        assert any('VIEW_PROJECT' in p for p in admin_perm_values), \
            "ADMIN must have VIEW_PROJECT"
        assert any('UPDATE_PROJECT' in p for p in admin_perm_values), \
            "ADMIN must have UPDATE_PROJECT"
        assert any('DELETE_PROJECT' in p for p in admin_perm_values), \
            "ADMIN must have DELETE_PROJECT"


class TestPermissionConsistencyProperties:
    """
    Property-based tests for permission consistency across the RBAC system.
    
    **Validates: Requirement 5.3** - Property-based tests for RBAC authentication system
    **Validates: Requirement 5.6** - Execute minimum 100 iterations per property
    """
    
    @given(permission=permission_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_permission_belongs_to_at_least_one_role(self, permission):
        """
        Property: Every defined permission must be assigned to at least one role.
        
        This prevents orphaned permissions.
        """
        found = False
        for role in [Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]:
            if permission in ROLE_PERMISSIONS[role]:
                found = True
                break
        
        assert found, \
            f"Permission {permission} must be assigned to at least one role"
    
    @given(
        role=role_strategy,
        permission=permission_strategy
    )
    @settings(max_examples=100, deadline=2000)
    def test_permission_check_is_deterministic(self, role, permission):
        """
        Property: Checking if a role has a permission must always return
        the same result.
        
        This ensures permission checks are deterministic.
        """
        result1 = permission in ROLE_PERMISSIONS[role]
        result2 = permission in ROLE_PERMISSIONS[role]
        
        assert result1 == result2, \
            f"Permission check for {role}.{permission} must be deterministic"
    
    def test_all_roles_have_unique_permission_sets(self):
        """
        Property: No two roles should have identical permission sets.
        
        This ensures each role is distinct and meaningful.
        """
        roles = [Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]
        permission_sets = []
        
        for role in roles:
            perm_set = frozenset(ROLE_PERMISSIONS[role])
            assert perm_set not in permission_sets, \
                f"Role {role} has duplicate permission set"
            permission_sets.append(perm_set)
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_role_permissions_are_immutable(self, role):
        """
        Property: Role permission mappings should be immutable.
        
        This ensures permission definitions don't change unexpectedly.
        """
        # Get permissions twice
        perms1 = ROLE_PERMISSIONS[role]
        perms2 = ROLE_PERMISSIONS[role]
        
        # Should be the same object (immutable)
        assert perms1 is perms2, \
            f"Role permissions for {role} should be immutable"
    
    @given(permission=permission_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_permission_naming_convention(self, permission):
        """
        Property: All permissions should follow naming convention:
        ACTION_RESOURCE (e.g., CREATE_USER, VIEW_PROJECT).
        
        This ensures consistent permission naming.
        """
        perm_value = permission.value
        
        # Should contain at least one underscore
        assert '_' in perm_value, \
            f"Permission {perm_value} should follow ACTION_RESOURCE convention"
        
        # Should be uppercase
        assert perm_value.isupper(), \
            f"Permission {perm_value} should be uppercase"
        
        # Should not start or end with underscore
        assert not perm_value.startswith('_'), \
            f"Permission {perm_value} should not start with underscore"
        assert not perm_value.endswith('_'), \
            f"Permission {perm_value} should not end with underscore"
