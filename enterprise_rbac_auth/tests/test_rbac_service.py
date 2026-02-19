"""
Property-based tests for RBAC service.
"""
import pytest
import uuid
from hypothesis import given, strategies as st, settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import User, Project, ProjectAccess, Role, Permission, ROLE_PERMISSIONS
from ..models.user import Base
from ..services.rbac_service import RBACService


# Test database setup
@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


# Hypothesis strategies for generating test data
@st.composite
def user_strategy(draw, role=None):
    """Generate a random user."""
    if role is None:
        role = draw(st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]))
    return {
        "id": str(uuid.uuid4()),
        "username": draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        "password_hash": "dummy_hash_" + draw(st.text(min_size=10, max_size=20)),
        "role": role,
        "is_active": True
    }


@st.composite
def permission_strategy(draw):
    """Generate a random permission."""
    return draw(st.sampled_from(list(Permission)))


# Feature: enterprise-rbac-authentication, Property 32: Authorization checks verify role permissions
# For any authorization check for a specific permission, the check should return true if and only if 
# the user's role includes that permission in the role-permission mapping.
@given(
    role=st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]),
    permission=permission_strategy()
)
@settings(max_examples=100)
def test_property_32_authorization_checks_verify_role_permissions(role, permission):
    """
    **Validates: Requirements 9.5**
    
    Property 32: Authorization checks verify role permissions
    
    For any authorization check for a specific permission, the check should return true 
    if and only if the user's role includes that permission in the role-permission mapping.
    """
    # Create a fresh database session for this test
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    try:
        # Create a user with the given role
        user_data = {
            "id": str(uuid.uuid4()),
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "password_hash": "dummy_hash",
            "role": role,
            "is_active": True
        }
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        
        # Check if user has the permission
        has_perm = RBACService.has_permission(db_session, user.id, permission)
        
        # Get expected permissions for the role
        expected_permissions = ROLE_PERMISSIONS.get(role, [])
        should_have_perm = permission in expected_permissions
        
        # Verify the property: has_permission should return true if and only if 
        # the permission is in the role's permission list
        assert has_perm == should_have_perm, (
            f"User with role {role} should {'have' if should_have_perm else 'not have'} "
            f"permission {permission}, but has_permission returned {has_perm}"
        )
    finally:
        db_session.close()


