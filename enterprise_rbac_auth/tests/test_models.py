"""
Unit tests for data models.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from enterprise_rbac_auth.models import (
    Base, User, Project, ProjectAccess, Session as SessionModel, AuditLog,
    Role, Permission, ROLE_PERMISSIONS
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestEnums:
    """Test Role and Permission enums."""
    
    def test_role_enum_values(self):
        """Test that Role enum has correct values."""
        assert Role.ADMIN.value == "ADMIN"
        assert Role.PROGRAMMER.value == "PROGRAMMER"
        assert Role.VISITOR.value == "VISITOR"
    
    def test_permission_enum_values(self):
        """Test that Permission enum has all required permissions."""
        expected_permissions = {
            "CREATE_USER", "DELETE_USER", "UPDATE_USER", "VIEW_USER",
            "CREATE_PROJECT", "DELETE_PROJECT", "UPDATE_PROJECT", "VIEW_PROJECT",
            "MODIFY_CONFIG", "VIEW_CONFIG", "EXPORT_REPORT"
        }
        actual_permissions = {p.value for p in Permission}
        assert actual_permissions == expected_permissions
    
    def test_role_permissions_mapping(self):
        """Test that role-permission mapping is correct."""
        # Admin should have all permissions
        assert len(ROLE_PERMISSIONS[Role.ADMIN]) == 11
        assert set(ROLE_PERMISSIONS[Role.ADMIN]) == set(Permission)
        
        # Programmer should have 5 permissions
        assert len(ROLE_PERMISSIONS[Role.PROGRAMMER]) == 5
        assert Permission.CREATE_PROJECT in ROLE_PERMISSIONS[Role.PROGRAMMER]
        assert Permission.CREATE_USER not in ROLE_PERMISSIONS[Role.PROGRAMMER]
        
        # Visitor should have 1 permission
        assert len(ROLE_PERMISSIONS[Role.VISITOR]) == 1
        assert Permission.VIEW_PROJECT in ROLE_PERMISSIONS[Role.VISITOR]


class TestUserModel:
    """Test User model."""
    
    def test_create_user(self, db_session: Session):
        """Test creating a user."""
        user = User(
            id=str(uuid.uuid4()),
            username="testuser",
            password_hash="hashed_password",
            role=Role.PROGRAMMER,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        retrieved = db_session.query(User).filter_by(username="testuser").first()
        assert retrieved is not None
        assert retrieved.username == "testuser"
        assert retrieved.role == Role.PROGRAMMER
        assert retrieved.is_active is True
    
    def test_user_unique_username(self, db_session: Session):
        """Test that username must be unique."""
        user1 = User(
            id=str(uuid.uuid4()),
            username="duplicate",
            password_hash="hash1",
            role=Role.PROGRAMMER
        )
        user2 = User(
            id=str(uuid.uuid4()),
            username="duplicate",
            password_hash="hash2",
            role=Role.VISITOR
        )
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()


class TestProjectModel:
    """Test Project and ProjectAccess models."""
    
    def test_create_project(self, db_session: Session):
        """Test creating a project."""
        user = User(
            id=str(uuid.uuid4()),
            username="owner",
            password_hash="hash",
            role=Role.PROGRAMMER
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="A test project",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        retrieved = db_session.query(Project).filter_by(name="Test Project").first()
        assert retrieved is not None
        assert retrieved.owner_id == user.id
        assert retrieved.owner.username == "owner"
    
    def test_project_access_grant(self, db_session: Session):
        """Test granting project access."""
        owner = User(id=str(uuid.uuid4()), username="owner", password_hash="hash", role=Role.PROGRAMMER)
        grantee = User(id=str(uuid.uuid4()), username="grantee", password_hash="hash", role=Role.PROGRAMMER)
        db_session.add_all([owner, grantee])
        db_session.commit()
        
        project = Project(id=str(uuid.uuid4()), name="Project", owner_id=owner.id)
        db_session.add(project)
        db_session.commit()
        
        access = ProjectAccess(
            project_id=project.id,
            user_id=grantee.id,
            granted_by=owner.id
        )
        db_session.add(access)
        db_session.commit()
        
        retrieved = db_session.query(ProjectAccess).filter_by(project_id=project.id).first()
        assert retrieved is not None
        assert retrieved.user_id == grantee.id
        assert retrieved.granted_by == owner.id


class TestSessionModel:
    """Test Session model."""
    
    def test_create_session(self, db_session: Session):
        """Test creating a session."""
        user = User(id=str(uuid.uuid4()), username="user", password_hash="hash", role=Role.PROGRAMMER)
        db_session.add(user)
        db_session.commit()
        
        session = SessionModel(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token="jwt_token_here",
            issued_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_valid=True,
            ip_address="192.168.1.1"
        )
        db_session.add(session)
        db_session.commit()
        
        retrieved = db_session.query(SessionModel).filter_by(user_id=user.id).first()
        assert retrieved is not None
        assert retrieved.token == "jwt_token_here"
        assert retrieved.is_valid is True


class TestAuditLogModel:
    """Test AuditLog model."""
    
    def test_create_audit_log(self, db_session: Session):
        """Test creating an audit log entry."""
        user = User(id=str(uuid.uuid4()), username="user", password_hash="hash", role=Role.ADMIN)
        db_session.add(user)
        db_session.commit()
        
        log = AuditLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user.id,
            username=user.username,
            action="LOGIN",
            ip_address="192.168.1.1",
            success=True
        )
        db_session.add(log)
        db_session.commit()
        
        retrieved = db_session.query(AuditLog).filter_by(user_id=user.id).first()
        assert retrieved is not None
        assert retrieved.action == "LOGIN"
        assert retrieved.success is True
