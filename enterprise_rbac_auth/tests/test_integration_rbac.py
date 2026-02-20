"""
Integration tests for Role-Based Access Control (RBAC).

Tests role-based access control across different user roles:
- Admin users can access all endpoints
- Programmer users can access project endpoints
- Visitor users have read-only access
- Unauthorized access returns 403
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.project import Project
from ..models.enums import UserRole, Permission
from ..services.auth_service import AuthService


@pytest.fixture
def admin_user(db_session: Session):
    """Create an admin user."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="admin_user",
        email="admin@example.com",
        password="AdminPass123!",
        role=UserRole.ADMIN
    )


@pytest.fixture
def programmer_user(db_session: Session):
    """Create a programmer user."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="programmer_user",
        email="programmer@example.com",
        password="ProgPass123!",
        role=UserRole.PROGRAMMER
    )


@pytest.fixture
def visitor_user(db_session: Session):
    """Create a visitor user."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="visitor_user",
        email="visitor@example.com",
        password="VisitorPass123!",
        role=UserRole.VISITOR
    )


@pytest.fixture
def test_project(db_session: Session, programmer_user: User):
    """Create a test project owned by programmer."""
    project = Project(
        name="Test Project",
        description="A test project for RBAC testing",
        owner_id=programmer_user.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


def get_auth_headers(client: TestClient, username: str, password: str) -> dict:
    """Helper function to get authentication headers."""
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAdminAccess:
    """Test admin user access to all endpoints."""
    
    def test_admin_can_access_all_users(self, client: TestClient, admin_user: User, programmer_user: User):
        """Test admin can list and view all users."""
        headers = get_auth_headers(client, "admin_user", "AdminPass123!")
        
        # List all users
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 2  # At least admin and programmer
    
    def test_admin_can_manage_users(self, client: TestClient, admin_user: User):
        """Test admin can create, update, and delete users."""
        headers = get_auth_headers(client, "admin_user", "AdminPass123!")
        
        # Create user
        create_response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "new_user",
                "email": "newuser@example.com",
                "password": "NewPass123!",
                "role": "programmer"
            }
        )
        assert create_response.status_code == 201
        new_user_id = create_response.json()["id"]
        
        # Update user
        update_response = client.put(
            f"/api/users/{new_user_id}",
            headers=headers,
            json={"role": "visitor"}
        )
        assert update_response.status_code == 200
        
        # Delete user
        delete_response = client.delete(f"/api/users/{new_user_id}", headers=headers)
        assert delete_response.status_code == 200
    
    def test_admin_can_access_all_projects(self, client: TestClient, admin_user: User, test_project: Project):
        """Test admin can access all projects regardless of ownership."""
        headers = get_auth_headers(client, "admin_user", "AdminPass123!")
        
        # List all projects
        response = client.get("/api/projects", headers=headers)
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) >= 1
        
        # Access specific project
        response = client.get(f"/api/projects/{test_project.id}", headers=headers)
        assert response.status_code == 200
    
    def test_admin_can_view_audit_logs(self, client: TestClient, admin_user: User):
        """Test admin can view audit logs."""
        headers = get_auth_headers(client, "admin_user", "AdminPass123!")
        
        response = client.get("/api/audit/logs", headers=headers)
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)


class TestProgrammerAccess:
    """Test programmer user access to project endpoints."""
    
    def test_programmer_can_access_own_projects(self, client: TestClient, programmer_user: User, test_project: Project):
        """Test programmer can access their own projects."""
        headers = get_auth_headers(client, "programmer_user", "ProgPass123!")
        
        # Access own project
        response = client.get(f"/api/projects/{test_project.id}", headers=headers)
        assert response.status_code == 200
        project_data = response.json()
        assert project_data["id"] == test_project.id
    
    def test_programmer_can_create_projects(self, client: TestClient, programmer_user: User):
        """Test programmer can create new projects."""
        headers = get_auth_headers(client, "programmer_user", "ProgPass123!")
        
        response = client.post(
            "/api/projects",
            headers=headers,
            json={
                "name": "New Project",
                "description": "A new project created by programmer"
            }
        )
        assert response.status_code == 201
        project_data = response.json()
        assert project_data["name"] == "New Project"
        assert project_data["owner_id"] == programmer_user.id
    
    def test_programmer_can_update_own_projects(self, client: TestClient, programmer_user: User, test_project: Project):
        """Test programmer can update their own projects."""
        headers = get_auth_headers(client, "programmer_user", "ProgPass123!")
        
        response = client.put(
            f"/api/projects/{test_project.id}",
            headers=headers,
            json={"description": "Updated description"}
        )
        assert response.status_code == 200
        updated_project = response.json()
        assert updated_project["description"] == "Updated description"
    
    def test_programmer_cannot_access_others_projects(self, client: TestClient, db_session: Session, programmer_user: User, admin_user: User):
        """Test programmer cannot access projects they don't own."""
        # Create a project owned by admin
        admin_project = Project(
            name="Admin Project",
            description="Project owned by admin",
            owner_id=admin_user.id
        )
        db_session.add(admin_project)
        db_session.commit()
        db_session.refresh(admin_project)
        
        headers = get_auth_headers(client, "programmer_user", "ProgPass123!")
        
        # Try to access admin's project
        response = client.get(f"/api/projects/{admin_project.id}", headers=headers)
        assert response.status_code == 403
    
    def test_programmer_cannot_manage_users(self, client: TestClient, programmer_user: User, visitor_user: User):
        """Test programmer cannot create, update, or delete users."""
        headers = get_auth_headers(client, "programmer_user", "ProgPass123!")
        
        # Try to create user
        create_response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "unauthorized_user",
                "email": "unauth@example.com",
                "password": "Pass123!",
                "role": "programmer"
            }
        )
        assert create_response.status_code == 403
        
        # Try to update user
        update_response = client.put(
            f"/api/users/{visitor_user.id}",
            headers=headers,
            json={"role": "admin"}
        )
        assert update_response.status_code == 403
        
        # Try to delete user
        delete_response = client.delete(f"/api/users/{visitor_user.id}", headers=headers)
        assert delete_response.status_code == 403
    
    def test_programmer_cannot_view_audit_logs(self, client: TestClient, programmer_user: User):
        """Test programmer cannot view audit logs."""
        headers = get_auth_headers(client, "programmer_user", "ProgPass123!")
        
        response = client.get("/api/audit/logs", headers=headers)
        assert response.status_code == 403


