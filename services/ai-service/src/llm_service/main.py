"""
LLM Service - Dedicated microservice for local LLM inference
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import logging

from .llm_manager import llm_manager, ModelType
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("Starting LLM Service...")
    await llm_manager.initialize()
    logger.info("LLM Service started successfully")
    yield
    logger.info("Shutting down LLM Service...")


app = FastAPI(
    title="LLM Service",
    description="Local LLM inference service for code analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    """Generation request"""
    prompt: str = Field(..., description="Input prompt")
    model_type: ModelType = Field(default=ModelType.CODE_REVIEW)
    temperature: Optional[float] = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=8192)
    stop: Optional[List[str]] = Field(default=None)


class CodeAnalysisRequest(BaseModel):
    """Code analysis request"""
    code: str
    language: str
    analysis_type: str = "review"


class ArchitectureRequest(BaseModel):
    """Architecture analysis request"""
    components: List[str]
    dependencies: List[Dict[str, str]]
    patterns: Optional[List[str]] = []


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LLM Service",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check"""
    health = await llm_manager.health_check()
    return {
        "status": "healthy" if health["initialized"] else "initializing",
        "service": "ai-service",
        "health": health,
    }


@app.post("/generate")
async def generate(request: GenerateRequest):
    """Generate text"""
    try:
        response = await llm_manager.generate(
            prompt=request.prompt,
            model_type=request.model_type,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop=request.stop or [],
        )
        
        return {
            "success": True,
            "response": response,
            "model": request.model_type.value,
        }
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/code")
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code"""
    try:
        result = await llm_manager.analyze_code(
            code=request.code,
            language=request.language,
            analysis_type=request.analysis_type,
        )
        
        return {
            "success": True,
            "analysis": result,
        }
    except Exception as e:
        logger.error(f"Code analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/architecture")
async def analyze_architecture(request: ArchitectureRequest):
    """Analyze architecture"""
    try:
        architecture_data = {
            "components": request.components,
            "dependencies": request.dependencies,
            "patterns": request.patterns,
        }
        
        result = await llm_manager.generate_architecture_insights(architecture_data)
        
        return {
            "success": True,
            "insights": result,
        }
    except Exception as e:
        logger.error(f"Architecture analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List available models"""
    models_info = {}
    for model_type in ModelType:
        models_info[model_type.value] = await llm_manager.get_model_info(model_type)
    
    return {
        "success": True,
        "models": models_info,
    }


@app.post("/models/{model_type}/load")
async def load_model(model_type: ModelType):
    """Load a model"""
    try:
        success = await llm_manager.load_model(model_type)
        if success:
            return {
                "success": True,
                "message": f"Model {model_type.value} loaded",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to load model")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/{model_type}/unload")
async def unload_model(model_type: ModelType):
    """Unload a model"""
    try:
        await llm_manager.unload_model(model_type)
        return {
            "success": True,
            "message": f"Model {model_type.value} unloaded",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
