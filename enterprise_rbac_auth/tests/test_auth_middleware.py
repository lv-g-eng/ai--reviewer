"""
Property-based tests for authorization middleware.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, MagicMock
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..middleware.auth_middleware import AuthMiddleware
from ..services.auth_service import AuthService
from ..models import Role, Permission, User
from ..models.user import Base
from ..config import settings as app_settings


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


# Test data generators
@st.composite
def valid_token_strategy(draw):
    """Generate valid JWT tokens."""
    user_id = draw(st.uuids()).hex
    username = draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    role = draw(st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]))
    
    # Generate token
    token = AuthService.generate_token(user_id, username, role)
    return token, user_id, username, role


@st.composite
def invalid_token_strategy(draw):
    """Generate invalid JWT tokens."""
    choice = draw(st.integers(min_value=0, max_value=3))
    
    if choice == 0:
        # Expired token
        user_id = draw(st.uuids()).hex
        username = draw(st.text(min_size=3, max_size=20))
        role = draw(st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]))
        
        now = datetime.now(timezone.utc)
        iat = int((now - timedelta(hours=2)).timestamp())
        exp = int((now - timedelta(hours=1)).timestamp())
        
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role.value,
            "iat": iat,
            "exp": exp
        }
        
        token = jwt.encode(payload, app_settings.jwt_secret_key, algorithm=app_settings.jwt_algorithm)
        return token
    
    elif choice == 1:
        # Malformed token (invalid signature)
        user_id = draw(st.uuids()).hex
        username = draw(st.text(min_size=3, max_size=20))
        role = draw(st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]))
        
        now = datetime.now(timezone.utc)
        iat = int(now.timestamp())
        exp = int((now + timedelta(hours=1)).timestamp())
        
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role.value,
            "iat": iat,
            "exp": exp
        }
        
        # Use wrong secret key
        token = jwt.encode(payload, "wrong-secret-key", algorithm=app_settings.jwt_algorithm)
        return token
    
    elif choice == 2:
        # Random string (not a JWT)
        return draw(st.text(min_size=10, max_size=100))
    
    else:
        # Empty token
        return ""


class TestAuthMiddleware:
    """Property-based tests for authentication middleware."""
    
    # Feature: enterprise-rbac-authentication, Property 15: Invalid tokens return 401
    # **Validates: Requirements 3.5**
    @given(invalid_token_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_15_invalid_tokens_return_401(self, invalid_token):
        """
        Property 15: Invalid tokens return 401
        
        For any request with an invalid, expired, or missing JWT token,
        the authorization middleware should return a 401 Unauthorized response.
        """
        # Create mock request and credentials
        request = Mock(spec=Request)
        request.state = Mock()
        
        if invalid_token:
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=invalid_token)
        else:
            credentials = None
        
        # Test that invalid token raises 401
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(AuthMiddleware.authenticate_token(request, credentials))
        
        assert exc_info.value.status_code == 401
        assert "WWW-Authenticate" in exc_info.value.headers
    
    # Feature: enterprise-rbac-authentication, Property 12: Middleware validates JWT tokens
    # **Validates: Requirements 3.2**
    @given(valid_token_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_12_middleware_validates_jwt_tokens(self, token_data):
        """
        Property 12: Middleware validates JWT tokens
        
        For any request to a protected endpoint, the authorization middleware
        should extract and validate the JWT token before allowing the request to proceed.
        """
        token, user_id, username, role = token_data
        
        # Create mock request and credentials
        request = Mock(spec=Request)
        request.state = Mock()
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Test that valid token is accepted
        import asyncio
        payload = asyncio.run(AuthMiddleware.authenticate_token(request, credentials))
        
        # Verify payload contains correct information
        assert payload is not None
        assert payload.user_id == user_id
        assert payload.username == username
        assert payload.role == role.value
        
        # Verify user info is stored in request state
        assert hasattr(request.state, 'user')
        assert request.state.user == payload


class TestRoleAuthorization:
    """Property-based tests for role-based authorization."""
    
    # Feature: enterprise-rbac-authentication, Property 13: Matching roles grant access
    # **Validates: Requirements 3.3**
    @given(
        role=st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]),
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=100, deadline=None)
    def test_property_13_matching_roles_grant_access(self, role, user_id, username):
        """
        Property 13: Matching roles grant access
        
        For any user whose role matches the required role for an endpoint,
        the authorization middleware should allow the request to proceed to the handler.
        """
        # Generate token with specific role
        token = AuthService.generate_token(user_id.hex, username, role)
        
        # Create mock request and credentials
        request = Mock(spec=Request)
        request.state = Mock()
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Create role checker for the same role
        role_checker = AuthMiddleware.check_role(role)
        
        # Test that matching role is accepted
        import asyncio
        payload = asyncio.run(role_checker(request, credentials))
        
        # Verify payload is returned (no exception raised)
        assert payload is not None
        assert payload.role == role.value
    
    # Feature: enterprise-rbac-authentication, Property 14: Non-matching roles return 403
    # **Validates: Requirements 3.4**
    @given(
        user_role=st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]),
        required_role=st.sampled_from([Role.ADMIN, Role.PROGRAMMER, Role.VISITOR]),
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=100, deadline=None)
    def test_property_14_non_matching_roles_return_403(self, user_role, required_role, user_id, username):
        """
        Property 14: Non-matching roles return 403
        
        For any user whose role does not match the required role for an endpoint,
        the authorization middleware should return a 403 Forbidden response.
        """
        # Skip if roles match (that's tested in property 13)
        assume(user_role != required_role)
        
        # Generate token with user's role
        token = AuthService.generate_token(user_id.hex, username, user_role)
        
        # Create mock request and credentials
        request = Mock(spec=Request)
        request.state = Mock()
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Create role checker for different role
        role_checker = AuthMiddleware.check_role(required_role)
        
        # Test that non-matching role raises 403
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(role_checker(request, credentials))
        
        assert exc_info.value.status_code == 403
        assert required_role.value in exc_info.value.detail



class TestPermissionAuthorization:
    """Property-based tests for permission-based authorization."""
    
    # Feature: enterprise-rbac-authentication, Property 7: Admin users have all permissions
    # **Validates: Requirements 2.2**
    @given(
        permission=st.sampled_from(list(Permission)),
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=100, deadline=None)
    def test_property_7_admin_users_have_all_permissions(self, permission, user_id, username):
        """
        Property 7: Admin users have all permissions
        
        For any user with the Admin role and any permission check,
        the permission check should return true.
        """
        from unittest.mock import patch
        
        # Create test database session
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Generate token with ADMIN role
            token = AuthService.generate_token(user_id.hex, username, Role.ADMIN)
            
            # Create admin user in test database
            admin_user = User(
                id=user_id.hex,
                username=username,
                password_hash=AuthService.hash_password("test_password"),
                role=Role.ADMIN,
                is_active=True
            )
            db_session.add(admin_user)
            db_session.commit()
            
            # Create mock request and credentials
            request = Mock(spec=Request)
            request.state = Mock()
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            
            # Create permission checker
            permission_checker = AuthMiddleware.check_permission(permission)
            
            # Mock get_db to return our test session
            with patch('enterprise_rbac_auth.middleware.auth_middleware.get_db') as mock_get_db:
                mock_get_db.return_value = iter([db_session])
                
                # Test that admin has all permissions
                import asyncio
                payload = asyncio.run(permission_checker(request, credentials))
                
                # Verify payload is returned (no exception raised)
                assert payload is not None
                assert payload.role == Role.ADMIN.value
        finally:
            db_session.close()
    
    # Feature: enterprise-rbac-authentication, Property 10: Visitors cannot modify resources
    # **Validates: Requirements 2.5**
    @given(
        permission=st.sampled_from([
            Permission.CREATE_USER, Permission.DELETE_USER, Permission.UPDATE_USER,
            Permission.CREATE_PROJECT, Permission.DELETE_PROJECT, Permission.UPDATE_PROJECT,
            Permission.MODIFY_CONFIG
        ]),
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=100, deadline=None)
    def test_property_10_visitors_cannot_modify_resources(self, permission, user_id, username):
        """
        Property 10: Visitors cannot modify resources
        
        For any user with the Visitor role and any modification operation
        (create, update, delete), the operation should be denied with a 403 Forbidden response.
        """
        from unittest.mock import patch
        
        # Create test database session
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Generate token with VISITOR role
            token = AuthService.generate_token(user_id.hex, username, Role.VISITOR)
            
            # Create visitor user in test database
            visitor_user = User(
                id=user_id.hex,
                username=username,
                password_hash=AuthService.hash_password("test_password"),
                role=Role.VISITOR,
                is_active=True
            )
            db_session.add(visitor_user)
            db_session.commit()
            
            # Create mock request and credentials
            request = Mock(spec=Request)
            request.state = Mock()
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            
            # Create permission checker
            permission_checker = AuthMiddleware.check_permission(permission)
            
            # Mock get_db to return our test session
            with patch('enterprise_rbac_auth.middleware.auth_middleware.get_db') as mock_get_db:
                mock_get_db.return_value = iter([db_session])
                
                # Test that visitor cannot perform modification operations
                with pytest.raises(HTTPException) as exc_info:
                    import asyncio
                    asyncio.run(permission_checker(request, credentials))
                
                assert exc_info.value.status_code == 403
        finally:
            db_session.close()



class TestProjectAccessMiddleware:
    """Property-based tests for project access middleware."""
    
    # Feature: enterprise-rbac-authentication, Property 9: Unauthorized project access is denied
    # **Validates: Requirements 2.4, 4.3**
    @given(
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        project_id=st.uuids(),
        owner_id=st.uuids(),
        permission=st.sampled_from([Permission.VIEW_PROJECT, Permission.UPDATE_PROJECT, Permission.DELETE_PROJECT])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_9_unauthorized_project_access_denied(self, user_id, username, project_id, owner_id, permission):
        """
        Property 9: Unauthorized project access is denied
        
        For any user attempting to access a project they don't own and haven't been granted access to,
        the authorization middleware should return a 403 Forbidden response.
        """
        from unittest.mock import patch
        from ..models import Project
        
        # Ensure user is not the owner
        assume(user_id.hex != owner_id.hex)
        
        # Create test database session
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Generate token with PROGRAMMER role (not admin, to test access control)
            token = AuthService.generate_token(user_id.hex, username, Role.PROGRAMMER)
            
            # Create user in test database
            user = User(
                id=user_id.hex,
                username=username,
                password_hash=AuthService.hash_password("test_password"),
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(user)
            
            # Create project owned by someone else
            project = Project(
                id=project_id.hex,
                name="Test Project",
                description="Test Description",
                owner_id=owner_id.hex
            )
            db_session.add(project)
            db_session.commit()
            
            # Create mock request and credentials
            request = Mock(spec=Request)
            request.state = Mock()
            request.path_params = {"project_id": project_id.hex}
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            
            # Create project access checker
            project_access_checker = AuthMiddleware.check_project_access(permission)
            
            # Mock get_db to return our test session
            with patch('enterprise_rbac_auth.middleware.auth_middleware.get_db') as mock_get_db:
                mock_get_db.return_value = iter([db_session])
                
                # Test that unauthorized access is denied
                with pytest.raises(HTTPException) as exc_info:
                    import asyncio
                    asyncio.run(project_access_checker(request, credentials))
                
                assert exc_info.value.status_code == 403
                assert "access" in exc_info.value.detail.lower()
        finally:
            db_session.close()
    
    @given(
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        project_id=st.uuids(),
        permission=st.sampled_from([Permission.VIEW_PROJECT, Permission.UPDATE_PROJECT, Permission.DELETE_PROJECT])
    )
    @settings(max_examples=100, deadline=None)
    def test_project_owner_has_access(self, user_id, username, project_id, permission):
        """
        Test that project owners can access their own projects.
        """
        from unittest.mock import patch
        from ..models import Project
        
        # Create test database session
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Generate token with PROGRAMMER role
            token = AuthService.generate_token(user_id.hex, username, Role.PROGRAMMER)
            
            # Create user in test database
            user = User(
                id=user_id.hex,
                username=username,
                password_hash=AuthService.hash_password("test_password"),
                role=Role.PROGRAMMER,
                is_active=True
            )
            db_session.add(user)
            
            # Create project owned by the user
            project = Project(
                id=project_id.hex,
                name="Test Project",
                description="Test Description",
                owner_id=user_id.hex
            )
            db_session.add(project)
            db_session.commit()
            
            # Create mock request and credentials
            request = Mock(spec=Request)
            request.state = Mock()
            request.path_params = {"project_id": project_id.hex}
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            
            # Create project access checker
            project_access_checker = AuthMiddleware.check_project_access(permission)
            
            # Mock get_db to return our test session
            with patch('enterprise_rbac_auth.middleware.auth_middleware.get_db') as mock_get_db:
                mock_get_db.return_value = iter([db_session])
                
                # Test that owner has access
                import asyncio
                payload = asyncio.run(project_access_checker(request, credentials))
                
                # Verify payload is returned (no exception raised)
                assert payload is not None
                assert payload.user_id == user_id.hex
        finally:
            db_session.close()
    
    @given(
        user_id=st.uuids(),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        project_id=st.uuids(),
        permission=st.sampled_from([Permission.VIEW_PROJECT, Permission.UPDATE_PROJECT, Permission.DELETE_PROJECT])
    )
    @settings(max_examples=100, deadline=None)
    def test_admin_bypasses_project_access(self, user_id, username, project_id, permission):
        """
        Test that admins can access all projects regardless of ownership.
        """
        from unittest.mock import patch
        from ..models import Project
        import uuid
        
        # Create test database session
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Generate token with ADMIN role
            token = AuthService.generate_token(user_id.hex, username, Role.ADMIN)
            
            # Create admin user in test database
            admin_user = User(
                id=user_id.hex,
                username=username,
                password_hash=AuthService.hash_password("test_password"),
                role=Role.ADMIN,
                is_active=True
            )
            db_session.add(admin_user)
            
            # Create project owned by someone else
            other_owner_id = uuid.uuid4().hex
            project = Project(
                id=project_id.hex,
                name="Test Project",
                description="Test Description",
                owner_id=other_owner_id
            )
            db_session.add(project)
            db_session.commit()
            
            # Create mock request and credentials
            request = Mock(spec=Request)
            request.state = Mock()
            request.path_params = {"project_id": project_id.hex}
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            
            # Create project access checker
            project_access_checker = AuthMiddleware.check_project_access(permission)
            
            # Mock get_db to return our test session
            with patch('enterprise_rbac_auth.middleware.auth_middleware.get_db') as mock_get_db:
                mock_get_db.return_value = iter([db_session])
                
                # Test that admin has access
                import asyncio
                payload = asyncio.run(project_access_checker(request, credentials))
                
                # Verify payload is returned (no exception raised)
                assert payload is not None
                assert payload.role == Role.ADMIN.value
        finally:
            db_session.close()
