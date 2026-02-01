"""
LLM Manager - Handles model loading and inference
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

from .config import settings

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Available model types"""
    CODE_REVIEW = "code_review"
    GENERAL = "general"
    VISION = "vision"


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


class LLMManager:
    """Manages LLM models and inference"""
    
    def __init__(self):
        self.models: Dict[ModelType, Optional[Llama]] = {
            ModelType.CODE_REVIEW: None,
            ModelType.GENERAL: None,
            ModelType.VISION: None,
        }
        self.configs: Dict[ModelType, LLMConfig] = {}
        self.models_dir = Path(settings.MODELS_DIR)
        self._initialized = False
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize LLM manager"""
        if self._initialized:
            return
            
        if Llama is None:
            logger.warning("llama-cpp-python not installed")
            return
            
        logger.info("Initializing LLM manager...")
        
        # Configure models
        self.configs = {
            ModelType.CODE_REVIEW: LLMConfig(
                model_path=str(self.models_dir / "Qwen2.5-Coder-14B-Instruct-Q4_0.gguf"),
                n_ctx=8192,
                n_threads=settings.LLM_THREADS,
                n_gpu_layers=settings.LLM_GPU_LAYERS,
                temperature=0.1,
                max_tokens=2048,
            ),
            ModelType.GENERAL: LLMConfig(
                model_path=str(self.models_dir / "DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf"),
                n_ctx=4096,
                n_threads=settings.LLM_THREADS,
                n_gpu_layers=settings.LLM_GPU_LAYERS,
                temperature=0.3,
                max_tokens=1024,
            ),
            ModelType.VISION: LLMConfig(
                model_path=str(self.models_dir / "Qwen3-VL-8B-Instruct-abliterated-v2.0.Q4_K_M.gguf"),
                n_ctx=4096,
                n_threads=settings.LLM_THREADS,
                n_gpu_layers=settings.LLM_GPU_LAYERS,
                temperature=0.2,
                max_tokens=1024,
            ),
        }
        
        self._initialized = True
        logger.info("LLM manager initialized")
        
    async def load_model(self, model_type: ModelType) -> bool:
        """Load a specific model"""
        async with self._lock:
            if self.models[model_type] is not None:
                return True
                
            config = self.configs.get(model_type)
            if not config:
                logger.error(f"No configuration for {model_type}")
                return False
                
            if not os.path.exists(config.model_path):
                logger.error(f"Model file not found: {config.model_path}")
                return False
                
            try:
                logger.info(f"Loading model: {model_type.value}")
                
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
                logger.info(f"Model loaded: {model_type.value}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                return False
                
    async def unload_model(self, model_type: ModelType):
        """Unload a model"""
        async with self._lock:
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
    ) -> str:
        """Generate text"""
        if not self._initialized:
            await self.initialize()
            
        if self.models[model_type] is None:
            success = await self.load_model(model_type)
            if not success:
                raise RuntimeError(f"Failed to load model: {model_type.value}")
                
        model = self.models[model_type]
        config = self.configs[model_type]
        
        temp = temperature if temperature is not None else config.temperature
        max_tok = max_tokens if max_tokens is not None else config.max_tokens
        
        try:
            loop = asyncio.get_event_loop()
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
        """Analyze code"""
        prompt = self._build_code_prompt(code, language, analysis_type)
        response = await self.generate(
            prompt=prompt,
            model_type=ModelType.CODE_REVIEW,
            temperature=0.1,
            max_tokens=2048,
        )
        
        return self._parse_analysis(response)
        
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
        
        return {
            "insights": response,
            "recommendations": self._extract_recommendations(response),
        }
        
    def _build_code_prompt(self, code: str, language: str, analysis_type: str) -> str:
        """Build code analysis prompt"""
        if analysis_type == "review":
            return f"""<|im_start|>system
You are an expert code reviewer. Analyze code for quality, bugs, security, and best practices.<|im_end|>
<|im_start|>user
Analyze this {language} code:

```{language}
{code}
```

Provide:
1. Code quality assessment
2. Potential bugs
3. Security issues
4. Performance concerns
5. Improvement suggestions<|im_end|>
<|im_start|>assistant"""

        elif analysis_type == "security":
            return f"""<|im_start|>system
You are a security expert. Find vulnerabilities in code.<|im_end|>
<|im_start|>user
Security analysis for {language} code:

```{language}
{code}
```

Identify security vulnerabilities with severity levels.<|im_end|>
<|im_start|>assistant"""

        else:
            return f"""<|im_start|>system
You are a code analysis expert.<|im_end|>
<|im_start|>user
Analyze this {language} code:

{code}<|im_end|>
<|im_start|>assistant"""
            
    def _build_architecture_prompt(self, data: Dict[str, Any]) -> str:
        """Build architecture analysis prompt"""
        return f"""<|im_start|>system
You are a software architecture expert.<|im_end|>
<|im_start|>user
Analyze this system architecture:

Components: {data.get('components', [])}
Dependencies: {data.get('dependencies', [])}
Patterns: {data.get('patterns', [])}

Provide architecture quality assessment and recommendations.<|im_end|>
<|im_start|>assistant"""

    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """Parse analysis response"""
        return {
            "analysis": response,
            "issues": self._extract_issues(response),
            "suggestions": self._extract_suggestions(response),
            "severity": self._assess_severity(response),
        }
        
    def _extract_issues(self, text: str) -> List[str]:
        """Extract issues"""
        issues = []
        for line in text.split('\n'):
            if any(k in line.lower() for k in ['bug', 'issue', 'problem', 'vulnerability']):
                issues.append(line.strip())
        return issues
        
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract suggestions"""
        suggestions = []
        for line in text.split('\n'):
            if any(k in line.lower() for k in ['suggest', 'recommend', 'should', 'consider']):
                suggestions.append(line.strip())
        return suggestions
        
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations"""
        return self._extract_suggestions(text)
        
    def _assess_severity(self, text: str) -> str:
        """Assess severity"""
        text_lower = text.lower()
        if any(w in text_lower for w in ['critical', 'severe', 'high']):
            return "high"
        elif any(w in text_lower for w in ['moderate', 'medium']):
            return "medium"
        return "low"
        
    async def get_model_info(self, model_type: ModelType) -> Dict[str, Any]:
        """Get model info"""
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
            }
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Health check"""
        return {
            "initialized": self._initialized,
            "models": {
                mt.value: {
                    "loaded": self.models[mt] is not None,
                    "configured": mt in self.configs,
                    "exists": os.path.exists(self.configs[mt].model_path) if mt in self.configs else False,
                }
                for mt in ModelType
            }
        }


llm_manager = LLMManager()
