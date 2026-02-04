# 🧹 Project Cleanup Checklist

**Date**: February 4, 2026  
**Status**: Ready for Execution

---

## 📋 Quick Action Items

### Immediate (Do First - 2 hours)
- [ ] **CRITICAL**: Remove hardcoded passwords from `docker-compose.backend.yml`
- [ ] Create backup branch: `git checkout -b cleanup/project-lean-out`
- [ ] Archive redundant summary files to `docs/archive/planning/`
- [ ] Delete `docker-compose.backend.yml` (security risk)

### High Priority (Week 1 - 8 hours)
- [ ] Consolidate documentation (README, QUICK_START, QUICK_REFERENCE)
- [ ] Clean up docker-compose files (keep 2, delete 2)
- [ ] Consolidate requirements files
- [ ] Archive analysis/planning documents

### Medium Priority (Week 2 - 12 hours)
- [ ] Consolidate scripts to Python
- [ ] Implement TODO items in repositories.py
- [ ] Add admin checks in llm.py endpoints
- [ ] Test all changes

### Low Priority (Week 3 - 16 hours)
- [ ] Apply DRY refactoring
- [ ] Optimize service configurations
- [ ] Performance testing
- [ ] Update all documentation

---

## 🗂️ Detailed Cleanup Tasks

### PHASE 1: DOCUMENTATION CLEANUP

#### Step 1.1: Archive Summary Files (30 min)
```bash
# Create archive directory
mkdir -p docs/archive/planning

# Move summary files
mv IMPLEMENTATION_SUMMARY.md docs/archive/planning/
mv FINAL_SUMMARY.md docs/archive/planning/
mv PHASE_IMPLEMENTATION_SUMMARY.md docs/archive/planning/
mv OPTIMIZATION_IMPLEMENTATION_SUMMARY.md docs/archive/planning/
mv DOCUMENTATION_ORGANIZATION_SUMMARY.md docs/archive/planning/
mv TASK_2_COMPLETION_SUMMARY.md docs/archive/planning/
mv INTEGRATION_TEST_FIX_SUMMARY.md docs/archive/planning/
mv ENVIRONMENT_CLEANUP.md docs/archive/planning/
mv BACKEND_STARTUP_OPTIMIZATION_COMPLETION.md docs/archive/planning/
mv CI_CD_FIXES_SUMMARY.md docs/archive/planning/

# Create index
echo "# Planning & Summary Archive" > docs/archive/planning/INDEX.md
echo "Historical planning and completion summaries" >> docs/archive/planning/INDEX.md
```

**Checklist:**
- [ ] Create `docs/archive/planning/` directory
- [ ] Move 10 summary files
- [ ] Create INDEX.md in archive
- [ ] Verify files moved successfully
- [ ] Commit: "Archive historical summary documents"

#### Step 1.2: Archive Analysis Files (15 min)
```bash
# Create archive directory
mkdir -p docs/archive/analysis

# Move analysis files
mv COMPREHENSIVE_BACKEND_FIX_AND_OPTIMIZATION_ANALYSIS.md docs/archive/analysis/
mv COMPREHENSIVE_OPTIMIZATION_PLAN.md docs/archive/analysis/
mv COMPREHENSIVE_PERFORMANCE_OPTIMIZATION_ANALYSIS.md docs/archive/analysis/
mv COMPREHENSIVE_PERFORMANCE_OPTIMIZATION_REPORT.md docs/archive/analysis/
mv PERFORMANCE_OPTIMIZATION_ANALYSIS_2026.md docs/archive/analysis/

# Create index
echo "# Performance Analysis Archive" > docs/archive/analysis/INDEX.md
echo "Historical performance analysis and optimization plans" >> docs/archive/analysis/INDEX.md
```

**Checklist:**
- [ ] Create `docs/archive/analysis/` directory
- [ ] Move 5 analysis files
- [ ] Create INDEX.md in archive
- [ ] Commit: "Archive historical analysis documents"

#### Step 1.3: Archive Merged Docs (10 min)
```bash
# Create archive directory
mkdir -p docs/archive/merged

# Move merged docs
mv MERGED_DOCS_01_PROJECT_OVERVIEW.md docs/archive/merged/
mv MERGED_DOCS_02_SETUP_CONFIGURATION.md docs/archive/merged/
mv MERGED_DOCS_03_FEATURES_GUIDES.md docs/archive/merged/
mv MERGED_DOCS_04_TECHNICAL_REFERENCE.md docs/archive/merged/

# Create index
echo "# Merged Documentation Archive" > docs/archive/merged/INDEX.md
echo "Previous documentation consolidation attempts" >> docs/archive/merged/INDEX.md
```

