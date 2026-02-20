"""
Property-based and unit tests for the Audit Service.
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from ..services.audit_service import AuditService, AuditFilter
from ..models import AuditLog, User, Role
from ..models.user import Base


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


class TestAuditLogging:
    """Property-based tests for audit logging."""
    
    # Feature: enterprise-rbac-authentication, Property 24: Audit logs contain required fields
    # **Validates: Requirements 7.1**
    @given(
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        action=st.sampled_from(['LOGIN', 'LOGOUT', 'CREATE_USER', 'DELETE_USER', 'UPDATE_ROLE', 'CREATE_PROJECT', 'DELETE_PROJECT']),
        ip_address=st.from_regex(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', fullmatch=True),
        success=st.booleans(),
        resource_type=st.one_of(st.none(), st.sampled_from(['user', 'project', 'config'])),
        resource_id=st.one_of(st.none(), st.uuids().map(lambda x: x.hex)),
        user_agent=st.one_of(st.none(), st.text(min_size=10, max_size=100))
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_24_audit_logs_contain_required_fields(
        self, db_session, user_id, username, action, ip_address, success, 
        resource_type, resource_id, user_agent
    ):
        """
        Property 24: Audit logs contain required fields
        
        For any sensitive operation performed in the system, the audit log entry
        should contain all required fields: timestamp, user_id, username, action,
        ip_address, user_agent, success status, and optional resource information.
        
        **Validates: Requirements 7.1**
        """
        # Log the action
        log_entry = AuditService.log_action(
            db=db_session,
            user_id=user_id.hex,
            username=username,
            action=action,
            ip_address=ip_address,
            success=success,
            resource_type=resource_type,
            resource_id=resource_id,
            user_agent=user_agent
        )
        
        # Verify all required fields are present
        assert log_entry.id is not None, "Log entry should have an ID"
        assert log_entry.timestamp is not None, "Log entry should have a timestamp"
        assert log_entry.user_id == user_id.hex, "Log entry should have correct user_id"
        assert log_entry.username == username, "Log entry should have correct username"
        assert log_entry.action == action, "Log entry should have correct action"
        assert log_entry.ip_address == ip_address, "Log entry should have correct IP address"
        assert log_entry.success == success, "Log entry should have correct success status"
        
        # Verify optional fields
        if resource_type:
            assert log_entry.resource_type == resource_type
        if resource_id:
            assert log_entry.resource_id == resource_id
        if user_agent:
            assert log_entry.user_agent == user_agent
        
        # Verify timestamp is recent (within last minute)
        now = datetime.now(timezone.utc)
        # Ensure both timestamps are timezone-aware for comparison
        log_timestamp = log_entry.timestamp
        if log_timestamp.tzinfo is None:
            log_timestamp = log_timestamp.replace(tzinfo=timezone.utc)
        time_diff = (now - log_timestamp).total_seconds()
        assert time_diff < 60, "Log entry timestamp should be recent"
    
    # Feature: enterprise-rbac-authentication, Property 25: Audit logs persist immediately
    # **Validates: Requirements 7.3**
    @given(
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        action=st.text(min_size=3, max_size=50),
        ip_address=st.from_regex(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', fullmatch=True)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_25_audit_logs_persist_immediately(
        self, user_id, username, action, ip_address
    ):
        """
        Property 25: Audit logs persist immediately
        
        For any audit log entry created, the entry should be immediately persisted
        to the database and be queryable without requiring additional commits.
        
        **Validates: Requirements 7.3**
        """
        # Create a new database session for this test
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Log the action
            log_entry = AuditService.log_action(
                db=db_session,
                user_id=user_id.hex,
                username=username,
                action=action,
                ip_address=ip_address,
                success=True
            )
            
            # Immediately query for the log entry (without additional commit)
            queried_log = db_session.query(AuditLog).filter(
                AuditLog.id == log_entry.id
            ).first()
            
            # Verify the log entry was persisted
            assert queried_log is not None, "Log entry should be immediately queryable"
            assert queried_log.id == log_entry.id
            assert queried_log.user_id == user_id.hex
            assert queried_log.action == action
        finally:
            db_session.close()
    
    # Feature: enterprise-rbac-authentication, Property 26: Users cannot modify audit logs
    # **Validates: Requirements 7.4**
    @given(
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        action=st.text(min_size=3, max_size=50),
        ip_address=st.from_regex(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', fullmatch=True)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_26_users_cannot_modify_audit_logs(
        self, user_id, username, action, ip_address
    ):
        """
        Property 26: Users cannot modify audit logs
        
        The audit service should not provide any methods to modify or delete
        audit log entries. Once created, audit logs should be immutable.
        
        **Validates: Requirements 7.4**
        """
        # Verify AuditService does not have update or delete methods
        assert not hasattr(AuditService, 'update_log'), \
            "AuditService should not have update_log method"
        assert not hasattr(AuditService, 'delete_log'), \
            "AuditService should not have delete_log method"
        assert not hasattr(AuditService, 'modify_log'), \
            "AuditService should not have modify_log method"
        
        # Create a test database session
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Create a log entry
            log_entry = AuditService.log_action(
                db=db_session,
                user_id=user_id.hex,
                username=username,
                action=action,
                ip_address=ip_address,
                success=True
            )
            
            original_timestamp = log_entry.timestamp
            original_action = log_entry.action
            
            # Verify the log entry exists
            queried_log = db_session.query(AuditLog).filter(
                AuditLog.id == log_entry.id
            ).first()
            
            assert queried_log is not None
            assert queried_log.timestamp == original_timestamp
            assert queried_log.action == original_action
            
            # Note: In a real system, database constraints would prevent
            # modification. Here we verify the service doesn't provide methods.
        finally:
            db_session.close()


class TestAuditLogQueries:
    """Tests for audit log query functionality."""
    
    # Feature: enterprise-rbac-authentication, Property 27: Audit log queries filter correctly
    # **Validates: Requirements 7.5**
    @given(
        num_logs=st.integers(min_value=5, max_value=20),
        target_user_id=st.uuids(),
        target_action=st.sampled_from(['LOGIN', 'LOGOUT', 'CREATE_USER'])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_27_audit_log_queries_filter_correctly(
        self, num_logs, target_user_id, target_action
    ):
        """
        Property 27: Audit log queries filter correctly
        
        For any query with filters (user_id, action, date range), the returned
        audit logs should match all specified filter criteria.
        
        **Validates: Requirements 7.5**
        """
        # Create a test database session
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Create multiple log entries with different attributes
            target_logs = []
            other_logs = []
            
            for i in range(num_logs):
                if i % 3 == 0:
                    # Create logs matching our target criteria
                    log = AuditService.log_action(
                        db=db_session,
                        user_id=target_user_id.hex,
                        username=f"user_{i}",
                        action=target_action,
                        ip_address=f"192.168.1.{i}",
                        success=True
                    )
                    target_logs.append(log)
                else:
                    # Create logs with different criteria
                    log = AuditService.log_action(
                        db=db_session,
                        user_id=str(uuid.uuid4()),
                        username=f"other_user_{i}",
                        action='OTHER_ACTION',
                        ip_address=f"10.0.0.{i}",
                        success=True
                    )
                    other_logs.append(log)
            
            # Query with user_id filter
            filter_user = AuditFilter(user_id=target_user_id.hex)
            results_user = AuditService.query_logs(db_session, filter_user)
            
            # Verify all results match the user_id filter
            assert len(results_user) == len(target_logs), \
                f"Should return {len(target_logs)} logs for target user"
            for log in results_user:
                assert log.user_id == target_user_id.hex, \
                    "All returned logs should match user_id filter"
            
            # Query with action filter
            filter_action = AuditFilter(action=target_action)
            results_action = AuditService.query_logs(db_session, filter_action)
            
            # Verify all results match the action filter
            assert len(results_action) == len(target_logs), \
                f"Should return {len(target_logs)} logs for target action"
            for log in results_action:
                assert log.action == target_action, \
                    "All returned logs should match action filter"
            
            # Query with combined filters
            filter_combined = AuditFilter(
                user_id=target_user_id.hex,
                action=target_action
            )
            results_combined = AuditService.query_logs(db_session, filter_combined)
            
            # Verify all results match both filters
            assert len(results_combined) == len(target_logs), \
                f"Should return {len(target_logs)} logs matching both filters"
            for log in results_combined:
                assert log.user_id == target_user_id.hex
                assert log.action == target_action
        finally:
            db_session.close()
    
    def test_get_user_logs(self, db_session):
        """Test getting logs for a specific user."""
        user_id = str(uuid.uuid4())
        
        # Create multiple logs for the user
        for i in range(5):
            AuditService.log_action(
                db=db_session,
                user_id=user_id,
                username="test_user",
                action=f"ACTION_{i}",
                ip_address="192.168.1.1",
                success=True
            )
        
        # Create logs for other users
        for i in range(3):
            AuditService.log_action(
                db=db_session,
                user_id=str(uuid.uuid4()),
                username=f"other_user_{i}",
                action="OTHER_ACTION",
                ip_address="10.0.0.1",
                success=True
            )
        
        # Get logs for the target user
        user_logs = AuditService.get_user_logs(db_session, user_id)
        
        # Verify only the target user's logs are returned
        assert len(user_logs) == 5
        for log in user_logs:
            assert log.user_id == user_id
    
    def test_query_logs_with_date_range(self, db_session):
        """Test querying logs with date range filters."""
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Create a log entry
        log = AuditService.log_action(
            db=db_session,
            user_id=user_id,
            username="test_user",
            action="TEST_ACTION",
            ip_address="192.168.1.1",
            success=True
        )
        
        # Query with date range that includes the log
        filter_include = AuditFilter(
            start_date=now - timedelta(minutes=5),
            end_date=now + timedelta(minutes=5)
        )
        results_include = AuditService.query_logs(db_session, filter_include)
        assert len(results_include) >= 1
        assert any(r.id == log.id for r in results_include)
        
        # Query with date range that excludes the log
        filter_exclude = AuditFilter(
            start_date=now + timedelta(hours=1),
            end_date=now + timedelta(hours=2)
        )
        results_exclude = AuditService.query_logs(db_session, filter_exclude)
        assert not any(r.id == log.id for r in results_exclude)
    
    def test_query_logs_pagination(self, db_session):
        """Test pagination in audit log queries."""
        user_id = str(uuid.uuid4())
        
        # Create 15 log entries
        for i in range(15):
            AuditService.log_action(
                db=db_session,
                user_id=user_id,
                username="test_user",
                action=f"ACTION_{i}",
                ip_address="192.168.1.1",
                success=True
            )
        
        # Query first page (limit 10)
        filter_page1 = AuditFilter(user_id=user_id, limit=10, offset=0)
        results_page1 = AuditService.query_logs(db_session, filter_page1)
        assert len(results_page1) == 10
        
        # Query second page (limit 10, offset 10)
        filter_page2 = AuditFilter(user_id=user_id, limit=10, offset=10)
        results_page2 = AuditService.query_logs(db_session, filter_page2)
        assert len(results_page2) == 5
        
        # Verify no overlap between pages
        page1_ids = {log.id for log in results_page1}
        page2_ids = {log.id for log in results_page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
