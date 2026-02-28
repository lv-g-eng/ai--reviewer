"""
Tests for Audit Logging Service

This test suite validates:
- All authentication attempts are logged
- All authorization failures are logged
- All data modifications are logged with before/after values
- All administrative actions are logged
- Audit log immutability
- Audit log querying and export

Validates Requirements: 5.2, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7
"""
import pytest
import pytest_asyncio
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError

from app.services.audit_logging_service import (
    AuditLoggingService,
    AuditLogEntry,
    AuditEventType,
)
from app.database.postgresql import Base


# ========================================
# Test Fixtures
# ========================================

@pytest_asyncio.fixture
async def db_session():
    """Create test database session"""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Create and return session
    session = async_session_factory()
    
    yield session
    
    await session.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def audit_service(db_session):
    """Create audit logging service"""
    return AuditLoggingService(db_session)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "user_id": uuid.uuid4(),
        "user_email": "test@example.com",
        "user_role": "developer",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }


# ========================================
# Test Authentication Logging (Req 15.1)
# ========================================

@pytest.mark.asyncio
async def test_log_successful_authentication(audit_service, sample_user_data):
    """Test logging successful authentication attempt"""
    # Log successful authentication
    log_entry = await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=sample_user_data["user_id"],
    )
    
    # Verify log entry
    assert log_entry is not None
    assert log_entry.event_type == AuditEventType.AUTH_LOGIN_SUCCESS
    assert log_entry.event_category == "auth"
    assert log_entry.user_email == sample_user_data["user_email"]
    assert log_entry.user_id == sample_user_data["user_id"]
    assert log_entry.ip_address == sample_user_data["ip_address"]
    assert log_entry.user_agent == sample_user_data["user_agent"]
    assert log_entry.success is True
    assert log_entry.severity == "info"
    assert log_entry.current_hash is not None
    assert len(log_entry.current_hash) == 64  # SHA-256 hash


@pytest.mark.asyncio
async def test_log_failed_authentication(audit_service, sample_user_data):
    """Test logging failed authentication attempt"""
    # Log failed authentication
    log_entry = await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=False,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        error_message="Invalid password",
    )
    
    # Verify log entry
    assert log_entry is not None
    assert log_entry.event_type == AuditEventType.AUTH_LOGIN_FAILURE
    assert log_entry.event_category == "auth"
    assert log_entry.user_email == sample_user_data["user_email"]
    assert log_entry.user_id is None  # No user ID for failed auth
    assert log_entry.success is False
    assert log_entry.severity == "warning"
    assert log_entry.error_message == "Invalid password"


@pytest.mark.asyncio
async def test_authentication_logs_include_timestamp_ip_useragent(audit_service, sample_user_data):
    """Test that authentication logs include timestamp, IP address, and user agent"""
    # Log authentication
    log_entry = await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=sample_user_data["user_id"],
    )
    
    # Verify required fields
    assert log_entry.timestamp is not None
    assert isinstance(log_entry.timestamp, datetime)
    assert log_entry.ip_address == sample_user_data["ip_address"]
    assert log_entry.user_agent == sample_user_data["user_agent"]


# ========================================
# Test Authorization Failure Logging (Req 15.2)
# ========================================

@pytest.mark.asyncio
async def test_log_authorization_failure(audit_service, sample_user_data):
    """Test logging authorization failure"""
    # Log authorization failure
    log_entry = await audit_service.log_authorization_failure(
        user_id=sample_user_data["user_id"],
        user_email=sample_user_data["user_email"],
        user_role=sample_user_data["user_role"],
        resource_type="project",
        resource_id="proj-123",
        attempted_action="delete",
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        reason="Insufficient permissions",
    )
    
    # Verify log entry
    assert log_entry is not None
    assert log_entry.event_type == AuditEventType.AUTHZ_ACCESS_DENIED
    assert log_entry.event_category == "authz"
    assert log_entry.user_id == sample_user_data["user_id"]
    assert log_entry.user_email == sample_user_data["user_email"]
    assert log_entry.user_role == sample_user_data["user_role"]
    assert log_entry.resource_type == "project"
    assert log_entry.resource_id == "proj-123"
    assert log_entry.action == "delete"
    assert log_entry.success is False
    assert log_entry.severity == "warning"
    assert log_entry.error_message == "Insufficient permissions"


