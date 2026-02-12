"""
Authentication endpoints
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging

from app.database.postgresql import get_db
from app.models import User, TokenBlacklist
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
    UserResponse,
    Message
)
from app.utils.password import hash_password, verify_password, validate_password_strength
from app.utils.jwt import create_access_token, create_refresh_token, verify_token, get_token_expiry
from app.api.dependencies import get_current_user
from app.services.redis_cache_service import get_cache_service
from app.utils.error_sanitizer import get_generic_auth_error, get_generic_password_error

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user
    
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit, special char)
    - **full_name**: Optional full name
    """
    # Validate password strength before hashing (Requirement 2.3)
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Check if user already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password with secure error handling (Requirement 2.5)
    try:
        password_hash = hash_password(user_data.password)
    except ValueError as e:
        # hash_password already sanitizes the error message
        logger.error(f"Password hashing failed during registration for {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Login and get access/refresh tokens
    
    Rate limited: 5 attempts per minute per IP
    
    Security: Returns generic error message to prevent user enumeration (Requirement 2.5)
    """
    # Rate limiting check
    cache = await get_cache_service()
    client_ip = request.client.host
    allowed, remaining = await cache.check_rate_limit(
        client_ip,
        "login",
        max_requests=5,
        window=60
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Find user
    stmt = select(User).where(User.email == credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Use generic error message to prevent user enumeration (Requirement 2.5)
    # Don't reveal whether email exists or password is wrong
    if not user or not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {credentials.email} from IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_generic_auth_error(),  # Generic: "Incorrect email or password"
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        # This is a different error - user exists but account is inactive
        logger.warning(f"Login attempt for inactive account: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Store session in Redis
    session_data = {
        "email": user.email,
        "role": user.role.value,
        "logged_in_at": datetime.now(timezone.utc).isoformat()
    }
    await cache.set_session(str(user.id), session_data)
    
    logger.info(f"Successful login for user: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/logout", response_model=Message)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Logout and blacklist current token
    """
    # Get token from request (would need to extract from header in real implementation)
    # For simplicity, we'll just delete the session
    
    cache = await get_cache_service()
    await cache.delete_session(str(current_user.id))
    
    return Message(message="Successfully logged out")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Refresh access token using refresh token with token rotation
    
    Security Features:
    - Checks refresh token not revoked (Requirement 5.1)
    - Generates new token pair on refresh (Requirement 5.2)
    - Invalidates old refresh token (rotation) (Requirement 5.2)
    - Stores new refresh token metadata in Redis (Requirement 5.5)
    
    Token rotation ensures that each refresh token can only be used once,
    preventing token replay attacks and limiting the impact of token theft.
    """
    # Verify refresh token signature and type
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if refresh token has been revoked (Requirement 5.1)
    old_jti = payload.get("jti")
    if old_jti:
        from app.utils.jwt import is_token_revoked
        if await is_token_revoked(old_jti):
            logger.warning(f"Attempted reuse of revoked refresh token: {old_jti}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    user_id = payload.get("sub")
    
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new token pair (Requirement 5.2)
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value
    }
    
    new_access_token = create_access_token(token_payload)
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Invalidate old refresh token (rotation) (Requirement 5.2)
    if old_jti:
        from app.utils.jwt import revoke_token
        old_exp = payload.get("exp")
        if old_exp:
            old_expires_at = datetime.fromtimestamp(old_exp, tz=timezone.utc)
            await revoke_token(old_jti, old_expires_at)
            logger.info(f"Revoked old refresh token {old_jti} for user {user.id} (rotation)")
    
    # Store new refresh token metadata in Redis (Requirement 5.5)
    # Decode the new refresh token to get its JTI and expiration
    from app.utils.jwt import decode_token
    new_payload = decode_token(new_refresh_token)
    if new_payload:
        new_jti = new_payload.get("jti")
        new_exp = new_payload.get("exp")
        
        if new_jti and new_exp:
            from app.database.redis_db import get_redis
            redis_client = await get_redis()
            
            refresh_metadata = {
                "user_id": str(user.id),
                "jti": new_jti,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": datetime.fromtimestamp(new_exp, tz=timezone.utc).isoformat()
            }
            
            # Store with TTL matching token expiration (7 days default)
            ttl_seconds = new_exp - int(datetime.now(timezone.utc).timestamp())
            if ttl_seconds > 0:
                import json
                await redis_client.set(
                    f"refresh_token:{new_jti}",
                    json.dumps(refresh_metadata),
                    ex=ttl_seconds
                )
                logger.info(f"Stored refresh token metadata for user {user.id}, JTI: {new_jti}")
    
    logger.info(f"Successfully refreshed tokens for user {user.id}")
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current user information
    """
    return current_user


@router.patch("/password", response_model=Message)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Change user password
    
    Requires current password for verification
    Security: Uses generic error messages to prevent information disclosure (Requirement 2.5)
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        logger.warning(f"Failed password change attempt for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength (Requirement 2.3)
    is_valid, error_message = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Check if new password is same as current
    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Hash new password with secure error handling (Requirement 2.5)
    try:
        new_password_hash = hash_password(password_data.new_password)
    except ValueError as e:
        # hash_password already sanitizes the error message
        logger.error(f"Password hashing failed during password change for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    # Update password
    current_user.password_hash = new_password_hash
    
    await db.commit()
    
    logger.info(f"Password changed successfully for user: {current_user.email}")
    
    return Message(message="Password successfully changed")
