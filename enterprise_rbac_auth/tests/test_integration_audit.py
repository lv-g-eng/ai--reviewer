"""
Integration tests for audit logging.

Tests audit trail functionality:
- Sensitive operations are logged
- Audit logs can be queried
- Audit logs are immutable
- Proper audit context is captured
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.project import Project
from ..models.audit_log import AuditLog
from ..models.enums import UserRole, AuditAction
from ..services.auth_service import AuthService


@pytest.fixture
def admin_user(db_session: Session):
    """Create an admin user for audit log access."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="audit_admin",
        email="audit_admin@example.com",
        password="AdminPass123!",
        role=UserRole.ADMIN
    )


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user for audit operations."""
    auth_service = AuthService(db_session)
    return auth_service.register_user(
        username="audit_user",
        email="audit_user@example.com",
        password="UserPass123!",
        role=UserRole.PROGRAMMER
    )


def get_auth_headers(client: TestClient, username: str, password: str) -> dict:
    """Helper function to get authentication headers."""
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuditLogging:
    """Test that sensitive operations are logged."""
    
    def test_user_login_is_logged(self, client: TestClient, db_session: Session, test_user: User):
        """Test user login creates audit log entry."""
        # Perform login
        response = client.post(
            "/api/auth/login",
            json={
                "username": "audit_user",
                "password": "UserPass123!"
            }
        )
        assert response.status_code == 200
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == test_user.id,
            AuditLog.action == AuditAction.USER_LOGIN
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        assert audit_log.user_id == test_user.id
        assert audit_log.action == AuditAction.USER_LOGIN
        assert audit_log.ip_address is not None
    
    def test_user_logout_is_logged(self, client: TestClient, db_session: Session, test_user: User):
        """Test user logout creates audit log entry."""
        # Login first
        headers = get_auth_headers(client, "audit_user", "UserPass123!")
        
        # Perform logout
        response = client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == test_user.id,
            AuditLog.action == AuditAction.USER_LOGOUT
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        assert audit_log.action == AuditAction.USER_LOGOUT
    
    def test_failed_login_is_logged(self, client: TestClient, db_session: Session, test_user: User):
        """Test failed login attempts are logged."""
        # Attempt login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "username": "audit_user",
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == AuditAction.LOGIN_FAILED,
            AuditLog.details.contains("audit_user")
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        assert audit_log.action == AuditAction.LOGIN_FAILED
    
    def test_user_creation_is_logged(self, client: TestClient, db_session: Session, admin_user: User):
        """Test user creation is logged."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Create new user
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "new_audit_user",
                "email": "newaudit@example.com",
                "password": "NewPass123!",
                "role": "programmer"
            }
        )
        assert response.status_code == 201
        new_user_id = response.json()["id"]
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == AuditAction.USER_CREATED,
            AuditLog.resource_id == str(new_user_id)
        ).first()
        
        assert audit_log is not None
        assert audit_log.user_id == admin_user.id
        assert audit_log.action == AuditAction.USER_CREATED
    
    def test_user_update_is_logged(self, client: TestClient, db_session: Session, admin_user: User, test_user: User):
        """Test user updates are logged."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Update user
        response = client.put(
            f"/api/users/{test_user.id}",
            headers=headers,
            json={"role": "visitor"}
        )
        assert response.status_code == 200
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == AuditAction.USER_UPDATED,
            AuditLog.resource_id == str(test_user.id)
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        assert audit_log.user_id == admin_user.id
    
    def test_user_deletion_is_logged(self, client: TestClient, db_session: Session, admin_user: User):
        """Test user deletion is logged."""
        # Create a user to delete
        auth_service = AuthService(db_session)
        user_to_delete = auth_service.register_user(
            username="user_to_delete",
            email="delete@example.com",
            password="DeletePass123!",
            role=UserRole.PROGRAMMER
        )
        
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Delete user
        response = client.delete(f"/api/users/{user_to_delete.id}", headers=headers)
        assert response.status_code == 200
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == AuditAction.USER_DELETED,
            AuditLog.resource_id == str(user_to_delete.id)
        ).first()
        
        assert audit_log is not None
        assert audit_log.user_id == admin_user.id
    
    def test_project_creation_is_logged(self, client: TestClient, db_session: Session, test_user: User):
        """Test project creation is logged."""
        headers = get_auth_headers(client, "audit_user", "UserPass123!")
        
        # Create project
        response = client.post(
            "/api/projects",
            headers=headers,
            json={
                "name": "Audit Test Project",
                "description": "Project for audit testing"
            }
        )
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == AuditAction.PROJECT_CREATED,
            AuditLog.resource_id == str(project_id)
        ).first()
        
        assert audit_log is not None
        assert audit_log.user_id == test_user.id
    
    def test_permission_change_is_logged(self, client: TestClient, db_session: Session, admin_user: User, test_user: User):
        """Test permission changes are logged."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Change user role (permission change)
        response = client.put(
            f"/api/users/{test_user.id}",
            headers=headers,
            json={"role": "admin"}
        )
        assert response.status_code == 200
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == AuditAction.PERMISSION_CHANGED,
            AuditLog.resource_id == str(test_user.id)
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        assert "role" in audit_log.details.lower() or "permission" in audit_log.details.lower()


