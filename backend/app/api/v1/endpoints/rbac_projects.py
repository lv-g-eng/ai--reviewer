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
import logging

from app.database.postgresql import get_db
from app.auth import (
    Permission,
    RBACService,
    AuditService,
    TokenPayload,
    get_current_user,
    require_permission,
    require_project_access,
)
from app.models import GitHubConnectionType, SSHKey, Project, ProjectAccess


logger = logging.getLogger(__name__)
router = APIRouter()
_log_audit_action = AuditService.log_action


# Request/Response Models
class CreateProjectRequest(BaseModel):
    """Create project request model with GitHub connection options."""
    name: str
    description: Optional[str] = None
    github_repo_url: Optional[str] = None
    github_connection_type: str = "https"  # "https", "ssh", "cli"
    github_ssh_key_id: Optional[str] = None
    github_cli_token: Optional[str] = None
    language: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    """Update project request model."""
    name: Optional[str] = None
    description: Optional[str] = None


class GrantAccessRequest(BaseModel):
    """Grant project access request model."""
    user_id: str


class ProjectResponse(BaseModel):
    """Project response model with GitHub connection details."""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    github_repo_url: Optional[str]
    github_connection_type: str
    github_ssh_key_id: Optional[str]
    language: Optional[str]
    is_active: bool
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


async def _validate_github_connection(project_data: CreateProjectRequest, user_id: str, db: AsyncSession):
    """Validate GitHub connection configuration."""
    if not project_data.github_repo_url:
        return  # No GitHub connection to validate

    connection_type = project_data.github_connection_type.lower()

    if connection_type == "ssh":
        if not project_data.github_ssh_key_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="github_ssh_key_id is required for SSH connections"
            )

        # Validate SSH key exists and belongs to user
        result = await db.execute(
            select(SSHKey).filter(
                SSHKey.id == project_data.github_ssh_key_id,
                SSHKey.user_id == user_id,
                SSHKey.is_active == True
            )
        )
        ssh_key = result.scalar_one_or_none()
        if not ssh_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SSH key not found or not accessible"
            )

    elif connection_type == "cli":
        if not project_data.github_cli_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="github_cli_token is required for CLI connections"
            )
        # TODO: Validate GitHub CLI token format and potentially test connection

    elif connection_type == "https":
        # For HTTPS, we could validate the URL format
        if not project_data.github_repo_url.startswith(("https://", "http://")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub repository URL must start with https:// or http:// for HTTPS connections"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported connection type: {connection_type}"
        )


# Async wrappers for RBACService methods
async def _grant_project_access(db: AsyncSession, project_id: str, user_id: str, granted_by: str) -> bool:
    """Async wrapper for RBACService.grant_project_access"""
    try:
        # Use run_in_executor to call sync RBAC method
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def sync_grant():
            sync_session = db.sync_session
            return RBACService.grant_project_access(
                db=sync_session,
                project_id=project_id,
                user_id=user_id,
                granted_by=granted_by
            )

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, sync_grant)

    except Exception as e:
        logger.warning(f"Failed to grant project access: {str(e)}")
        return False