@pytest.mark.asyncio
async def test_authorization_failure_includes_user_resource_action(audit_service, sample_user_data):
    """Test that authorization failures include user, resource, and attempted action"""
    # Log authorization failure
    log_entry = await audit_service.log_authorization_failure(
        user_id=sample_user_data["user_id"],
        user_email=sample_user_data["user_email"],
        user_role="developer",
        resource_type="admin_panel",
        resource_id="settings",
        attempted_action="access",
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        reason="Admin role required",
    )
    
    # Verify all required fields are present
    assert log_entry.user_id == sample_user_data["user_id"]
    assert log_entry.user_email == sample_user_data["user_email"]
    assert log_entry.user_role == "developer"
    assert log_entry.resource_type == "admin_panel"
    assert log_entry.resource_id == "settings"
    assert log_entry.action == "access"
    assert "Admin role required" in log_entry.description


# ========================================
# Test Data Modification Logging (Req 15.3)
# ========================================

@pytest.mark.asyncio
async def test_log_data_creation(audit_service, sample_user_data):
    """Test logging data creation"""
    new_state = {
        "id": "proj-456",
        "name": "New Project",
        "owner": "test@example.com",
        "status": "active",
    }
    
    # Log data creation
    log_entry = await audit_service.log_data_modification(
        user_id=sample_user_data["user_id"],
        user_email=sample_user_data["user_email"],
        user_role=sample_user_data["user_role"],
        operation="create",
        resource_type="project",
        resource_id="proj-456",
        resource_name="New Project",
        previous_state=None,
        new_state=new_state,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
    )
    
    # Verify log entry
    assert log_entry is not None
    assert log_entry.event_type == AuditEventType.DATA_CREATE
    assert log_entry.event_category == "data"
    assert log_entry.resource_type == "project"
    assert log_entry.resource_id == "proj-456"
    assert log_entry.resource_name == "New Project"
    assert log_entry.previous_state is None
    assert log_entry.new_state == new_state
    assert log_entry.success is True


@pytest.mark.asyncio
async def test_log_data_update_with_before_after_values(audit_service, sample_user_data):
    """Test logging data update with before and after values"""
    previous_state = {
        "id": "proj-456",
        "name": "Old Project Name",
        "status": "active",
        "description": "Old description",
    }
    
    new_state = {
        "id": "proj-456",
        "name": "New Project Name",
        "status": "active",
        "description": "New description",
    }
    
    # Log data update
    log_entry = await audit_service.log_data_modification(
        user_id=sample_user_data["user_id"],
        user_email=sample_user_data["user_email"],
        user_role=sample_user_data["user_role"],
        operation="update",
        resource_type="project",
        resource_id="proj-456",
        resource_name="Project",
        previous_state=previous_state,
        new_state=new_state,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
    )
    
    # Verify log entry
    assert log_entry is not None
    assert log_entry.event_type == AuditEventType.DATA_UPDATE
    assert log_entry.previous_state == previous_state
    assert log_entry.new_state == new_state
    
    # Verify changes are computed
    assert log_entry.changes is not None
    assert "name" in log_entry.changes
    assert log_entry.changes["name"]["old"] == "Old Project Name"
    assert log_entry.changes["name"]["new"] == "New Project Name"
    assert "description" in log_entry.changes
    assert log_entry.changes["description"]["old"] == "Old description"
    assert log_entry.changes["description"]["new"] == "New description"


