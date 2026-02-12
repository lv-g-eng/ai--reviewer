"""
Optimized FastAPI Application with Resilient Startup

Enhanced main application with:
- Graceful degradation for missing services
- Intelligent service discovery
- Performance optimizations
- Comprehensive error handling
- Health check improvements
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.resilient_config import resilient_settings
from app.core.logging_config import setup_logging
from app.api.v1.router import api_router

# Setup logging early
setup_logging(level=resilient_settings.LOG_LEVEL, enable_json=True)
logger = logging.getLogger(__name__)


class OptimizedHealthService:
    """Optimized health service with graceful degradation"""
    
    def __init__(self):
        self.startup_time = time.time()
        self.service_status = {}
        self.degraded_mode = False
    
    async def initialize_services(self) -> Dict[str, Any]:
        """Initialize services with graceful degradation"""
        logger.info("🚀 Starting optimized service initialization...")
        
        # Check service availability
        availability = await resilient_settings.check_service_availability()
        self.service_status = availability
        
        # Determine if we can start in degraded mode
        can_start_degraded = resilient_settings.can_start_in_degraded_mode()
        degraded_info = resilient_settings.get_degraded_mode_info()
        
        logger.info(f"Service availability: {availability}")
        logger.info(f"Degraded mode info: {degraded_info}")
        
        initialization_results = {
            "services_checked": len(availability),
            "services_available": sum(availability.values()),
            "degraded_mode": not can_start_degraded,
            "can_start": True,  # Always allow startup with graceful degradation
            "details": {}
        }
        
        # Initialize available services
        if availability.get("postgresql", False):
            try:
                await self._initialize_postgresql()
                initialization_results["details"]["postgresql"] = "✅ Initialized"
            except Exception as e:
                logger.error(f"PostgreSQL initialization failed: {e}")
                initialization_results["details"]["postgresql"] = f"❌ Failed: {str(e)[:50]}"
        else:
            initialization_results["details"]["postgresql"] = "⚠️ Service unavailable"
        
        if availability.get("neo4j", False):
            try:
                await self._initialize_neo4j()
                initialization_results["details"]["neo4j"] = "✅ Initialized"
            except Exception as e:
                logger.warning(f"Neo4j initialization failed: {e}")
                initialization_results["details"]["neo4j"] = f"⚠️ Failed: {str(e)[:50]}"
        else:
            initialization_results["details"]["neo4j"] = "⚠️ Service unavailable"
        
        if availability.get("redis", False):
            try:
                await self._initialize_redis()
                initialization_results["details"]["redis"] = "✅ Initialized"
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                initialization_results["details"]["redis"] = f"⚠️ Failed: {str(e)[:50]}"
        else:
            initialization_results["details"]["redis"] = "⚠️ Service unavailable"
        
        # Set degraded mode flag
        self.degraded_mode = not can_start_degraded
        
        return initialization_results
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL with error handling"""
        try:
            from app.database.postgresql import init_postgres
            await init_postgres()
            logger.info("✅ PostgreSQL initialized successfully")
        except Exception as e:
            logger.error(f"PostgreSQL initialization failed: {e}")
            raise
    
    async def _initialize_neo4j(self):
        """Initialize Neo4j with error handling"""
        try:
            from app.database.neo4j_db import init_neo4j
            await init_neo4j()
            logger.info("✅ Neo4j initialized successfully")
        except Exception as e:
            logger.warning(f"Neo4j initialization failed: {e}")
            # Don't raise - Neo4j is optional
    
    async def _initialize_redis(self):
        """Initialize Redis with error handling"""
        try:
            from app.database.redis_db import init_redis
            await init_redis()
            logger.info("✅ Redis initialized successfully")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            # Don't raise - Redis is optional
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        current_time = time.time()
        uptime_seconds = current_time - self.startup_time
        
        # Re-check service availability
        current_availability = await resilient_settings.check_service_availability()
        
        # Determine overall health
        available_services = sum(current_availability.values())
        total_services = len(current_availability)
        
        if available_services == total_services:
            overall_status = "healthy"
        elif available_services >= len(resilient_settings.REQUIRED_SERVICES):
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "version": resilient_settings.VERSION,
            "environment": resilient_settings.ENVIRONMENT,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "uptime_seconds": round(uptime_seconds, 2),
            "degraded_mode": self.degraded_mode,
            "services": {
                name: {
                    "available": available,
                    "required": name in resilient_settings.REQUIRED_SERVICES,
                    "status": "connected" if available else "disconnected"
                }
                for name, available in current_availability.items()
            },
            "summary": {
                "total_services": total_services,
                "available_services": available_services,
                "required_services_available": sum(
                    1 for service in resilient_settings.REQUIRED_SERVICES
                    if current_availability.get(service, False)
                ),
                "optional_services_available": sum(
                    1 for service in resilient_settings.OPTIONAL_SERVICES
                    if current_availability.get(service, False)
                )
            }
        }


