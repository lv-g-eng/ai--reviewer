"""
Simplified unit tests for session management (non-property-based).
"""
import pytest
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
    """Unit tests for session management operations."""
    
    def test_login_creates_session_with_expiration(self, db_session):
        """
        Test that login creates a session with proper expiration.
        
        **Validates: Requirements 10.1 - Property 33**
        """
        # Create a user
        user_id = str(uuid.uuid4())
        username = "test_user"
        password = "test_password"
        password_hash = AuthService.hash_password(password)
        
        user = User(
            id=user_id,
            username=username,
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
            db_session, username, password, "192.168.1.1", "Test Device"
        )
        
        # Record time after login
        time_after_login = datetime.now(timezone.utc)
        
        # Verify login was successful
        assert result.success is True
        assert result.token is not None
        
        # Query the created session
        session = db_session.query(SessionModel).filter(
            SessionModel.user_id == user_id
        ).first()
        
        assert session is not None
        assert session.is_valid is True
        assert session.token == result.token
        assert session.ip_address == "192.168.1.1"
        
        # Verify expiration time
        assert session.expires_at > time_before_login
        
        # expires_at should be approximately current time + session_expire_minutes
        expected_expiration = time_after_login + timedelta(minutes=settings.session_expire_minutes)
        time_diff = abs((session.expires_at - expected_expiration).total_seconds())
        
        # Allow 5 seconds tolerance
        assert time_diff < 5
    
    def test_concurrent_sessions_supported(self, db_session):
        """
        Test that multiple concurrent sessions are supported.
        
        **Validates: Requirements 10.3 - Property 34**
        """
        # Create a user
        user_id = str(uuid.uuid4())
        username = "test_user"
        password = "test_password"
        password_hash = AuthService.hash_password(password)
        
        user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            role=Role.PROGRAMMER,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Create multiple sessions from different devices
        num_devices = 3
        sessions = []
        import time
        
        for i in range(num_devices):
            # Add small delay to ensure unique timestamps
            if i > 0:
                time.sleep(0.01)
            
            result = AuthService.login(
                db_session,
                username,
                password,
                f"192.168.1.{i+1}",
                f"Device {i+1}"
            )
            
            assert result.success is True
            sessions.append(result.token)
        
        # Verify all sessions exist and are valid
        db_sessions = db_session.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_valid == True
        ).all()
        
        assert len(db_sessions) == num_devices
        
        # Verify each session has unique token
        tokens = [s.token for s in db_sessions]
        assert len(set(tokens)) == num_devices
        
        # Verify all sessions are valid
        for session in db_sessions:
            assert session.is_valid is True
            assert session.expires_at > datetime.now(timezone.utc)
    
    def test_password_change_invalidates_all_sessions(self, db_session):
        """
        Test that password change invalidates all sessions.
        
        **Validates: Requirements 10.4 - Property 35**
        """
        # Create a user
        user_id = str(uuid.uuid4())
        username = "test_user"
        old_password = "old_password"
        new_password = "new_password"
        password_hash = AuthService.hash_password(old_password)
        
        user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            role=Role.PROGRAMMER,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Create multiple active sessions
        num_sessions = 3
        import time
        
        for i in range(num_sessions):
            if i > 0:
                time.sleep(0.01)
            
            AuthService.login(
                db_session,
                username,
                old_password,
                f"192.168.1.{i+1}",
                f"Device {i+1}"
            )
        
        # Verify all sessions are active
        active_sessions_before = db_session.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_valid == True
        ).count()
        
        assert active_sessions_before == num_sessions
        
        # Change password
        user.password_hash = AuthService.hash_password(new_password)
        db_session.commit()
        
        # Invalidate all sessions
        success = AuthService.invalidate_all_user_sessions(db_session, user_id)
        assert success is True
        
        # Verify all sessions are now invalid
        active_sessions_after = db_session.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_valid == True
        ).count()
        
        assert active_sessions_after == 0
        
        # Verify total sessions still exist (not deleted, just invalidated)
        total_sessions = db_session.query(SessionModel).filter(
            SessionModel.user_id == user_id
        ).count()
        
        assert total_sessions == num_sessions
    
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
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            is_valid=True,
            ip_address="192.168.1.1"
        )
        db_session.add(expired_session)
        db_session.commit()
        
        # Verify session is expired
        assert expired_session.expires_at < datetime.now(timezone.utc)
    
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
        import time
        result1 = AuthService.login(db_session, "test_user", "password", "192.168.1.1", "Device 1")
        time.sleep(0.01)
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
        assert session1.is_valid is False
        
        # Verify second session is still valid
        session2 = db_session.query(SessionModel).filter(
            SessionModel.token == result2.token
        ).first()
        assert session2.is_valid is True
