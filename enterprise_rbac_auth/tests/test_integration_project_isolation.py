"""
Integration tests for project isolation.

Tests that users can only access their own projects:
- Users can only access projects they own
- Project owners can grant access to other users
- Admin can access all projects
- Proper isolation between different users' projects
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.project import Project, ProjectMember
from ..models.enums import UserRole, Permission
from ..services.auth_service import AuthService


@pytest.fixture
def user1(db_session: Session):
    """Create first test user."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="user1",
        email="user1@example.com",
        password="User1Pass123!",
        role=UserRole.PROGRAMMER
    )


@pytest.fixture
def user2(db_session: Session):
    """Create second test user."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="user2",
        email="user2@example.com",
        password="User2Pass123!",
        role=UserRole.PROGRAMMER
    )


@pytest.fixture
def user3(db_session: Session):
    """Create third test user."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="user3",
        email="user3@example.com",
        password="User3Pass123!",
        role=UserRole.PROGRAMMER
    )


@pytest.fixture
def admin_user(db_session: Session):
    """Create admin user."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="admin",
        email="admin@example.com",
        password="AdminPass123!",
        role=UserRole.ADMIN
    )


@pytest.fixture
def user1_project(db_session: Session, user1: User):
    """Create a project owned by user1."""
    project = Project(
        name="User1 Project",
        description="Project owned by user1",
        owner_id=user1.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def user2_project(db_session: Session, user2: User):
    """Create a project owned by user2."""
    project = Project(
        name="User2 Project",
        description="Project owned by user2",
        owner_id=user2.id
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


class TestProjectOwnershipIsolation:
    """Test that users can only access their own projects."""
    
    def test_user_can_access_own_project(self, client: TestClient, user1: User, user1_project: Project):
        """Test user can access their own project."""
        headers = get_auth_headers(client, "user1", "User1Pass123!")
        
        response = client.get(f"/api/projects/{user1_project.id}", headers=headers)
        assert response.status_code == 200
        project_data = response.json()
        assert project_data["id"] == user1_project.id
        assert project_data["owner_id"] == user1.id
    
    def test_user_cannot_access_others_project(self, client: TestClient, user1: User, user2_project: Project):
        """Test user cannot access another user's project."""
        headers = get_auth_headers(client, "user1", "User1Pass123!")
        
        response = client.get(f"/api/projects/{user2_project.id}", headers=headers)
        assert response.status_code == 403
        assert "access" in response.json()["detail"].lower()
    
    def test_user_cannot_update_others_project(self, client: TestClient, user1: User, user2_project: Project):
        """Test user cannot update another user's project."""
        headers = get_auth_headers(client, "user1", "User1Pass123!")
        
        response = client.put(
            f"/api/projects/{user2_project.id}",
            headers=headers,
            json={"description": "Unauthorized update"}
        )
        assert response.status_code == 403
    
    def test_user_cannot_delete_others_project(self, client: TestClient, user1: User, user2_project: Project):
        """Test user cannot delete another user's project."""
        headers = get_auth_headers(client, "user1", "User1Pass123!")
        
        response = client.delete(f"/api/projects/{user2_project.id}", headers=headers)
        assert response.status_code == 403
    
    def test_user_lists_only_own_projects(self, client: TestClient, user1: User, user1_project: Project, user2_project: Project):
        """Test user only sees their own projects in list."""
        headers = get_auth_headers(client, "user1", "User1Pass123!")
        
        response = client.get("/api/projects", headers=headers)
        assert response.status_code == 200
        projects = response.json()
        
        # Should only see own project
        project_ids = [p["id"] for p in projects]
        assert user1_project.id in project_ids
        assert user2_project.id not in project_ids


