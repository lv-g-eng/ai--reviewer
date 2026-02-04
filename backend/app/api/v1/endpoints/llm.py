"""
LLM API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

from app.services.llm_service import llm_service, ModelType
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.auth import UserResponse

router = APIRouter()


class AnalysisType(str, Enum):
    """Analysis types"""
    REVIEW = "review"
    SECURITY = "security"
    PERFORMANCE = "performance"


class CodeAnalysisRequest(BaseModel):
    """Code analysis request"""
    code: str = Field(..., description="Code to analyze")
    language: str = Field(..., description="Programming language")
    analysis_type: AnalysisType = Field(
        default=AnalysisType.REVIEW,
        description="Type of analysis to perform"
    )


class GenerateRequest(BaseModel):
    """General text generation request"""
    prompt: str = Field(..., description="Input prompt")
    model_type: ModelType = Field(
        default=ModelType.CODE_REVIEW,
        description="Model to use"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=4096,
        description="Maximum tokens to generate"
    )


class ArchitectureAnalysisRequest(BaseModel):
    """Architecture analysis request"""
    components: List[str] = Field(..., description="System components")
    dependencies: List[Dict[str, str]] = Field(..., description="Component dependencies")
    patterns: Optional[List[str]] = Field(default=[], description="Design patterns used")


@router.post("/analyze-code")
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Analyze code using local LLM
    
    Performs code review, security analysis, or performance analysis
    """
    try:
        result = await llm_service.analyze_code(
            code=request.code,
            language=request.language,
            analysis_type=request.analysis_type.value,
        )
        
        return {
            "success": True,
            "analysis": result,
            "model": ModelType.CODE_REVIEW.value,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/generate")
async def generate_text(
    request: GenerateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Generate text using local LLM
    
    General-purpose text generation endpoint
    """
    try:
        response = await llm_service.generate(
            prompt=request.prompt,
            model_type=request.model_type,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        return {
            "success": True,
            "response": response,
            "model": request.model_type.value,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/analyze-architecture")
async def analyze_architecture(
    request: ArchitectureAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Analyze system architecture using local LLM
    
    Provides insights and recommendations for architecture improvements
    """
    try:
        architecture_data = {
            "components": request.components,
            "dependencies": request.dependencies,
            "patterns": request.patterns,
        }
        
        result = await llm_service.generate_architecture_insights(architecture_data)
        
        return {
            "success": True,
            "insights": result,
            "model": ModelType.GENERAL.value,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/models")
async def list_models(current_user: UserResponse = Depends(get_current_user)):
    """
    List available LLM models and their status
    """
    try:
        models_info = {}
        for model_type in ModelType:
            models_info[model_type.value] = await llm_service.get_model_info(model_type)
            
        return {
            "success": True,
            "models": models_info,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models info: {str(e)}")


@router.post("/models/{model_type}/load")
async def load_model(
    model_type: ModelType,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Load a specific model into memory
    
    Requires admin privileges
    """
    # Check admin privileges
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required to load models"
        )
    
    try:
        success = await llm_service.load_model(model_type)
        
        if success:
            return {
                "success": True,
                "message": f"Model {model_type.value} loaded successfully",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to load model")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@router.post("/models/{model_type}/unload")
async def unload_model(
    model_type: ModelType,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Unload a model from memory
    
    Requires admin privileges
    """
    # Check admin privileges
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required to unload models"
        )
    
    try:
        await llm_service.unload_model(model_type)
        
        return {
            "success": True,
            "message": f"Model {model_type.value} unloaded successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unload model: {str(e)}")


@router.get("/health")
async def llm_health_check():
    """
    Check LLM service health
    
    Public endpoint for monitoring
    """
    try:
        health = await llm_service.health_check()
        return {
            "success": True,
            "health": health,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
