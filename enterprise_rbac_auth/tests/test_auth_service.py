"""
Property-based and unit tests for the Authentication Service.
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
import jwt
import time

from ..services.auth_service import AuthService, TokenPayload
from ..models import Role, User, Session as SessionModel
from ..config import settings as app_settings


class TestPasswordHashing:
    """Tests for password hashing and verification."""
    
    @given(password=st.text(min_size=1, max_size=128))
    @settings(deadline=None, max_examples=100)
    def test_property_5_passwords_never_stored_plaintext(self, password: str):
        """
        Property 5: Passwords are never stored in plaintext
        
        For any password provided during user creation or password change,
        the stored value in the database should not equal the plaintext password
        and should be a valid hash from the configured hashing algorithm.
        
        **Validates: Requirements 1.5**
        """
        # Hash the password
        password_hash = AuthService.hash_password(password)
        
        # The hash should never equal the plaintext password
        assert password_hash != password, "Password hash should not equal plaintext password"
        
        # The hash should be a valid bcrypt hash (starts with $2b$ and has proper length)
        assert password_hash.startswith('$2b$'), "Hash should be a valid bcrypt hash"
        assert len(password_hash) == 60, "Bcrypt hash should be 60 characters long"
        
        # The hash should be verifiable with the original password
        assert AuthService.verify_password(password, password_hash), \
            "Hash should be verifiable with original password"
    
    def test_password_hashing_consistency(self):
        """Test that the same password produces different hashes (due to salt)."""
        password = "test_password_123"
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        
        # Different hashes due to different salts
        assert hash1 != hash2
        
        # Both should verify correctly
        assert AuthService.verify_password(password, hash1)
        assert AuthService.verify_password(password, hash2)
    
    def test_password_verification_rejects_wrong_password(self):
        """Test that wrong passwords are rejected."""
        password = "correct_password"
        wrong_password = "wrong_password"
        password_hash = AuthService.hash_password(password)
        
        assert not AuthService.verify_password(wrong_password, password_hash)
    
    def test_password_verification_handles_invalid_hash(self):
        """Test that invalid hashes are handled gracefully."""
        password = "test_password"
        invalid_hash = "not_a_valid_hash"
        
        assert not AuthService.verify_password(password, invalid_hash)


class TestTokenOperations:
    """Tests for JWT token generation and validation."""
    
    def test_basic_token_generation(self):
        """Basic test to ensure token generation and validation works."""
        user_id = "test-user-123"
        username = "testuser"
        role = Role.ADMIN
        
        # Generate token
        token = AuthService.generate_token(user_id, username, role)
        print(f"\nGenerated token: {token[:100]}...")
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Try to decode manually first
        import jwt as pyjwt
        try:
            decoded = pyjwt.decode(token, app_settings.jwt_secret_key, algorithms=[app_settings.jwt_algorithm])
            print(f"Manual decode successful: {decoded}")
        except Exception as e:
            print(f"Manual decode failed: {e}")
            raise
        
        # Validate token
        payload = AuthService.validate_token(token)
        print(f"Payload from validate_token: {payload}")
        assert payload is not None, "Token should be valid"
        assert payload.user_id == user_id
        assert payload.username == username
        assert payload.role == role.value
    
    @given(
        user_id=st.uuids().map(str),
        username=st.text(min_size=3, max_size=50),
        role=st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR])
    )
    @settings(deadline=None, max_examples=100)
    def test_property_1_valid_credentials_generate_valid_tokens(
        self, user_id: str, username: str, role: Role
    ):
        """
        Property 1: Valid credentials generate valid JWT tokens
        
        For any valid user credentials (username and password), when the user logs in,
        the returned JWT token should contain the correct userId and role,
        and should be verifiable by the token validation function.
        
        **Validates: Requirements 1.1**
        """
        from datetime import timezone
        # Generate token
        token = AuthService.generate_token(user_id, username, role)
        
        # Token should be a non-empty string
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 0, "Token should not be empty"
        
        # Validate token
        payload = AuthService.validate_token(token)
        
        # Payload should not be None
        assert payload is not None, "Token should be valid"
        
        # Payload should contain correct user information
        assert payload.user_id == user_id, "Token should contain correct user_id"
        assert payload.username == username, "Token should contain correct username"
        assert payload.role == role.value, "Token should contain correct role"
        
        # Token should have valid timestamps
        now = int(datetime.now(timezone.utc).timestamp())
        assert payload.iat <= now + 1, "Token issued_at should be in the past or present (with 1s tolerance)"
        assert payload.exp > now, "Token expiration should be in the future"
    
    def test_property_4_expired_tokens_require_reauthentication(self):
        """
        Property 4: Expired tokens require re-authentication
        
        For any JWT token with an expiration time in the past,
        any request using that token should be rejected with a 401 Unauthorized response.
        
        **Validates: Requirements 1.4, 10.2**
        """
        from datetime import timezone
        # Create a token that's already expired
        user_id = "test-user-123"
        username = "testuser"
        role = Role.PROGRAMMER
        
        # Manually create an expired token
        now = datetime.now(timezone.utc)
        iat = int((now - timedelta(hours=2)).timestamp())
        exp = int((now - timedelta(hours=1)).timestamp())  # Expired 1 hour ago
        
        payload = TokenPayload(
            user_id=user_id,
            username=username,
            role=role.value,
            iat=iat,
            exp=exp
        )
        
        expired_token = jwt.encode(
            payload.to_dict(),
            app_settings.jwt_secret_key,
            algorithm=app_settings.jwt_algorithm
        )
        
        # Validate the expired token
        result = AuthService.validate_token(expired_token)
        
        # Should return None for expired token
        assert result is None, "Expired token should be rejected"
    
    def test_property_36_active_usage_refreshes_tokens(self):
        """
        Property 36: Active usage refreshes tokens
        
        For any user with an active session, making requests within the refresh window
        before token expiration should result in a new token with an extended expiration time.
        
        **Validates: Requirements 10.5**
        """
        from datetime import timezone
        # Create a token that's close to expiration (within refresh window)
        user_id = "test-user-456"
        username = "activeuser"
        role = Role.ADMIN
        
        # Create a token that expires in 5 minutes (within 10-minute refresh window)
        now = datetime.now(timezone.utc)
        iat = int((now - timedelta(minutes=55)).timestamp())
        exp = int((now + timedelta(minutes=5)).timestamp())
        
        payload = TokenPayload(
            user_id=user_id,
            username=username,
            role=role.value,
            iat=iat,
            exp=exp
        )
        
        old_token = jwt.encode(
            payload.to_dict(),
            app_settings.jwt_secret_key,
            algorithm=app_settings.jwt_algorithm
        )
        
        # Refresh the token
        new_token = AuthService.refresh_token(old_token)
        
        # Should return a new token
        assert new_token is not None, "Token should be refreshed within refresh window"
        assert new_token != old_token, "New token should be different from old token"
        
        # Validate new token
        new_payload = AuthService.validate_token(new_token)
        assert new_payload is not None, "New token should be valid"
        assert new_payload.user_id == user_id, "New token should have same user_id"
        assert new_payload.username == username, "New token should have same username"
        assert new_payload.role == role.value, "New token should have same role"
        assert new_payload.exp > exp, "New token should have later expiration"
    
    def test_token_refresh_outside_window(self):
        """Test that tokens outside refresh window are not refreshed."""
        # Create a token with plenty of time left (not in refresh window)
        user_id = "test-user-789"
        username = "freshuser"
        role = Role.VISITOR
        
        token = AuthService.generate_token(user_id, username, role)
        
        # Try to refresh (should return None since not in refresh window)
        refreshed = AuthService.refresh_token(token)
        
        # Should not refresh token that's not close to expiration
        assert refreshed is None, "Token should not be refreshed outside refresh window"
    
    def test_invalid_token_validation(self):
        """Test that invalid tokens are rejected."""
        invalid_tokens = [
            "not.a.token",
            "invalid_token_format",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        for token in invalid_tokens:
            result = AuthService.validate_token(token)
            assert result is None, f"Invalid token '{token}' should be rejected"
    
    def test_tampered_token_validation(self):
        """Test that tampered tokens are rejected."""
        # Generate a valid token
        token = AuthService.generate_token("user123", "testuser", Role.PROGRAMMER)
        
        # Tamper with the token by changing a character
        tampered_token = token[:-5] + "XXXXX"
        
        # Should be rejected
        result = AuthService.validate_token(tampered_token)
        assert result is None, "Tampered token should be rejected"



class TestAuthentication:
    """Tests for login and logout functionality."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        from ..database import engine, SessionLocal
        from ..models import Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Create session
        db = SessionLocal()
        yield db
        
        # Cleanup
        db.close()
        Base.metadata.drop_all(bind=engine)
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create a test user."""
        import uuid
        from datetime import timezone
        
        user = User(
            id=str(uuid.uuid4()),
            username="testuser",
            password_hash=AuthService.hash_password("correct_password"),
            role=Role.PROGRAMMER,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    def test_property_2_invalid_credentials_rejected(self, db_session, test_user):
        """
        Property 2: Invalid credentials are rejected
        
        For any invalid credentials (non-existent username, incorrect password,
        or malformed input), the login attempt should be rejected and return
        an error message without revealing which part was incorrect.
        
        **Validates: Requirements 1.2, 6.2**
        """
        # Test with wrong password
        result = AuthService.login(db_session, "testuser", "wrong_password")
        assert not result.success, "Login with wrong password should fail"
        assert result.error == "Invalid username or password", "Should return generic error"
        assert result.token is None, "Should not return token"
        
        # Test with non-existent username
        result = AuthService.login(db_session, "nonexistent", "any_password")
        assert not result.success, "Login with non-existent user should fail"
        assert result.error == "Invalid username or password", "Should return generic error"
        assert result.token is None, "Should not return token"
        
        # Test with empty username
        result = AuthService.login(db_session, "", "password")
        assert not result.success, "Login with empty username should fail"
        assert result.error == "Invalid username or password", "Should return generic error"
        
        # Test with empty password
        result = AuthService.login(db_session, "testuser", "")
        assert not result.success, "Login with empty password should fail"
        assert result.error == "Invalid username or password", "Should return generic error"
    
    def test_property_3_logout_invalidates_sessions(self, db_session, test_user):
        """
        Property 3: Logout invalidates sessions
        
        For any active user session, when the user logs out, the session should
        be marked as invalid and subsequent requests using that token should be rejected.
        
        **Validates: Requirements 1.3**
        """
        # Login to create a session
        result = AuthService.login(db_session, "testuser", "correct_password")
        assert result.success, "Login should succeed"
        assert result.token is not None, "Should return token"
        
        token = result.token
        user_id = test_user.id
        
        # Verify session exists and is valid
        session = db_session.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.token == token
        ).first()
        assert session is not None, "Session should exist"
        assert session.is_valid, "Session should be valid"
        
        # Logout
        logout_success = AuthService.logout(db_session, user_id, token)
        assert logout_success, "Logout should succeed"
        
        # Verify session is now invalid
        db_session.refresh(session)
        assert not session.is_valid, "Session should be invalidated after logout"
        
        # Try to logout again with same token (should fail)
        logout_again = AuthService.logout(db_session, user_id, token)
        assert not logout_again, "Second logout with same token should fail"
    
    def test_successful_login(self, db_session, test_user):
        """Test successful login flow."""
        result = AuthService.login(db_session, "testuser", "correct_password")
        
        assert result.success, "Login should succeed"
        assert result.token is not None, "Should return token"
        assert result.user is not None, "Should return user info"
        assert result.user["username"] == "testuser", "Should return correct username"
        assert result.user["role"] == Role.PROGRAMMER.value, "Should return correct role"
        assert result.error is None, "Should not have error"
        
        # Verify token is valid
        payload = AuthService.validate_token(result.token)
        assert payload is not None, "Token should be valid"
        assert payload.user_id == test_user.id, "Token should contain correct user_id"
    
    def test_inactive_user_login(self, db_session, test_user):
        """Test that inactive users cannot login."""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()
        
        result = AuthService.login(db_session, "testuser", "correct_password")
        assert not result.success, "Login should fail for inactive user"
        assert result.error == "Account is disabled", "Should return disabled account error"
    
    def test_login_updates_last_login(self, db_session, test_user):
        """Test that login updates the last_login timestamp."""
        from datetime import timezone
        
        # Initial last_login should be None
        assert test_user.last_login is None, "Initial last_login should be None"
        
        # Login
        result = AuthService.login(db_session, "testuser", "correct_password")
        assert result.success, "Login should succeed"
        
        # Refresh user and check last_login
        db_session.refresh(test_user)
        assert test_user.last_login is not None, "last_login should be set"
        
        # Verify it's recent (within last minute)
        # Handle both timezone-aware and naive datetimes
        now = datetime.now(timezone.utc)
        last_login = test_user.last_login
        if last_login.tzinfo is None:
            # Convert naive datetime to UTC
            last_login = last_login.replace(tzinfo=timezone.utc)
        
        time_diff = (now - last_login).total_seconds()
        assert time_diff < 60, "last_login should be recent"