**Checklist:**
- [ ] Create `docs/archive/merged/` directory
- [ ] Move 4 merged doc files
- [ ] Create INDEX.md in archive
- [ ] Commit: "Archive merged documentation attempts"

#### Step 1.4: Consolidate Main Documentation (2 hours)

**Task 1: Enhance README.md**
- [ ] Review content from PROJECT_GUIDE.md and MASTER_GUIDE.md
- [ ] Merge essential sections into README.md
- [ ] Keep README focused on:
  - Project overview
  - Quick start (3 commands)
  - Architecture diagram
  - Links to detailed docs
- [ ] Remove redundant information
- [ ] Test all links
- [ ] Commit: "Consolidate main README"

**Task 2: Consolidate QUICK_START.md**
- [ ] Merge content from SETUP_GUIDE.md and README_STARTUP.md
- [ ] Structure:
  - Prerequisites
  - 5-minute setup
  - Common issues
  - Next steps
- [ ] Remove duplicate content
- [ ] Test all commands
- [ ] Commit: "Consolidate setup documentation"

**Task 3: Consolidate QUICK_REFERENCE.md**
- [ ] Merge content from:
  - QUICK_ACTIONS.md
  - QUICK_COMMANDS.md
  - QUICK_REFERENCE_REPOSITORY.md
- [ ] Organize by category:
  - Development commands
  - Docker commands
  - Database commands
  - Testing commands
  - Repository management
- [ ] Add table of contents
- [ ] Commit: "Consolidate quick reference"

**Task 4: Delete Redundant Files**
```bash
# After consolidation is complete and tested
git rm MASTER_GUIDE.md
git rm PROJECT_GUIDE.md
git rm README_STARTUP.md
git rm SETUP_GUIDE.md
git rm QUICK_ACTIONS.md
git rm QUICK_COMMANDS.md
git rm QUICK_REFERENCE_REPOSITORY.md
git rm PROJECT_INDEX.md

git commit -m "Remove redundant documentation files"
```

**Checklist:**
- [ ] README.md enhanced with essential content
- [ ] QUICK_START.md consolidated
- [ ] QUICK_REFERENCE.md consolidated
- [ ] All links tested and working
- [ ] 8 redundant files deleted
- [ ] Documentation structure validated

---

### PHASE 2: CONFIGURATION CLEANUP

#### Step 2.1: Remove Insecure Docker Compose (CRITICAL - 15 min)
```bash
# IMMEDIATE ACTION - Security Risk!
# docker-compose.backend.yml contains hardcoded passwords

# Backup first
cp docker-compose.backend.yml docker-compose.backend.yml.backup

# Remove from git
git rm docker-compose.backend.yml

# Update .gitignore to prevent re-adding
echo "*.backup" >> .gitignore

git commit -m "SECURITY: Remove docker-compose with hardcoded passwords"
```

**Checklist:**
- [ ] Backup file created
- [ ] File removed from git
- [ ] .gitignore updated
- [ ] Verify no passwords in remaining files
- [ ] Commit immediately

#### Step 2.2: Remove Unused Docker Compose (15 min)
```bash
# docker-compose.optimized.yml is 500+ lines and not used

# Archive it first (might be useful reference)
mkdir -p archive/docker-configs
mv docker-compose.optimized.yml archive/docker-configs/

# Create index
echo "# Docker Configuration Archive" > archive/docker-configs/INDEX.md
echo "Experimental and unused docker configurations" >> archive/docker-configs/INDEX.md

git add archive/docker-configs/
git commit -m "Archive unused optimized docker-compose"
```

**Checklist:**
- [ ] Archive directory created
- [ ] docker-compose.optimized.yml archived
- [ ] INDEX.md created
- [ ] Commit completed

#### Step 2.3: Consolidate Requirements Files (1 hour)

**Task 1: Analyze Current Requirements**
- [ ] Compare all requirements files
- [ ] Identify unique dependencies in each
- [ ] Check for version conflicts
- [ ] Document platform-specific needs

