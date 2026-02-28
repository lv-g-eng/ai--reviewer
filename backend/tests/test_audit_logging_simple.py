"""
Simple Audit Logging Tests

Basic tests to verify audit logging functionality works.
"""
import pytest
import uuid
from datetime import datetime, timezone

# Simple test to verify imports work
def test_imports():
    """Test that audit logging service can be imported"""
    from app.services.audit_logging_service import (
        AuditLoggingService,
        AuditLogEntry,
        AuditEventType,
    )
    
    assert AuditLoggingService is not None
    assert AuditLogEntry is not None
    assert AuditEventType is not None


def test_event_types():
    """Test that event type constants are defined"""
    from app.services.audit_logging_service import AuditEventType
    
    assert hasattr(AuditEventType, 'AUTH_LOGIN_SUCCESS')
    assert hasattr(AuditEventType, 'AUTH_LOGIN_FAILURE')
    assert hasattr(AuditEventType, 'AUTHZ_ACCESS_DENIED')
    assert hasattr(AuditEventType, 'DATA_CREATE')
    assert hasattr(AuditEventType, 'DATA_UPDATE')
    assert hasattr(AuditEventType, 'DATA_DELETE')
    assert hasattr(AuditEventType, 'ADMIN_USER_CREATE')


def test_audit_log_entry_model():
    """Test that AuditLogEntry model has required fields"""
    from app.services.audit_logging_service import AuditLogEntry
    
    # Verify model has required columns
    assert hasattr(AuditLogEntry, 'id')
    assert hasattr(AuditLogEntry, 'timestamp')
    assert hasattr(AuditLogEntry, 'event_type')
    assert hasattr(AuditLogEntry, 'event_category')
    assert hasattr(AuditLogEntry, 'user_id')
    assert hasattr(AuditLogEntry, 'user_email')
    assert hasattr(AuditLogEntry, 'ip_address')
    assert hasattr(AuditLogEntry, 'user_agent')
    assert hasattr(AuditLogEntry, 'action')
    assert hasattr(AuditLogEntry, 'description')
    assert hasattr(AuditLogEntry, 'success')
    assert hasattr(AuditLogEntry, 'previous_state')
    assert hasattr(AuditLogEntry, 'new_state')
    assert hasattr(AuditLogEntry, 'changes')
    assert hasattr(AuditLogEntry, 'current_hash')
    assert hasattr(AuditLogEntry, 'previous_hash')


def test_audit_service_initialization():
    """Test that audit service can be initialized"""
    from app.services.audit_logging_service import AuditLoggingService
    from unittest.mock import Mock
    
    mock_session = Mock()
    service = AuditLoggingService(mock_session)
    
    assert service is not None
    assert service.db == mock_session
    assert service.default_retention_days == 2555  # 7 years


def test_compute_changes():
    """Test the _compute_changes method"""
    from app.services.audit_logging_service import AuditLoggingService
    from unittest.mock import Mock
    
    mock_session = Mock()
    service = AuditLoggingService(mock_session)
    
    previous_state = {
        "name": "Old Name",
        "status": "active",
        "count": 10,
    }
    
    new_state = {
        "name": "New Name",
        "status": "active",
        "count": 20,
        "new_field": "value",
    }
    
    changes = service._compute_changes(previous_state, new_state)
    
    # Verify changes are computed correctly
    assert "name" in changes
    assert changes["name"]["old"] == "Old Name"
    assert changes["name"]["new"] == "New Name"
    
    assert "count" in changes
    assert changes["count"]["old"] == 10
    assert changes["count"]["new"] == 20
    
    assert "new_field" in changes
    assert changes["new_field"]["old"] is None
    assert changes["new_field"]["new"] == "value"
    
    # status didn't change, should not be in changes
    assert "status" not in changes


def test_generate_hash():
    """Test the _generate_hash method"""
    from app.services.audit_logging_service import AuditLoggingService, AuditLogEntry
    from unittest.mock import Mock
    
    mock_session = Mock()
    service = AuditLoggingService(mock_session)
    
    # Create a mock log entry
    log_entry = Mock(spec=AuditLogEntry)
    log_entry.id = uuid.uuid4()
    log_entry.previous_hash = "abc123"
    log_entry.timestamp = datetime.now(timezone.utc)
    log_entry.event_type = "test.event"
    log_entry.event_category = "test"
    log_entry.resource_type = "test_resource"
    log_entry.resource_id = "123"
    log_entry.user_id = uuid.uuid4()
    log_entry.user_email = "test@example.com"
    log_entry.action = "test_action"
    log_entry.description = "Test description"
    log_entry.success = True
    
    # Generate hash
    hash_value = service._generate_hash(log_entry)
    
    # Verify hash is SHA-256 (64 hex characters)
    assert hash_value is not None
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64
    assert all(c in '0123456789abcdef' for c in hash_value)
    
    # Verify hash is deterministic
    hash_value2 = service._generate_hash(log_entry)
    assert hash_value == hash_value2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
