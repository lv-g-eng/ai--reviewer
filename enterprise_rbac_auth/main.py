"""
Main application entry point for Enterprise RBAC Authentication System.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

# Import API routers
from api.auth_routes import router as auth_router
from api.user_routes import router as user_router
from api.project_routes import router as project_router
from api.audit_routes import router as audit_router

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(audit_router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Get host from environment or use localhost for security
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(
        "main:app",
        host=host,
        port=int(os.environ.get("PORT", "8000")),
        reload=settings.debug
    )