# Global health service
health_service = OptimizedHealthService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Optimized application lifespan with graceful degradation"""
    logger.info("🚀 Starting AI Code Review Platform (Optimized)")
    
    try:
        # Initialize services with graceful degradation
        init_results = await health_service.initialize_services()
        
        logger.info("📊 Initialization Summary:")
        for service, status in init_results["details"].items():
            logger.info(f"  {service}: {status}")
        
        if init_results["degraded_mode"]:
            logger.warning("⚠️ Starting in DEGRADED MODE - some features may be limited")
        else:
            logger.info("✅ All required services initialized successfully")
        
        # Log startup summary
        logger.info(f"🎯 Application ready:")
        logger.info(f"  - Services available: {init_results['services_available']}/{init_results['services_checked']}")
        logger.info(f"  - Degraded mode: {init_results['degraded_mode']}")
        logger.info(f"  - Health endpoint: /health")
        logger.info(f"  - API docs: /docs")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Still yield to allow the app to start in minimal mode
        yield
    
    finally:
        # Cleanup
        logger.info("🛑 Shutting down application...")
        try:
            # Graceful cleanup of connections
            from app.database.postgresql import close_postgres
            from app.database.neo4j_db import close_neo4j
            from app.database.redis_db import close_redis
            
            await asyncio.gather(
                close_postgres(),
                close_neo4j(),
                close_redis(),
                return_exceptions=True
            )
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Create FastAPI app with optimizations
app = FastAPI(
    title=resilient_settings.PROJECT_NAME,
    version=resilient_settings.VERSION,
    description="AI-powered code review and architecture analysis platform (Optimized)",
    openapi_url=f"{resilient_settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    # Performance optimizations
    docs_url="/docs" if resilient_settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if resilient_settings.ENVIRONMENT == "development" else None,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"] if resilient_settings.ENVIRONMENT == "development" else ["yourdomain.com"]
)

# CORS middleware with optimized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ] if resilient_settings.ENVIRONMENT == "development" else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Monitor request performance"""
    start_time = time.time()
    
    # Add correlation ID
    correlation_id = f"{int(start_time * 1000)}-{id(request)}"
    request.state.correlation_id = correlation_id
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        response.headers["X-Correlation-ID"] = correlation_id
        
        # Log slow requests
        if process_time > 1.0:  # Log requests taking more than 1 second
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.2f}s (correlation: {correlation_id})"
            )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"after {process_time:.2f}s - {str(e)} (correlation: {correlation_id})"
        )
        raise


# Global exception handler with detailed error information
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Enhanced global exception handler"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error(
        f"Unhandled exception in {request.method} {request.url.path}: "
        f"{type(exc).__name__}: {str(exc)} (correlation: {correlation_id})"
    )
    
    # Return appropriate error response based on environment
    if resilient_settings.ENVIRONMENT == "development":
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__,
                "correlation_id": correlation_id,
                "path": str(request.url.path)
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "correlation_id": correlation_id
            }
        )


