"""
Unit tests for authentication helper utilities.
"""
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.utils.auth_helpers import (
    require_self_or_admin,
    require_admin,
    require_active_user,
    require_email_confirmed,
    require_role,
    get_client_ip,
    get_user_agent
)


class MockUser:
    """Mock user for testing."""
    def __init__(self, id="123", role="developer", is_active=True, email_confirmed=True):
        self.id = id
        self.role = MagicMock()
        self.role.value = role
        self.is_active = is_active
        self.email_confirmed = email_confirmed


class TestRequireSelfOrAdmin:
    """Tests for require_self_or_admin function."""
    
    def test_require_self_or_admin_self_access(self):
        """Test allows user to access their own data."""
        user = MockUser(id="123")
        
        # Should not raise
        require_self_or_admin(user, "123")
    
    def test_require_self_or_admin_admin_access(self):
        """Test allows admin to access any user's data."""
        admin = MockUser(id="456", role="admin")
        
        # Should not raise
        require_self_or_admin(admin, "123")
    
    def test_require_self_or_admin_forbidden(self):
        """Test raises 403 when non-admin tries to access other user's data."""
        user = MockUser(id="123", role="developer")
        
        with pytest.raises(HTTPException) as exc_info:
            require_self_or_admin(user, "456")
        
        assert exc_info.value.status_code == 403
        assert "own data" in exc_info.value.detail
    
    def test_require_self_or_admin_custom_error(self):
        """Test custom error message."""
        user = MockUser(id="123", role="developer")
        
        with pytest.raises(HTTPException) as exc_info:
            require_self_or_admin(user, "456", error_message="Custom error")
        
        assert exc_info.value.detail == "Custom error"


class TestRequireAdmin:
    """Tests for require_admin function."""
    
    def test_require_admin_success(self):
        """Test allows admin user."""
        admin = MockUser(role="admin")
        
        # Should not raise
        require_admin(admin)
    
    def test_require_admin_forbidden(self):
        """Test raises 403 for non-admin user."""
        user = MockUser(role="developer")
        
        with pytest.raises(HTTPException) as exc_info:
            require_admin(user)
        
        assert exc_info.value.status_code == 403
        assert "Admin" in exc_info.value.detail


class TestRequireActiveUser:
    """Tests for require_active_user function."""
    
    def test_require_active_user_success(self):
        """Test allows active user."""
        user = MockUser(is_active=True)
        
        # Should not raise
        require_active_user(user)
    
    def test_require_active_user_forbidden(self):
        """Test raises 403 for inactive user."""
        user = MockUser(is_active=False)
        
        with pytest.raises(HTTPException) as exc_info:
            require_active_user(user)
        
        assert exc_info.value.status_code == 403
        assert "not active" in exc_info.value.detail


class TestRequireEmailConfirmed:
    """Tests for require_email_confirmed function."""
    
    def test_require_email_confirmed_success(self):
        """Test allows user with confirmed email."""
        user = MockUser(email_confirmed=True)
        
        # Should not raise
        require_email_confirmed(user)
    
    def test_require_email_confirmed_forbidden(self):
        """Test raises 403 for unconfirmed email."""
        user = MockUser(email_confirmed=False)
        
        with pytest.raises(HTTPException) as exc_info:
            require_email_confirmed(user)
        
        assert exc_info.value.status_code == 403
        assert "confirmed" in exc_info.value.detail


class TestRequireRole:
    """Tests for require_role function."""
    
    def test_require_role_success(self):
        """Test allows user with required role."""
        user = MockUser(role="admin")
        
        # Should not raise
        require_role(user, ["admin", "manager"])
    
    def test_require_role_forbidden(self):
        """Test raises 403 when user doesn't have required role."""
        user = MockUser(role="developer")
        
        with pytest.raises(HTTPException) as exc_info:
            require_role(user, ["admin", "manager"])
        
        assert exc_info.value.status_code == 403
        assert "required" in exc_info.value.detail


class TestGetClientIp:
    """Tests for get_client_ip function."""
    
    def test_get_client_ip_success(self):
        """Test extracts client IP from request."""
        request = MagicMock()
        request.client.host = "192.168.1.1"
        
        result = get_client_ip(request)
        
        assert result == "192.168.1.1"
    
    def test_get_client_ip_no_client(self):
        """Test returns default IP when client is None."""
        request = MagicMock()
        request.client = None
        
        result = get_client_ip(request)
        
        assert result == "0.0.0.0"


class TestGetUserAgent:
    """Tests for get_user_agent function."""
    
    def test_get_user_agent_success(self):
        """Test extracts user agent from request headers."""
        request = MagicMock()
        request.headers = {"user-agent": "Mozilla/5.0"}
        
        result = get_user_agent(request)
        
        assert result == "Mozilla/5.0"
    
    def test_get_user_agent_missing(self):
        """Test returns 'unknown' when user agent header is missing."""
        request = MagicMock()
        request.headers = {}
        
        result = get_user_agent(request)
        
        assert result == "unknown"
