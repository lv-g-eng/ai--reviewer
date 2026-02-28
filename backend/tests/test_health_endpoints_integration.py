"""
Integration Tests for Health Check Endpoints

Tests the health check endpoints with real FastAPI application:
- /health - Overall health status
- /health/ready - Readiness probe
- /health/live - Liveness probe

Tests with both healthy and unhealthy dependencies.

Validates Requirements: 12.8, 5.2
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.database.connection_manager import ConnectionStatus


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_healthy_dependencies():
    """Mock all dependencies as healthy"""
    return {
        "PostgreSQL": ConnectionStatus(
            service="PostgreSQL",
            is_connected=True,
            response_time_ms=10.5,
            is_critical=True,
        ),
        "Neo4j": ConnectionStatus(
            service="Neo4j",
            is_connected=True,
            response_time_ms=15.2,
            is_critical=False,
        ),
        "Redis": ConnectionStatus(
            service="Redis",
            is_connected=True,
            response_time_ms=5.1,
            is_critical=False,
        ),
    }


@pytest.fixture
def mock_unhealthy_dependencies():
    """Mock all dependencies as unhealthy"""
    return {
        "PostgreSQL": ConnectionStatus(
            service="PostgreSQL",
            is_connected=False,
            response_time_ms=0.0,
            error="Connection refused",
            is_critical=True,
        ),
        "Neo4j": ConnectionStatus(
            service="Neo4j",
            is_connected=False,
            response_time_ms=0.0,
            error="Authentication failed",
            is_critical=False,
        ),
        "Redis": ConnectionStatus(
            service="Redis",
            is_connected=False,
            response_time_ms=0.0,
            error="Connection timeout",
            is_critical=False,
        ),
    }


@pytest.fixture
def mock_degraded_dependencies():
    """Mock dependencies in degraded state (PostgreSQL down, others up)"""
    return {
        "PostgreSQL": ConnectionStatus(
            service="PostgreSQL",
            is_connected=False,
            response_time_ms=0.0,
            error="Connection refused",
            is_critical=True,
        ),
        "Neo4j": ConnectionStatus(
            service="Neo4j",
            is_connected=True,
            response_time_ms=15.2,
            is_critical=False,
        ),
        "Redis": ConnectionStatus(
            service="Redis",
            is_connected=True,
            response_time_ms=5.1,
            is_critical=False,
        ),
    }


class TestHealthEndpoint:
    """Tests for /health endpoint"""
    
    def test_health_endpoint_healthy(self, client, mock_healthy_dependencies):
        """Test /health returns 200 when all dependencies are healthy"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_all.return_value = mock_healthy_dependencies
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "healthy"
            assert "version" in data
            assert "environment" in data
            assert "timestamp" in data
            assert "databases" in data
            
            # Check database details
            assert "PostgreSQL" in data["databases"]
            assert data["databases"]["PostgreSQL"]["is_connected"] is True
            assert data["databases"]["PostgreSQL"]["response_time_ms"] == 10.5
            
            assert "Neo4j" in data["databases"]
            assert data["databases"]["Neo4j"]["is_connected"] is True
            
            assert "Redis" in data["databases"]
            assert data["databases"]["Redis"]["is_connected"] is True
    
    def test_health_endpoint_unhealthy(self, client, mock_unhealthy_dependencies):
        """Test /health returns 503 when all dependencies are unhealthy"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_all.return_value = mock_unhealthy_dependencies
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health")
            
            assert response.status_code == 503
            data = response.json()
            
            assert data["status"] == "unhealthy"
            
            # Check error messages are included
            assert data["databases"]["PostgreSQL"]["error"] == "Connection refused"
            assert data["databases"]["Neo4j"]["error"] == "Authentication failed"
            assert data["databases"]["Redis"]["error"] == "Connection timeout"
    
    def test_health_endpoint_degraded(self, client, mock_degraded_dependencies):
        """Test /health returns 503 when in degraded state"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_all.return_value = mock_degraded_dependencies
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health")
            
            assert response.status_code == 503
            data = response.json()
            
            assert data["status"] == "degraded"
            
            # PostgreSQL should be down
            assert data["databases"]["PostgreSQL"]["is_connected"] is False
            assert data["databases"]["PostgreSQL"]["error"] == "Connection refused"
            
            # Neo4j and Redis should be up
            assert data["databases"]["Neo4j"]["is_connected"] is True
            assert data["databases"]["Redis"]["is_connected"] is True
    
    def test_health_endpoint_includes_response_times(self, client, mock_healthy_dependencies):
        """Test /health includes response times for each dependency"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_all.return_value = mock_healthy_dependencies
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response times are included
            assert "response_time_ms" in data["databases"]["PostgreSQL"]
            assert data["databases"]["PostgreSQL"]["response_time_ms"] == 10.5
            
            assert "response_time_ms" in data["databases"]["Neo4j"]
            assert data["databases"]["Neo4j"]["response_time_ms"] == 15.2
            
            assert "response_time_ms" in data["databases"]["Redis"]
            assert data["databases"]["Redis"]["response_time_ms"] == 5.1


class TestReadinessEndpoint:
    """Tests for /health/ready endpoint"""
    
    def test_readiness_endpoint_ready(self, client):
        """Test /health/ready returns 200 when system is ready"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_postgres.return_value = ConnectionStatus(
                service="PostgreSQL",
                is_connected=True,
                response_time_ms=10.5,
                is_critical=True,
            )
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["ready"] is True
            assert "ready" in data["reason"].lower()
            assert "timestamp" in data
    
    def test_readiness_endpoint_not_ready(self, client):
        """Test /health/ready returns 503 when PostgreSQL is not connected"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_postgres.return_value = ConnectionStatus(
                service="PostgreSQL",
                is_connected=False,
                response_time_ms=0.0,
                error="Connection refused",
                is_critical=True,
            )
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health/ready")
            
            assert response.status_code == 503
            data = response.json()
            
            assert data["ready"] is False
            assert "PostgreSQL" in data["reason"]
            assert "Connection refused" in data["reason"]
    
    def test_readiness_endpoint_includes_error_details(self, client):
        """Test /health/ready includes detailed error information"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_postgres.return_value = ConnectionStatus(
                service="PostgreSQL",
                is_connected=False,
                response_time_ms=0.0,
                error="Connection timeout after 5 seconds",
                is_critical=True,
            )
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health/ready")
            
            assert response.status_code == 503
            data = response.json()
            
            # Verify error details are included
            assert "Connection timeout after 5 seconds" in data["reason"]