class TestProjectAccessGrants:
    """Test project owners can grant access to other users."""
    
    def test_owner_can_grant_access(self, client: TestClient, db_session: Session, user1: User, user2: User, user1_project: Project):
        """Test project owner can grant access to another user."""
        headers = get_auth_headers(client, "user1", "User1Pass123!")
        
        # Grant access to user2
        response = client.post(
            f"/api/projects/{user1_project.id}/members",
            headers=headers,
            json={
                "user_id": user2.id,
                "permissions": ["read", "write"]
            }
        )
        assert response.status_code == 201
        
        # Verify user2 can now access the project
        user2_headers = get_auth_headers(client, "user2", "User2Pass123!")
        response = client.get(f"/api/projects/{user1_project.id}", headers=user2_headers)
        assert response.status_code == 200
    
    def test_granted_user_has_specified_permissions(self, client: TestClient, db_session: Session, user1: User, user2: User, user1_project: Project):
        """Test granted user has only the specified permissions."""
        # Grant read-only access to user2
        member = ProjectMember(
            project_id=user1_project.id,
            user_id=user2.id,
            permissions=[Permission.PROJECT_READ]
        )
        db_session.add(member)
        db_session.commit()
        
        user2_headers = get_auth_headers(client, "user2", "User2Pass123!")
        
        # User2 can read
        response = client.get(f"/api/projects/{user1_project.id}", headers=user2_headers)
        assert response.status_code == 200
        
        # User2 cannot write
        response = client.put(
            f"/api/projects/{user1_project.id}",
            headers=user2_headers,
            json={"description": "Unauthorized update"}
        )
        assert response.status_code == 403
    
    def test_owner_can_revoke_access(self, client: TestClient, db_session: Session, user1: User, user2: User, user1_project: Project):
        """Test project owner can revoke access from a user."""
        # First grant access
        member = ProjectMember(
            project_id=user1_project.id,
            user_id=user2.id,
            permissions=[Permission.PROJECT_READ, Permission.PROJECT_WRITE]
        )
        db_session.add(member)
        db_session.commit()
        
        # Verify user2 has access
        user2_headers = get_auth_headers(client, "user2", "User2Pass123!")
        response = client.get(f"/api/projects/{user1_project.id}", headers=user2_headers)
        assert response.status_code == 200
        
        # Revoke access
        user1_headers = get_auth_headers(client, "user1", "User1Pass123!")
        response = client.delete(
            f"/api/projects/{user1_project.id}/members/{user2.id}",
            headers=user1_headers
        )
        assert response.status_code == 200
        
        # Verify user2 no longer has access
        response = client.get(f"/api/projects/{user1_project.id}", headers=user2_headers)
        assert response.status_code == 403
    
    def test_non_owner_cannot_grant_access(self, client: TestClient, db_session: Session, user1: User, user2: User, user3: User, user1_project: Project):
        """Test non-owner cannot grant access to project."""
        # Grant user2 access to the project
        member = ProjectMember(
            project_id=user1_project.id,
            user_id=user2.id,
            permissions=[Permission.PROJECT_READ, Permission.PROJECT_WRITE]
        )
        db_session.add(member)
        db_session.commit()
        
        # User2 tries to grant access to user3
        user2_headers = get_auth_headers(client, "user2", "User2Pass123!")
        response = client.post(
            f"/api/projects/{user1_project.id}/members",
            headers=user2_headers,
            json={
                "user_id": user3.id,
                "permissions": ["read"]
            }
        )
        assert response.status_code == 403


