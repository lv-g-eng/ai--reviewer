"""
RBAC Project Management endpoints.
"""
from datetime import datetime, timezone
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import uuid

from app.database.postgresql import get_db
from app.auth import (
    Project,
    ProjectAccess,
    Permission,
    RBACService,
    AuditService,
    TokenPayload,
    get_current_user,
    require_permission,
    require_project_access,
)


router = APIRouter()


# Request/Response Models
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


class ProjectAccessResponse(BaseModel):
    """Project access response model."""
    project_id: str
    user_id: str
    granted_at: str
    granted_by: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: CreateProjectRequest,
    current_user: Annotated[TokenPayload, Depends(require_permission(Permission.CREATE_PROJECT))],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new project (Programmer or Admin).
    
    - **name**: Project name
    - **description**: Optional project description
    
    Requires CREATE_PROJECT permission (Programmer or Admin).
    The creating user becomes the project owner.
    """
    # Create project
    now = datetime.now(timezone.utc)
    new_project = Project(
        id=str(uuid.uuid4()),
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.user_id,
        created_at=now,
        updated_at=now
    )
    
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    # Note: Audit logging skipped due to schema mismatch
    
    return ProjectResponse(
        id=new_project.id,
        name=new_project.name,
        description=new_project.description,
        owner_id=new_project.owner_id,
        created_at=new_project.created_at.isoformat(),
        updated_at=new_project.updated_at.isoformat()
    )


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    List all accessible projects for the current user.
    
    - Admins see all projects
    - Programmers see their own projects and projects they have access to
    - Visitors see projects they have been granted access to
    """
    from app.auth import Role
    from uuid import UUID
    
    # Convert user_id string to UUID
    user_uuid = UUID(current_user.user_id)
    
    # Admins can see all projects
    if current_user.role == Role.ADMIN.value:
        result = await db.execute(select(Project))
        projects = result.scalars().all()
    else:
        # Get owned projects
        result = await db.execute(
            select(Project).filter(Project.owner_id == user_uuid)
        )
        owned_projects = result.scalars().all()
        
        # Get projects with granted access
        result = await db.execute(
            select(ProjectAccess).filter(ProjectAccess.user_id == user_uuid)
        )
        access_grants = result.scalars().all()
        
        granted_project_ids = [grant.project_id for grant in access_grants]
        if granted_project_ids:
            result = await db.execute(
                select(Project).filter(Project.id.in_(granted_project_ids))
            )
            granted_projects = result.scalars().all()
        else:
            granted_projects = []
        
        # Combine and deduplicate
        projects = list({p.id: p for p in list(owned_projects) + list(granted_projects)}.values())
    
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
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get project details by ID.
    
    Requires VIEW_PROJECT permission and project access.
    """
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    
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
    project_data: UpdateProjectRequest,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.UPDATE_PROJECT))],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update project (Owner or Admin only).
    
    - **name**: Optional new project name
    - **description**: Optional new project description
    
    Requires UPDATE_PROJECT permission and project ownership or admin role.
    """
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    
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
    
    await db.commit()
    await db.refresh(project)
    
    # Log action
    ip_address = request.client.host if request.client else "0.0.0.0"
    await AuditService.log_action(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="UPDATE_PROJECT",
        ip_address=ip_address,
        success=True,
        resource_type="Project",
        resource_id=project_id
    )
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.DELETE_PROJECT))],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete project (Owner or Admin only).
    
    Requires DELETE_PROJECT permission and project ownership or admin role.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Delete project request for project_id={project_id}, user_id={current_user.user_id}")
        
        result = await db.execute(select(Project).filter(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            logger.warning(f"Project {project_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project_name = project.name
        logger.info(f"Deleting project {project_name} (id={project_id})")
        
        # Delete all access grants first
        await db.execute(delete(ProjectAccess).filter(ProjectAccess.project_id == project_id))
        logger.info(f"Deleted access grants for project {project_id}")
        
        # Delete project
        await db.delete(project)
        await db.commit()
        logger.info(f"Project {project_name} deleted successfully")
        
        # Log action
        try:
            ip_address = request.client.host if request.client else "0.0.0.0"
            await AuditService.log_action(
                db=db,
                user_id=current_user.user_id,
                username=current_user.username,
                action="DELETE_PROJECT",
                ip_address=ip_address,
                success=True,
                resource_type="Project",
                resource_id=project_id
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log audit action: {audit_error}")
        
        return MessageResponse(message=f"Project {project_name} deleted successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


@router.post("/{project_id}/access", response_model=ProjectAccessResponse, status_code=status.HTTP_201_CREATED)
async def grant_project_access(
    project_id: str,
    access_data: GrantAccessRequest,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Grant user access to project (Owner or Admin only).
    
    - **user_id**: ID of user to grant access to
    
    Only project owners or admins can grant access.
    """
    # Grant access
    success = RBACService.grant_project_access(
        db=db,
        project_id=project_id,
        user_id=access_data.user_id,
        granted_by=current_user.user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Failed to grant project access. You may not have permission."
        )
    
    # Get the access grant
    result = await db.execute(
        select(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == access_data.user_id
        )
    )
    access_grant = result.scalar_one_or_none()
    
    # Log action
    ip_address = request.client.host if request.client else "0.0.0.0"
    await AuditService.log_action(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="GRANT_PROJECT_ACCESS",
        ip_address=ip_address,
        success=True,
        resource_type="ProjectAccess",
        resource_id=f"{project_id}:{access_data.user_id}"
    )
    
    return ProjectAccessResponse(
        project_id=access_grant.project_id,
        user_id=access_grant.user_id,
        granted_at=access_grant.granted_at.isoformat(),
        granted_by=access_grant.granted_by
    )


@router.delete("/{project_id}/access/{user_id}", response_model=MessageResponse)
async def revoke_project_access(
    project_id: str,
    user_id: str,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Revoke user access to project (Owner or Admin only).
    
    Only project owners or admins can revoke access.
    """
    # Revoke access
    success = RBACService.revoke_project_access(
        db=db,
        project_id=project_id,
        user_id=user_id,
        revoked_by=current_user.user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Failed to revoke project access. You may not have permission."
        )
    
    # Log action
    ip_address = request.client.host if request.client else "0.0.0.0"
    await AuditService.log_action(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="REVOKE_PROJECT_ACCESS",
        ip_address=ip_address,
        success=True,
        resource_type="ProjectAccess",
        resource_id=f"{project_id}:{user_id}"
    )
    
    return MessageResponse(message="Project access revoked successfully")