**Task 2: Create Consolidated Structure**
```bash
# Keep modular approach in backend/requirements/
# backend/requirements/
#   ├── base.txt (production dependencies)
#   ├── dev.txt (development tools)
#   ├── llm.txt (optional LLM features)
#   └── test.txt (testing dependencies)

# Main requirements.txt should include base
echo "-r requirements/base.txt" > backend/requirements.txt
```

**Task 3: Remove Redundant Files**
```bash
cd backend

# Archive old files
mkdir -p archive/requirements
mv requirements-fixed.txt archive/requirements/
mv requirements-windows.txt archive/requirements/

# Update main requirements.txt
# (manual editing required)

git add requirements.txt requirements/
git rm requirements-fixed.txt requirements-windows.txt
git commit -m "Consolidate requirements files"
```

**Checklist:**
- [ ] Requirements analyzed
- [ ] Modular structure in requirements/ directory
- [ ] Main requirements.txt updated
- [ ] Redundant files archived
- [ ] All dependencies tested
- [ ] Commit completed

---

### PHASE 3: SCRIPT CONSOLIDATION

#### Step 3.1: Consolidate NPM Cache Scripts (30 min)

**Create: scripts/clean_npm_cache.py**
```python
#!/usr/bin/env python3
"""Cross-platform NPM cache cleaning script."""
import subprocess
import sys
import platform

def clean_npm_cache():
    """Clean NPM cache on any platform."""
    try:
        print("Cleaning NPM cache...")
        subprocess.run(["npm", "cache", "clean", "--force"], check=True)
        print("✓ NPM cache cleaned successfully")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"✗ Error cleaning NPM cache: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(clean_npm_cache())
```

**Checklist:**
- [ ] Create scripts/clean_npm_cache.py
- [ ] Make executable: `chmod +x scripts/clean_npm_cache.py`
- [ ] Test on current platform
- [ ] Delete clean-npm-cache.bat and clean-npm-cache.sh
- [ ] Update documentation
- [ ] Commit: "Consolidate NPM cache cleaning to Python"

#### Step 3.2: Consolidate Path Verification Scripts (30 min)

**Create: scripts/verify_paths.py**
```python
#!/usr/bin/env python3
"""Cross-platform path verification script."""
import os
import sys
from pathlib import Path

def verify_paths():
    """Verify project paths are clean and valid."""
    issues = []
    
    # Check for spaces in paths
    cwd = Path.cwd()
    if ' ' in str(cwd):
        issues.append(f"Path contains spaces: {cwd}")
    
    # Check for special characters
    # Add more checks as needed
    
    if issues:
        print("✗ Path issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("✓ All paths verified successfully")
        return 0

if __name__ == "__main__":
    sys.exit(verify_paths())
```

**Checklist:**
- [ ] Create scripts/verify_paths.py
- [ ] Make executable
- [ ] Test verification logic
- [ ] Delete verify-path-clean.bat and verify-path-clean.sh
- [ ] Commit: "Consolidate path verification to Python"

#### Step 3.3: Consolidate Frontend Verification (30 min)

**Create: scripts/verify_frontend.py**
- [ ] Consolidate verify-frontend-env.sh and verify-frontend-env-enhanced.sh
- [ ] Add cross-platform support
- [ ] Test on multiple platforms
- [ ] Delete old scripts
- [ ] Commit changes

#### Step 3.4: Consolidate Test Scripts (30 min)

**Create: scripts/run_tests.py**
- [ ] Consolidate run-integration-tests.bat and run-integration-tests.sh
- [ ] Add options for different test types
- [ ] Support parallel execution
- [ ] Delete old scripts
- [ ] Commit changes

#### Step 3.5: Consolidate Setup Scripts (45 min)

**Create: scripts/setup_dev.py**
- [ ] Consolidate setup-dev.ps1 and setup-dev.sh
- [ ] Add platform detection
- [ ] Support all development tools
- [ ] Delete old scripts
- [ ] Commit changes

#### Step 3.6: Consolidate Fix Scripts (1 hour)

**Create: scripts/fix_code_issues.py**
- [ ] Consolidate:
  - fix_typescript_errors.py
  - fix_unused_imports.py
  - fix_all_unused_vars.bat
  - fix_frontend_build.bat
  - fix_frontend_complete.bat
- [ ] Add command-line options for different fix types
- [ ] Test all fix operations
- [ ] Delete old scripts
- [ ] Commit changes