class TestAuditLogQuery:
    """Test audit log querying functionality."""
    
    def test_admin_can_query_audit_logs(self, client: TestClient, admin_user: User):
        """Test admin can query audit logs."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        response = client.get("/api/audit/logs", headers=headers)
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
    
    def test_non_admin_cannot_query_audit_logs(self, client: TestClient, test_user: User):
        """Test non-admin users cannot query audit logs."""
        headers = get_auth_headers(client, "audit_user", "UserPass123!")
        
        response = client.get("/api/audit/logs", headers=headers)
        assert response.status_code == 403
    
    def test_filter_audit_logs_by_user(self, client: TestClient, db_session: Session, admin_user: User, test_user: User):
        """Test filtering audit logs by user."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Query logs for specific user
        response = client.get(
            f"/api/audit/logs?user_id={test_user.id}",
            headers=headers
        )
        assert response.status_code == 200
        logs = response.json()
        
        # All logs should be for the specified user
        for log in logs:
            assert log["user_id"] == test_user.id
    
    def test_filter_audit_logs_by_action(self, client: TestClient, admin_user: User):
        """Test filtering audit logs by action type."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Query logs for specific action
        response = client.get(
            f"/api/audit/logs?action={AuditAction.USER_LOGIN.value}",
            headers=headers
        )
        assert response.status_code == 200
        logs = response.json()
        
        # All logs should be for the specified action
        for log in logs:
            assert log["action"] == AuditAction.USER_LOGIN.value
    
    def test_filter_audit_logs_by_date_range(self, client: TestClient, admin_user: User):
        """Test filtering audit logs by date range."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Query logs for last 24 hours
        start_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        end_date = datetime.utcnow().isoformat()
        
        response = client.get(
            f"/api/audit/logs?start_date={start_date}&end_date={end_date}",
            headers=headers
        )
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
    
    def test_audit_log_pagination(self, client: TestClient, admin_user: User):
        """Test audit log pagination."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Query first page
        response = client.get("/api/audit/logs?page=1&page_size=10", headers=headers)
        assert response.status_code == 200
        page1 = response.json()
        
        # Query second page
        response = client.get("/api/audit/logs?page=2&page_size=10", headers=headers)
        assert response.status_code == 200
        page2 = response.json()
        
        # Pages should be different (if enough logs exist)
        if len(page1) == 10 and len(page2) > 0:
            assert page1[0]["id"] != page2[0]["id"]


class TestAuditLogImmutability:
    """Test that audit logs cannot be modified or deleted."""
    
    def test_audit_logs_cannot_be_updated(self, client: TestClient, db_session: Session, admin_user: User):
        """Test audit logs cannot be updated via API."""
        # Create an audit log
        audit_log = AuditLog(
            user_id=admin_user.id,
            action=AuditAction.USER_LOGIN,
            resource_type="User",
            resource_id=str(admin_user.id),
            details="Test login",
            ip_address="127.0.0.1"
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)
        
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Try to update audit log
        response = client.put(
            f"/api/audit/logs/{audit_log.id}",
            headers=headers,
            json={"details": "Modified details"}
        )
        # Should return 404 (endpoint doesn't exist) or 405 (method not allowed)
        assert response.status_code in [404, 405]
    
    def test_audit_logs_cannot_be_deleted(self, client: TestClient, db_session: Session, admin_user: User):
        """Test audit logs cannot be deleted via API."""
        # Create an audit log
        audit_log = AuditLog(
            user_id=admin_user.id,
            action=AuditAction.USER_LOGIN,
            resource_type="User",
            resource_id=str(admin_user.id),
            details="Test login",
            ip_address="127.0.0.1"
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)
        
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Try to delete audit log
        response = client.delete(f"/api/audit/logs/{audit_log.id}", headers=headers)
        # Should return 404 (endpoint doesn't exist) or 405 (method not allowed)
        assert response.status_code in [404, 405]
        
        # Verify log still exists
        log_exists = db_session.query(AuditLog).filter(
            AuditLog.id == audit_log.id
        ).first()
        assert log_exists is not None


class TestAuditContext:
    """Test that proper context is captured in audit logs."""
    
    def test_audit_log_captures_ip_address(self, client: TestClient, db_session: Session, test_user: User):
        """Test audit logs capture IP address."""
        # Perform login
        response = client.post(
            "/api/auth/login",
            json={
                "username": "audit_user",
                "password": "UserPass123!"
            }
        )
        assert response.status_code == 200
        
        # Check audit log has IP address
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == test_user.id,
            AuditLog.action == AuditAction.USER_LOGIN
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        assert audit_log.ip_address is not None
        assert len(audit_log.ip_address) > 0
    
    def test_audit_log_captures_user_agent(self, client: TestClient, db_session: Session, test_user: User):
        """Test audit logs capture user agent."""
        # Perform login with custom user agent
        response = client.post(
            "/api/auth/login",
            json={
                "username": "audit_user",
                "password": "UserPass123!"
            },
            headers={"User-Agent": "TestClient/1.0"}
        )
        assert response.status_code == 200
        
        # Check audit log has user agent
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == test_user.id,
            AuditLog.action == AuditAction.USER_LOGIN
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        # User agent might be in details or separate field
        assert audit_log.user_agent is not None or "TestClient" in audit_log.details
    
    def test_audit_log_captures_timestamp(self, client: TestClient, db_session: Session, test_user: User):
        """Test audit logs capture accurate timestamp."""
        before_time = datetime.utcnow()
        
        # Perform login
        response = client.post(
            "/api/auth/login",
            json={
                "username": "audit_user",
                "password": "UserPass123!"
            }
        )
        assert response.status_code == 200
        
        after_time = datetime.utcnow()
        
        # Check audit log timestamp
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == test_user.id,
            AuditLog.action == AuditAction.USER_LOGIN
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        assert before_time <= audit_log.timestamp <= after_time
    
    def test_audit_log_captures_resource_details(self, client: TestClient, db_session: Session, test_user: User):
        """Test audit logs capture resource type and ID."""
        headers = get_auth_headers(client, "audit_user", "UserPass123!")
        
        # Create project
        response = client.post(
            "/api/projects",
            headers=headers,
            json={
                "name": "Resource Test Project",
                "description": "Testing resource capture"
            }
        )
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == AuditAction.PROJECT_CREATED,
            AuditLog.resource_id == str(project_id)
        ).first()
        
        assert audit_log is not None
        assert audit_log.resource_type == "Project"
        assert audit_log.resource_id == str(project_id)
        assert audit_log.details is not None


class TestAuditLogSecurity:
    """Test security aspects of audit logging."""
    
    def test_sensitive_data_not_logged(self, client: TestClient, db_session: Session, admin_user: User):
        """Test that sensitive data like passwords are not logged."""
        headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        
        # Create user with password
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "sensitive_user",
                "email": "sensitive@example.com",
                "password": "SensitivePass123!",
                "role": "programmer"
            }
        )
        assert response.status_code == 201
        new_user_id = response.json()["id"]
        
        # Check audit log doesn't contain password
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == AuditAction.USER_CREATED,
            AuditLog.resource_id == str(new_user_id)
        ).first()
        
        assert audit_log is not None
        assert "SensitivePass123!" not in audit_log.details
        assert "password" not in audit_log.details.lower() or "***" in audit_log.details
    
    def test_audit_logs_survive_user_deletion(self, client: TestClient, db_session: Session, admin_user: User):
        """Test audit logs remain after user is deleted."""
        # Create a user
        auth_service = AuthService(db_session)
        temp_user = auth_service.register_user(
            username="temp_user",
            email="temp@example.com",
            password="TempPass123!",
            role=UserRole.PROGRAMMER
        )
        
        # Perform some actions to create audit logs
        headers = get_auth_headers(client, "temp_user", "TempPass123!")
        client.get("/api/users/me", headers=headers)
        
        # Verify audit logs exist
        logs_before = db_session.query(AuditLog).filter(
            AuditLog.user_id == temp_user.id
        ).count()
        assert logs_before > 0
        
        # Delete user
        admin_headers = get_auth_headers(client, "audit_admin", "AdminPass123!")
        response = client.delete(f"/api/users/{temp_user.id}", headers=admin_headers)
        assert response.status_code == 200
        
        # Verify audit logs still exist
        logs_after = db_session.query(AuditLog).filter(
            AuditLog.user_id == temp_user.id
        ).count()
        assert logs_after >= logs_before  # Should have deletion log too
