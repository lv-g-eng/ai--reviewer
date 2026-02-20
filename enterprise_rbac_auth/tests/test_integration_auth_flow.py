"""
Integration tests for complete authentication flow.

Tests the full authentication lifecycle:
- Login → Token acquisition → Protected resource access → Token refresh → Logout
- Session expiration handling
- Invalid token handling
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..main import app
from ..models.user import User
from ..models.session import Session as UserSession
from ..models.enums import UserRole
from ..services.auth_service import AuthService


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user for authentication flow tests."""
    auth_service = AuthService(db_session)
    user = auth_service.register_user(
        username="auth_flow_user",
        email="authflow@example.com",
        password="SecurePass123!",
        role=UserRole.PROGRAMMER
    )
    return user


class TestCompleteAuthFlow:
    """Test complete authentication flow from login to logout."""
    
    def test_complete_auth_lifecycle(self, client: TestClient, db_session: Session, test_user: User):
        """Test: Login → Get Token → Access Protected Resource → Refresh Token → Logout."""
        # Step 1: Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "SecurePass123!"
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert "refresh_token" in login_data
        assert login_data["token_type"] == "bearer"
        
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]
        
        # Step 2: Access protected resource with token
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/users/me", headers=headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["username"] == "auth_flow_user"
        assert profile_data["email"] == "authflow@example.com"
        
        # Step 3: Refresh token
        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        assert "access_token" in refresh_data
        new_access_token = refresh_data["access_token"]
        assert new_access_token != access_token  # Should be a new token
        
        # Step 4: Access protected resource with new token
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        profile_response2 = client.get("/api/users/me", headers=new_headers)
        assert profile_response2.status_code == 200
        
        # Step 5: Logout
        logout_response = client.post("/api/auth/logout", headers=new_headers)
        assert logout_response.status_code == 200
        
        # Step 6: Verify token is invalidated after logout
        profile_response3 = client.get("/api/users/me", headers=new_headers)
        assert profile_response3.status_code == 401
    
    def test_session_expiration_handling(self, client: TestClient, db_session: Session, test_user: User):
        """Test that expired sessions are properly rejected."""
        # Login to create a session
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "SecurePass123!"
            }
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]
        
        # Manually expire the session in database
        session = db_session.query(UserSession).filter(
            UserSession.user_id == test_user.id,
            UserSession.is_active == True
        ).first()
        assert session is not None
        session.expires_at = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()
        
        # Try to access protected resource with expired session
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    def test_invalid_token_handling(self, client: TestClient):
        """Test that invalid tokens are properly rejected."""
        # Test with completely invalid token
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401
        
        # Test with malformed token
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401
        
        # Test without token
        response = client.get("/api/users/me")
        assert response.status_code == 401
    
    def test_concurrent_sessions(self, client: TestClient, test_user: User):
        """Test that multiple concurrent sessions work correctly."""
        # Login from "device 1"
        login1 = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "SecurePass123!"
            }
        )
        assert login1.status_code == 200
        token1 = login1.json()["access_token"]
        
        # Login from "device 2"
        login2 = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "SecurePass123!"
            }
        )
        assert login2.status_code == 200
        token2 = login2.json()["access_token"]
        
        # Both tokens should work
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        response1 = client.get("/api/users/me", headers=headers1)
        response2 = client.get("/api/users/me", headers=headers2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Logout from device 1
        logout1 = client.post("/api/auth/logout", headers=headers1)
        assert logout1.status_code == 200
        
        # Token 1 should be invalid, token 2 should still work
        response1_after = client.get("/api/users/me", headers=headers1)
        response2_after = client.get("/api/users/me", headers=headers2)
        
        assert response1_after.status_code == 401
        assert response2_after.status_code == 200
    
    def test_password_change_invalidates_sessions(self, client: TestClient, db_session: Session, test_user: User):
        """Test that changing password invalidates all existing sessions."""
        # Login and get token
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "SecurePass123!"
            }
        )
        assert login_response.status_code == 200
        old_token = login_response.json()["access_token"]
        
        # Verify token works
        headers = {"Authorization": f"Bearer {old_token}"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        
        # Change password
        change_password_response = client.post(
            "/api/users/change-password",
            headers=headers,
            json={
                "old_password": "SecurePass123!",
                "new_password": "NewSecurePass456!"
            }
        )
        assert change_password_response.status_code == 200
        
        # Old token should be invalidated
        response_after = client.get("/api/users/me", headers=headers)
        assert response_after.status_code == 401
        
        # Should be able to login with new password
        new_login = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "NewSecurePass456!"
            }
        )
        assert new_login.status_code == 200


class TestTokenRefreshFlow:
    """Test token refresh mechanisms."""
    
    def test_refresh_token_rotation(self, client: TestClient, test_user: User):
        """Test that refresh tokens are rotated on use."""
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "SecurePass123!"
            }
        )
        original_refresh = login_response.json()["refresh_token"]
        
        # Use refresh token
        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": original_refresh}
        )
        assert refresh_response.status_code == 200
        new_refresh = refresh_response.json().get("refresh_token")
        
        # If rotation is enabled, new refresh token should be different
        if new_refresh:
            assert new_refresh != original_refresh
            
            # Old refresh token should be invalid
            old_refresh_response = client.post(
                "/api/auth/refresh",
                json={"refresh_token": original_refresh}
            )
            assert old_refresh_response.status_code == 401
    
    def test_expired_refresh_token(self, client: TestClient, db_session: Session, test_user: User):
        """Test that expired refresh tokens are rejected."""
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "SecurePass123!"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Manually expire the session
        session = db_session.query(UserSession).filter(
            UserSession.user_id == test_user.id,
            UserSession.is_active == True
        ).first()
        session.expires_at = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()
        
        # Try to refresh with expired token
        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 401


class TestAuthenticationEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_login_with_wrong_password(self, client: TestClient, test_user: User):
        """Test login fails with incorrect password."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "auth_flow_user",
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_with_nonexistent_user(self, client: TestClient):
        """Test login fails with non-existent user."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent_user",
                "password": "SomePassword123!"
            }
        )
        assert response.status_code == 401
    
    def test_access_protected_resource_without_auth(self, client: TestClient):
        """Test accessing protected resources without authentication."""
        response = client.get("/api/users/me")
        assert response.status_code == 401
    
    def test_malformed_authorization_header(self, client: TestClient):
        """Test various malformed authorization headers."""
        # Missing "Bearer" prefix
        headers = {"Authorization": "some_token"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401
        
        # Empty authorization header
        headers = {"Authorization": ""}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401
        
        # Bearer without token
        headers = {"Authorization": "Bearer "}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401
