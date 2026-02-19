"""
Project management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

from ..database import get_db_session
from ..models import User, Project, ProjectAccess, Role, Permission
from ..services.rbac_service import RBACService
from ..services.audit_service import AuditService
from ..middleware.auth_middleware import security, AuthMiddleware


router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    """Create project request model."""
    name: str
    description: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    """Update project request model."""
    name: Optional[str] = None
    description: Optional[str] = None


class GrantAccessRequest(BaseModel):
    """Grant project access request model."""
    user_id: str


class ProjectResponse(BaseModel):
    """Project response model."""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: str
    updated_at: str


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: Request,
    project_data: CreateProjectRequest,
    credentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Create a new project (programmer or admin).
    
    - **name**: Project name
    - **description**: Optional project description
    """
    # Authenticate and check permission
    payload = await AuthMiddleware.check_permission(Permission.CREATE_PROJECT)(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Create project
    new_project = Project(
        id=str(uuid.uuid4()),
        name=project_data.name,
        description=project_data.description,
        owner_id=payload.user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Log the action
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="CREATE_PROJECT",
        resource_type="project",
        resource_id=new_project.id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    return ProjectResponse(
        id=new_project.id,
        name=new_project.name,
        description=new_project.description,
        owner_id=new_project.owner_id,
        created_at=new_project.created_at.isoformat(),
        updated_at=new_project.updated_at.isoformat()
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    request: Request,
    credentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    List all accessible projects.
    
    - Admins see all projects
    - Other users see projects they own or have access to
    """
    # Authenticate
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    # Get user
    user = db.query(User).filter(User.id == payload.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Admins see all projects
    if user.role == Role.ADMIN:
        projects = db.query(Project).all()
    else:
        # Get projects owned by user
        owned_projects = db.query(Project).filter(Project.owner_id == payload.user_id).all()
        
        # Get projects user has access to
        access_grants = db.query(ProjectAccess).filter(ProjectAccess.user_id == payload.user_id).all()
        accessible_project_ids = [grant.project_id for grant in access_grants]
        accessible_projects = db.query(Project).filter(Project.id.in_(accessible_project_ids)).all() if accessible_project_ids else []
        
        # Combine and deduplicate
        projects_dict = {p.id: p for p in owned_projects}
        for p in accessible_projects:
            if p.id not in projects_dict:
                projects_dict[p.id] = p
        
        projects = list(projects_dict.values())
    
    return [
        ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            owner_id=project.owner_id,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat()
        )
        for project in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    request: Request,
    credentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Get project details.
    
    Requires project access.
    """
    # Authenticate
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    # Check project access
    can_access = RBACService.can_access_project(db, payload.user_id, project_id, Permission.VIEW_PROJECT)
    
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project"
        )
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: Request,
    project_data: UpdateProjectRequest,
    credentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Update project (owner or admin).
    
    - **name**: Optional new project name
    - **description**: Optional new project description
    """
    # Authenticate
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Check project access with modify permission
    can_access = RBACService.can_access_project(db, payload.user_id, project_id, Permission.MODIFY_PROJECT)
    
    if not can_access:
        AuditService.log_action(
            db,
            user_id=payload.user_id,
            username=payload.username,
            action="UPDATE_PROJECT_FAILED",
            resource_type="project",
            resource_id=project_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message="Access denied"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this project"
        )
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    
    project.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(project)
    
    # Log the action
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="UPDATE_PROJECT",
        resource_type="project",
        resource_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    request: Request,
    credentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Delete project (owner or admin).
    """
    # Authenticate
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Check project access with delete permission
    can_access = RBACService.can_access_project(db, payload.user_id, project_id, Permission.DELETE_PROJECT)
    
    if not can_access:
        AuditService.log_action(
            db,
            user_id=payload.user_id,
            username=payload.username,
            action="DELETE_PROJECT_FAILED",
            resource_type="project",
            resource_id=project_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message="Access denied"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this project"
        )
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Delete project (cascade will delete access grants)
    db.delete(project)
    db.commit()
    
    # Log the action
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="DELETE_PROJECT",
        resource_type="project",
        resource_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    return None


@router.post("/{project_id}/access", status_code=status.HTTP_201_CREATED)
async def grant_project_access(
    project_id: str,
    request: Request,
    access_data: GrantAccessRequest,
    credentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Grant user access to project (owner or admin).
    
    - **user_id**: ID of user to grant access to
    """
    # Authenticate
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Check if user can grant access (must be owner or admin)
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    user = db.query(User).filter(User.id == payload.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only owner or admin can grant access
    if project.owner_id != payload.user_id and user.role != Role.ADMIN:
        AuditService.log_action(
            db,
            user_id=payload.user_id,
            username=payload.username,
            action="GRANT_PROJECT_ACCESS_FAILED",
            resource_type="project",
            resource_id=project_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message="Access denied"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner or admin can grant access"
        )
    
    # Grant access
    success = RBACService.grant_project_access(db, project_id, access_data.user_id, payload.user_id)
    
    if not success:
        AuditService.log_action(
            db,
            user_id=payload.user_id,
            username=payload.username,
            action="GRANT_PROJECT_ACCESS_FAILED",
            resource_type="project",
            resource_id=project_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message="Failed to grant access"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant project access"
        )
    
    # Log the action
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="GRANT_PROJECT_ACCESS",
        resource_type="project",
        resource_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    return {"message": "Access granted successfully"}


@router.delete("/{project_id}/access/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_project_access(
    project_id: str,
    user_id: str,
    request: Request,
    credentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Revoke user access to project (owner or admin).
    """
    # Authenticate
    payload = await AuthMiddleware.authenticate_token(request, credentials)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Check if user can revoke access (must be owner or admin)
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    user = db.query(User).filter(User.id == payload.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only owner or admin can revoke access
    if project.owner_id != payload.user_id and user.role != Role.ADMIN:
        AuditService.log_action(
            db,
            user_id=payload.user_id,
            username=payload.username,
            action="REVOKE_PROJECT_ACCESS_FAILED",
            resource_type="project",
            resource_id=project_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message="Access denied"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner or admin can revoke access"
        )
    
    # Revoke access
    success = RBACService.revoke_project_access(db, project_id, user_id, payload.user_id)
    
    if not success:
        AuditService.log_action(
            db,
            user_id=payload.user_id,
            username=payload.username,
            action="REVOKE_PROJECT_ACCESS_FAILED",
            resource_type="project",
            resource_id=project_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message="Failed to revoke access"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke project access"
        )
    
    # Log the action
    AuditService.log_action(
        db,
        user_id=payload.user_id,
        username=payload.username,
        action="REVOKE_PROJECT_ACCESS",
        resource_type="project",
        resource_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    return None
