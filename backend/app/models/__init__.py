"""
SQLAlchemy models for database tables
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sqlalchemy as sa
import uuid
import enum

from app.database.postgresql import Base

# Import models from separate files
from app.models.code_review import (
    CodeReview, 
    ReviewComment, 
    ArchitectureAnalysis, 
    ArchitectureViolation,
    PRStatus as CodeReviewPRStatus,
    ReviewStatus,
    PullRequest as CodeReviewPullRequest
)
from app.models.library import (
    Library,
    LibraryDependency,
    RegistryType,
    ProjectContext
)


class UserRole(str, enum.Enum):
    """User role enum"""
    admin = "admin"
    developer = "developer"
    reviewer = "reviewer"
    compliance_officer = "compliance_officer"
    manager = "manager"


class PRStatus(str, enum.Enum):
    """Pull request status enum"""
    pending = "pending"
    analyzing = "analyzing"
    reviewed = "reviewed"
    approved = "approved"
    rejected = "rejected"


class AuditAction(str, enum.Enum):
    """Audit action enum"""
    create = "create"
    update = "update"
    delete = "delete"
    approve = "approve"
    reject = "reject"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.developer)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    github_token = Column(String(500), nullable=True)
    github_username = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    pull_requests = relationship("PullRequest", back_populates="author")


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    github_repo_url = Column(String(500), unique=True)
    github_webhook_secret = Column(String(255))
    language = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    pull_requests = relationship("PullRequest", back_populates="project")


# Use PullRequest from code_review module
PullRequest = CodeReviewPullRequest


class ReviewResult(Base):
    """Review Result model"""
    __tablename__ = "review_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pull_request_id = Column(UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    ai_suggestions = Column(JSONB)
    architectural_impact = Column(JSONB)
    security_issues = Column(JSONB)
    compliance_status = Column(JSONB)
    confidence_score = Column(Float)
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pull_request = relationship("PullRequest", back_populates="review_result")


class AuditLog(Base):
    """Audit Log model"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(SQLEnum(AuditAction), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    changes = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class ArchitecturalBaseline(Base):
    """Architectural Baseline model"""
    __tablename__ = "architectural_baselines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    graph_snapshot = Column(JSONB, nullable=False)
    metrics = Column(JSONB)
    commit_sha = Column(String(40))
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TokenBlacklist(Base):
    """Token blacklist for logout"""
    __tablename__ = "token_blacklist"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)


class ProjectAccess(Base):
    """Project access control model for managing user access to projects"""
    __tablename__ = "project_accesses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    access_level = Column(String(50), nullable=False, default="read")  # read, write, admin
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Composite unique constraint to prevent duplicate access grants
    __table_args__ = (
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_user_access'),
    )


class Session(Base):
    """User session model for tracking active sessions"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)  # JWT ID claim
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, index=True)


class CodeEntity(Base):
    """Code entity model for storing parsed code elements"""
    __tablename__ = "code_entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    pull_request_id = Column(UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # function, class, method, module, etc.
    name = Column(String(500), nullable=False, index=True)
    qualified_name = Column(String(1000), nullable=False)  # Full path including module/class
    file_path = Column(String(1000), nullable=False, index=True)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    complexity = Column(Integer, nullable=True)  # Cyclomatic complexity
    parameters = Column(JSONB, nullable=True)  # Function/method parameters
    return_type = Column(String(255), nullable=True)
    docstring = Column(Text, nullable=True)
    entity_metadata = Column(JSONB, nullable=True)  # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Composite index for efficient queries
    __table_args__ = (
        sa.Index('idx_code_entity_project_type', 'project_id', 'entity_type'),
        sa.Index('idx_code_entity_file_name', 'file_path', 'name'),
    )
