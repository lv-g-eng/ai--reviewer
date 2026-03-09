"""
User management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional, Annotated
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..models import User, Role
from ..services.auth_service import AuthService
from ..services.rbac_service import RBACService
from ..services.audit_service import AuditService
from ..middleware.auth_middleware import security, AuthMiddleware
from ..utils import get_client_ip


router = APIRouter(prefix="/api/v1/users", tags=["users"])


class CreateUserRequest(BaseModel):
    """Create user request model."""
    username: str
    password: str
    role: str


class UpdateRoleRequest(BaseModel):
    """Update user role request model."""
    role: str


class UserResponse(BaseModel):
    """User response model."""
    id: str
    username: str
    role: str
    created_at: str
    last_login: Optional[str]
    is_active: bool


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_data: CreateUserRequest,
    credentials = Depends(security),
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    Create a new user (admin only).
    
    - **username**: User's username
    - **password**: User's password
    - **role**: User's role (ADMIN, PROGRAMMER, VISITOR)
    """
    # Authenticate and check admin role
    payload = await AuthMiddleware.check_role(Role.ADMIN)(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Validate role
    if not RBACService.validate_role(user_data.role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {user_data.role}"
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        AuditService.log_action(
            db,
            user_id=payload.user_id,
            username=payload.username,
            action="CREATE_USER_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message="Username already exists"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user
    import uuid
    from datetime import datetime, timezone
    
    new_user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        password_hash=AuthService.hash_password(user_data.password),
        role=Role(user_data.role),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log the action
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="CREATE_USER",
        resource_type="user",
        resource_id=new_user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role.value,
        created_at=new_user.created_at.isoformat(),
        last_login=new_user.last_login.isoformat() if new_user.last_login else None,
        is_active=new_user.is_active
    )


@router.get("", response_model=List[UserResponse])
async def list_users(
    request: Request,
    credentials = Depends(security),
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    List all users (admin only).
    """
    # Authenticate and check admin role
    payload = await AuthMiddleware.check_role(Role.ADMIN)(request, credentials)
    
    # Get all users
    users = db.query(User).all()
    
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            role=user.role.value,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None,
            is_active=user.is_active
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    request: Request,
    credentials = Depends(security),
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    Get user details.
    
    Users can view their own details. Admins can view any user.
    """
    # Authenticate
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    # Check if user is viewing their own details or is an admin
    if payload.user_id != user_id and payload.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own user details"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role.value,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None,
        is_active=user.is_active
    )


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    request: Request,
    role_data: UpdateRoleRequest,
    credentials = Depends(security),
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    Update user role (admin only).
    
    - **role**: New role (ADMIN, PROGRAMMER, VISITOR)
    """
    # Authenticate and check admin role
    payload = await AuthMiddleware.check_role(Role.ADMIN)(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Validate role
    if not RBACService.validate_role(role_data.role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {role_data.role}"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Assign new role
    success = RBACService.assign_role(db, user_id, Role(role_data.role), payload.user_id)
    
    if not success:
        AuditService.log_action(
            db,
            user_id=payload.user_id,
            username=payload.username,
            action="UPDATE_USER_ROLE_FAILED",
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message="Failed to update user role"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )
    
    # Log the action
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="UPDATE_USER_ROLE",
        resource_type="user",
        resource_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    # Refresh user data
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role.value,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None,
        is_active=user.is_active
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    request: Request,
    credentials = Depends(security),
    db: Annotated[Session, Depends(get_db_session)]
):
    """
    Delete a user (admin only).
    
    Cannot delete the last admin user.
    """
    # Authenticate and check admin role
    payload = await AuthMiddleware.check_role(Role.ADMIN)(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if this is the last admin
    if user.role == Role.ADMIN:
        admin_count = db.query(User).filter(User.role == Role.ADMIN).count()
        if admin_count <= 1:
            AuditService.log_action(
                db,
                user_id=payload.user_id,
                username=payload.username,
                action="DELETE_USER_FAILED",
                resource_type="user",
                resource_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                error_message="Cannot delete the last admin user"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin user"
            )
    
    # Delete user
    db.delete(user)
    db.commit()
    
    # Log the action
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="DELETE_USER",
        resource_type="user",
        resource_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    return None
