"""
Configuration management for Enterprise RBAC Authentication System.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # JWT Configuration
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    
    # Database Configuration
    database_url: str = "sqlite:///./enterprise_rbac.db"
    
    # Application Configuration
    app_name: str = "Enterprise RBAC Authentication"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Security Configuration
    bcrypt_rounds: int = 12
    
    # Session Configuration
    session_expire_minutes: int = 60
    allow_concurrent_sessions: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