**Checklist:**
- [ ] All scripts consolidated to Python
- [ ] Cross-platform compatibility verified
- [ ] Old scripts deleted
- [ ] scripts/README.md updated
- [ ] All commits completed

---

### PHASE 4: CODE COMPLETION

#### Step 4.1: Implement Repository CRUD Operations (3 hours)

**File: backend/app/api/v1/repositories.py**

**Task 1: Implement get_repository()**
```python
@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific repository"""
    repository = await db.get(Repository, repository_id)
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    # Check ownership
    if repository.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this repository"
        )
    
    return repository
```

**Task 2: Implement list_repositories()**
```python
@router.get("", response_model=RepositoryListResponse)
async def list_repositories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[RepositoryStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all repository dependencies with pagination"""
    query = select(Repository).where(Repository.created_by == current_user.id)
    
    if status:
        query = query.where(Repository.status == status)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    repositories = result.scalars().all()
    
    return RepositoryListResponse(
        repositories=repositories,
        total=total,
        page=page,
        page_size=page_size
    )
```

**Task 3: Implement update_repository()**
```python
@router.patch("/{repository_id}", response_model=RepositoryResponse)
async def update_repository(
    repository_id: UUID,
    update_data: RepositoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update repository configuration and settings"""
    repository = await db.get(Repository, repository_id)
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    if repository.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this repository"
        )
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(repository, field, value)
    
    repository.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(repository)
    
    return repository
```

**Task 4: Implement delete_repository()**
```python
@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(
    repository_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a repository dependency"""
    repository = await db.get(Repository, repository_id)
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    if repository.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this repository"
        )
    
    # Soft delete
    repository.status = RepositoryStatus.ARCHIVED
    repository.updated_at = datetime.utcnow()
    
    await db.commit()
```

**Task 5: Implement sync_repository()**
```python
@router.post("/{repository_id}/sync", response_model=RepositoryResponse)
async def sync_repository(
    repository_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    repository_service: RepositoryService = Depends()
):
    """Sync repository with remote and update metadata"""
    repository = await db.get(Repository, repository_id)
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    if repository.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to sync this repository"
        )
    
    # Trigger sync
    try:
        updated_repo = await repository_service.sync_repository(repository)
        await db.commit()
        await db.refresh(updated_repo)
        return updated_repo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )
```

**Checklist:**
- [ ] get_repository() implemented
- [ ] list_repositories() implemented with pagination
- [ ] update_repository() implemented
- [ ] delete_repository() implemented (soft delete)
- [ ] sync_repository() implemented
- [ ] All endpoints tested
- [ ] Error handling verified
- [ ] Authorization checks working
- [ ] Commit: "Implement repository CRUD operations"

#### Step 4.2: Add Admin Authorization (1 hour)

**File: backend/app/core/dependencies.py**

**Create admin_required decorator:**
```python
from functools import wraps
from fastapi import HTTPException, status

def admin_required(func):
    """Decorator to require admin privileges."""
    @wraps(func)
    async def wrapper(*args, current_user: User = None, **kwargs):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper
```

**Update: backend/app/api/v1/endpoints/llm.py**
```python
from app.core.dependencies import admin_required

@router.post("/models/{model_type}/load")
@admin_required
async def load_model(
    model_type: str,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends()
):
    """Load a specific LLM model. Requires admin privileges."""
    try:
        success = await llm_service.load_model(model_type)
        # ... rest of implementation
```

**Checklist:**
- [ ] admin_required decorator created
- [ ] Applied to load_model endpoint
- [ ] Applied to unload_model endpoint
- [ ] Tests added for authorization
- [ ] Non-admin access blocked
- [ ] Commit: "Add admin authorization checks"

---

### PHASE 5: REFACTORING & DRY

#### Step 5.1: Consolidate Service Configuration (2 hours)

**Create: shared/config/service-config.ts**
- [ ] Extract common service configuration
- [ ] Create shared configuration module
- [ ] Update all services to use shared config
- [ ] Remove duplicate configuration code
- [ ] Test all services
- [ ] Commit changes

#### Step 5.2: Consolidate Database Connection Logic (2 hours)

**Create: backend/app/core/database_manager.py**
- [ ] Extract common database connection patterns
- [ ] Create unified connection manager
- [ ] Add connection pooling
- [ ] Update all services to use manager
- [ ] Remove duplicate connection code
- [ ] Test all database operations
- [ ] Commit changes

