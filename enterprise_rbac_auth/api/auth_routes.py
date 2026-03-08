from typing import Annotated
"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..services.auth_service import AuthService
from ..services.audit_service import AuditService
from ..middleware.auth_middleware import security, AuthMiddleware


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    """Token refresh request model."""
    token: str


class RefreshResponse(BaseModel):
    """Token refresh response model."""
    access_token: str
    token_type: str = "bearer"


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    credentials: LoginRequest,
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    Authenticate user and return JWT token.
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT token and user information.
    """
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Attempt login
    result = AuthService.login(
        db,
        credentials.username,
        credentials.password,
        ip_address=ip_address,
        device_info=user_agent
    )
    
    # Log the login attempt
    if result.success:
        AuditService.log_action(
            db,
            user_id=result.user["id"],
            username=result.user["username"],
            action="LOGIN",
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
    else:
        # Log failed login attempt (use username from request)
        AuditService.log_action(
            db,
            user_id="unknown",
            username=credentials.username,
            action="LOGIN_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message=result.error
        )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return LoginResponse(
        access_token=result.token,
        user=result.user
    )


@router.post("/logout")
async def logout(
    request: Request,
    credentials = Depends(security),
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    Logout user and invalidate session.
    
    Requires valid JWT token in Authorization header.
    """
    # Validate token
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Logout
    success = AuthService.logout(db, payload.user_id, credentials.credentials)
    
    # Log the logout
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="LOGOUT",
        ip_address=ip_address,
        user_agent=user_agent,
        success=success
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )
    
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    refresh_req: RefreshRequest,
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    Refresh JWT token.
    
    - **token**: Current JWT token
    
    Returns new JWT token with extended expiration.
    """
    new_token = AuthService.refresh_token(refresh_req.token)
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return RefreshResponse(access_token=new_token)


@router.get("/me")
async def get_current_user(
    request: Request,
    credentials = Depends(security),
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    # Get user from database
    from ..models import User
    user = db.query(User).filter(User.id == payload.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.value,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "is_active": user.is_active
    }
