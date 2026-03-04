"""
Test feature flag audit endpoint

Validates Requirement: 10.6
"""
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def admin_auth_headers(db_session: AsyncSession):
    """Get admin authentication headers"""
    from app.models import User
    from app.utils.password import hash_password
    from app.utils.jwt import create_access_token
    
    # Create admin user
    admin_user = User(
        email="admin@example.com",
        password_hash=hash_password("AdminPass123!"),
        full_name="Admin User",
        role="admin"
    )
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)
    
    # Generate token
    token = create_access_token({
        "sub": str(admin_user.id),
        "email": admin_user.email,
        "role": admin_user.role.value
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_log_feature_flag_change_success(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict
):
    """
    Test successful feature flag change logging
    
    Validates Requirement: 10.6
    """
    # Prepare test data
    change_log = {
        "flag_name": "use-production-api",
        "old_value": False,
        "new_value": True,
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "metadata": {
            "source": "admin_panel",
            "reason": "enabling production API for testing"
        }
    }
    
    # Make request
    response = await client.post(
        "/api/v1/audit-logs/feature-flags",
        json=change_log,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "log_id" in data
    assert data["message"] == "Feature flag change logged successfully"


@pytest.mark.asyncio
async def test_log_feature_flag_change_without_user_id(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict
):
    """
    Test feature flag change logging without explicit user_id
    (should use current_user from auth)
    
    Validates Requirement: 10.6
    """
    # Prepare test data without user_id
    change_log = {
        "flag_name": "architecture-graph-production",
        "old_value": True,
        "new_value": False,
    }
    
    # Make request
    response = await client.post(
        "/api/v1/audit-logs/feature-flags",
        json=change_log,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "log_id" in data


@pytest.mark.asyncio
async def test_log_feature_flag_change_with_timestamp(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict
):
    """
    Test feature flag change logging with custom timestamp
    
    Validates Requirement: 10.6
    """
    # Prepare test data with timestamp
    custom_timestamp = datetime.now(timezone.utc).isoformat()
    change_log = {
        "flag_name": "performance-dashboard-production",
        "old_value": False,
        "new_value": True,
        "timestamp": custom_timestamp,
        "metadata": {
            "deployment": "v1.2.3"
        }
    }
    
    # Make request
    response = await client.post(
        "/api/v1/audit-logs/feature-flags",
        json=change_log,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_log_feature_flag_change_missing_required_fields(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict
):
    """
    Test feature flag change logging with missing required fields
    
    Should return 422 validation error
    """
    # Prepare incomplete test data (missing new_value)
    change_log = {
        "flag_name": "test-flag",
        "old_value": False,
        # missing new_value
    }
    
    # Make request
    response = await client.post(
        "/api/v1/audit-logs/feature-flags",
        json=change_log,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_log_feature_flag_change_unauthorized(
    client: AsyncClient,
    db_session: AsyncSession
):
    """
    Test feature flag change logging without authentication
    
    Should return 401 unauthorized
    """
    # Prepare test data
    change_log = {
        "flag_name": "test-flag",
        "old_value": False,
        "new_value": True,
    }
    
    # Make request without auth headers
    response = await client.post(
        "/api/v1/audit-logs/feature-flags",
        json=change_log
    )
    
    # Verify response
    assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
async def test_query_feature_flag_audit_logs(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    admin_auth_headers: dict
):
    """
    Test querying feature flag audit logs
    
    Validates Requirement: 10.6
    """
    # First, log a feature flag change
    change_log = {
        "flag_name": "test-query-flag",
        "old_value": False,
        "new_value": True,
    }
    
    await client.post(
        "/api/v1/audit-logs/feature-flags",
        json=change_log,
        headers=auth_headers
    )
    
    # Query audit logs for feature flags
    response = await client.get(
        "/api/v1/audit-logs/",
        params={
            "resource_type": "feature_flag",
            "action": "update_feature_flag"
        },
        headers=admin_auth_headers
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] > 0
    
    # Verify the logged entry exists
    feature_flag_logs = [
        item for item in data["items"]
        if item["resource_type"] == "feature_flag"
        and item["action"] == "update_feature_flag"
    ]
    assert len(feature_flag_logs) > 0