#### Step 5.3: Consolidate Error Handling (2 hours)

**Create: backend/app/core/error_handlers.py**
- [ ] Extract common error handling patterns
- [ ] Create standardized error responses
- [ ] Add error logging
- [ ] Update all endpoints to use handlers
- [ ] Remove duplicate error handling
- [ ] Test error scenarios
- [ ] Commit changes

#### Step 5.4: Consolidate Logging Configuration (1 hour)

**Create: backend/app/core/logging_config.py**
- [ ] Extract common logging configuration
- [ ] Create unified logging setup
- [ ] Add structured logging
- [ ] Update all services to use config
- [ ] Remove duplicate logging code
- [ ] Test logging output
- [ ] Commit changes

#### Step 5.5: Consolidate Health Check Endpoints (1 hour)

**Create: shared/health/health-check.ts**
- [ ] Extract common health check logic
- [ ] Create shared health check module
- [ ] Add dependency checks
- [ ] Update all services to use module
- [ ] Remove duplicate health checks
- [ ] Test all health endpoints
- [ ] Commit changes

---

## ✅ Final Verification

### Documentation Verification
- [ ] All links in README.md work
- [ ] QUICK_START.md tested end-to-end
- [ ] QUICK_REFERENCE.md commands verified
- [ ] No broken links in docs/
- [ ] Archive directories have INDEX.md files

### Configuration Verification
- [ ] docker-compose.yml works for development
- [ ] docker-compose.prod.yml works for production
- [ ] No hardcoded secrets in any config
- [ ] All environment variables documented
- [ ] Requirements files install successfully

### Script Verification
- [ ] All Python scripts are executable
- [ ] Scripts work on Windows, Mac, and Linux
- [ ] No duplicate functionality
- [ ] scripts/README.md is up-to-date
- [ ] All old scripts deleted

### Code Verification
- [ ] No TODO comments in production code
- [ ] All endpoints return proper responses (no 501)
- [ ] Authorization checks in place
- [ ] Tests passing
- [ ] No code duplication

### Testing
- [ ] Run full test suite: `pytest backend/tests/`
- [ ] Run frontend tests: `cd frontend && npm test`
- [ ] Run integration tests: `python scripts/run_tests.py`
- [ ] Manual testing of key features
- [ ] Performance testing

---

## 📊 Progress Tracking

### Phase 1: Documentation (Target: Week 1)
- [ ] Step 1.1: Archive summary files
- [ ] Step 1.2: Archive analysis files
- [ ] Step 1.3: Archive merged docs
- [ ] Step 1.4: Consolidate main docs

**Progress**: 0/4 steps complete

### Phase 2: Configuration (Target: Week 1)
- [ ] Step 2.1: Remove insecure docker-compose
- [ ] Step 2.2: Remove unused docker-compose
- [ ] Step 2.3: Consolidate requirements

**Progress**: 0/3 steps complete

### Phase 3: Scripts (Target: Week 2)
- [ ] Step 3.1: NPM cache scripts
- [ ] Step 3.2: Path verification scripts
- [ ] Step 3.3: Frontend verification
- [ ] Step 3.4: Test scripts
- [ ] Step 3.5: Setup scripts
- [ ] Step 3.6: Fix scripts

**Progress**: 0/6 steps complete

### Phase 4: Code Completion (Target: Week 2)
- [ ] Step 4.1: Repository CRUD operations
- [ ] Step 4.2: Admin authorization

**Progress**: 0/2 steps complete

### Phase 5: Refactoring (Target: Week 3)
- [ ] Step 5.1: Service configuration
- [ ] Step 5.2: Database connection
- [ ] Step 5.3: Error handling
- [ ] Step 5.4: Logging configuration
- [ ] Step 5.5: Health checks

**Progress**: 0/5 steps complete

---

## 🎯 Overall Progress

**Total Tasks**: 20 major steps  
**Completed**: 0  
**In Progress**: 0  
**Remaining**: 20  

**Estimated Time**: 36-48 hours  
**Target Completion**: 3 weeks  

---

## 📝 Notes

- Always create backups before deleting files
- Test thoroughly after each phase
- Commit frequently with clear messages
- Update documentation as you go
- Communicate changes to the team

**Ready to start?** Begin with Phase 1, Step 1.1!

