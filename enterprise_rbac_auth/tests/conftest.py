"""
Pytest configuration and fixtures for tests.
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from ..models import Base
from ..database import get_db_session
from ..main import app


@pytest.fixture(scope="session", autouse=True)
def reduce_bcrypt_rounds_for_tests():
    """
    Reduce bcrypt rounds for faster test execution.
    
    In production, we use 12 rounds for security.
    In tests, we use 4 rounds for speed.
    """
    from enterprise_rbac_auth import config
    
    # Store original value
    original_rounds = config.settings.bcrypt_rounds
    
    # Set to 4 rounds for tests (much faster)
    config.settings.bcrypt_rounds = 4
    
    yield
    
    # Restore original value
    config.settings.bcrypt_rounds = original_rounds


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Uses in-memory SQLite database for fast testing.
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Create a test client with database session override.
    """
    def override_get_db_session():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
