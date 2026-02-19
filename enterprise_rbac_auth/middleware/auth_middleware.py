"""
Authorization middleware for FastAPI endpoints.
"""
from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps

from ..services.auth_service import AuthService, TokenPayload
from ..services.rbac_service import RBACService
from ..models import Role, Permission
from ..database import get_db


# HTTP Bearer token security scheme
security = HTTPBearer()


class AuthMiddleware:
    """Middleware for authentication and authorization."""
    
    @staticmethod
    async def authenticate_token(request: Request, credentials: HTTPAuthorizationCredentials) -> TokenPayload:
        """
        Middleware to validate JWT token from Authorization header.
        
        Args:
            request: FastAPI request object
            credentials: HTTP Bearer credentials
            
        Returns:
            TokenPayload if token is valid
            
        Raises:
            HTTPException: 401 if token is invalid or missing
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        # Validate token
        payload = AuthService.validate_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Store user info in request state for downstream handlers
        request.state.user = payload
        
        return payload
    
    @staticmethod
    def check_role(required_role: Role):
        """
        Middleware factory to check if user has required role.
        
        Args:
            required_role: Role required to access the endpoint
            
        Returns:
            Middleware function that checks role
        """
        async def role_checker(request: Request, credentials: HTTPAuthorizationCredentials) -> TokenPayload:
            # First authenticate the token
            payload = await AuthMiddleware.authenticate_token(request, credentials)
            
            # Check if user's role matches required role
            user_role = Role(payload.role)
            
            if user_role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This action requires {required_role.value} role"
                )
            
            return payload
        
        return role_checker
    
    @staticmethod
    def check_permission(required_permission: Permission):
        """
        Middleware factory to check if user has required permission.
        
        Args:
            required_permission: Permission required to access the endpoint
            
        Returns:
            Middleware function that checks permission
        """
        async def permission_checker(request: Request, credentials: HTTPAuthorizationCredentials) -> TokenPayload:
            # First authenticate the token
            payload = await AuthMiddleware.authenticate_token(request, credentials)
            
            # Check if user has the required permission
            db = next(get_db())
            try:
                has_perm = RBACService.has_permission(db, payload.user_id, required_permission)
                
                if not has_perm:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have permission to perform this action"
                    )
                
                return payload
            finally:
                db.close()
        
        return permission_checker
    
    @staticmethod
    def check_project_access(required_permission: Permission):
        """
        Middleware factory to check if user can access a specific project.
        
        Args:
            required_permission: Permission required for the project operation
            
        Returns:
            Middleware function that checks project access
        """
        async def project_access_checker(request: Request, credentials: HTTPAuthorizationCredentials) -> TokenPayload:
            # First authenticate the token
            payload = await AuthMiddleware.authenticate_token(request, credentials)
            
            # Extract project_id from path parameters
            project_id = request.path_params.get("project_id")
            
            if not project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project ID is required"
                )
            
            # Check if user can access the project
            db = next(get_db())
            try:
                can_access = RBACService.can_access_project(
                    db, 
                    payload.user_id, 
                    project_id, 
                    required_permission
                )
                
                if not can_access:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have access to this project"
                    )
                
                return payload
            finally:
                db.close()
        
        return project_access_checker


# Convenience functions for dependency injection
def get_current_user(credentials: HTTPAuthorizationCredentials = security) -> Callable:
    """Dependency to get current authenticated user."""
    async def _get_current_user(request: Request) -> TokenPayload:
        return await AuthMiddleware.authenticate_token(request, credentials)
    return _get_current_user


def require_role(role: Role) -> Callable:
    """Dependency to require specific role."""
    checker = AuthMiddleware.check_role(role)
    
    async def _require_role(request: Request, credentials: HTTPAuthorizationCredentials = security) -> TokenPayload:
        return await checker(request, credentials)
    
    return _require_role


def require_permission(permission: Permission) -> Callable:
    """Dependency to require specific permission."""
    checker = AuthMiddleware.check_permission(permission)
    
    async def _require_permission(request: Request, credentials: HTTPAuthorizationCredentials = security) -> TokenPayload:
        return await checker(request, credentials)
    
    return _require_permission


def require_project_access(permission: Permission) -> Callable:
    """Dependency to require project access with specific permission."""
    checker = AuthMiddleware.check_project_access(permission)
    
    async def _require_project_access(request: Request, credentials: HTTPAuthorizationCredentials = security) -> TokenPayload:
        return await checker(request, credentials)
    
    return _require_project_access