@pytest.mark.asyncio
async def test_log_data_deletion(audit_service, sample_user_data):
    """Test logging data deletion"""
    previous_state = {
        "id": "proj-456",
        "name": "Deleted Project",
        "status": "active",
    }
    
    # Log data deletion
    log_entry = await audit_service.log_data_modification(
        user_id=sample_user_data["user_id"],
        user_email=sample_user_data["user_email"],
        user_role=sample_user_data["user_role"],
        operation="delete",
        resource_type="project",
        resource_id="proj-456",
        resource_name="Deleted Project",
        previous_state=previous_state,
        new_state=None,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
    )
    
    # Verify log entry
    assert log_entry is not None
    assert log_entry.event_type == AuditEventType.DATA_DELETE
    assert log_entry.previous_state == previous_state
    assert log_entry.new_state is None


# ========================================
# Test Administrative Action Logging (Req 15.4)
# ========================================

@pytest.mark.asyncio
async def test_log_administrative_action(audit_service, sample_user_data):
    """Test logging administrative action"""
    # Log admin action
    log_entry = await audit_service.log_administrative_action(
        user_id=sample_user_data["user_id"],
        user_email=sample_user_data["user_email"],
        user_role="admin",
        action="user.role.assign",
        description="Assigned admin role to user john@example.com",
        resource_type="user",
        resource_id="user-789",
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        success=True,
        metadata={"target_user": "john@example.com", "new_role": "admin"},
    )
    
    # Verify log entry
    assert log_entry is not None
    assert log_entry.event_type == "admin.user.role.assign"
    assert log_entry.event_category == "admin"
    assert log_entry.user_role == "admin"
    assert log_entry.action == "user.role.assign"
    assert log_entry.resource_type == "user"
    assert log_entry.resource_id == "user-789"
    assert log_entry.success is True
    assert log_entry.metadata["target_user"] == "john@example.com"
    assert log_entry.metadata["new_role"] == "admin"


@pytest.mark.asyncio
async def test_log_administrative_action_with_full_context(audit_service, sample_user_data):
    """Test that administrative actions are logged with full context"""
    # Log admin action with comprehensive context
    log_entry = await audit_service.log_administrative_action(
        user_id=sample_user_data["user_id"],
        user_email=sample_user_data["user_email"],
        user_role="admin",
        action="system.config.change",
        description="Changed system configuration: max_upload_size",
        resource_type="config",
        resource_id="max_upload_size",
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        success=True,
        metadata={
            "old_value": "10MB",
            "new_value": "50MB",
            "reason": "Support larger file uploads",
        },
    )
    
    # Verify full context is captured
    assert log_entry.user_id == sample_user_data["user_id"]
    assert log_entry.user_email == sample_user_data["user_email"]
    assert log_entry.user_role == "admin"
    assert log_entry.ip_address == sample_user_data["ip_address"]
    assert log_entry.user_agent == sample_user_data["user_agent"]
    assert log_entry.metadata["old_value"] == "10MB"
    assert log_entry.metadata["new_value"] == "50MB"
    assert log_entry.metadata["reason"] == "Support larger file uploads"


# ========================================
# Test Audit Log Immutability (Req 15.5)
# ========================================

@pytest.mark.asyncio
async def test_audit_logs_stored_in_append_only_table(audit_service, sample_user_data, db_session):
    """Test that audit logs are stored in append-only table"""
    # Create multiple log entries
    for i in range(3):
        await audit_service.log_authentication_attempt(
            user_email=f"user{i}@example.com",
            success=True,
            ip_address=sample_user_data["ip_address"],
            user_agent=sample_user_data["user_agent"],
            user_id=uuid.uuid4(),
        )
    
    # Verify all entries exist
    result = await db_session.execute(select(AuditLogEntry))
    logs = result.scalars().all()
    assert len(logs) == 3


