"""
Health Check Service

Provides comprehensive health status of the application and all dependencies.
Implements Kubernetes-style probes (liveness, readiness).

Validates Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6
"""

import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

from app.core.config import settings
from app.database.connection_manager import get_connection_manager

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class DatabaseHealth:
    """Health status of a database"""
    name: str
    is_connected: bool
    response_time_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class ServiceHealth:
    """Health status of a service"""
    name: str
    is_available: bool
    error: Optional[str] = None


@dataclass
class HealthCheckResponse:
    """Response from health check endpoint"""
    status: str  # "healthy", "degraded", "unhealthy"
    version: str
    environment: str
    timestamp: str
    databases: Dict[str, DatabaseHealth]
    services: Dict[str, ServiceHealth]
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "status": self.status,
            "version": self.version,
            "environment": self.environment,
            "timestamp": self.timestamp,
            "databases": {
                name: asdict(db) for name, db in self.databases.items()
            },
            "services": {
                name: asdict(svc) for name, svc in self.services.items()
            },
        }


@dataclass
class ReadinessCheckResponse:
    """Response from readiness check endpoint"""
    ready: bool
    reason: str
    timestamp: str
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "ready": self.ready,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


@dataclass
class LivenessCheckResponse:
    """Response from liveness check endpoint"""
    alive: bool
    timestamp: str
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "alive": self.alive,
            "timestamp": self.timestamp,
        }


