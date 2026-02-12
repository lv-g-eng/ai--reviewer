"""
Tests for Neo4j Client with Authentication Resilience

This module tests the enhanced Neo4j client implementation including
authentication failure handling, session management, and retry logic.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import neo4j
from neo4j.exceptions import AuthError, ServiceUnavailable, ClientError

from app.database.neo4j_client import Neo4jClient, AuthFailureTracker, SessionManager
from app.database.models import DatabaseConfig, RetryConfig
from app.database.retry_manager import RetryManager


# Constants for testing to avoid hard-coded credentials in literal strings
TEST_PASSWORD = "test_password_123"
TEST_USER = "test_user"


@pytest.fixture
def database_config():
    """Create test database configuration"""
    return DatabaseConfig(
        postgresql_dsn=f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/test",
        neo4j_uri="bolt://localhost:7687",
        neo4j_auth=("neo4j", TEST_PASSWORD),
        connection_timeout=10,
        pool_min_size=1,
        pool_max_size=5,
        retry_config=RetryConfig(
            max_retries=2,
            base_delay=0.1,
            max_delay=1.0,
            backoff_multiplier=2.0
        )
    )


@pytest.fixture
def retry_manager():
    """Create test retry manager"""
    return RetryManager()


@pytest.fixture
def neo4j_client(database_config, retry_manager):
    """Create test Neo4j client"""
    return Neo4jClient(database_config, retry_manager)


class TestAuthFailureTracker:
    """Test authentication failure tracking functionality"""
    
    def test_auth_failure_tracker_initialization(self):
        """Test that auth failure tracker initializes correctly"""
        tracker = AuthFailureTracker()
        
        assert tracker.failure_count == 0
        assert tracker.consecutive_failures == 0
        assert tracker.first_failure_time is None
        assert tracker.last_failure_time is None
        assert tracker.rate_limit_detected is False
        assert tracker.last_success_time is None
    
    def test_record_auth_failure(self):
        """Test recording authentication failures"""
        tracker = AuthFailureTracker()
        error = AuthError("Authentication failed")
        
        tracker.record_auth_failure(error)
        
        assert tracker.failure_count == 1
        assert tracker.consecutive_failures == 1
        assert tracker.first_failure_time is not None
        assert tracker.last_failure_time is not None
        assert tracker.rate_limit_detected is False
    
    def test_record_auth_failure_rate_limit_detection(self):
        """Test rate limit detection in auth failures"""
        tracker = AuthFailureTracker()
        error = AuthError("Too many authentication attempts")
        
        tracker.record_auth_failure(error)
        
        assert tracker.rate_limit_detected is True
    
    def test_record_auth_success_resets_failures(self):
        """Test that successful auth resets failure tracking"""
        tracker = AuthFailureTracker()
        error = AuthError("Authentication failed")
        
        # Record some failures
        tracker.record_auth_failure(error)
        tracker.record_auth_failure(error)
        
        # Record success
        tracker.record_auth_success()
        
        assert tracker.consecutive_failures == 0
        assert tracker.rate_limit_detected is False
        assert tracker.last_success_time is not None
        # Total failures should remain for statistics
        assert tracker.failure_count == 2
    
    def test_should_increase_backoff(self):
        """Test backoff increase logic"""
        tracker = AuthFailureTracker()
        
        # No failures - no backoff increase
        assert tracker.should_increase_backoff() is False
        
        # Few failures - no backoff increase
        error = AuthError("Authentication failed")
        tracker.record_auth_failure(error)
        tracker.record_auth_failure(error)
        assert tracker.should_increase_backoff() is False
        
        # Many failures - should increase backoff
        tracker.record_auth_failure(error)
        assert tracker.should_increase_backoff() is True
        
        # Rate limit detected - should increase backoff
        tracker = AuthFailureTracker()
        rate_limit_error = AuthError("Rate limit exceeded")
        tracker.record_auth_failure(rate_limit_error)
        assert tracker.should_increase_backoff() is True
    
    def test_get_recommended_delay_multiplier(self):
        """Test delay multiplier recommendations"""
        tracker = AuthFailureTracker()
        
        # No failures
        assert tracker.get_recommended_delay_multiplier() == 1.0
        
        # Few failures
        error = AuthError("Authentication failed")
        tracker.record_auth_failure(error)
        tracker.record_auth_failure(error)
        assert tracker.get_recommended_delay_multiplier() == 2.0
        
        # Many failures
        tracker.record_auth_failure(error)
        tracker.record_auth_failure(error)
        assert tracker.get_recommended_delay_multiplier() == 2.5
        
        # Rate limit detected
        tracker = AuthFailureTracker()
        rate_limit_error = AuthError("Rate limit exceeded")
        tracker.record_auth_failure(rate_limit_error)
        assert tracker.get_recommended_delay_multiplier() == 3.0


class TestSessionManager:
    """Test session management functionality"""
    
    @pytest.fixture
    def mock_client(self, neo4j_client):
        """Create mock client for session manager tests"""
        mock_client = MagicMock()
        mock_client.retry_manager = neo4j_client.retry_manager
        return mock_client
    
    def test_session_manager_initialization(self, mock_client):
        """Test session manager initialization"""
        manager = SessionManager(mock_client)
        
        assert manager.client == mock_client
        assert len(manager.active_sessions) == 0
        assert manager.session_stats['created'] == 0
        assert manager.session_stats['closed'] == 0
        assert manager.session_stats['failed'] == 0
        assert manager.session_stats['active_count'] == 0
    
    @pytest.mark.asyncio
    async def test_session_creation_and_cleanup(self, mock_client):
        """Test session creation and automatic cleanup"""
        manager = SessionManager(mock_client)
        
        # Mock session creation
        mock_session = AsyncMock()
        mock_client.retry_manager.execute_with_retry = AsyncMock(return_value=mock_session)
        
        async with manager.get_session("test_db") as session:
            assert session == mock_session
            assert manager.session_stats['created'] == 1
            assert manager.session_stats['active_count'] == 1
        
        # Session should be closed after context exit
        mock_session.close.assert_called_once()
        assert manager.session_stats['closed'] == 1
    
    @pytest.mark.asyncio
    async def test_session_creation_failure(self, mock_client):
        """Test session creation failure handling"""
        manager = SessionManager(mock_client)
        
        # Mock session creation failure
        mock_client.retry_manager.execute_with_retry = AsyncMock(
            side_effect=ServiceUnavailable("Service unavailable")
        )
        
        with pytest.raises(ServiceUnavailable):
            async with manager.get_session("test_db"):
                pass
        
        assert manager.session_stats['failed'] == 1
        assert manager.session_stats['created'] == 0
    
    def test_get_session_statistics(self, mock_client):
        """Test session statistics retrieval"""
        manager = SessionManager(mock_client)
        
        stats = manager.get_session_statistics()
        
        assert 'created' in stats
        assert 'closed' in stats
        assert 'failed' in stats
        assert 'active_count' in stats


class TestNeo4jClient:
    """Test Neo4j client functionality"""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, neo4j_client):
        """Test Neo4j client initialization"""
        assert neo4j_client.config is not None
        assert neo4j_client.retry_manager is not None
        assert neo4j_client.auth_tracker is not None
        assert neo4j_client.session_manager is not None
        assert neo4j_client._driver is None
    
    @pytest.mark.asyncio
    async def test_driver_creation_success(self, neo4j_client):
        """Test successful driver creation"""
        with patch('neo4j.AsyncGraphDatabase.driver') as mock_driver_class:
            mock_driver = AsyncMock()
            mock_driver.verify_connectivity = AsyncMock()
            mock_driver_class.return_value = mock_driver
            
            driver = await neo4j_client.get_driver()
            
            assert driver == mock_driver
            mock_driver.verify_connectivity.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_driver_creation_auth_failure(self, neo4j_client):
        """Test driver creation with authentication failure"""
        with patch('neo4j.AsyncGraphDatabase.driver') as mock_driver_class:
            mock_driver = AsyncMock()
            mock_driver.verify_connectivity = AsyncMock(
                side_effect=AuthError("Authentication failed")
            )
            mock_driver_class.return_value = mock_driver
            
            with pytest.raises(AuthError):
                await neo4j_client.get_driver()
            
            # Auth failure should be tracked
            assert neo4j_client.auth_tracker.failure_count > 0
    
    @pytest.mark.asyncio
    async def test_query_execution_success(self, neo4j_client):
        """Test successful query execution"""
        with patch.object(neo4j_client.session_manager, 'get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_session.run = AsyncMock(return_value=mock_result)
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await neo4j_client.execute_query("RETURN 1", {"param": "value"})
            
            assert result == mock_result
            mock_session.run.assert_called_once_with("RETURN 1", {"param": "value"})
    
    @pytest.mark.asyncio
    async def test_query_execution_auth_error(self, neo4j_client):
        """Test query execution with authentication error"""
        with patch.object(neo4j_client.session_manager, 'get_session') as mock_get_session:
            mock_session = AsyncMock()
            auth_error = AuthError("Authentication failed")
            mock_session.run = AsyncMock(side_effect=auth_error)
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            with pytest.raises(AuthError):
                await neo4j_client.execute_query("RETURN 1")
            
            # Auth failure should be tracked
            assert neo4j_client.auth_tracker.failure_count > 0
    
    @pytest.mark.asyncio
    async def test_connectivity_test_success(self, neo4j_client):
        """Test successful connectivity test"""
        with patch.object(neo4j_client, 'execute_query') as mock_execute:
            mock_result = AsyncMock()
            mock_record = {"test": 1}
            mock_result.single = AsyncMock(return_value=mock_record)
            mock_execute.return_value = mock_result
            
            result = await neo4j_client.test_connectivity()
            
            assert result is True
            mock_execute.assert_called_once_with("RETURN 1 AS test")
    
    @pytest.mark.asyncio
    async def test_connectivity_test_failure(self, neo4j_client):
        """Test connectivity test failure"""
        with patch.object(neo4j_client, 'execute_query') as mock_execute:
            mock_execute.side_effect = ServiceUnavailable("Service unavailable")
            
            result = await neo4j_client.test_connectivity()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_client_close(self, neo4j_client):
        """Test client cleanup and resource closure"""
        # Mock session manager and driver
        neo4j_client.session_manager.close_all_sessions = AsyncMock()
        mock_driver = AsyncMock()
        neo4j_client._driver = mock_driver
        
        await neo4j_client.close()
        
        neo4j_client.session_manager.close_all_sessions.assert_called_once()
        mock_driver.close.assert_called_once()
        assert neo4j_client._driver is None
    
    @pytest.mark.asyncio
    async def test_get_auth_statistics(self, neo4j_client):
        """Test authentication statistics retrieval"""
        # Record some auth failures
        error = AuthError("Test error")
        neo4j_client.auth_tracker.record_auth_failure(error)
        neo4j_client.auth_tracker.record_auth_success()
        
        stats = await neo4j_client.get_auth_statistics()
        
        assert 'total_failures' in stats
        assert 'consecutive_failures' in stats
        assert 'rate_limit_detected' in stats
        assert 'last_success_time' in stats
        assert stats['total_failures'] == 1
        assert stats['consecutive_failures'] == 0  # Reset after success
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, neo4j_client):
        """Test health check when client is healthy"""
        with patch.object(neo4j_client, 'test_connectivity', return_value=True):
            with patch.object(neo4j_client, 'get_client_statistics', return_value={}):
                health = await neo4j_client.health_check()
                
                assert health['status'] == 'healthy'
                assert health['connectivity'] is True
                assert health['authentication'] == 'success'
                assert health['session_management'] == 'operational'
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, neo4j_client):
        """Test health check when client is unhealthy"""
        with patch.object(neo4j_client, 'test_connectivity', return_value=False):
            with patch.object(neo4j_client, 'get_client_statistics', return_value={}):
                health = await neo4j_client.health_check()
                
                assert health['status'] == 'unhealthy'
                assert health['connectivity'] is False
                assert health['authentication'] == 'failed'


if __name__ == "__main__":
    pytest.main([__file__])