class TestAdminProjectAccess:
    """Test admin can access all projects."""
    
    def test_admin_can_access_any_project(self, client: TestClient, admin_user: User, user1_project: Project, user2_project: Project):
        """Test admin can access any project regardless of ownership."""
        headers = get_auth_headers(client, "admin", "AdminPass123!")
        
        # Access user1's project
        response = client.get(f"/api/projects/{user1_project.id}", headers=headers)
        assert response.status_code == 200
        
        # Access user2's project
        response = client.get(f"/api/projects/{user2_project.id}", headers=headers)
        assert response.status_code == 200
    
    def test_admin_can_update_any_project(self, client: TestClient, admin_user: User, user1_project: Project):
        """Test admin can update any project."""
        headers = get_auth_headers(client, "admin", "AdminPass123!")
        
        response = client.put(
            f"/api/projects/{user1_project.id}",
            headers=headers,
            json={"description": "Updated by admin"}
        )
        assert response.status_code == 200
        updated_project = response.json()
        assert updated_project["description"] == "Updated by admin"
    
    def test_admin_can_delete_any_project(self, client: TestClient, db_session: Session, admin_user: User, user1: User):
        """Test admin can delete any project."""
        # Create a project to delete
        project = Project(
            name="Project to Delete",
            description="Will be deleted by admin",
            owner_id=user1.id
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        headers = get_auth_headers(client, "admin", "AdminPass123!")
        
        response = client.delete(f"/api/projects/{project.id}", headers=headers)
        assert response.status_code == 200
        
        # Verify project is deleted
        response = client.get(f"/api/projects/{project.id}", headers=headers)
        assert response.status_code == 404
    
    def test_admin_sees_all_projects(self, client: TestClient, admin_user: User, user1_project: Project, user2_project: Project):
        """Test admin sees all projects in list."""
        headers = get_auth_headers(client, "admin", "AdminPass123!")
        
        response = client.get("/api/projects", headers=headers)
        assert response.status_code == 200
        projects = response.json()
        
        project_ids = [p["id"] for p in projects]
        assert user1_project.id in project_ids
        assert user2_project.id in project_ids


class TestProjectIsolationEdgeCases:
    """Test edge cases in project isolation."""
    
    def test_deleted_user_projects_are_inaccessible(self, client: TestClient, db_session: Session, user1: User, user1_project: Project, admin_user: User):
        """Test projects of deleted users become inaccessible."""
        # Admin deletes user1
        admin_headers = get_auth_headers(client, "admin", "AdminPass123!")
        response = client.delete(f"/api/users/{user1.id}", headers=admin_headers)
        assert response.status_code == 200
        
        # Try to access the project (should fail)
        response = client.get(f"/api/projects/{user1_project.id}", headers=admin_headers)
        assert response.status_code in [404, 403]  # Either not found or forbidden
    
    def test_project_transfer_updates_ownership(self, client: TestClient, db_session: Session, user1: User, user2: User, user1_project: Project, admin_user: User):
        """Test transferring project ownership."""
        # Admin transfers project from user1 to user2
        admin_headers = get_auth_headers(client, "admin", "AdminPass123!")
        response = client.put(
            f"/api/projects/{user1_project.id}/transfer",
            headers=admin_headers,
            json={"new_owner_id": user2.id}
        )
        assert response.status_code == 200
        
        # User1 should no longer have access
        user1_headers = get_auth_headers(client, "user1", "User1Pass123!")
        response = client.get(f"/api/projects/{user1_project.id}", headers=user1_headers)
        assert response.status_code == 403
        
        # User2 should now have access
        user2_headers = get_auth_headers(client, "user2", "User2Pass123!")
        response = client.get(f"/api/projects/{user1_project.id}", headers=user2_headers)
        assert response.status_code == 200
        project_data = response.json()
        assert project_data["owner_id"] == user2.id
    
    def test_public_projects_accessible_to_all(self, client: TestClient, db_session: Session, user1: User, user2: User):
        """Test public projects are accessible to all authenticated users."""
        # Create a public project
        public_project = Project(
            name="Public Project",
            description="A public project",
            owner_id=user1.id,
            is_public=True
        )
        db_session.add(public_project)
        db_session.commit()
        db_session.refresh(public_project)
        
        # User2 should be able to access it
        user2_headers = get_auth_headers(client, "user2", "User2Pass123!")
        response = client.get(f"/api/projects/{public_project.id}", headers=user2_headers)
        assert response.status_code == 200
    
    def test_private_projects_not_accessible(self, client: TestClient, db_session: Session, user1: User, user2: User):
        """Test private projects are not accessible to other users."""
        # Create a private project
        private_project = Project(
            name="Private Project",
            description="A private project",
            owner_id=user1.id,
            is_public=False
        )
        db_session.add(private_project)
        db_session.commit()
        db_session.refresh(private_project)
        
        # User2 should not be able to access it
        user2_headers = get_auth_headers(client, "user2", "User2Pass123!")
        response = client.get(f"/api/projects/{private_project.id}", headers=user2_headers)
        assert response.status_code == 403


class TestConcurrentProjectAccess:
    """Test concurrent access to projects."""
    
    def test_multiple_users_with_access(self, client: TestClient, db_session: Session, user1: User, user2: User, user3: User, user1_project: Project):
        """Test multiple users can have concurrent access to same project."""
        # Grant access to both user2 and user3
        member2 = ProjectMember(
            project_id=user1_project.id,
            user_id=user2.id,
            permissions=[Permission.PROJECT_READ, Permission.PROJECT_WRITE]
        )
        member3 = ProjectMember(
            project_id=user1_project.id,
            user_id=user3.id,
            permissions=[Permission.PROJECT_READ]
        )
        db_session.add_all([member2, member3])
        db_session.commit()
        
        # All three users should be able to access
        user1_headers = get_auth_headers(client, "user1", "User1Pass123!")
        user2_headers = get_auth_headers(client, "user2", "User2Pass123!")
        user3_headers = get_auth_headers(client, "user3", "User3Pass123!")
        
        response1 = client.get(f"/api/projects/{user1_project.id}", headers=user1_headers)
        response2 = client.get(f"/api/projects/{user1_project.id}", headers=user2_headers)
        response3 = client.get(f"/api/projects/{user1_project.id}", headers=user3_headers)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