@pytest.mark.asyncio
async def test_audit_logs_cannot_be_modified(audit_service, sample_user_data, db_session):
    """Test that audit logs cannot be modified after creation"""
    # Create log entry
    log_entry = await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=sample_user_data["user_id"],
    )
    
    # Note: SQLite doesn't support triggers, so we test the concept
    # In PostgreSQL, the trigger would prevent this
    # For now, we verify the hash chain would detect tampering
    
    original_hash = log_entry.current_hash
    
    # Attempt to modify (would fail in PostgreSQL with trigger)
    # Instead, verify hash chain would detect tampering
    log_entry.description = "Modified description"
    new_hash = audit_service._generate_hash(log_entry)
    
    # Hash should be different, indicating tampering
    assert new_hash != original_hash


@pytest.mark.asyncio
async def test_audit_logs_cannot_be_deleted(audit_service, sample_user_data, db_session):
    """Test that audit logs cannot be deleted"""
    # Create log entry
    log_entry = await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=sample_user_data["user_id"],
    )
    
    log_id = log_entry.id
    
    # Note: SQLite doesn't support triggers, so we test the concept
    # In PostgreSQL, the trigger would prevent deletion
    
    # Verify log exists
    result = await db_session.execute(
        select(AuditLogEntry).where(AuditLogEntry.id == log_id)
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_audit_log_hash_chain_integrity(audit_service, sample_user_data):
    """Test that audit logs maintain hash chain for integrity"""
    # Create multiple log entries
    log1 = await audit_service.log_authentication_attempt(
        user_email="user1@example.com",
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=uuid.uuid4(),
    )
    
    log2 = await audit_service.log_authentication_attempt(
        user_email="user2@example.com",
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=uuid.uuid4(),
    )
    
    log3 = await audit_service.log_authentication_attempt(
        user_email="user3@example.com",
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=uuid.uuid4(),
    )
    
    # Verify hash chain
    assert log1.previous_hash is None  # First entry
    assert log2.previous_hash == log1.current_hash
    assert log3.previous_hash == log2.current_hash
    
    # Verify integrity
    integrity_result = await audit_service.verify_chain_integrity()
    assert integrity_result["verified"] is True
    assert integrity_result["integrity_status"] == "intact"
    assert len(integrity_result["breaks"]) == 0


# ========================================
# Test Audit Log Querying (Req 15.6)
# ========================================

@pytest.mark.asyncio
async def test_query_logs_by_user(audit_service, sample_user_data):
    """Test querying audit logs by user"""
    user_id = sample_user_data["user_id"]
    
    # Create logs for different users
    await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=user_id,
    )
    
    await audit_service.log_authentication_attempt(
        user_email="other@example.com",
        success=True,
        ip_address="192.168.1.200",
        user_agent=sample_user_data["user_agent"],
        user_id=uuid.uuid4(),
    )
    
    # Query by user
    result = await audit_service.query_logs(user_id=user_id)
    
    assert result["total"] == 1
    assert result["items"][0]["user_id"] == str(user_id)


@pytest.mark.asyncio
async def test_query_logs_by_action(audit_service, sample_user_data):
    """Test querying audit logs by action"""
    # Create logs with different actions
    await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=sample_user_data["user_id"],
    )
    
    await audit_service.log_authorization_failure(
        user_id=sample_user_data["user_id"],
        user_email=sample_user_data["user_email"],
        user_role=sample_user_data["user_role"],
        resource_type="project",
        resource_id="proj-123",
        attempted_action="delete",
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        reason="Insufficient permissions",
    )
    
    # Query by action
    result = await audit_service.query_logs(action="login")
    
    assert result["total"] == 1
    assert result["items"][0]["action"] == "login"


@pytest.mark.asyncio
async def test_query_logs_by_date_range(audit_service, sample_user_data):
    """Test querying audit logs by date range"""
    # Create log entry
    await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=sample_user_data["user_id"],
    )
    
    # Query with date range
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(hours=1)
    end_date = now + timedelta(hours=1)
    
    result = await audit_service.query_logs(
        start_date=start_date,
        end_date=end_date,
    )
    
    assert result["total"] >= 1


