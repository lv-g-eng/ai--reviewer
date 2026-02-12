"""
Tests for Health Service

Tests comprehensive health status checking, database connectivity verification,
and Kubernetes-style probes (liveness, readiness).

Validates Requirements: 1.2, 1.4, 2.1, 2.4, 2.5
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.health_service import (
    HealthService,
    HealthStatus,
    HealthCheckResponse,
    ReadinessCheckResponse,
    LivenessCheckResponse,
    DatabaseHealth,
    ServiceHealth,
)
from app.core.config import settings


@pytest.fixture
def health_service():
    """Create a health service instance for testing"""
    return HealthService()


@pytest.fixture
def mock_connection_manager():
    """Create a mock connection manager"""
    manager = AsyncMock()
    return manager


class TestHealthCheckResponse:
    """Tests for HealthCheckResponse model"""
    
    def test_health_check_response_to_dict(self):
        """Test HealthCheckResponse.to_dict() converts to dictionary"""
        response = HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            environment="test",
            timestamp=datetime.now(timezone.utc).isoformat(),
            databases={
                "PostgreSQL": DatabaseHealth(
                    name="PostgreSQL",
                    is_connected=True,
                    response_time_ms=10.5,
                )
            },
            services={
                "Celery": ServiceHealth(
                    name="Celery",
                    is_available=True,
                )
            },
        )
        
        result = response.to_dict()
        
        assert result["status"] == "healthy"
        assert result["version"] == "1.0.0"
        assert result["environment"] == "test"
        assert "PostgreSQL" in result["databases"]
        assert result["databases"]["PostgreSQL"]["is_connected"] is True
        assert "Celery" in result["services"]
        assert result["services"]["Celery"]["is_available"] is True


class TestReadinessCheckResponse:
    """Tests for ReadinessCheckResponse model"""
    
    def test_readiness_check_response_to_dict(self):
        """Test ReadinessCheckResponse.to_dict() converts to dictionary"""
        response = ReadinessCheckResponse(
            ready=True,
            reason="All required dependencies ready",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        result = response.to_dict()
        
        assert result["ready"] is True
        assert result["reason"] == "All required dependencies ready"
        assert "timestamp" in result


class TestLivenessCheckResponse:
    """Tests for LivenessCheckResponse model"""
    
    def test_liveness_check_response_to_dict(self):
        """Test LivenessCheckResponse.to_dict() converts to dictionary"""
        response = LivenessCheckResponse(
            alive=True,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        result = response.to_dict()
        
        assert result["alive"] is True
        assert "timestamp" in result


class TestHealthService:
    """Tests for HealthService"""
    
    @pytest.mark.asyncio
    async def test_get_health_status_all_connected(self, health_service, mock_connection_manager):
        """Test get_health_status when all databases are connected"""
        from app.database.connection_manager import ConnectionStatus
        
        # Mock connection manager
        mock_connection_manager.verify_all.return_value = {
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
        
        health_service.connection_manager = mock_connection_manager
        
        # Get health status
        response = await health_service.get_health_status()
        
        # Verify response
        assert response.status == "healthy"
        assert "PostgreSQL" in response.databases
        assert response.databases["PostgreSQL"].is_connected is True
        assert response.databases["PostgreSQL"].response_time_ms == 10.5
        
    @pytest.mark.asyncio
    async def test_get_health_status_with_errors(self, health_service, mock_connection_manager):
        """Test get_health_status includes error messages when dependencies fail"""
        from app.database.connection_manager import ConnectionStatus
        
        # Mock connection manager with errors
        mock_connection_manager.verify_all.return_value = {
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
                is_connected=False,
                response_time_ms=0.0,
                error="Timeout",
                is_critical=False,
            ),
        }
        
        health_service.connection_manager = mock_connection_manager
        
        # Get health status
        response = await health_service.get_health_status()
        
        # Verify response includes error messages
        # Status is "degraded" because Neo4j is connected (any_connected=True)
        # but PostgreSQL (critical) is not connected (all_critical_connected=False)
        assert response.status == "degraded"
        assert response.databases["PostgreSQL"].error == "Connection refused"
        assert response.databases["Redis"].error == "Timeout"
        
    @pytest.mark.asyncio
    async def test_get_readiness_status_ready(self, health_service, mock_connection_manager):
        """Test get_readiness_status when system is ready"""
        from app.database.connection_manager import ConnectionStatus
        
        # Mock PostgreSQL connected
        mock_connection_manager.verify_postgres.return_value = ConnectionStatus(
            service="PostgreSQL",
            is_connected=True,
            response_time_ms=10.5,
            is_critical=True,
        )
        
        health_service.connection_manager = mock_connection_manager
        
        # Get readiness status
        response = await health_service.get_readiness_status()
        
        # Verify response
        assert response.ready is True
        assert "ready" in response.reason.lower()
        
    @pytest.mark.asyncio
    async def test_get_readiness_status_not_ready(self, health_service, mock_connection_manager):
        """Test get_readiness_status when PostgreSQL is not connected"""
        from app.database.connection_manager import ConnectionStatus
        
        # Mock PostgreSQL not connected
        mock_connection_manager.verify_postgres.return_value = ConnectionStatus(
            service="PostgreSQL",
            is_connected=False,
            response_time_ms=0.0,
            error="Connection refused",
            is_critical=True,
        )
        
        health_service.connection_manager = mock_connection_manager
        
        # Get readiness status
        response = await health_service.get_readiness_status()
        
        # Verify response
        assert response.ready is False
        assert "PostgreSQL" in response.reason
        assert "Connection refused" in response.reason
        
    @pytest.mark.asyncio
    async def test_get_liveness_status(self, health_service):
        """Test get_liveness_status returns alive"""
        response = await health_service.get_liveness_status()
        
        assert response.alive is True
        assert response.timestamp is not None
        
    @pytest.mark.asyncio
    async def test_check_dependency_postgresql(self, health_service, mock_connection_manager):
        """Test check_dependency for PostgreSQL"""
        from app.database.connection_manager import ConnectionStatus
        
        # Mock PostgreSQL status
        mock_connection_manager.verify_postgres.return_value = ConnectionStatus(
            service="PostgreSQL",
            is_connected=True,
            response_time_ms=10.5,
            is_critical=True,
        )
        
        health_service.connection_manager = mock_connection_manager
        
        # Check dependency
        result = await health_service.check_dependency("PostgreSQL")
        
        # Verify result
        assert result.name == "PostgreSQL"
        assert result.is_connected is True
        assert result.response_time_ms == 10.5
        
    @pytest.mark.asyncio
    async def test_check_dependency_with_error(self, health_service, mock_connection_manager):
        """Test check_dependency includes error message when dependency fails"""
        from app.database.connection_manager import ConnectionStatus
        
        # Mock Neo4j with error
        mock_connection_manager.verify_neo4j.return_value = ConnectionStatus(
            service="Neo4j",
            is_connected=False,
            response_time_ms=0.0,
            error="Authentication failed",
            is_critical=False,
        )
        
        health_service.connection_manager = mock_connection_manager
        
        # Check dependency
        result = await health_service.check_dependency("Neo4j")
        
        # Verify result includes error
        assert result.name == "Neo4j"
        assert result.is_connected is False
        assert result.error == "Authentication failed"
        
    @pytest.mark.asyncio
    async def test_check_dependency_invalid_name(self, health_service):
        """Test check_dependency raises ValueError for unknown dependency"""
        with pytest.raises(ValueError, match="Unknown dependency"):
            await health_service.check_dependency("InvalidService")