async def _revoke_project_access(db: AsyncSession, project_id: str, user_id: str, revoked_by: str) -> bool:
    """Async wrapper for RBACService.revoke_project_access"""
    try:
        # Use run_in_executor to call sync RBAC method
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def sync_revoke():
            sync_session = db.sync_session
            return RBACService.revoke_project_access(
                db=sync_session,
                project_id=project_id,
                user_id=user_id,
                revoked_by=revoked_by
            )

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, sync_revoke)

    except Exception as e:
        logger.warning(f"Failed to revoke project access: {str(e)}")
        return False


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: CreateProjectRequest,
    current_user: Annotated[TokenPayload, Depends(require_permission(Permission.CREATE_PROJECT))],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project with GitHub connection options.

    - **name**: Project name
    - **description**: Optional project description
    - **github_repo_url**: GitHub repository URL
    - **github_connection_type**: Connection method ("https", "ssh", "cli")
    - **github_ssh_key_id**: SSH key ID for SSH connections
    - **github_cli_token**: GitHub CLI token for CLI connections
    - **language**: Primary programming language

    Requires CREATE_PROJECT permission (Programmer or Admin).
    The creating user becomes the project owner.
    """
    try:
        # Validate GitHub connection configuration
        await _validate_github_connection(project_data, current_user.user_id, db)

        # Convert connection type string to enum
        try:
            connection_type = GitHubConnectionType(project_data.github_connection_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid github_connection_type: {project_data.github_connection_type}. Must be 'https', 'ssh', or 'cli'"
            )

        # Create project
        now = datetime.now(timezone.utc)
        new_project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=current_user.user_id,
            github_repo_url=project_data.github_repo_url,
            github_connection_type=connection_type,
            github_ssh_key_id=project_data.github_ssh_key_id,
            github_cli_token=project_data.github_cli_token,
            language=project_data.language,
            created_at=now,
            updated_at=now
        )

        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)

        # Log audit event
        ip_address = request.client.host if request.client else "0.0.0.0"
        await _log_audit_action(
            db=db,
            user_id=current_user.user_id,
            username=current_user.username,
            action="CREATE_PROJECT",
            ip_address=ip_address,
            success=True,
            resource_type="Project",
            resource_id=str(new_project.id),
            user_agent=request.headers.get("user-agent")
        )

        return ProjectResponse(
            id=str(getattr(new_project, 'id')),
            name=getattr(new_project, 'name'),
            description=getattr(new_project, 'description'),
            owner_id=str(getattr(new_project, 'owner_id')),
            github_repo_url=getattr(new_project, 'github_repo_url'),
            github_connection_type=getattr(new_project, 'github_connection_type').value if getattr(new_project, 'github_connection_type') else "https",
            github_ssh_key_id=str(getattr(new_project, 'github_ssh_key_id')) if getattr(new_project, 'github_ssh_key_id') else None,
            language=getattr(new_project, 'language'),
            is_active=getattr(new_project, 'is_active'),
            created_at=getattr(new_project, 'created_at').isoformat(),
            updated_at=getattr(new_project, 'updated_at').isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
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
            id=str(getattr(project, 'id')),
            name=getattr(project, 'name'),
            description=getattr(project, 'description'),
            owner_id=str(getattr(project, 'owner_id')),
            github_repo_url=getattr(project, 'github_repo_url'),
            github_connection_type=getattr(project, 'github_connection_type').value if getattr(project, 'github_connection_type') else "https",
            github_ssh_key_id=str(getattr(project, 'github_ssh_key_id')) if getattr(project, 'github_ssh_key_id') else None,
            language=getattr(project, 'language'),
            is_active=getattr(project, 'is_active'),
            created_at=getattr(project, 'created_at').isoformat(),
            updated_at=getattr(project, 'updated_at').isoformat()
        )
        for project in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: AsyncSession = Depends(get_db)
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
        id=str(getattr(project, 'id')),
        name=getattr(project, 'name'),
        description=getattr(project, 'description'),
        owner_id=str(getattr(project, 'owner_id')),
        github_repo_url=getattr(project, 'github_repo_url'),
        github_connection_type=getattr(project, 'github_connection_type').value if getattr(project, 'github_connection_type') else "https",
        github_ssh_key_id=str(getattr(project, 'github_ssh_key_id')) if getattr(project, 'github_ssh_key_id') else None,
        language=getattr(project, 'language'),
        is_active=getattr(project, 'is_active'),
        created_at=getattr(project, 'created_at').isoformat(),
        updated_at=getattr(project, 'updated_at').isoformat()
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: UpdateProjectRequest,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.UPDATE_PROJECT))],
    request: Request,
    db: AsyncSession = Depends(get_db)
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
        setattr(project, 'name', project_data.name)
    if project_data.description is not None:
        setattr(project, 'description', project_data.description)
    
    setattr(project, 'updated_at', datetime.now(timezone.utc))
    
    await db.commit()
    await db.refresh(project)
    
    # Log action
    ip_address = request.client.host if request.client else "0.0.0.0"
    await _log_audit_action(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="UPDATE_PROJECT",
        ip_address=ip_address,
        success=True,
        resource_type="Project",
        resource_id=project_id,
        user_agent=request.headers.get("user-agent")
    )
    
    return ProjectResponse(
        id=str(getattr(project, 'id')),
        name=getattr(project, 'name'),
        description=getattr(project, 'description'),
        owner_id=str(getattr(project, 'owner_id')),
        github_repo_url=getattr(project, 'github_repo_url'),
        github_connection_type=getattr(project, 'github_connection_type').value if getattr(project, 'github_connection_type') else "https",
        github_ssh_key_id=str(getattr(project, 'github_ssh_key_id')) if getattr(project, 'github_ssh_key_id') else None,
        language=getattr(project, 'language'),
        is_active=getattr(project, 'is_active'),
        created_at=getattr(project, 'created_at').isoformat(),
        updated_at=getattr(project, 'updated_at').isoformat()
    )


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.DELETE_PROJECT))],
    request: Request,
    db: AsyncSession = Depends(get_db)
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
            await _log_audit_action(
                db=db,
                user_id=current_user.user_id,
                username=current_user.username,
                action="DELETE_PROJECT",
                ip_address=ip_address,
                success=True,
                resource_type="Project",
                resource_id=project_id,
                user_agent=request.headers.get("user-agent")
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
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Grant user access to project (Owner or Admin only).
    
    - **user_id**: ID of user to grant access to
    
    Only project owners or admins can grant access.
    """
    # Grant access
    success = await _grant_project_access(
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
    await _log_audit_action(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="GRANT_PROJECT_ACCESS",
        ip_address=ip_address,
        success=True,
        resource_type="ProjectAccess",
        resource_id=f"{project_id}:{access_data.user_id}",
        user_agent=request.headers.get("user-agent")
    )
    
    return ProjectAccessResponse(
        project_id=getattr(access_grant, 'project_id'),
        user_id=getattr(access_grant, 'user_id'),
        granted_at=getattr(access_grant, 'granted_at').isoformat(),
        granted_by=getattr(access_grant, 'granted_by')
    )


@router.delete("/{project_id}/access/{user_id}", response_model=MessageResponse)
async def revoke_project_access(
    project_id: str,
    user_id: str,
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke user access to project (Owner or Admin only).
    
    Only project owners or admins can revoke access.
    """
    # Revoke access
    success = await _revoke_project_access(
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
    await _log_audit_action(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="REVOKE_PROJECT_ACCESS",
        ip_address=ip_address,
        success=True,
        resource_type="ProjectAccess",
        resource_id=f"{project_id}:{user_id}",
        user_agent=request.headers.get("user-agent")
    )
    
    return MessageResponse(message="Project access revoked successfully")


# SSH Key Management Models
class SSHKeyRequest(BaseModel):
    """SSH key creation request model."""
    name: str
    public_key: str
    private_key: str  # This will be encrypted
    github_username: Optional[str] = None


class SSHKeyResponse(BaseModel):
    """SSH key response model."""
    id: str
    name: str
    public_key: str
    key_fingerprint: str
    github_username: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
    last_used_at: Optional[str]


# SSH Key Management Endpoints
@router.post("/ssh-keys", response_model=SSHKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_ssh_key(
    key_data: SSHKeyRequest,
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new SSH key for GitHub connections.

    - **name**: User-friendly name for the key
    - **public_key**: SSH public key content
    - **private_key**: SSH private key content (will be encrypted)
    - **github_username**: Associated GitHub username (optional)
    """
    try:
        from cryptography.fernet import Fernet
        import base64
        import hashlib

        # Generate key fingerprint from public key
        key_fingerprint = hashlib.sha256(key_data.public_key.encode()).hexdigest()[:16]

        # Encrypt private key (simplified - in production use proper key management)
        encryption_key = Fernet.generate_key()
        fernet = Fernet(encryption_key)
        encrypted_private_key = fernet.encrypt(key_data.private_key.encode()).decode()

        # Create SSH key
        new_ssh_key = SSHKey(
            name=key_data.name,
            public_key=key_data.public_key,
            private_key=encrypted_private_key,
            key_fingerprint=key_fingerprint,
            github_username=key_data.github_username,
            user_id=current_user.user_id
        )

        db.add(new_ssh_key)
        await db.commit()
        await db.refresh(new_ssh_key)

        # Log audit event
        ip_address = request.client.host if request.client else "0.0.0.0"
        await _log_audit_action(
            db=db,
            user_id=current_user.user_id,
            username=current_user.username,
            action="CREATE_SSH_KEY",
            ip_address=ip_address,
            success=True,
            resource_type="SSHKey",
            resource_id=str(new_ssh_key.id),
            user_agent=request.headers.get("user-agent")
        )

        return SSHKeyResponse(
            id=str(getattr(new_ssh_key, 'id')),
            name=getattr(new_ssh_key, 'name'),
            public_key=getattr(new_ssh_key, 'public_key'),
            key_fingerprint=getattr(new_ssh_key, 'key_fingerprint'),
            github_username=getattr(new_ssh_key, 'github_username'),
            is_active=getattr(new_ssh_key, 'is_active'),
            created_at=getattr(new_ssh_key, 'created_at').isoformat(),
            updated_at=getattr(new_ssh_key, 'updated_at').isoformat(),
            last_used_at=getattr(new_ssh_key, 'last_used_at').isoformat() if getattr(new_ssh_key, 'last_used_at') else None
        )

    except Exception as e:
        logger.error(f"Error creating SSH key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SSH key"
        )


@router.get("/ssh-keys", response_model=List[SSHKeyResponse])
async def list_ssh_keys(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all SSH keys for the current user.
    """
    result = await db.execute(
        select(SSHKey).filter(
            SSHKey.user_id == current_user.user_id,
            SSHKey.is_active == True
        )
    )
    ssh_keys = result.scalars().all()

    return [
        SSHKeyResponse(
            id=str(getattr(key, 'id')),
            name=getattr(key, 'name'),
            public_key=getattr(key, 'public_key'),
            key_fingerprint=getattr(key, 'key_fingerprint'),
            github_username=getattr(key, 'github_username'),
            is_active=getattr(key, 'is_active'),
            created_at=getattr(key, 'created_at').isoformat(),
            updated_at=getattr(key, 'updated_at').isoformat(),
            last_used_at=getattr(key, 'last_used_at').isoformat() if getattr(key, 'last_used_at') else None
        )
        for key in ssh_keys
    ]


@router.delete("/ssh-keys/{key_id}", response_model=MessageResponse)
async def delete_ssh_key(
    key_id: str,
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an SSH key (owner only).
    """
    result = await db.execute(
        select(SSHKey).filter(
            SSHKey.id == key_id,
            SSHKey.user_id == current_user.user_id
        )
    )
    ssh_key = result.scalar_one_or_none()

    if not ssh_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSH key not found"
        )

    # Check if key is being used by any projects
    result = await db.execute(
        select(Project).filter(Project.github_ssh_key_id == key_id)
    )
    projects_using_key = result.scalars().all()

    if projects_using_key:
        project_names = [str(p.name) for p in projects_using_key]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSH key is being used by projects: {', '.join(project_names)}. Remove the key from these projects first."
        )

    await db.delete(ssh_key)
    await db.commit()

    # Log audit event
    ip_address = request.client.host if request.client else "0.0.0.0"
    await _log_audit_action(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="DELETE_SSH_KEY",
        ip_address=ip_address,
        success=True,
        resource_type="SSHKey",
        resource_id=key_id,
        user_agent=request.headers.get("user-agent")
    )

    return MessageResponse(message=f"SSH key '{ssh_key.name}' deleted successfully")
