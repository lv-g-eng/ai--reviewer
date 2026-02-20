"""
Configuration for Enterprise RBAC Authentication System integrated into backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class AuthSettings(BaseSettings):
    """Authentication settings loaded from environment variables."""
    
    # JWT Configuration
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    
    # Security Configuration
    bcrypt_rounds: int = 12
    
    # Session Configuration
    session_expire_minutes: int = 1440  # 24 hours
    allow_concurrent_sessions: bool = True
    
    class Config:
        env_prefix = "AUTH_"  # Prefix for auth-specific env vars
        case_sensitive = False
        extra = "ignore"


# Global auth settings instance
auth_settings = AuthSettings()
