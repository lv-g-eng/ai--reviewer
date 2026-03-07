"""
Tests for Audit Log API Endpoints

This test suite validates the audit log query and export API endpoints.

Validates Requirements: 15.6, 15.7
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import uuid
import json

from app.main import app
from app.api.dependencies import get_current_user
from app.database.postgresql import get_db


# ========================================
# Test Fixtures
# ========================================

@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_admin_user():
    """Mock admin user for authentication"""
    return {
        "id": str(uuid.uuid4()),
        "email": "admin@example.com",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def mock_compliance_user():
    """Mock compliance officer user for authentication"""
    return {
        "id": str(uuid.uuid4()),
        "email": "compliance@example.com",
        "role": "compliance_officer",
        "is_active": True,
    }


@pytest.fixture
def mock_regular_user():
    """Mock regular user for authentication"""
    return {
        "id": str(uuid.uuid4()),
        "email": "user@example.com",
        "role": "developer",
        "is_active": True,
    }


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


# ========================================
# Test Query Endpoint (Req 15.6)
# ========================================

def test_query_audit_logs_requires_authentication(client):
    """Test that querying audit logs requires authentication"""
    response = client.get("/api/v1/audit-logs/")
    assert response.status_code == 401  # No auth header


def test_query_audit_logs_requires_admin_or_compliance_role(client, mock_regular_user, mock_db):
    """Test that only admin and compliance_officer can query audit logs"""
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_regular_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get("/api/v1/audit-logs/")
    
    assert response.status_code == 403
    assert "administrators and compliance officers" in response.json()["detail"].lower()
    
    # Clean up
    app.dependency_overrides.clear()


@patch('app.api.v1.endpoints.audit_logs.AuditLoggingService')
def test_query_audit_logs_with_filters(mock_service_class, client, mock_admin_user, mock_db):
    """Test querying audit logs with various filters"""
    # Setup mock service
    mock_service = AsyncMock()
    mock_service.query_logs.return_value = {
        "total": 2,
        "limit": 100,
        "offset": 0,
        "items": [
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "auth.login.success",
                "event_category": "auth",
                "user_email": "test@example.com",
                "action": "login",
                "description": "User logged in",
                "success": True,
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "auth.login.failure",
                "event_category": "auth",
                "user_email": "test@example.com",
                "action": "login",
                "description": "Login failed",
                "success": False,
            },
        ],
    }
    mock_service_class.return_value = mock_service
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Query with filters
    response = client.get(
        "/api/v1/audit-logs/",
        params={
            "user_email": "test@example.com",
            "action": "login",
            "limit": 100,
            "offset": 0,
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["user_email"] == "test@example.com"
    
    # Verify service was called with correct parameters
    mock_service.query_logs.assert_called_once()
    
    # Clean up
    app.dependency_overrides.clear()


@patch('app.api.v1.endpoints.audit_logs.AuditLoggingService')
def test_query_audit_logs_with_date_range(mock_service_class, client, mock_compliance_user, mock_db):
    """Test querying audit logs with date range filter"""
    # Setup mock service
    mock_service = AsyncMock()
    mock_service.query_logs.return_value = {
        "total": 1,
        "limit": 100,
        "offset": 0,
        "items": [
            {
                "id": str(uuid.uuid4()),
                "timestamp": "2024-01-15T10:00:00Z",
                "event_type": "data.update",
                "event_category": "data",
                "user_email": "admin@example.com",
                "action": "update_project",
                "description": "Updated project",
                "success": True,
            },
        ],
    }
    mock_service_class.return_value = mock_service
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_compliance_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Query with date range
    response = client.get(
        "/api/v1/audit-logs/",
        params={
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-31T23:59:59Z",
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    
    # Clean up
    app.dependency_overrides.clear()


@patch('app.api.v1.endpoints.audit_logs.AuditLoggingService')
def test_query_audit_logs_with_pagination(mock_service_class, client, mock_admin_user, mock_db):
    """Test querying audit logs with pagination"""
    # Setup mock service
    mock_service = AsyncMock()
    mock_service.query_logs.return_value = {
        "total": 50,
        "limit": 10,
        "offset": 20,
        "items": [{"id": str(uuid.uuid4())} for _ in range(10)],
    }
    mock_service_class.return_value = mock_service
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Query with pagination
    response = client.get(
        "/api/v1/audit-logs/",
        params={
            "limit": 10,
            "offset": 20,
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 50
    assert data["limit"] == 10
    assert data["offset"] == 20
    assert len(data["items"]) == 10
    
    # Clean up
    app.dependency_overrides.clear()


# ========================================
# Test Export Endpoint (Req 15.7)
# ========================================

@patch('app.api.v1.endpoints.audit_logs.AuditLoggingService')
def test_export_audit_logs_json_format(mock_service_class, client, mock_admin_user, mock_db):
    """Test exporting audit logs in JSON format"""
    # Setup mock service
    mock_service = AsyncMock()
    export_data = {
        "total": 2,
        "items": [
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "auth.login.success",
                "user_email": "test@example.com",
            },
        ],
    }
    mock_service.export_logs.return_value = json.dumps(export_data, indent=2)
    mock_service_class.return_value = mock_service
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Export as JSON
    response = client.post(
        "/api/v1/audit-logs/export",
        json={
            "format": "json",
            "user_email": "test@example.com",
        }
    )
    
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
    assert ".json" in response.headers["content-disposition"]
    
    # Clean up
    app.dependency_overrides.clear()


@patch('app.api.v1.endpoints.audit_logs.AuditLoggingService')
def test_export_audit_logs_csv_format(mock_service_class, client, mock_compliance_user, mock_db):
    """Test exporting audit logs in CSV format"""
    # Setup mock service
    mock_service = AsyncMock()
    mock_service.export_logs.return_value = "id,timestamp,event_type,user_email\n123,2024-01-01,login,test@example.com\n"
    mock_service_class.return_value = mock_service
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_compliance_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Export as CSV
    response = client.post(
        "/api/v1/audit-logs/export",
        json={
            "format": "csv",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-31T23:59:59Z",
        }
    )
    
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
    assert ".csv" in response.headers["content-disposition"]
    
    # Clean up
    app.dependency_overrides.clear()


def test_export_audit_logs_requires_admin_or_compliance_role(client, mock_regular_user, mock_db):
    """Test that only admin and compliance_officer can export audit logs"""
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_regular_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.post(
        "/api/v1/audit-logs/export",
        json={"format": "json"}
    )
    
    assert response.status_code == 403
    assert "administrators and compliance officers" in response.json()["detail"].lower()
    
    # Clean up
    app.dependency_overrides.clear()


@patch('app.api.v1.endpoints.audit_logs.AuditLoggingService')
def test_export_audit_logs_invalid_format(mock_service_class, client, mock_admin_user, mock_db):
    """Test that invalid export format returns error"""
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.post(
        "/api/v1/audit-logs/export",
        json={"format": "xml"}  # Invalid format
    )
    
    assert response.status_code == 400
    assert "Invalid export format" in response.json()["detail"]
    
    # Clean up
    app.dependency_overrides.clear()


# ========================================
# Test Additional Endpoints
# ========================================

@patch('app.api.v1.endpoints.audit_logs.AuditEventType')
def test_get_event_types(mock_event_type, client, mock_admin_user):
    """Test getting available event types"""
    # Setup mock
    mock_event_type.AUTH_LOGIN_SUCCESS = "auth.login.success"
    mock_event_type.AUTH_LOGIN_FAILURE = "auth.login.failure"
    mock_event_type.DATA_CREATE = "data.create"
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    
    response = client.get("/api/v1/audit-logs/event-types")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Clean up
    app.dependency_overrides.clear()


@patch('app.api.v1.endpoints.audit_logs.AuditLoggingService')
def test_verify_audit_log_integrity(mock_service_class, client, mock_admin_user, mock_db):
    """Test verifying audit log integrity"""
    # Setup mock service
    mock_service = AsyncMock()
    mock_service.verify_chain_integrity.return_value = {
        "total_logs": 100,
        "verified": True,
        "integrity_status": "intact",
        "breaks": [],
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }
    mock_service_class.return_value = mock_service
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get("/api/v1/audit-logs/verify-integrity")
    
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["integrity_status"] == "intact"
    
    # Clean up
    app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