class TestVisitorAccess:
    """Test visitor user has read-only access."""
    
    def test_visitor_can_view_own_profile(self, client: TestClient, visitor_user: User):
        """Test visitor can view their own profile."""
        headers = get_auth_headers(client, "visitor_user", "VisitorPass123!")
        
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["username"] == "visitor_user"
    
    def test_visitor_can_view_public_projects(self, client: TestClient, db_session: Session, visitor_user: User, programmer_user: User):
        """Test visitor can view public projects."""
        # Create a public project
        public_project = Project(
            name="Public Project",
            description="A public project",
            owner_id=programmer_user.id,
            is_public=True
        )
        db_session.add(public_project)
        db_session.commit()
        db_session.refresh(public_project)
        
        headers = get_auth_headers(client, "visitor_user", "VisitorPass123!")
        
        response = client.get(f"/api/projects/{public_project.id}", headers=headers)
        assert response.status_code == 200
    
    def test_visitor_cannot_create_projects(self, client: TestClient, visitor_user: User):
        """Test visitor cannot create projects."""
        headers = get_auth_headers(client, "visitor_user", "VisitorPass123!")
        
        response = client.post(
            "/api/projects",
            headers=headers,
            json={
                "name": "Unauthorized Project",
                "description": "Should not be created"
            }
        )
        assert response.status_code == 403
    
    def test_visitor_cannot_update_projects(self, client: TestClient, visitor_user: User, test_project: Project):
        """Test visitor cannot update projects."""
        headers = get_auth_headers(client, "visitor_user", "VisitorPass123!")
        
        response = client.put(
            f"/api/projects/{test_project.id}",
            headers=headers,
            json={"description": "Unauthorized update"}
        )
        assert response.status_code == 403
    
    def test_visitor_cannot_delete_projects(self, client: TestClient, visitor_user: User, test_project: Project):
        """Test visitor cannot delete projects."""
        headers = get_auth_headers(client, "visitor_user", "VisitorPass123!")
        
        response = client.delete(f"/api/projects/{test_project.id}", headers=headers)
        assert response.status_code == 403
    
    def test_visitor_cannot_manage_users(self, client: TestClient, visitor_user: User):
        """Test visitor cannot manage users."""
        headers = get_auth_headers(client, "visitor_user", "VisitorPass123!")
        
        # Try to list users
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 403
        
        # Try to create user
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "new_user",
                "email": "new@example.com",
                "password": "Pass123!",
                "role": "visitor"
            }
        )
        assert response.status_code == 403


class TestUnauthorizedAccess:
    """Test unauthorized access returns 403."""
    
    def test_unauthenticated_access_returns_401(self, client: TestClient):
        """Test accessing protected endpoints without authentication."""
        # Try to access user profile
        response = client.get("/api/users/me")
        assert response.status_code == 401
        
        # Try to list projects
        response = client.get("/api/projects")
        assert response.status_code == 401
        
        # Try to create project
        response = client.post(
            "/api/projects",
            json={"name": "Test", "description": "Test"}
        )
        assert response.status_code == 401
    
    def test_insufficient_permissions_returns_403(self, client: TestClient, visitor_user: User):
        """Test accessing endpoints without sufficient permissions."""
        headers = get_auth_headers(client, "visitor_user", "VisitorPass123!")
        
        # Try to access admin-only endpoint
        response = client.get("/api/audit/logs", headers=headers)
        assert response.status_code == 403
        
        # Try to create project (requires programmer role)
        response = client.post(
            "/api/projects",
            headers=headers,
            json={"name": "Test", "description": "Test"}
        )
        assert response.status_code == 403


class TestRoleHierarchy:
    """Test role hierarchy and permission inheritance."""
    
    def test_admin_has_all_permissions(self, client: TestClient, admin_user: User):
        """Test admin role has all permissions."""
        headers = get_auth_headers(client, "admin_user", "AdminPass123!")
        
        # Can manage users
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        
        # Can manage projects
        response = client.get("/api/projects", headers=headers)
        assert response.status_code == 200
        
        # Can view audit logs
        response = client.get("/api/audit/logs", headers=headers)
        assert response.status_code == 200
    
    def test_programmer_has_project_permissions(self, client: TestClient, programmer_user: User):
        """Test programmer role has project management permissions."""
        headers = get_auth_headers(client, "programmer_user", "ProgPass123!")
        
        # Can create projects
        response = client.post(
            "/api/projects",
            headers=headers,
            json={"name": "Test Project", "description": "Test"}
        )
        assert response.status_code == 201
        
        # Cannot manage users
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 403
    
    def test_visitor_has_read_only_permissions(self, client: TestClient, visitor_user: User):
        """Test visitor role has only read permissions."""
        headers = get_auth_headers(client, "visitor_user", "VisitorPass123!")
        
        # Can view own profile
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        
        # Cannot create projects
        response = client.post(
            "/api/projects",
            headers=headers,
            json={"name": "Test", "description": "Test"}
        )
        assert response.status_code == 403
        
        # Cannot manage users
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 403
