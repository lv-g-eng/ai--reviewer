"""
Main FastAPI application entry point
"""
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging_config import setup_logging, log_request, log_exception
from app.api.v1.router import api_router
from app.database.postgresql import init_postgres, close_postgres
from app.database.neo4j_db import init_neo4j, close_neo4j
from app.database.redis_db import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging(level=settings.LOG_LEVEL, enable_json=True)
    
    # Run comprehensive startup validation (Requirement 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7)
    from app.core.startup_validator import run_startup_validation
    validation_result = await run_startup_validation()
    
    # Initialize databases (optional - will continue if they fail)
    db_status = {}
    postgres_available = False
    
    try:
        await init_postgres()
        db_status["PostgreSQL"] = {"is_connected": True, "response_time_ms": 0}
        postgres_available = True
    except Exception as e:
        db_status["PostgreSQL"] = {"is_connected": False, "error": str(e)[:50]}
        print(f"⚠️  PostgreSQL not available: {e}")
    
    try:
        await init_neo4j()
        db_status["Neo4j"] = {"is_connected": True, "response_time_ms": 0}
    except Exception as e:
        db_status["Neo4j"] = {"is_connected": False, "error": str(e)[:50]}
        print(f"⚠️  Neo4j not available: {e}")
    
    try:
        await init_redis()
        db_status["Redis"] = {"is_connected": True, "response_time_ms": 0}
    except Exception as e:
        db_status["Redis"] = {"is_connected": False, "error": str(e)[:50]}
        print(f"⚠️  Redis not available: {e}")
    
    # Apply database migrations if PostgreSQL is available
    if postgres_available:
        try:
            from app.database.migration_manager import get_migration_manager
            migration_manager = get_migration_manager()
            
            print("🔄 Checking for pending migrations...")
            migration_status = await migration_manager.get_migration_status()
            print(f"📊 {migration_status}")
            
            if migration_status.pending_count > 0:
                print(f"⏳ Applying {migration_status.pending_count} pending migration(s)...")
                migration_status = await migration_manager.apply_pending_migrations()
                print(f"✅ {migration_status}")
                
                if migration_status.errors:
                    print("❌ Migration errors:")
                    for error in migration_status.errors:
                        print(f"   - {error}")
                    print("⚠️  Some migrations failed, but continuing startup")
            else:
                print("✅ Database is up to date")
        except Exception as e:
            print(f"⚠️  Error during migration: {e}")
            import traceback
            traceback.print_exc()
    
    # Initialize LLM service if enabled
    if settings.LLM_ENABLED:
        from app.services.llm_service import llm_service
        await llm_service.initialize()
        print("✅ LLM service initialized")
    
    # Log startup summary (Requirement 11.1, 11.2, 11.3, 11.4, 11.5, 11.6)
    from app.core.logging_config import log_startup_summary, log_database_status
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Log database status with masking
    log_database_status(db_status, logger)
    
    features_enabled = {
        "GitHub Integration": settings.is_github_integration_enabled(),
        "OpenAI": settings.is_openai_enabled(),
        "Anthropic": settings.is_anthropic_enabled(),
        "Ollama Local LLM": settings.is_ollama_enabled(),
        "Celery": settings.is_celery_enabled(),
    }
    
    security_warnings = settings.validate_security_settings()
    
    log_startup_summary(
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        config_file=".env",
        database_status=db_status,
        features_enabled=features_enabled,
        security_warnings=security_warnings if security_warnings else None
    )
    
    yield
    
    # Shutdown (gracefully handle if connections weren't established)
    try:
        await close_postgres()
    except Exception:
        pass
    
    try:
        await close_neo4j()
    except Exception:
        pass
    
    try:
        await close_redis()
    except Exception:
        pass
    
    print("✅ Shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered code review and architecture analysis platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request Logging Middleware
app.middleware("http")(log_request)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_exception(exc, {"path": request.url.path, "method": request.method})
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Code Review Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint - returns overall health status.
    
    Returns 200 with health status (healthy, degraded, unhealthy).
    Includes database and service status information.
    
    Validates Requirements: 1.1, 1.2, 1.4, 1.5, 1.6
    """
    from app.services.health_service import get_health_service
    
    health_service = get_health_service()
    health_status = await health_service.get_health_status()
    
    # Return appropriate status code based on health
    status_code = 200 if health_status.status == "healthy" else 503
    
    response_content = health_status.to_dict()
    if status_code == 503:
        # Add basic diagnosis if not healthy
        response_content["detail"] = "One or more critical dependencies are unhealthy"
    
    return JSONResponse(
        status_code=status_code,
        content=response_content
    )


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness probe endpoint - Kubernetes readiness probe.
    
    Returns 200 only if all required dependencies are ready:
    - PostgreSQL connected
    - Migrations applied
    
    Validates Requirements: 1.1, 1.2, 2.1, 2.4, 2.5
    """
    from app.services.health_service import get_health_service
    
    health_service = get_health_service()
    readiness_status = await health_service.get_readiness_status()
    
    status_code = 200 if readiness_status.ready else 503
    
    return JSONResponse(
        status_code=status_code,
        content=readiness_status.to_dict()
    )


@app.get("/health/live")
async def liveness_check():
    """
    Liveness probe endpoint - Kubernetes liveness probe.
    
    Returns 200 if the application process is running.
    This is a simple check that doesn't verify dependencies.
    
    Validates Requirements: 1.1, 1.2, 2.5
    """
    from app.services.health_service import get_health_service
    
    health_service = get_health_service()
    liveness_status = await health_service.get_liveness_status()
    
    return JSONResponse(
        status_code=200,
        content=liveness_status.to_dict()
    )
