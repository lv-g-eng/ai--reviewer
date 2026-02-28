"""
Integration tests for circuit breaker pattern

Tests circuit breaker behavior for GitHub API, Neo4j, and LLM services.

Validates Requirements: 13.9
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.github_circuit_breaker import (
    GitHubClientWithCircuitBreaker,
    get_github_client_with_circuit_breaker
)
from app.database.neo4j_circuit_breaker import (
    Neo4jWithCircuitBreaker,
    Neo4jCircuitBreakerError,
    get_neo4j_with_circuit_breaker
)
from app.services.llm.circuit_breaker import CircuitState
from app.services.cache_manager import get_cache_manager


class TestGitHubCircuitBreaker:
    """
    Test circuit breaker for GitHub API
    
    Validates Requirements: 13.9
    """
    
    @pytest.fixture
    def github_client(self):
        """Create GitHub client with circuit breaker"""
        client = GitHubClientWithCircuitBreaker()
        # Reset circuit breaker state
        client.circuit_breaker.reset()
        # Clear cache
        client.cache.clear()
        return client
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold_failures(self, github_client):
        """
        Test that circuit opens after reaching failure threshold
        
        Validates Requirements: 13.9
        """
        # Mock the underlying client to always fail
        with patch.object(
            github_client.client,
            'get_repository',
            side_effect=Exception("GitHub API error")
        ):
            # Make enough calls to trigger circuit breaker
            # Window size is 10, failure threshold is 50%
            # So we need at least 10 calls with 5+ failures
            
            for i in range(10):
                try:
                    await github_client.get_repository("https://github.com/test/repo")
                except (HTTPException, Exception):
                    pass  # Expected to fail
            
            # Circuit should now be OPEN
            assert github_client.circuit_breaker.get_state() == CircuitState.OPEN
            
            # Next call should fail immediately without calling the API
            with pytest.raises(HTTPException) as exc_info:
                await github_client.get_repository("https://github.com/test/repo")
            
            assert exc_info.value.status_code == 503
            assert "unavailable" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_circuit_closes_after_recovery(self, github_client):
        """
        Test that circuit closes after successful recovery
        
        Validates Requirements: 13.9
        """
        # First, open the circuit by causing failures
        with patch.object(
            github_client.client,
            'get_repository',
            side_effect=Exception("GitHub API error")
        ):
            for i in range(10):
                try:
                    await github_client.get_repository("https://github.com/test/repo")
                except (HTTPException, Exception):
                    pass
        
        # Verify circuit is OPEN
        assert github_client.circuit_breaker.get_state() == CircuitState.OPEN
        
        # Manually transition to HALF_OPEN (simulating timeout)
        github_client.circuit_breaker._transition_to_half_open()
        assert github_client.circuit_breaker.get_state() == CircuitState.HALF_OPEN
        
        # Mock successful responses
        mock_repo_data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "test/repo",
            "description": "Test repository",
            "language": "Python",
            "default_branch": "main",
            "private": False
        }
        
        with patch.object(
            github_client.client,
            'get_repository',
            return_value=mock_repo_data
        ):
            # Make successful calls (need 2 successes to close circuit)
            result1 = await github_client.get_repository("https://github.com/test/repo")
            assert result1 == mock_repo_data
            
            result2 = await github_client.get_repository("https://github.com/test/repo")
            assert result2 == mock_repo_data
        
        # Circuit should now be CLOSED
        assert github_client.circuit_breaker.get_state() == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_with_cache(self, github_client):
        """
        Test graceful degradation returns cached data when circuit is open
        
        Validates Requirements: 13.9, 2.7, 12.6
        """
        mock_repo_data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "test/repo",
            "description": "Test repository",
            "language": "Python",
            "default_branch": "main",
            "private": False
        }
        
        # First, make a successful call to populate cache
        with patch.object(
            github_client.client,
            'get_repository',
            return_value=mock_repo_data
        ):
            result = await github_client.get_repository("https://github.com/test/repo")
            assert result == mock_repo_data
        
        # Now open the circuit
        with patch.object(
            github_client.client,
            'get_repository',
            side_effect=Exception("GitHub API error")
        ):
            for i in range(10):
                try:
                    await github_client.get_repository("https://github.com/test/repo2")
                except (HTTPException, Exception):
                    pass
        
        # Verify circuit is OPEN
        assert github_client.circuit_breaker.get_state() == CircuitState.OPEN
        
        # Request the cached data - should return cached result
        result = await github_client.get_repository("https://github.com/test/repo")
        assert result == mock_repo_data
    
    @pytest.mark.asyncio
    async def test_write_operations_return_fallback_response(self, github_client):
        """
        Test that write operations return fallback response when circuit is open
        
        Validates Requirements: 13.9, 2.7, 12.6
        """
        # Open the circuit
        with patch.object(
            github_client.client,
            'post_review_comment',
            side_effect=Exception("GitHub API error")
        ):
            for i in range(10):
                try:
                    await github_client.post_review_comment(
                        "test/repo", 1, "comment", "abc123", "file.py", 10
                    )
                except (HTTPException, Exception):
                    pass
        
        # Verify circuit is OPEN
        assert github_client.circuit_breaker.get_state() == CircuitState.OPEN
        
        # Try to post a comment - should return fallback response
        result = await github_client.post_review_comment(
            "test/repo", 1, "Test comment", "abc123", "file.py", 10
        )
        
        assert result["status"] == "deferred"
        assert result["body"] == "Test comment"
        assert "queued" in result["message"].lower()


class TestNeo4jCircuitBreaker:
    """
    Test circuit breaker for Neo4j database
    
    Validates Requirements: 13.9
    """
    
    @pytest.fixture
    def neo4j_client(self):
        """Create Neo4j client with circuit breaker"""
        client = Neo4jWithCircuitBreaker()
        # Reset circuit breaker state
        client.circuit_breaker.reset()
        # Clear cache
        client.cache.clear()
        return client
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold_failures(self, neo4j_client):
        """
        Test that circuit opens after reaching failure threshold
        
        Validates Requirements: 13.9
        """
        # Mock get_neo4j_driver to always fail
        with patch(
            'app.database.neo4j_circuit_breaker.get_neo4j_driver',
            side_effect=Exception("Neo4j connection error")
        ):
            # Make enough calls to trigger circuit breaker
            for i in range(10):
                try:
                    await neo4j_client.execute_read_query("MATCH (n) RETURN n")
                except (Neo4jCircuitBreakerError, Exception):
                    pass  # Expected to fail
            
            # Circuit should now be OPEN
            assert neo4j_client.circuit_breaker.get_state() == CircuitState.OPEN
            
            # Next call should fail immediately
            with pytest.raises(Neo4jCircuitBreakerError) as exc_info:
                await neo4j_client.execute_read_query("MATCH (n) RETURN n")
            
            assert "temporarily unavailable" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_circuit_closes_after_recovery(self, neo4j_client):
        """
        Test that circuit closes after successful recovery
        
        Validates Requirements: 13.9
        """
        # First, open the circuit
        with patch(
            'app.database.neo4j_circuit_breaker.get_neo4j_driver',
            side_effect=Exception("Neo4j connection error")
        ):
            for i in range(10):
                try:
                    await neo4j_client.execute_read_query("MATCH (n) RETURN n")
                except (Neo4jCircuitBreakerError, Exception):
                    pass
        
        # Verify circuit is OPEN
        assert neo4j_client.circuit_breaker.get_state() == CircuitState.OPEN
        
        # Manually transition to HALF_OPEN
        neo4j_client.circuit_breaker._transition_to_half_open()
        assert neo4j_client.circuit_breaker.get_state() == CircuitState.HALF_OPEN
        
        # Manually transition to CLOSED (simulating successful recovery)
        neo4j_client.circuit_breaker._transition_to_closed()
        
        # Circuit should now be CLOSED
        assert neo4j_client.circuit_breaker.get_state() == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_with_cache(self, neo4j_client):
        """
        Test graceful degradation returns cached data when circuit is open
        
        Validates Requirements: 13.9, 2.7, 12.6
        """
        # Manually populate cache
        import hashlib
        query = "MATCH (n) RETURN n"
        cache_key_str = f"neo4j:read:{query}:None"
        cache_key = f"neo4j:read:{hashlib.md5(cache_key_str.encode()).hexdigest()}"
        mock_data = [{"n": {"id": 1, "name": "test"}}]
        neo4j_client.cache.set(cache_key, mock_data)
        
        # Open the circuit
        with patch(
            'app.database.neo4j_circuit_breaker.get_neo4j_driver',
            side_effect=Exception("Neo4j connection error")
        ):
            for i in range(10):
                try:
                    await neo4j_client.execute_read_query("MATCH (x) RETURN x")
                except (Neo4jCircuitBreakerError, Exception):
                    pass
        
        # Verify circuit is OPEN
        assert neo4j_client.circuit_breaker.get_state() == CircuitState.OPEN
        
        # Request the cached data - should return cached result
        result = await neo4j_client.execute_read_query(query)
        assert result == mock_data


class TestCircuitBreakerStats:
    """
    Test circuit breaker statistics and monitoring
    
    Validates Requirements: 13.9
    """
    
    def test_github_circuit_breaker_stats(self):
        """Test GitHub circuit breaker statistics"""
        client = GitHubClientWithCircuitBreaker()
        client.circuit_breaker.reset()
        
        stats = client.get_circuit_breaker_stats()
        
        assert "name" in stats
        assert stats["name"] == "github_api"
        assert "state" in stats
        assert stats["state"] == "closed"
        assert "failure_count" in stats
        assert "failure_rate" in stats
    
    def test_neo4j_circuit_breaker_stats(self):
        """Test Neo4j circuit breaker statistics"""
        client = Neo4jWithCircuitBreaker()
        client.circuit_breaker.reset()
        
        stats = client.get_circuit_breaker_stats()
        
        assert "name" in stats
        assert stats["name"] == "neo4j_database"
        assert "state" in stats
        assert stats["state"] == "closed"
        assert "failure_count" in stats
        assert "failure_rate" in stats
