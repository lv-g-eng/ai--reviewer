"""
LLM Service Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Service settings"""
    
    # Service
    SERVICE_NAME: str = "ai-service"
    PORT: int = 8000
    
    # Models
    MODELS_DIR: str = "/app/models"
    LLM_THREADS: int = 8
    LLM_GPU_LAYERS: int = 35
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