class HealthService:
    """
    Service for checking application and dependency health.
    
    Provides:
    - Overall health status (healthy, degraded, unhealthy)
    - Readiness probe (all required dependencies ready)
    - Liveness probe (process running)
    - Detailed database and service status
    
    Validates Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6
    """
    
    def __init__(self):
        """Initialize health service"""
        self.connection_manager = get_connection_manager()
    
    async def get_health_status(self) -> HealthCheckResponse:
        """
        Get overall health status of the application.
        Enhanced to include response times for each dependency.
        
        Returns:
            HealthCheckResponse with status and details including response times
            
        Validates Requirements: 12.1, 12.2, 12.3, 12.4, 4.1, 4.4, 4.5
        """
        logger.info("Checking application health...")
        
        # Check database connections (includes response times)
        db_status = await self.connection_manager.verify_all()
        
        databases = {}
        all_critical_connected = True
        any_connected = False
        
        for service_name, status in db_status.items():
            # Include response times and error messages for each dependency
            databases[service_name] = DatabaseHealth(
                name=service_name,
                is_connected=status.is_connected,
                response_time_ms=status.response_time_ms,  # Response time included
                error=status.error  # Error message included when dependency fails
            )
            
            if status.is_connected:
                any_connected = True
            elif status.is_critical:
                all_critical_connected = False
        
        # Check services
        services = {}
        
        # Check Celery if enabled
        if settings.is_celery_enabled():
            celery_available = await self._check_celery_health()
            services["Celery"] = ServiceHealth(
                name="Celery",
                is_available=celery_available,
                error=None if celery_available else "Celery broker unavailable"
            )
        
        # Check LLM service if enabled
        if settings.LLM_ENABLED:
            llm_available = await self._check_llm_health()
            services["LLM"] = ServiceHealth(
                name="LLM",
                is_available=llm_available,
                error=None if llm_available else "LLM service unavailable"
            )
        
        # Determine overall health status
        if all_critical_connected and any_connected:
            health_status = HealthStatus.HEALTHY
        elif any_connected:
            health_status = HealthStatus.DEGRADED
        else:
            health_status = HealthStatus.UNHEALTHY
        
        response = HealthCheckResponse(
            status=health_status.value,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT,
            timestamp=datetime.utcnow().isoformat(),
            databases=databases,
            services=services,
        )
        
        logger.info(f"Health check: {health_status.value}")
        return response
    
    async def get_readiness_status(self) -> ReadinessCheckResponse:
        """
        Get readiness status (Kubernetes readiness probe).
        Enhanced to check PostgreSQL and migrations.
        
        Returns 200 only if all required dependencies are ready:
        - PostgreSQL connected
        - Migrations applied
        
        Returns:
            ReadinessCheckResponse with ready status
            
        Validates Requirements: 12.5, 4.2
        """
        logger.info("Checking readiness...")
        
        # Check PostgreSQL connection
        postgres_status = await self.connection_manager.verify_postgres()
        
        if not postgres_status.is_connected:
            error_msg = postgres_status.error or "PostgreSQL not connected"
            response = ReadinessCheckResponse(
                ready=False,
                reason=f"PostgreSQL not connected: {error_msg}",
                timestamp=datetime.utcnow().isoformat(),
            )
            logger.warning(f"Not ready: PostgreSQL not connected - {error_msg}")
            return response
        
        # Check migrations (if available)
        try:
            from app.database.migration_manager import get_migration_manager
            migration_manager = get_migration_manager()
            migration_status = await migration_manager.get_migration_status()
            
            if migration_status.pending_count > 0:
                response = ReadinessCheckResponse(
                    ready=False,
                    reason=f"{migration_status.pending_count} pending migrations",
                    timestamp=datetime.utcnow().isoformat(),
                )
                logger.warning(f"Not ready: {migration_status.pending_count} pending migrations")
                return response
        except Exception as e:
            logger.warning(f"Could not check migration status: {e}")
            # Don't fail readiness if we can't check migrations
        
        response = ReadinessCheckResponse(
            ready=True,
            reason="All required dependencies ready",
            timestamp=datetime.utcnow().isoformat(),
        )
        logger.info("Ready")
        return response
    
    async def get_liveness_status(self) -> LivenessCheckResponse:
        """
        Get liveness status (Kubernetes liveness probe).
        
        Returns 200 if the application process is running.
        This is a simple check that doesn't verify dependencies.
        
        Returns:
            LivenessCheckResponse with alive status
            
        Validates Requirements: 12.6, 4.3
        """
        logger.info("Checking liveness...")
        
        response = LivenessCheckResponse(
            alive=True,
            timestamp=datetime.utcnow().isoformat(),
        )
        logger.info("Alive")
        return response
    
    async def check_dependency(self, name: str) -> DatabaseHealth:
        """
        Check individual dependency health.
        
        Args:
            name: Name of the dependency to check (PostgreSQL, Neo4j, Redis, Celery, LLM)
            
        Returns:
            DatabaseHealth or ServiceHealth with dependency status
            
        Raises:
            ValueError: If dependency name is not recognized
            
        Validates Requirements: 4.1, 4.4, 4.5
        """
        logger.info(f"Checking dependency: {name}")
        
        # Check database dependencies
        if name in ["PostgreSQL", "Neo4j", "Redis"]:
            if name == "PostgreSQL":
                status = await self.connection_manager.verify_postgres()
            elif name == "Neo4j":
                status = await self.connection_manager.verify_neo4j()
            elif name == "Redis":
                status = await self.connection_manager.verify_redis()
            
            return DatabaseHealth(
                name=name,
                is_connected=status.is_connected,
                response_time_ms=status.response_time_ms,
                error=status.error
            )
        
        # Check service dependencies
        elif name == "Celery":
            if not settings.is_celery_enabled():
                return DatabaseHealth(
                    name=name,
                    is_connected=False,
                    response_time_ms=0.0,
                    error="Celery is not enabled"
                )
            
            celery_available = await self._check_celery_health()
            return DatabaseHealth(
                name=name,
                is_connected=celery_available,
                response_time_ms=0.0,
                error=None if celery_available else "Celery broker unavailable"
            )
        
        elif name == "LLM":
            if not settings.LLM_ENABLED:
                return DatabaseHealth(
                    name=name,
                    is_connected=False,
                    response_time_ms=0.0,
                    error="LLM service is not enabled"
                )
            
            llm_available = await self._check_llm_health()
            return DatabaseHealth(
                name=name,
                is_connected=llm_available,
                response_time_ms=0.0,
                error=None if llm_available else "LLM service unavailable"
            )
        
        else:
            raise ValueError(f"Unknown dependency: {name}")
    
    async def _check_celery_health(self) -> bool:
        """
        Check if Celery is healthy.
        
        Returns:
            True if Celery is available, False otherwise
        """
        try:
            from app.celery_config import celery_app
            
            # Try to ping the Celery broker
            result = celery_app.control.inspect().ping()
            return result is not None and len(result) > 0
        except Exception as e:
            logger.warning(f"Celery health check failed: {e}")
            return False
    
    async def _check_llm_health(self) -> bool:
        """
        Check if LLM service is healthy.
        
        Returns:
            True if LLM service is available, False otherwise
        """
        try:
            from app.services.llm_service import llm_service
            
            # Check if LLM service is initialized
            return llm_service.is_initialized()
        except Exception as e:
            logger.warning(f"LLM health check failed: {e}")
            return False


# Global health service instance
_health_service: Optional[HealthService] = None


def get_health_service() -> HealthService:
    """Get or create health service instance"""
    global _health_service
    if _health_service is None:
        _health_service = HealthService()
    return _health_service
