"""
User model for the Enterprise RBAC Authentication System.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from .enums import Role


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """User entity with authentication and role information."""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    owned_projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")
    project_accesses: Mapped[list["ProjectAccess"]] = relationship(
        "ProjectAccess", 
        back_populates="user", 
        foreign_keys="ProjectAccess.user_id",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
