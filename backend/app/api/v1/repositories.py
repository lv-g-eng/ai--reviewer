"""
Repository management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database.postgresql import get_db
from app.services.repository_service import RepositoryService
from app.schemas.repository import (
    AddRepositoryRequest,
    RepositoryResponse,
    RepositoryListResponse,
    RepositoryUpdateRequest,
    RepositoryValidationResult
)
from app.core.security import get_current_user
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post(
    "/",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new repository dependency"
)
async def add_repository(
    request: AddRepositoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new GitHub repository as a dependency.
    
    Supports both HTTPS and SSH URL formats:
    - HTTPS: https://github.com/owner/repo.git
    - SSH: git@github.com:owner/repo.git
    
    The system will:
    1. Validate the repository URL format
    2. Check repository accessibility
    3. Verify branch/tag existence
    4. Extract dependency information
    5. Store repository metadata
    """
    try:
        service = RepositoryService(db)
        repository = await service.add_repository(request, current_user["sub"])
        
        logger.info(
            f"Repository added successfully: {repository.owner}/{repository.name} "
            f"by user {current_user['sub']}"
        )
        
        return repository
        
    except ValueError as e:
        logger.warning(f"Repository validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding repository: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add repository"
        )


@router.get(
    "/validate",
    response_model=RepositoryValidationResult,
    summary="Validate a repository URL"
)
async def validate_repository(
    repository_url: str = Query(..., description="GitHub repository URL to validate"),
    branch: Optional[str] = Query(None, description="Optional branch to validate"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Validate a GitHub repository URL without adding it.
    
    Returns:
    - Repository existence
    - Accessibility status
    - Available branches and tags
    - Default branch
    """
    try:
        service = RepositoryService(db)
        repo_info = service.parse_repository_url(repository_url)
        validation = await service.validate_repository(repo_info, branch)
        
        return validation
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error validating repository: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate repository"
        )


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
    summary="Get repository details"
)
async def get_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific repository"""
    # TODO: Implement database retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Repository retrieval not yet implemented"
    )


@router.get(
    "/",
    response_model=RepositoryListResponse,
    summary="List all repositories"
)
async def list_repositories(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all repository dependencies with pagination"""
    # TODO: Implement database listing
    return RepositoryListResponse(
        repositories=[],
        total=0,
        page=page,
        page_size=page_size
    )


@router.patch(
    "/{repository_id}",
    response_model=RepositoryResponse,
    summary="Update repository settings"
)
async def update_repository(
    repository_id: str,
    request: RepositoryUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update repository configuration and settings"""
    # TODO: Implement database update
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Repository update not yet implemented"
    )


@router.delete(
    "/{repository_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a repository"
)
async def delete_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Remove a repository dependency"""
    # TODO: Implement database deletion
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Repository deletion not yet implemented"
    )


@router.post(
    "/{repository_id}/sync",
    response_model=RepositoryResponse,
    summary="Sync repository with remote"
)
async def sync_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Synchronize repository with remote source.
    
    This will:
    1. Fetch latest changes
    2. Update dependency information
    3. Trigger analysis if configured
    """
    # TODO: Implement repository sync
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Repository sync not yet implemented"
    )