# Include API router
app.include_router(api_router, prefix=resilient_settings.API_V1_STR)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    service_info = await health_service.get_health_status()
    
    return {
        "message": "AI Code Review Platform API (Optimized)",
        "version": resilient_settings.VERSION,
        "environment": resilient_settings.ENVIRONMENT,
        "status": service_info["status"],
        "degraded_mode": service_info["degraded_mode"],
        "uptime_seconds": service_info["uptime_seconds"],
        "endpoints": {
            "health": "/health",
            "docs": "/docs" if resilient_settings.ENVIRONMENT == "development" else None,
            "api": resilient_settings.API_V1_STR
        }
    }


# Optimized health check endpoint
@app.get("/health")
async def health_check():
    """
    Comprehensive health check with graceful degradation
    
    Returns:
        - 200: Healthy (all required services available)
        - 200: Degraded (some optional services unavailable)
        - 503: Unhealthy (required services unavailable)
    """
    try:
        health_status = await health_service.get_health_status()
        
        # Determine HTTP status code
        if health_status["status"] == "healthy":
            status_code = 200
        elif health_status["status"] == "degraded":
            status_code = 200  # Still operational in degraded mode
        else:
            status_code = 503
        
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": "Health check failed",
                "detail": str(e),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        )


# Readiness probe (Kubernetes)
@app.get("/health/ready")
async def readiness_check():
    """
    Readiness probe - returns 200 if app can serve requests
    """
    try:
        # Check if at least the basic app is ready
        health_status = await health_service.get_health_status()
        
        # Ready if we have at least one required service or degraded mode is allowed
        is_ready = (
            health_status["summary"]["required_services_available"] > 0 or
            resilient_settings.ALLOW_DEGRADED_MODE
        )
        
        if is_ready:
            return JSONResponse(
                status_code=200,
                content={
                    "ready": True,
                    "status": health_status["status"],
                    "degraded_mode": health_status["degraded_mode"],
                    "timestamp": health_status["timestamp"]
                }
            )
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "ready": False,
                    "reason": "No required services available",
                    "timestamp": health_status["timestamp"]
                }
            )
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        )


# Liveness probe (Kubernetes)
@app.get("/health/live")
async def liveness_check():
    """
    Liveness probe - returns 200 if app process is running
    """
    return JSONResponse(
        status_code=200,
        content={
            "alive": True,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "uptime_seconds": round(time.time() - health_service.startup_time, 2)
        }
    )


# Service status endpoint
@app.get("/status")
async def service_status():
    """
    Detailed service status information
    """
    try:
        health_status = await health_service.get_health_status()
        degraded_info = resilient_settings.get_degraded_mode_info()
        
        return {
            "application": {
                "name": resilient_settings.PROJECT_NAME,
                "version": resilient_settings.VERSION,
                "environment": resilient_settings.ENVIRONMENT,
                "status": health_status["status"],
                "uptime_seconds": health_status["uptime_seconds"]
            },
            "services": health_status["services"],
            "degraded_mode": degraded_info,
            "configuration": {
                "allow_degraded_mode": resilient_settings.ALLOW_DEGRADED_MODE,
                "required_services": resilient_settings.REQUIRED_SERVICES,
                "optional_services": resilient_settings.OPTIONAL_SERVICES,
                "service_discovery_enabled": resilient_settings.ENABLE_SERVICE_DISCOVERY
            }
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get host from environment, default to localhost for security
    # Use 0.0.0.0 only in production with proper network security
    host = os.getenv("UVICORN_HOST", "127.0.0.1")
    
    # Run with optimized settings
    uvicorn.run(
        "app.main_optimized:app",
        host=host,
        port=8000,
        reload=resilient_settings.ENVIRONMENT == "development",
        log_level=resilient_settings.LOG_LEVEL.lower(),
        access_log=True,
        # Performance optimizations
        loop="uvloop" if resilient_settings.ENVIRONMENT == "production" else "asyncio",
        http="httptools" if resilient_settings.ENVIRONMENT == "production" else "h11",
        workers=1,  # Single worker for development
        backlog=2048,
        timeout_keep_alive=5,
        timeout_graceful_shutdown=30
    )