# Additional unit tests for specific scenarios
def test_has_permission_admin_has_all_permissions(db_session):
    """Admin users should have all permissions."""
    user = User(
        id=str(uuid.uuid4()),
        username="admin_user",
        password_hash="dummy_hash",
        role=Role.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Check all permissions
    for permission in Permission:
        assert RBACService.has_permission(db_session, user.id, permission), (
            f"Admin should have {permission}"
        )


def test_has_permission_programmer_limited_permissions(db_session):
    """Programmer users should have limited permissions."""
    user = User(
        id=str(uuid.uuid4()),
        username="programmer_user",
        password_hash="dummy_hash",
        role=Role.PROGRAMMER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Should have these permissions
    assert RBACService.has_permission(db_session, user.id, Permission.CREATE_PROJECT)
    assert RBACService.has_permission(db_session, user.id, Permission.VIEW_PROJECT)
    assert RBACService.has_permission(db_session, user.id, Permission.UPDATE_PROJECT)
    
    # Should NOT have these permissions
    assert not RBACService.has_permission(db_session, user.id, Permission.CREATE_USER)
    assert not RBACService.has_permission(db_session, user.id, Permission.DELETE_USER)
    assert not RBACService.has_permission(db_session, user.id, Permission.MODIFY_CONFIG)


def test_has_permission_visitor_minimal_permissions(db_session):
    """Visitor users should have minimal permissions."""
    user = User(
        id=str(uuid.uuid4()),
        username="visitor_user",
        password_hash="dummy_hash",
        role=Role.VISITOR,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Should only have VIEW_PROJECT permission
    assert RBACService.has_permission(db_session, user.id, Permission.VIEW_PROJECT)
    
    # Should NOT have any other permissions
    assert not RBACService.has_permission(db_session, user.id, Permission.CREATE_PROJECT)
    assert not RBACService.has_permission(db_session, user.id, Permission.UPDATE_PROJECT)
    assert not RBACService.has_permission(db_session, user.id, Permission.CREATE_USER)


def test_has_permission_inactive_user_denied(db_session):
    """Inactive users should be denied all permissions."""
    user = User(
        id=str(uuid.uuid4()),
        username="inactive_user",
        password_hash="dummy_hash",
        role=Role.ADMIN,
        is_active=False  # Inactive
    )
    db_session.add(user)
    db_session.commit()
    
    # Even admin permissions should be denied for inactive users
    assert not RBACService.has_permission(db_session, user.id, Permission.CREATE_USER)
    assert not RBACService.has_permission(db_session, user.id, Permission.VIEW_PROJECT)


def test_has_permission_nonexistent_user_denied(db_session):
    """Non-existent users should be denied all permissions."""
    fake_user_id = str(uuid.uuid4())
    
    # Should return False for non-existent user
    assert not RBACService.has_permission(db_session, fake_user_id, Permission.VIEW_PROJECT)


def test_get_role_permissions_returns_correct_permissions():
    """get_role_permissions should return the correct permissions for each role."""
    # Admin should have all permissions
    admin_perms = RBACService.get_role_permissions(Role.ADMIN)
    assert len(admin_perms) == 11  # All 11 permissions
    assert Permission.CREATE_USER in admin_perms
    assert Permission.DELETE_PROJECT in admin_perms
    
    # Programmer should have 5 permissions
    programmer_perms = RBACService.get_role_permissions(Role.PROGRAMMER)
    assert len(programmer_perms) == 5
    assert Permission.CREATE_PROJECT in programmer_perms
    assert Permission.VIEW_CONFIG in programmer_perms
    assert Permission.CREATE_USER not in programmer_perms
    
    # Visitor should have 1 permission
    visitor_perms = RBACService.get_role_permissions(Role.VISITOR)
    assert len(visitor_perms) == 1
    assert Permission.VIEW_PROJECT in visitor_perms



# Feature: enterprise-rbac-authentication, Property 16: Project access requires ownership or grant
# For any Programmer requesting access to a project, access should be granted if and only if 
# the user is the project owner or has an explicit access grant for that project.
@given(
    is_owner=st.booleans(),
    has_grant=st.booleans()
)
@settings(max_examples=100)
def test_property_16_project_access_requires_ownership_or_grant(is_owner, has_grant):
    """
    **Validates: Requirements 4.2**
    
    Property 16: Project access requires ownership or grant
    
    For any Programmer requesting access to a project, access should be granted if and only if 
    the user is the project owner or has an explicit access grant for that project.
    """
    # Create a fresh database session for this test
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    try:
        # Create a programmer user
        programmer = User(
            id=str(uuid.uuid4()),
            username=f"programmer_{uuid.uuid4().hex[:8]}",
            password_hash="dummy_hash",
            role=Role.PROGRAMMER,
            is_active=True
        )
        db_session.add(programmer)
        
        # Create a project owner (different from programmer unless is_owner is True)
        if is_owner:
            owner_id = programmer.id
        else:
            owner = User(
                id=str(uuid.uuid4()),
                username=f"owner_{uuid.uuid4().hex[:8]}",
                password_hash="dummy_hash",
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(owner)
            owner_id = owner.id
        
        # Create a project
        project = Project(
            id=str(uuid.uuid4()),
            name=f"project_{uuid.uuid4().hex[:8]}",
            owner_id=owner_id
        )
        db_session.add(project)
        db_session.commit()
        
        # Grant access if needed
        if has_grant and not is_owner:
            access_grant = ProjectAccess(
                project_id=project.id,
                user_id=programmer.id,
                granted_by=owner_id
            )
            db_session.add(access_grant)
            db_session.commit()
        
        # Check if programmer can access the project
        can_access = RBACService.can_access_project(
            db_session, programmer.id, project.id, Permission.VIEW_PROJECT
        )
        
        # Expected result: should have access if owner OR has grant
        should_have_access = is_owner or has_grant
        
        # Verify the property
        assert can_access == should_have_access, (
            f"Programmer should {'have' if should_have_access else 'not have'} access "
            f"(is_owner={is_owner}, has_grant={has_grant}), but can_access_project returned {can_access}"
        )
    finally:
        db_session.close()


# Feature: enterprise-rbac-authentication, Property 17: Admins bypass project isolation
# For any user with the Admin role and any project, the user should be able to access 
# the project regardless of ownership or access grants.
@given(
    is_owner=st.booleans(),
    has_grant=st.booleans()
)
@settings(max_examples=100)
def test_property_17_admins_bypass_project_isolation(is_owner, has_grant):
    """
    **Validates: Requirements 4.4**
    
    Property 17: Admins bypass project isolation
    
    For any user with the Admin role and any project, the user should be able to access 
    the project regardless of ownership or access grants.
    """
    # Create a fresh database session for this test
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    try:
        # Create an admin user
        admin = User(
            id=str(uuid.uuid4()),
            username=f"admin_{uuid.uuid4().hex[:8]}",
            password_hash="dummy_hash",
            role=Role.ADMIN,
            is_active=True
        )
        db_session.add(admin)
        
        # Create a project owner (different from admin unless is_owner is True)
        if is_owner:
            owner_id = admin.id
        else:
            owner = User(
                id=str(uuid.uuid4()),
                username=f"owner_{uuid.uuid4().hex[:8]}",
                password_hash="dummy_hash",
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(owner)
            owner_id = owner.id
        
        # Create a project
        project = Project(
            id=str(uuid.uuid4()),
            name=f"project_{uuid.uuid4().hex[:8]}",
            owner_id=owner_id
        )
        db_session.add(project)
        db_session.commit()
        
        # Optionally grant access (shouldn't matter for admin)
        if has_grant and not is_owner:
            access_grant = ProjectAccess(
                project_id=project.id,
                user_id=admin.id,
                granted_by=owner_id
            )
            db_session.add(access_grant)
            db_session.commit()
        
        # Check if admin can access the project
        can_access = RBACService.can_access_project(
            db_session, admin.id, project.id, Permission.VIEW_PROJECT
        )
        
        # Admin should ALWAYS have access, regardless of ownership or grants
        assert can_access is True, (
            f"Admin should always have access (is_owner={is_owner}, has_grant={has_grant}), "
            f"but can_access_project returned {can_access}"
        )
    finally:
        db_session.close()


# Feature: enterprise-rbac-authentication, Property 18: Access grants enable project access
# For any project with an explicit access grant to a Programmer, that Programmer should be 
# able to access the project even if they are not the owner.
@given(
    user_role=st.sampled_from([Role.PROGRAMMER, Role.VISITOR])
)
@settings(max_examples=100)
def test_property_18_access_grants_enable_project_access(user_role):
    """
    **Validates: Requirements 4.5**
    
    Property 18: Access grants enable project access
    
    For any project with an explicit access grant to a Programmer, that Programmer should be 
    able to access the project even if they are not the owner.
    """
    # Create a fresh database session for this test
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    try:
        # Create a user with the given role
        user = User(
            id=str(uuid.uuid4()),
            username=f"user_{uuid.uuid4().hex[:8]}",
            password_hash="dummy_hash",
            role=user_role,
            is_active=True
        )
        db_session.add(user)
        
        # Create a project owner (different from user)
        owner = User(
            id=str(uuid.uuid4()),
            username=f"owner_{uuid.uuid4().hex[:8]}",
            password_hash="dummy_hash",
            role=Role.PROGRAMMER,
            is_active=True
        )
        db_session.add(owner)
        
        # Create a project
        project = Project(
            id=str(uuid.uuid4()),
            name=f"project_{uuid.uuid4().hex[:8]}",
            owner_id=owner.id
        )
        db_session.add(project)
        db_session.commit()
        
        # Grant access to the user
        access_grant = ProjectAccess(
            project_id=project.id,
            user_id=user.id,
            granted_by=owner.id
        )
        db_session.add(access_grant)
        db_session.commit()
        
        # Check if user can access the project with VIEW_PROJECT permission
        can_access = RBACService.can_access_project(
            db_session, user.id, project.id, Permission.VIEW_PROJECT
        )
        
        # User should have access because of the explicit grant
        assert can_access is True, (
            f"User with role {user_role} should have access due to explicit grant, "
            f"but can_access_project returned {can_access}"
        )
        
        # However, they should NOT have access for other permissions (like UPDATE_PROJECT)
        can_update = RBACService.can_access_project(
            db_session, user.id, project.id, Permission.UPDATE_PROJECT
        )
        
        # Only owners can update projects (unless they're admin)
        assert can_update is False, (
            f"User with role {user_role} should NOT have UPDATE_PROJECT permission "
            f"even with access grant, but can_access_project returned {can_update}"
        )
    finally:
        db_session.close()



# Feature: enterprise-rbac-authentication, Property 6: Users have exactly one role
# For any user in the system, that user should have exactly one role assigned from 
# the set {Admin, Programmer, Visitor}.
@given(
    initial_role=st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR])
)
@settings(max_examples=100)
def test_property_6_users_have_exactly_one_role(initial_role):
    """
    **Validates: Requirements 2.1**
    
    Property 6: Users have exactly one role
    
    For any user in the system, that user should have exactly one role assigned from 
    the set {Admin, Programmer, Visitor}.
    """
    # Create a fresh database session for this test
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    try:
        # Create a user with the given role
        user = User(
            id=str(uuid.uuid4()),
            username=f"user_{uuid.uuid4().hex[:8]}",
            password_hash="dummy_hash",
            role=initial_role,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Retrieve the user from database
        retrieved_user = db_session.query(User).filter(User.id == user.id).first()
        
        # Verify the user has exactly one role
        assert retrieved_user is not None, "User should exist in database"
        assert retrieved_user.role == initial_role, (
            f"User should have role {initial_role}, but has {retrieved_user.role}"
        )
        
        # Verify the role is one of the valid roles
        assert retrieved_user.role in [Role.ADMIN, Role.PROGRAMMER, Role.VISITOR], (
            f"User role {retrieved_user.role} is not a valid role"
        )
    finally:
        db_session.close()


# Feature: enterprise-rbac-authentication, Property 29: Role updates apply immediately
# For any user whose role is changed, permission checks for that user should immediately 
# reflect the new role's permissions, even for active sessions.
@given(
    old_role=st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]),
    new_role=st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]),
    permission=permission_strategy()
)
@settings(max_examples=100)
def test_property_29_role_updates_apply_immediately(old_role, new_role, permission):
    """
    **Validates: Requirements 8.2**
    
    Property 29: Role updates apply immediately
    
    For any user whose role is changed, permission checks for that user should immediately 
    reflect the new role's permissions, even for active sessions.
    """
    # Create a fresh database session for this test
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    try:
        # Create an admin user who will assign roles
        admin = User(
            id=str(uuid.uuid4()),
            username=f"admin_{uuid.uuid4().hex[:8]}",
            password_hash="dummy_hash",
            role=Role.ADMIN,
            is_active=True
        )
        db_session.add(admin)
        
        # Create a user with the old role
        user = User(
            id=str(uuid.uuid4()),
            username=f"user_{uuid.uuid4().hex[:8]}",
            password_hash="dummy_hash",
            role=old_role,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Check permission with old role
        old_has_permission = RBACService.has_permission(db_session, user.id, permission)
        old_expected = permission in ROLE_PERMISSIONS.get(old_role, [])
        assert old_has_permission == old_expected, (
            f"Before role change: User with {old_role} should "
            f"{'have' if old_expected else 'not have'} {permission}"
        )
        
        # Assign new role
        success = RBACService.assign_role(db_session, user.id, new_role, admin.id)
        assert success is True, "Role assignment should succeed"
        
        # Check permission with new role - should reflect immediately
        new_has_permission = RBACService.has_permission(db_session, user.id, permission)
        new_expected = permission in ROLE_PERMISSIONS.get(new_role, [])
        assert new_has_permission == new_expected, (
            f"After role change: User with {new_role} should "
            f"{'have' if new_expected else 'not have'} {permission}, "
            f"but has_permission returned {new_has_permission}"
        )
        
        # Verify the role was actually changed
        updated_user = db_session.query(User).filter(User.id == user.id).first()
        assert updated_user.role == new_role, (
            f"User role should be {new_role}, but is {updated_user.role}"
        )
    finally:
        db_session.close()
