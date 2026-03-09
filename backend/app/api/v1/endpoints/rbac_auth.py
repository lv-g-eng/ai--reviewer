"""
RBAC Authentication endpoints for enterprise authentication system.
"""
from datetime import datetime, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_db
from app.auth import (
    AuthService,
    AuthResult,
    TokenPayload,
    get_current_user,
)
from app.services.audit_service import AuditService


router = APIRouter()


# Request/Response Models
class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    success: bool
    token: Optional[str] = None
    user: Optional[dict] = None
    error: Optional[str] = None


class RefreshRequest(BaseModel):
    """Token refresh request model."""
    token: str


class RefreshResponse(BaseModel):
    """Token refresh response model."""
    token: Optional[str] = None
    error: Optional[str] = None


class LogoutResponse(BaseModel):
    """Logout response model."""
    success: bool
    message: str


class UserInfoResponse(BaseModel):
    """User info response model."""
    user_id: str
    username: str
    role: str
    iat: int
    exp: int


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT token on success, error message on failure.
    Uses generic error messages to prevent username enumeration.
    Logs authentication failures to audit log (Requirement 8.8).
    """
    # Get client IP and user agent
    ip_address = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "Unknown")
    
    # Attempt login
    result = await AuthService.login(
        db=db,
        username=credentials.username,
        password=credentials.password,
        ip_address=ip_address,
        device_info=user_agent
    )
    
    # Log authentication failure if login failed (Requirement 8.8)
    if not result.success:
        await AuditService.log_auth_failure(
            db=db,
            email=credentials.username,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=result.error or "Authentication failed",
            user_id=None
        )
    
    return LoginResponse(
        success=result.success,
        token=result.token,
        user=result.user,
        error=result.error
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user and invalidate current session.
    
    Requires valid JWT token in Authorization header.
    Adds token to Redis blacklist to prevent reuse.
    """
    from app.utils.jwt import revoke_token, decode_token
    from datetime import datetime, timezone
    
    # Extract token from Authorization header
    auth_header = request.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token not provided"
        )
    
    # Decode token to get JTI and expiration
    payload = decode_token(token)
    if payload and 'jti' in payload and 'exp' in payload:
        jti = payload['jti']
        exp_timestamp = payload['exp']
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # Add token to Redis blacklist
        await revoke_token(jti, expires_at)
    
    # Invalidate session in database
    success = AuthService.logout(db, current_user.user_id, token)
    
    if success:
        return LogoutResponse(success=True, message="Successfully logged out")
    else:
        return LogoutResponse(success=False, message="Logout failed")


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh JWT token if it's close to expiration.
    
    - **token**: Current JWT token
    
    Returns new token if refresh is successful, error message otherwise.
    Token must be within refresh window (10 minutes before expiration).
    Logs refresh failures to audit log (Requirement 8.8).
    """
    # Get client IP and user agent for audit logging
    ip_address = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "Unknown")
    
    new_token = AuthService.refresh_token(refresh_data.token)
    
    if new_token:
        return RefreshResponse(token=new_token)
    else:
        # Log token refresh failure (Requirement 8.8)
        # Try to extract user_id from token if possible
        from app.utils.jwt import decode_token
        import uuid
        
        payload = decode_token(refresh_data.token)
        user_id = None
        if payload and 'sub' in payload:
            try:
                user_id = uuid.UUID(payload['sub'])
            except (ValueError, TypeError):
                pass
        
        await AuditService.log_token_refresh_failure(
            db=db,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason="Token refresh failed. Token may be too fresh or too old."
        )
        
        return RefreshResponse(
            error="Token refresh failed. Token may be too fresh or too old."
        )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Get current authenticated user information from JWT token.
    
    Requires valid JWT token in Authorization header.
    """
    return UserInfoResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role,
        iat=current_user.iat,
        exp=current_user.exp
    )