class TestLivenessEndpoint:
    """Tests for /health/live endpoint"""
    
    def test_liveness_endpoint_alive(self, client):
        """Test /health/live always returns 200 when process is running"""
        response = client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["alive"] is True
        assert "timestamp" in data
    
    def test_liveness_endpoint_independent_of_dependencies(self, client):
        """Test /health/live returns 200 even when dependencies are down"""
        # Liveness should not check dependencies
        response = client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["alive"] is True


class TestHealthEndpointIntegration:
    """Integration tests for health endpoints"""
    
    def test_health_endpoints_return_consistent_timestamps(self, client, mock_healthy_dependencies):
        """Test all health endpoints return valid timestamps"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_all.return_value = mock_healthy_dependencies
            mock_manager.verify_postgres.return_value = mock_healthy_dependencies["PostgreSQL"]
            mock_get_manager.return_value = mock_manager
            
            # Get all endpoints
            health_response = client.get("/health")
            ready_response = client.get("/health/ready")
            live_response = client.get("/health/live")
            
            # All should have timestamps
            assert "timestamp" in health_response.json()
            assert "timestamp" in ready_response.json()
            assert "timestamp" in live_response.json()
            
            # Timestamps should be ISO format
            import datetime
            for response in [health_response, ready_response, live_response]:
                timestamp = response.json()["timestamp"]
                # Should be parseable as ISO format
                datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_health_endpoint_checks_all_three_databases(self, client, mock_healthy_dependencies):
        """Test /health checks PostgreSQL, Neo4j, and Redis"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_all.return_value = mock_healthy_dependencies
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify all three databases are checked
            assert "PostgreSQL" in data["databases"]
            assert "Neo4j" in data["databases"]
            assert "Redis" in data["databases"]
            
            # Verify verify_all was called
            mock_manager.verify_all.assert_called_once()
    
    def test_readiness_endpoint_only_checks_postgresql(self, client):
        """Test /health/ready only checks PostgreSQL (critical dependency)"""
        with patch('app.services.health_service.get_connection_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.verify_postgres.return_value = ConnectionStatus(
                service="PostgreSQL",
                is_connected=True,
                response_time_ms=10.5,
                is_critical=True,
            )
            mock_get_manager.return_value = mock_manager
            
            response = client.get("/health/ready")
            
            assert response.status_code == 200
            
            # Verify only PostgreSQL was checked
            mock_manager.verify_postgres.assert_called_once()
            mock_manager.verify_neo4j.assert_not_called()
            mock_manager.verify_redis.assert_not_called()
