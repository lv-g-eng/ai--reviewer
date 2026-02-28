"""
Common test fixtures to eliminate duplication across test files.

This module provides reusable fixtures following the DRY principle.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx
from app.services.llm.circuit_breaker import AsyncCircuitBreaker


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client for testing."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def mock_circuit_breaker():
    """
    Create mock circuit breaker for testing.
    
    The mock allows function calls to pass through by default.
    """
    async def mock_call(func, *args, **kwargs):
        return await func(*args, **kwargs)
    
    breaker = AsyncMock(spec=AsyncCircuitBreaker)
    breaker.call = AsyncMock(side_effect=mock_call)
    return breaker


@pytest.fixture
def mock_redis_client():
    """Create mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    mock_redis.exists = AsyncMock(return_value=0)
    mock_redis.expire = AsyncMock(return_value=True)
    return mock_redis


@pytest.fixture
def mock_logger():
    """Create mock logger for testing."""
    return MagicMock()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "role": "developer",
        "is_active": True,
        "email_confirmed": True
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "id": "223e4567-e89b-12d3-a456-426614174000",
        "name": "Test Project",
        "description": "A test project",
        "repository_url": "https://github.com/test/repo",
        "owner_id": "123e4567-e89b-12d3-a456-426614174000"
    }


@pytest.fixture
def sample_pull_request_data():
    """Sample pull request data for testing."""
    return {
        "id": "323e4567-e89b-12d3-a456-426614174000",
        "title": "Test PR",
        "description": "A test pull request",
        "pr_number": 123,
        "status": "open",
        "project_id": "223e4567-e89b-12d3-a456-426614174000",
        "author_id": "123e4567-e89b-12d3-a456-426614174000"
    }


@pytest.fixture
def mock_db_session():
    """Create mock database session for testing."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_request():
    """Create mock FastAPI request for testing."""
    request = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {"user-agent": "test-agent"}
    return request


@pytest.fixture
def mock_response():
    """Create mock HTTP response for testing."""
    response = MagicMock()
    response.status_code = 200
    response.json = MagicMock(return_value={})
    response.text = ""
    response.headers = {}
    return response


@pytest.fixture
def mock_audit_service():
    """Create mock audit service for testing."""
    service = AsyncMock()
    service.log_data_access = AsyncMock()
    service.log_action = AsyncMock()
    return service
