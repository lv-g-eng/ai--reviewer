"""
Local LLM Service using llama-cpp-python for GGUF model inference
"""
import os
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum
import logging

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Available model types"""
    CODE_REVIEW = "code_review"  # Qwen2.5-Coder for code analysis
    GENERAL = "general"  # DeepSeek for general tasks
    VISION = "vision"  # Qwen3-VL for visual analysis


class LLMConfig:
    """LLM Configuration"""
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 4096,
        n_threads: int = 8,
        n_gpu_layers: int = 0,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        top_p: float = 0.95,
        top_k: int = 40,
    ):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_gpu_layers = n_gpu_layers
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k


class LLMService:
    """Service for managing local LLM inference"""
    
    def __init__(self):
        self.models: Dict[ModelType, Optional[Llama]] = {
            ModelType.CODE_REVIEW: None,
            ModelType.GENERAL: None,
            ModelType.VISION: None,
        }
        self.configs: Dict[ModelType, LLMConfig] = {}
        self.models_dir = Path(settings.MODELS_DIR)
        self._initialized = False
        
    async def initialize(self):
        """Initialize LLM models"""
        if self._initialized:
            return
            
        if Llama is None:
            logger.warning("llama-cpp-python not installed. LLM features disabled.")
            return
            
        logger.info("Initializing LLM service...")
        
        # Configure models
        self.configs = {
            ModelType.CODE_REVIEW: LLMConfig(
                model_path=str(self.models_dir / "Qwen2.5-Coder-14B-Instruct-Q4_0.gguf"),
                n_ctx=8192,
                n_threads=8,
                n_gpu_layers=35,  # Adjust based on GPU memory
                temperature=0.1,
                max_tokens=2048,
            ),
            ModelType.GENERAL: LLMConfig(
                model_path=str(self.models_dir / "DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf"),
                n_ctx=4096,
                n_threads=8,
                n_gpu_layers=32,
                temperature=0.3,
                max_tokens=1024,
            ),
            ModelType.VISION: LLMConfig(
                model_path=str(self.models_dir / "Qwen3-VL-8B-Instruct-abliterated-v2.0.Q4_K_M.gguf"),
                n_ctx=4096,
                n_threads=8,
                n_gpu_layers=30,
                temperature=0.2,
                max_tokens=1024,
            ),
        }
        
        # Load models on demand (lazy loading)
        self._initialized = True
        logger.info("LLM service initialized (models will load on first use)")
        
    async def load_model(self, model_type: ModelType) -> bool:
        """Load a specific model"""
        if self.models[model_type] is not None:
            return True
            
        config = self.configs.get(model_type)
        if not config:
            logger.error(f"No configuration for model type: {model_type}")
            return False
            
        if not os.path.exists(config.model_path):
            logger.error(f"Model file not found: {config.model_path}")
            return False
            
        try:
            logger.info(f"Loading model: {model_type.value} from {config.model_path}")
            
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            model = await loop.run_in_executor(
                None,
                lambda: Llama(
                    model_path=config.model_path,
                    n_ctx=config.n_ctx,
                    n_threads=config.n_threads,
                    n_gpu_layers=config.n_gpu_layers,
                    verbose=False,
                )
            )
            
            self.models[model_type] = model
            logger.info(f"Model loaded successfully: {model_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_type.value}: {e}")
            return False
            
    def is_initialized(self) -> bool:
        """Check if LLM service is initialized"""
        return self._initialized
            
    async def unload_model(self, model_type: ModelType):
        """Unload a model to free memory"""
        if self.models[model_type] is not None:
            del self.models[model_type]
            self.models[model_type] = None
            logger.info(f"Model unloaded: {model_type.value}")
            
    async def generate(
        self,
        prompt: str,
        model_type: ModelType = ModelType.CODE_REVIEW,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        stream: bool = False,
    ) -> str:
        """Generate text using specified model"""
        if not self._initialized:
            await self.initialize()
            
        # Load model if not already loaded
        if self.models[model_type] is None:
            success = await self.load_model(model_type)
            if not success:
                raise RuntimeError(f"Failed to load model: {model_type.value}")
                
        model = self.models[model_type]
        config = self.configs[model_type]
        
        # Use config defaults if not specified
        temp = temperature if temperature is not None else config.temperature
        max_tok = max_tokens if max_tokens is not None else config.max_tokens
        
        try:
            loop = asyncio.get_event_loop()
            
            if stream:
                # Streaming not implemented in this version
                raise NotImplementedError("Streaming not yet supported")
            else:
                # Generate in thread pool
                response = await loop.run_in_executor(
                    None,
                    lambda: model(
                        prompt,
                        max_tokens=max_tok,
                        temperature=temp,
                        top_p=config.top_p,
                        top_k=config.top_k,
                        stop=stop or [],
                        echo=False,
                    )
                )
                
                return response["choices"][0]["text"].strip()
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
            
    async def analyze_code(
        self,
        code: str,
        language: str,
        analysis_type: str = "review",
    ) -> Dict[str, Any]:
        """Analyze code using the code review model"""
        prompt = self._build_code_analysis_prompt(code, language, analysis_type)
        
        response = await self.generate(
            prompt=prompt,
            model_type=ModelType.CODE_REVIEW,
            temperature=0.1,
            max_tokens=2048,
        )
        
        return self._parse_code_analysis(response)
        
    async def generate_architecture_insights(
        self,
        architecture_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate architecture insights"""
        prompt = self._build_architecture_prompt(architecture_data)
        
        response = await self.generate(
            prompt=prompt,
            model_type=ModelType.GENERAL,
            temperature=0.2,
            max_tokens=1024,
        )
        
        return {"insights": response, "recommendations": self._extract_recommendations(response)}
        
    def _build_code_analysis_prompt(
        self,
        code: str,
        language: str,
        analysis_type: str,
    ) -> str:
        """Build prompt for code analysis"""
        if analysis_type == "review":
            return f"""You are an expert code reviewer. Analyze the following {language} code and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Security vulnerabilities
4. Performance concerns
5. Best practice violations
6. Suggestions for improvement

Code:
```{language}
{code}
```

Provide your analysis in a structured format."""

        elif analysis_type == "security":
            return f"""You are a security expert. Analyze the following {language} code for security vulnerabilities:

Code:
```{language}
{code}
```

Identify:
1. Security vulnerabilities (SQL injection, XSS, etc.)
2. Authentication/authorization issues
3. Data exposure risks
4. Cryptographic weaknesses
5. Input validation problems

Provide severity levels and remediation steps."""

        elif analysis_type == "performance":
            return f"""You are a performance optimization expert. Analyze the following {language} code:

Code:
```{language}
{code}
```

Identify:
1. Performance bottlenecks
2. Inefficient algorithms
3. Memory leaks
4. Resource management issues
5. Optimization opportunities

Provide specific recommendations."""

        else:
            return f"Analyze this {language} code:\n\n{code}"
            
    def _build_architecture_prompt(self, architecture_data: Dict[str, Any]) -> str:
        """Build prompt for architecture analysis"""
        return f"""You are a software architecture expert. Analyze the following system architecture:

Components: {architecture_data.get('components', [])}
Dependencies: {architecture_data.get('dependencies', [])}
Patterns: {architecture_data.get('patterns', [])}

Provide:
1. Architecture quality assessment
2. Design pattern analysis
3. Scalability concerns
4. Maintainability issues
5. Recommendations for improvement

Be specific and actionable."""

    def _parse_code_analysis(self, response: str) -> Dict[str, Any]:
        """Parse code analysis response"""
        # Simple parsing - can be enhanced with structured output
        return {
            "analysis": response,
            "issues": self._extract_issues(response),
            "suggestions": self._extract_suggestions(response),
            "severity": self._assess_severity(response),
        }
        
    def _extract_issues(self, text: str) -> List[str]:
        """Extract issues from analysis"""
        issues = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['bug', 'issue', 'problem', 'vulnerability', 'error']):
                issues.append(line.strip())
        return issues
        
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract suggestions from analysis"""
        suggestions = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['suggest', 'recommend', 'should', 'consider', 'improve']):
                suggestions.append(line.strip())
        return suggestions
        
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from text"""
        return self._extract_suggestions(text)
        
    def _assess_severity(self, text: str) -> str:
        """Assess overall severity"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['critical', 'severe', 'high risk', 'vulnerability']):
            return "high"
        elif any(word in text_lower for word in ['moderate', 'medium', 'warning']):
            return "medium"
        else:
            return "low"
            
    async def get_model_info(self, model_type: ModelType) -> Dict[str, Any]:
        """Get information about a model"""
        config = self.configs.get(model_type)
        if not config:
            return {"error": "Model not configured"}
            
        return {
            "type": model_type.value,
            "path": config.model_path,
            "loaded": self.models[model_type] is not None,
            "exists": os.path.exists(config.model_path),
            "config": {
                "n_ctx": config.n_ctx,
                "n_threads": config.n_threads,
                "n_gpu_layers": config.n_gpu_layers,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Check health of LLM service"""
        return {
            "initialized": self._initialized,
            "models": {
                model_type.value: {
                    "loaded": self.models[model_type] is not None,
                    "configured": model_type in self.configs,
                    "exists": os.path.exists(self.configs[model_type].model_path) if model_type in self.configs else False,
                }
                for model_type in ModelType
            }
        }


# Global instance
llm_service = LLMService()