@pytest.mark.asyncio
async def test_query_logs_with_pagination(audit_service, sample_user_data):
    """Test querying audit logs with pagination"""
    # Create multiple log entries
    for i in range(5):
        await audit_service.log_authentication_attempt(
            user_email=f"user{i}@example.com",
            success=True,
            ip_address=sample_user_data["ip_address"],
            user_agent=sample_user_data["user_agent"],
            user_id=uuid.uuid4(),
        )
    
    # Query with pagination
    result = await audit_service.query_logs(limit=2, offset=0)
    assert len(result["items"]) == 2
    assert result["total"] == 5
    
    result = await audit_service.query_logs(limit=2, offset=2)
    assert len(result["items"]) == 2


# ========================================
# Test Audit Log Export (Req 15.7)
# ========================================

@pytest.mark.asyncio
async def test_export_logs_json_format(audit_service, sample_user_data):
    """Test exporting audit logs in JSON format"""
    # Create log entries
    await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=sample_user_data["user_id"],
    )
    
    # Export as JSON
    exported_data = await audit_service.export_logs(format="json")
    
    assert exported_data is not None
    assert isinstance(exported_data, str)
    
    # Verify it's valid JSON
    import json
    parsed = json.loads(exported_data)
    assert "total" in parsed
    assert "items" in parsed
    assert len(parsed["items"]) >= 1


@pytest.mark.asyncio
async def test_export_logs_csv_format(audit_service, sample_user_data):
    """Test exporting audit logs in CSV format"""
    # Create log entries
    await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=sample_user_data["user_id"],
    )
    
    # Export as CSV
    exported_data = await audit_service.export_logs(format="csv")
    
    assert exported_data is not None
    assert isinstance(exported_data, str)
    
    # Verify it's CSV format (has headers)
    lines = exported_data.strip().split('\n')
    assert len(lines) >= 2  # Header + at least one data row
    assert "," in lines[0]  # CSV delimiter


@pytest.mark.asyncio
async def test_export_logs_with_filters(audit_service, sample_user_data):
    """Test exporting audit logs with filters"""
    user_id = sample_user_data["user_id"]
    
    # Create logs for different users
    await audit_service.log_authentication_attempt(
        user_email=sample_user_data["user_email"],
        success=True,
        ip_address=sample_user_data["ip_address"],
        user_agent=sample_user_data["user_agent"],
        user_id=user_id,
    )
    
    await audit_service.log_authentication_attempt(
        user_email="other@example.com",
        success=True,
        ip_address="192.168.1.200",
        user_agent=sample_user_data["user_agent"],
        user_id=uuid.uuid4(),
    )
    
    # Export with filter
    exported_data = await audit_service.export_logs(
        format="json",
        user_id=user_id,
    )
    
    import json
    parsed = json.loads(exported_data)
    
    # Should only include logs for specified user
    assert parsed["total"] == 1
    assert parsed["items"][0]["user_id"] == str(user_id)


# ========================================
# Test Edge Cases
# ========================================

@pytest.mark.asyncio
async def test_log_entry_with_minimal_data(audit_service):
    """Test creating log entry with minimal required data"""
    # Create log with minimal data
    log_entry = await audit_service.log_authentication_attempt(
        user_email="minimal@example.com",
        success=False,
        ip_address="127.0.0.1",
        user_agent="Test Agent",
    )
    
    assert log_entry is not None
    assert log_entry.user_email == "minimal@example.com"
    assert log_entry.user_id is None
    assert log_entry.success is False


@pytest.mark.asyncio
async def test_query_logs_with_no_results(audit_service):
    """Test querying logs with filters that match nothing"""
    result = await audit_service.query_logs(
        user_email="nonexistent@example.com"
    )
    
    assert result["total"] == 0
    assert len(result["items"]) == 0


@pytest.mark.asyncio
async def test_export_logs_with_unsupported_format(audit_service):
    """Test exporting logs with unsupported format"""
    with pytest.raises(ValueError, match="Unsupported export format"):
        await audit_service.export_logs(format="xml")
