"""
Application configuration settings with comprehensive validation
"""
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    """
    Application settings with secure environment variable handling.
    
    Implements comprehensive validation for:
    - Required field validation (JWT_SECRET, database credentials)
    - Optional field handling with sensible defaults
    - Security settings validation
    - Database URL validation
    - Celery configuration validation
    - Environment-specific configuration (development, staging, production)
    
    Validates Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """

    # ========================================
    # APPLICATION SETTINGS
    # ========================================
    PROJECT_NAME: str = "AI Code Review Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")

    # ========================================
    # REQUIRED SECRETS (will raise error if missing or empty)
    # ========================================

    # Security - REQUIRED for application to start (Requirement 1.1, 1.2, 1.3)
    JWT_SECRET: str = Field(
        default="",
        description="JWT signing secret - must be 32+ characters",
        min_length=0  # Allow empty for testing, validation happens in validator
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # PostgreSQL - REQUIRED database connection (Requirement 1.1, 1.2, 1.3)
    POSTGRES_HOST: str = Field(default="", description="PostgreSQL host")
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = Field(default="", description="PostgreSQL database name")
    POSTGRES_USER: str = Field(default="", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(
        default="",
        description="PostgreSQL password - must be non-empty",
        min_length=0  # Allow empty for testing, validation happens in validator
    )

    # Neo4j - REQUIRED graph database (Requirement 1.1, 1.2, 1.3)
    NEO4J_URI: str = Field(default="", description="Neo4j connection URI")
    NEO4J_USER: str = Field(default="", description="Neo4j username")
    NEO4J_PASSWORD: str = Field(
        default="",
        description="Neo4j password - must be non-empty",
        min_length=0  # Allow empty for testing, validation happens in validator
    )
    NEO4J_DATABASE: str = "neo4j"

    # Redis - REQUIRED cache/session store (Requirement 1.1, 1.2, 1.3)
    REDIS_HOST: str = Field(default="", description="Redis host")
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = Field(default="", description="Redis password - can be empty for local Redis")
    REDIS_DB: int = 0

    # ========================================
    # OPTIONAL SECRETS (can be None/disabled) - Requirement 1.4
    # ========================================

    # External APIs - Optional integrations
    GITHUB_TOKEN: Optional[str] = Field(default=None, description="GitHub API token")
    GITHUB_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="GitHub webhook secret")
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic Claude API key")
    OLLAMA_BASE_URL: Optional[str] = Field(default=None, description="Ollama local LLM base URL")
    
    # Local LLM Configuration
    MODELS_DIR: str = "models"
    LLM_ENABLED: bool = True
    LLM_GPU_LAYERS: int = 35
    LLM_THREADS: int = 8
    LLM_CONTEXT_SIZE: int = 4096

    # ========================================
    # NON-SECRETS (safe to expose)
    # ========================================

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://frontend:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Password Security
    BCRYPT_ROUNDS: int = 12

    # Logging
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # Celery Configuration (Requirement 1.1, 1.2, 1.3)
    CELERY_BROKER_URL: Optional[str] = Field(default=None, description="Celery broker URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None, description="Celery result backend URL")

    # ========================================
    # FIELD VALIDATORS
    # ========================================

    @field_validator("JWT_SECRET", mode="after")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT_SECRET is non-empty (Requirement 1.3)"""
        # Only validate if not in testing mode
        if not os.environ.get("TESTING"):
            if not v or not v.strip():
                raise ValueError("JWT_SECRET cannot be empty")
        return v

    @field_validator("POSTGRES_PASSWORD", mode="after")
    @classmethod
    def validate_postgres_password(cls, v: str) -> str:
        """Validate POSTGRES_PASSWORD is non-empty (Requirement 1.3)"""
        # Only validate if not in testing mode
        if not os.environ.get("TESTING"):
            if not v or not v.strip():
                raise ValueError("POSTGRES_PASSWORD cannot be empty")
        return v

    @field_validator("NEO4J_PASSWORD", mode="after")
    @classmethod
    def validate_neo4j_password(cls, v: str) -> str:
        """Validate NEO4J_PASSWORD is non-empty (Requirement 1.3)"""
        # Only validate if not in testing mode
        if not os.environ.get("TESTING"):
            if not v or not v.strip():
                raise ValueError("NEO4J_PASSWORD cannot be empty")
        return v

    @field_validator("ENVIRONMENT", mode="after")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate ENVIRONMENT is one of the supported values (Requirement 1.5)"""
        if not v:
            return "development"
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of {valid_environments}, got {v}")
        return v

    @field_validator("BCRYPT_ROUNDS", mode="after")
    @classmethod
    def validate_bcrypt_rounds(cls, v: int) -> int:
        """Validate BCRYPT_ROUNDS is at least 12 for security"""
        if v < 12:
            raise ValueError("BCRYPT_ROUNDS must be at least 12 for security")
        if v > 20:
            raise ValueError("BCRYPT_ROUNDS is very high (>20) - may impact performance")
        return v

    @model_validator(mode="after")
    def validate_celery_config(self) -> "Settings":
        """Validate Celery configuration if enabled (Requirement 1.1, 1.2, 1.3)"""
        # Celery URLs are optional but if one is set, both should be set
        if self.CELERY_BROKER_URL or self.CELERY_RESULT_BACKEND:
            if not self.CELERY_BROKER_URL:
                raise ValueError("CELERY_BROKER_URL must be set if CELERY_RESULT_BACKEND is set")
            if not self.CELERY_RESULT_BACKEND:
                raise ValueError("CELERY_RESULT_BACKEND must be set if CELERY_BROKER_URL is set")
        return self

    # ========================================
    # COMPUTED PROPERTIES
    # ========================================

    @property
    def postgres_url(self) -> str:
        """PostgreSQL async connection URL (Requirement 1.1)"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def sync_postgres_url(self) -> str:
        """PostgreSQL sync connection URL (Requirement 1.1)"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_url(self) -> str:
        """Redis connection URL with authentication (Requirement 1.1)"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def celery_broker_url(self) -> str:
        """Celery broker URL (Requirement 1.1)"""
        if self.CELERY_BROKER_URL:
            return self.CELERY_BROKER_URL
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        """Celery result backend URL (Requirement 1.1)"""
        if self.CELERY_RESULT_BACKEND:
            return self.CELERY_RESULT_BACKEND
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/1"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    # ========================================
    # VALIDATION METHODS
    # ========================================

    def validate_security_settings(self) -> List[str]:
        """
        Validate security-related settings and return warnings.
        
        Validates Requirements: 1.1, 1.2, 1.3, 1.5
        """
        warnings = []

        # JWT_SECRET length validation
        if len(self.JWT_SECRET) < 32:
            warnings.append(
                f"JWT_SECRET is only {len(self.JWT_SECRET)} characters (minimum 32 recommended). "
                "This may reduce security. Consider regenerating with: openssl rand -hex 32"
            )

        # JWT expiration validation
        if self.JWT_EXPIRATION_HOURS > 168:  # 1 week
            warnings.append(
                f"JWT_EXPIRATION_HOURS is very long ({self.JWT_EXPIRATION_HOURS} hours, >1 week). "
                "Consider reducing for better security."
            )

        # BCRYPT rounds validation
        if self.BCRYPT_ROUNDS < 12:
            warnings.append(
                f"BCRYPT_ROUNDS is {self.BCRYPT_ROUNDS} (minimum 12 required). "
                "This is a critical security issue."
            )

        if self.BCRYPT_ROUNDS > 20:
            warnings.append(
                f"BCRYPT_ROUNDS is {self.BCRYPT_ROUNDS} (>20). "
                "This may significantly impact performance."
            )

        # External API keys validation
        if not self.GITHUB_TOKEN and not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
            warnings.append(
                "No external API keys configured (GITHUB_TOKEN, OPENAI_API_KEY, ANTHROPIC_API_KEY). "
                "Limited functionality available."
            )

        return warnings

    def validate_database_urls(self) -> List[str]:
        """
        Validate database connection URLs and parameters.
        
        Validates Requirements: 1.1, 1.2, 1.3
        """
        errors = []

        # PostgreSQL validation
        if not self.POSTGRES_HOST:
            errors.append("POSTGRES_HOST is required")
        if not self.POSTGRES_DB:
            errors.append("POSTGRES_DB is required")
        if not self.POSTGRES_USER:
            errors.append("POSTGRES_USER is required")
        if not self.POSTGRES_PASSWORD:
            errors.append("POSTGRES_PASSWORD is required and cannot be empty")
        if self.POSTGRES_PORT <= 0 or self.POSTGRES_PORT > 65535:
            errors.append(f"POSTGRES_PORT must be between 1 and 65535, got {self.POSTGRES_PORT}")

        # Neo4j validation
        if not self.NEO4J_URI:
            errors.append("NEO4J_URI is required")
        if not self.NEO4J_USER:
            errors.append("NEO4J_USER is required")
        if not self.NEO4J_PASSWORD:
            errors.append("NEO4J_PASSWORD is required and cannot be empty")

        # Redis validation
        if not self.REDIS_HOST:
            errors.append("REDIS_HOST is required")
        if self.REDIS_PORT <= 0 or self.REDIS_PORT > 65535:
            errors.append(f"REDIS_PORT must be between 1 and 65535, got {self.REDIS_PORT}")

        return errors

    def validate_celery_config(self) -> List[str]:
        """
        Validate Celery configuration.
        
        Validates Requirements: 1.1, 1.2, 1.3
        """
        errors = []

        # If Celery is configured, validate both URLs are set
        if self.CELERY_BROKER_URL and not self.CELERY_RESULT_BACKEND:
            errors.append("CELERY_RESULT_BACKEND must be set if CELERY_BROKER_URL is set")

        if self.CELERY_RESULT_BACKEND and not self.CELERY_BROKER_URL:
            errors.append("CELERY_BROKER_URL must be set if CELERY_RESULT_BACKEND is set")

        return errors

    def get_environment_specific_defaults(self) -> dict:
        """
        Get environment-specific default values.
        
        Validates Requirement: 1.5
        """
        defaults = {
            "development": {
                "DEBUG": True,
                "LOG_LEVEL": "DEBUG",
                "ALLOWED_ORIGINS": [
                    "http://localhost:3000",
                    "http://localhost:8000",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:8000",
                    "http://frontend:3000",
                ],
            },
            "staging": {
                "DEBUG": False,
                "LOG_LEVEL": "INFO",
                "ALLOWED_ORIGINS": [
                    "https://staging.example.com",
                ],
            },
            "production": {
                "DEBUG": False,
                "LOG_LEVEL": "WARNING",
                "ALLOWED_ORIGINS": [
                    "https://example.com",
                ],
            },
        }
        return defaults.get(self.ENVIRONMENT, defaults["development"])

    def is_celery_enabled(self) -> bool:
        """Check if Celery is enabled (Requirement 1.4)"""
        return bool(self.CELERY_BROKER_URL and self.CELERY_RESULT_BACKEND)

    def is_github_integration_enabled(self) -> bool:
        """Check if GitHub integration is enabled (Requirement 1.4)"""
        return bool(self.GITHUB_TOKEN and self.GITHUB_WEBHOOK_SECRET)

    def is_openai_enabled(self) -> bool:
        """Check if OpenAI integration is enabled (Requirement 1.4)"""
        return bool(self.OPENAI_API_KEY)

    def is_anthropic_enabled(self) -> bool:
        """Check if Anthropic integration is enabled (Requirement 1.4)"""
        return bool(self.ANTHROPIC_API_KEY)

    def is_ollama_enabled(self) -> bool:
        """Check if Ollama local LLM is enabled (Requirement 1.4)"""
        return bool(self.OLLAMA_BASE_URL)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )


# Create global settings instance
settings = Settings()
