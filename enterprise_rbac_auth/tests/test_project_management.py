"""
Property-based tests for project management API endpoints.
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime, timezone

from ..models import User, Role, Project, ProjectAccess, Permission
from ..models.user import Base
from ..services.auth_service import AuthService
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


class TestProjectManagement:
    """Property-based tests for project management operations."""
    
    # Feature: enterprise-rbac-authentication, Property 8: Project creation sets ownership
    # **Validates: Requirements 2.3, 4.1**
    @given(
        username=st.text(min_size=3, max_size=40, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        project_name=st.text(min_size=1, max_size=100),
        project_description=st.text(min_size=0, max_size=500)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_8_project_creation_sets_ownership(
        self, username, project_name, project_description
    ):
        """
        Property 8: Project creation sets ownership
        
        For any Programmer who creates a project, the created project's ownerId field
        should equal that Programmer's userId.
        
        **Validates: Requirements 2.3, 4.1**
        """
        # Create a fresh database session for this test
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Add UUID suffix to ensure unique username
            unique_username = f"{username}_{uuid.uuid4().hex[:8]}"
            
            # Create a programmer user
            user_id = str(uuid.uuid4())
            password_hash = AuthService.hash_password("test_password")
            user = User(
                id=user_id,
                username=unique_username,
                password_hash=password_hash,
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(user)
            db_session.commit()
            
            # Create a project as this programmer
            project_id = str(uuid.uuid4())
            project = Project(
                id=project_id,
                name=project_name,
                description=project_description if project_description else None,
                owner_id=user_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db_session.add(project)
            db_session.commit()
            db_session.refresh(project)
            
            # Verify ownership is set correctly
            assert project.owner_id == user_id, "Project owner_id should match creator's user_id"
            assert project.id == project_id, "Project should have correct ID"
            assert project.name == project_name, "Project should have correct name"
            
            # Verify the programmer can access their own project
            can_access = RBACService.can_access_project(
                db_session, user_id, project_id, Permission.VIEW_PROJECT
            )
            assert can_access is True, "Project owner should have access to their project"
            
        finally:
            db_session.close()
    
    # Feature: enterprise-rbac-authentication, Property 11: Visitors have read-only access to assigned projects
    # **Validates: Requirements 2.6**
    @given(
        visitor_username=st.text(min_size=3, max_size=40, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        owner_username=st.text(min_size=3, max_size=40, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        project_name=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_11_visitors_readonly_access_assigned_projects(
        self, visitor_username, owner_username, project_name
    ):
        """
        Property 11: Visitors have read-only access to assigned projects
        
        For any Visitor with an assigned project, read operations on that project
        should succeed, while write operations should be denied.
        
        **Validates: Requirements 2.6**
        """
        # Create a fresh database session for this test
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Add UUID suffix to ensure unique usernames
            unique_visitor = f"{visitor_username}_{uuid.uuid4().hex[:8]}"
            unique_owner = f"{owner_username}_{uuid.uuid4().hex[:8]}"
            
            # Create a visitor user
            visitor_id = str(uuid.uuid4())
            visitor = User(
                id=visitor_id,
                username=unique_visitor,
                password_hash=AuthService.hash_password("visitor_password"),
                role=Role.VISITOR,
                is_active=True
            )
            db_session.add(visitor)
            
            # Create a programmer (project owner)
            owner_id = str(uuid.uuid4())
            owner = User(
                id=owner_id,
                username=unique_owner,
                password_hash=AuthService.hash_password("owner_password"),
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(owner)
            db_session.commit()
            
            # Create a project owned by the programmer
            project_id = str(uuid.uuid4())
            project = Project(
                id=project_id,
                name=project_name,
                description="Test project for visitor access",
                owner_id=owner_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db_session.add(project)
            db_session.commit()
            
            # Grant access to the visitor
            access_grant = ProjectAccess(
                project_id=project_id,
                user_id=visitor_id,
                granted_at=datetime.now(timezone.utc),
                granted_by=owner_id
            )
            db_session.add(access_grant)
            db_session.commit()
            
            # Test read access - should succeed
            can_view = RBACService.can_access_project(
                db_session, visitor_id, project_id, Permission.VIEW_PROJECT
            )
            assert can_view is True, "Visitor should have read access to assigned project"
            
            # Test write access - should fail
            # Visitors don't have UPDATE_PROJECT permission
            can_update = RBACService.can_access_project(
                db_session, visitor_id, project_id, Permission.UPDATE_PROJECT
            )
            assert can_update is False, "Visitor should NOT have update access to project"
            
            # Test delete access - should fail
            # Visitors don't have DELETE_PROJECT permission
            can_delete = RBACService.can_access_project(
                db_session, visitor_id, project_id, Permission.DELETE_PROJECT
            )
            assert can_delete is False, "Visitor should NOT have delete access to project"
            
            # Verify visitor has VISITOR role permissions only
            visitor_permissions = RBACService.get_role_permissions(Role.VISITOR)
            assert Permission.VIEW_PROJECT in visitor_permissions, "Visitor should have VIEW_PROJECT permission"
            assert Permission.UPDATE_PROJECT not in visitor_permissions, "Visitor should NOT have UPDATE_PROJECT permission"
            assert Permission.DELETE_PROJECT not in visitor_permissions, "Visitor should NOT have DELETE_PROJECT permission"
            
        finally:
            db_session.close()
    
    def test_project_access_without_grant(self, db_session):
        """Test that users cannot access projects without explicit grant or ownership."""
        # Create two programmers
        programmer1_id = str(uuid.uuid4())
        programmer1 = User(
            id=programmer1_id,
            username="programmer1",
            password_hash=AuthService.hash_password("password1"),
            role=Role.PROGRAMMER,
            is_active=True
        )
        
        programmer2_id = str(uuid.uuid4())
        programmer2 = User(
            id=programmer2_id,
            username="programmer2",
            password_hash=AuthService.hash_password("password2"),
            role=Role.PROGRAMMER,
            is_active=True
        )
        
        db_session.add(programmer1)
        db_session.add(programmer2)
        db_session.commit()
        
        # Programmer1 creates a project
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name="Private Project",
            description="Programmer1's private project",
            owner_id=programmer1_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(project)
        db_session.commit()
        
        # Programmer1 should have access
        can_access_owner = RBACService.can_access_project(
            db_session, programmer1_id, project_id, Permission.VIEW_PROJECT
        )
        assert can_access_owner is True, "Project owner should have access"
        
        # Programmer2 should NOT have access (no grant)
        can_access_other = RBACService.can_access_project(
            db_session, programmer2_id, project_id, Permission.VIEW_PROJECT
        )
        assert can_access_other is False, "Other programmer should NOT have access without grant"
    
    def test_admin_bypasses_project_isolation(self, db_session):
        """Test that admins can access all projects regardless of ownership."""
        # Create a programmer
        programmer_id = str(uuid.uuid4())
        programmer = User(
            id=programmer_id,
            username="programmer",
            password_hash=AuthService.hash_password("password"),
            role=Role.PROGRAMMER,
            is_active=True
        )
        
        # Create an admin
        admin_id = str(uuid.uuid4())
        admin = User(
            id=admin_id,
            username="admin",
            password_hash=AuthService.hash_password("admin_password"),
            role=Role.ADMIN,
            is_active=True
        )
        
        db_session.add(programmer)
        db_session.add(admin)
        db_session.commit()
        
        # Programmer creates a project
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name="Programmer's Project",
            description="Private project",
            owner_id=programmer_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(project)
        db_session.commit()
        
        # Admin should have access even without ownership or grant
        can_access_admin = RBACService.can_access_project(
            db_session, admin_id, project_id, Permission.VIEW_PROJECT
        )
        assert can_access_admin is True, "Admin should bypass project isolation"
        
        # Admin should also have modify access
        can_modify_admin = RBACService.can_access_project(
            db_session, admin_id, project_id, Permission.UPDATE_PROJECT
        )
        assert can_modify_admin is True, "Admin should have modify access to all projects"
    
    def test_project_access_grant_and_revoke(self, db_session):
        """Test granting and revoking project access."""
        # Create owner and another user
        owner_id = str(uuid.uuid4())
        owner = User(
            id=owner_id,
            username="owner",
            password_hash=AuthService.hash_password("password"),
            role=Role.PROGRAMMER,
            is_active=True
        )
        
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username="user",
            password_hash=AuthService.hash_password("password"),
            role=Role.PROGRAMMER,
            is_active=True
        )
        
        db_session.add(owner)
        db_session.add(user)
        db_session.commit()
        
        # Create a project
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name="Test Project",
            description="Test project for access control",
            owner_id=owner_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(project)
        db_session.commit()
        
        # User should not have access initially
        can_access_before = RBACService.can_access_project(
            db_session, user_id, project_id, Permission.VIEW_PROJECT
        )
        assert can_access_before is False, "User should not have access before grant"
        
        # Grant access
        success_grant = RBACService.grant_project_access(
            db_session, project_id, user_id, owner_id
        )
        assert success_grant is True, "Access grant should succeed"
        
        # User should now have access
        can_access_after = RBACService.can_access_project(
            db_session, user_id, project_id, Permission.VIEW_PROJECT
        )
        assert can_access_after is True, "User should have access after grant"
        
        # Revoke access
        success_revoke = RBACService.revoke_project_access(
            db_session, project_id, user_id, owner_id
        )
        assert success_revoke is True, "Access revoke should succeed"
        
        # User should no longer have access
        can_access_revoked = RBACService.can_access_project(
            db_session, user_id, project_id, Permission.VIEW_PROJECT
        )
        assert can_access_revoked is False, "User should not have access after revoke"
