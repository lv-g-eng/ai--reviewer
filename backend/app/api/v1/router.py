"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    health, 
    database, 
    auth, 
    github, 
    pull_request, 
    analyze, 
    llm, 
    libraries, 
    code_review_webhook,
    rbac_auth,
    rbac_users,
    rbac_projects,
    rbac_audit,
)
from app.api.v1 import repositories

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(database.router, prefix="/database", tags=["Database"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(github.router, prefix="/github", tags=["GitHub Integration"])
api_router.include_router(code_review_webhook.router, prefix="/code-review", tags=["Code Review"])
api_router.include_router(pull_request.router, prefix="/analysis", tags=["PR Analysis"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["Architecture Analysis"])
api_router.include_router(llm.router, prefix="/llm", tags=["Local LLM"])
api_router.include_router(libraries.router, prefix="/libraries", tags=["Library Management"])
api_router.include_router(repositories.router, tags=["Repository Management"])

# RBAC Authentication endpoints
api_router.include_router(rbac_auth.router, prefix="/rbac/auth", tags=["RBAC Authentication"])
api_router.include_router(rbac_users.router, prefix="/rbac/users", tags=["RBAC User Management"])
api_router.include_router(rbac_projects.router, prefix="/rbac/projects", tags=["RBAC Project Management"])
api_router.include_router(rbac_audit.router, prefix="/rbac/audit", tags=["RBAC Audit Logs"])
