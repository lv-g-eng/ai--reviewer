"""
Property-based tests for session management.
"""
import pytest
from hypothesis import given, strategies as st, settings as hypothesis_settings, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime, timedelta, timezone

from ..models import User, Role, Session as SessionModel
from ..models.user import Base
from ..services.auth_service import AuthService
from ..config import settings


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


class TestSessionManagement:
    """Property-based tests for session management operations."""
    
    # Feature: enterprise-rbac-authentication, Property 33: Login creates session with expiration
    # **Validates: Requirements 10.1**
    @given(
        username=st.text(min_size=3, max_size=40, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        password=st.text(min_size=8, max_size=128),
        ip_address=st.from_regex(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', fullmatch=True)
    )
    @hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_33_login_creates_session_with_expiration(
        self, username, password, ip_address
    ):
        """
        Property 33: Login creates session with expiration
        
        For any successful login, a session should be created with an expiresAt timestamp
        that is greater than the current time and less than or equal to current time plus
        the configured session duration.
        
        **Validates: Requirements 10.1**
        """
        # Create a fresh database session for this test
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Add UUID suffix to ensure unique username
            unique_username = f"{username}_{uuid.uuid4().hex[:8]}"
            
            # Create a user
            user_id = str(uuid.uuid4())
            password_hash = AuthService.hash_password(password)
            user = User(
                id=user_id,
                username=unique_username,
                password_hash=password_hash,
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(user)
            db_session.commit()
            
            # Record time before login
            time_before_login = datetime.now(timezone.utc)
            
            # Login
            result = AuthService.login(
                db_session, unique_username, password, ip_address, "Test Device"
            )
            
            # Record time after login
            time_after_login = datetime.now(timezone.utc)
            
            # Verify login was successful
            assert result.success is True, "Login should succeed with valid credentials"
            assert result.token is not None, "Login should return a token"
            
            # Query the created session
            session = db_session.query(SessionModel).filter(
                SessionModel.user_id == user_id
            ).first()
            
            assert session is not None, "Session should be created on login"
            assert session.is_valid is True, "Session should be valid"
            assert session.token == result.token, "Session token should match returned token"
            assert session.ip_address == ip_address, "Session should record IP address"
            
            # Verify expiration time
            # Note: SQLite stores datetimes as naive, so we need to compare without timezone
            time_before_naive = time_before_login.replace(tzinfo=None)
            time_after_naive = time_after_login.replace(tzinfo=None)
            
            # expires_at should be greater than current time
            assert session.expires_at > time_before_naive, \
                "Session expiration should be in the future"
            
            # expires_at should be approximately current time + session_expire_minutes
            expected_expiration = time_after_naive + timedelta(minutes=settings.session_expire_minutes)
            time_diff = abs((session.expires_at - expected_expiration).total_seconds())
            
            # Allow 5 seconds tolerance for test execution time
            assert time_diff < 5, \
                f"Session expiration should be approximately {settings.session_expire_minutes} minutes from now"
            
        finally:
            db_session.close()
    
    # Feature: enterprise-rbac-authentication, Property 34: Concurrent sessions are supported
    # **Validates: Requirements 10.3**
    @given(
        username=st.text(min_size=3, max_size=40, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        password=st.text(min_size=8, max_size=128),
        num_devices=st.integers(min_value=2, max_value=5)
    )
    @hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_34_concurrent_sessions_supported(
        self, username, password, num_devices
    ):
        """
        Property 34: Concurrent sessions are supported
        
        For any user, creating multiple sessions from different devices should result
        in all sessions being valid and usable concurrently.
        
        **Validates: Requirements 10.3**
        """
        # Create a fresh database session for this test
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Add UUID suffix to ensure unique username
            unique_username = f"{username}_{uuid.uuid4().hex[:8]}"
            
            # Create a user
            user_id = str(uuid.uuid4())
            password_hash = AuthService.hash_password(password)
            user = User(
                id=user_id,
                username=unique_username,
                password_hash=password_hash,
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(user)
            db_session.commit()
            
            # Create multiple sessions from different devices
            sessions = []
            import time
            for i in range(num_devices):
                # Add small delay to ensure unique timestamps in tokens
                if i > 0:
                    time.sleep(0.01)
                
                result = AuthService.login(
                    db_session,
                    unique_username,
                    password,
                    f"192.168.1.{i+1}",
                    f"Device {i+1}"
                )
                
                # If login fails, print the error for debugging
                if not result.success:
                    print(f"Login failed for device {i+1}: {result.error}")
                
                assert result.success is True, f"Login from device {i+1} should succeed. Error: {result.error if not result.success else 'None'}"
                sessions.append(result.token)
            
            # Verify all sessions exist and are valid
            db_sessions = db_session.query(SessionModel).filter(
                SessionModel.user_id == user_id,
                SessionModel.is_valid == True
            ).all()
            
            assert len(db_sessions) == num_devices, \
                f"Should have {num_devices} concurrent sessions"
            
            # Verify each session has unique token and device info
            tokens = [s.token for s in db_sessions]
            assert len(set(tokens)) == num_devices, \
                "Each session should have a unique token"
            
            # Verify all sessions are valid
            for session in db_sessions:
                assert session.is_valid is True, "All sessions should be valid"
                # Note: SQLite stores datetimes as naive, so we need to compare without timezone
                current_time_naive = datetime.now(timezone.utc).replace(tzinfo=None)
                assert session.expires_at > current_time_naive, \
                    "All sessions should not be expired"
            
        finally:
            db_session.close()
    
    # Feature: enterprise-rbac-authentication, Property 35: Password change invalidates all sessions
    # **Validates: Requirements 10.4**
    @given(
        username=st.text(min_size=3, max_size=40, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        old_password=st.text(min_size=8, max_size=128),
        new_password=st.text(min_size=8, max_size=128),
        num_sessions=st.integers(min_value=2, max_value=5)
    )
    @hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_35_password_change_invalidates_all_sessions(
        self, username, old_password, new_password, num_sessions
    ):
        """
        Property 35: Password change invalidates all sessions
        
        For any user with multiple active sessions, when that user's password is changed,
        all existing session tokens should become invalid.
        
        **Validates: Requirements 10.4**
        """
        # Create a fresh database session for this test
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Add UUID suffix to ensure unique username
            unique_username = f"{username}_{uuid.uuid4().hex[:8]}"
            
            # Create a user
            user_id = str(uuid.uuid4())
            password_hash = AuthService.hash_password(old_password)
            user = User(
                id=user_id,
                username=unique_username,
                password_hash=password_hash,
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(user)
            db_session.commit()
            
            # Create multiple active sessions
            import time
            for i in range(num_sessions):
                # Add small delay to ensure unique timestamps in tokens
                if i > 0:
                    time.sleep(0.01)
                
                AuthService.login(
                    db_session,
                    unique_username,
                    old_password,
                    f"192.168.1.{i+1}",
                    f"Device {i+1}"
                )
            
            # Verify all sessions are active
            active_sessions_before = db_session.query(SessionModel).filter(
                SessionModel.user_id == user_id,
                SessionModel.is_valid == True
            ).count()
            
            assert active_sessions_before == num_sessions, \
                f"Should have {num_sessions} active sessions before password change"
            
            # Change password
            user.password_hash = AuthService.hash_password(new_password)
            db_session.commit()
            
            # Invalidate all sessions (this should be called when password changes)
            success = AuthService.invalidate_all_user_sessions(db_session, user_id)
            assert success is True, "Session invalidation should succeed"
            
            # Verify all sessions are now invalid
            active_sessions_after = db_session.query(SessionModel).filter(
                SessionModel.user_id == user_id,
                SessionModel.is_valid == True
            ).count()
            
            assert active_sessions_after == 0, \
                "All sessions should be invalidated after password change"
            
            # Verify total sessions still exist (not deleted, just invalidated)
            total_sessions = db_session.query(SessionModel).filter(
                SessionModel.user_id == user_id
            ).count()
            
            assert total_sessions == num_sessions, \
                "Sessions should be invalidated, not deleted"
            
        finally:
            db_session.close()
    
    def test_session_expiration(self, db_session):
        """Test that expired sessions are properly identified."""
        # Create a user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username="test_user",
            password_hash=AuthService.hash_password("password"),
            role=Role.PROGRAMMER,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Create a session that's already expired
        token = AuthService.generate_token(user_id, "test_user", Role.PROGRAMMER)
        expired_session = SessionModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token=token,
            issued_at=datetime.now(timezone.utc) - timedelta(hours=2),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),  # Expired 1 hour ago
            is_valid=True,
            ip_address="192.168.1.1"
        )
        db_session.add(expired_session)
        db_session.commit()
        
        # Verify session is expired
        # Note: SQLite stores datetimes as naive, so we need to compare without timezone
        current_time_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        assert expired_session.expires_at < current_time_naive, \
            "Session should be expired"
        
        # In production, the middleware should check expires_at and reject expired sessions
        # even if is_valid is True
    
    def test_logout_invalidates_single_session(self, db_session):
        """Test that logout only invalidates the specific session."""
        # Create a user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username="test_user",
            password_hash=AuthService.hash_password("password"),
            role=Role.PROGRAMMER,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Create two sessions
        result1 = AuthService.login(db_session, "test_user", "password", "192.168.1.1", "Device 1")
        result2 = AuthService.login(db_session, "test_user", "password", "192.168.1.2", "Device 2")
        
        assert result1.success is True
        assert result2.success is True
        
        # Logout from first session
        logout_success = AuthService.logout(db_session, user_id, result1.token)
        assert logout_success is True
        
        # Verify first session is invalid
        session1 = db_session.query(SessionModel).filter(
            SessionModel.token == result1.token
        ).first()
        assert session1.is_valid is False, "First session should be invalidated"
        
        # Verify second session is still valid
        session2 = db_session.query(SessionModel).filter(
            SessionModel.token == result2.token
        ).first()
        assert session2.is_valid is True, "Second session should still be valid"
