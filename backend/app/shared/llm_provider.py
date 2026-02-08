"""
LLM Provider abstraction with failover logic

Provides unified interface for multiple LLM providers (OpenAI, Anthropic, Ollama)
with automatic failover on provider failures.

Validates Requirements: 1.7, 3.1, 3.7
"""

import logging
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio

from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
from .exceptions import LLMProviderException


logger = logging.getLogger(__name__)


class LLMProviderType(str, Enum):
    """Supported LLM provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class LLMProviderConfig:
    """Configuration for an LLM provider"""
    provider_type: LLMProviderType
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 60
    priority: int = 1  # Lower = higher priority
    rate_limit: int = 60  # Requests per minute
    
    def __post_init__(self):
        """Validate configuration"""
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if self.timeout < 1:
            raise ValueError("timeout must be >= 1")
        if self.priority < 1:
            raise ValueError("priority must be >= 1")


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMProviderConfig):
        """
        Initialize LLM provider.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.circuit_breaker = get_circuit_breaker(
            f"llm_{config.provider_type.value}_{config.model}",
            CircuitBreakerConfig(
                failure_threshold=3,
                success_threshold=2,
                timeout=30,
            )
        )
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
            
        Raises:
            LLMProviderException: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate text with conversation context.
        
        Args:
            prompt: User prompt
            context: List of previous messages [{"role": "user/assistant", "content": "..."}]
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
            
        Raises:
            LLMProviderException: If generation fails
        """
        pass
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return f"{self.config.provider_type.value}/{self.config.model}"


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation"""
    
    def __init__(self, config: LLMProviderConfig):
        super().__init__(config)
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
                timeout=config.timeout,
            )
        except ImportError:
            raise LLMProviderException(
                "OpenAI library not installed. Install with: pip install openai",
                provider="openai",
                error_code="IMPORT_ERROR"
            )
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using OpenAI API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            def _call_api():
                return asyncio.create_task(
                    self.client.chat.completions.create(
                        model=self.config.model,
                        messages=messages,
                        max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                        temperature=kwargs.get('temperature', self.config.temperature),
                    )
                )
            
            response = await self.circuit_breaker.call(_call_api)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(
                f"OpenAI generation failed: {e}",
                extra={'provider': 'openai', 'model': self.config.model}
            )
            raise LLMProviderException(
                f"OpenAI generation failed: {str(e)}",
                provider="openai",
                model=self.config.model,
                error_code="GENERATION_FAILED"
            )
    
    async def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate text with conversation context"""
        try:
            messages = context + [{"role": "user", "content": prompt}]
            
            def _call_api():
                return asyncio.create_task(
                    self.client.chat.completions.create(
                        model=self.config.model,
                        messages=messages,
                        max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                        temperature=kwargs.get('temperature', self.config.temperature),
                    )
                )
            
            response = await self.circuit_breaker.call(_call_api)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(
                f"OpenAI generation with context failed: {e}",
                extra={'provider': 'openai', 'model': self.config.model}
            )
            raise LLMProviderException(
                f"OpenAI generation failed: {str(e)}",
                provider="openai",
                model=self.config.model,
                error_code="GENERATION_FAILED"
            )


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) LLM provider implementation"""
    
    def __init__(self, config: LLMProviderConfig):
        super().__init__(config)
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(
                api_key=config.api_key,
                timeout=config.timeout,
            )
        except ImportError:
            raise LLMProviderException(
                "Anthropic library not installed. Install with: pip install anthropic",
                provider="anthropic",
                error_code="IMPORT_ERROR"
            )
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using Anthropic API"""
        try:
            def _call_api():
                return asyncio.create_task(
                    self.client.messages.create(
                        model=self.config.model,
                        max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                        temperature=kwargs.get('temperature', self.config.temperature),
                        system=system_prompt or "",
                        messages=[{"role": "user", "content": prompt}],
                    )
                )
            
            response = await self.circuit_breaker.call(_call_api)
            return response.content[0].text
            
        except Exception as e:
            logger.error(
                f"Anthropic generation failed: {e}",
                extra={'provider': 'anthropic', 'model': self.config.model}
            )
            raise LLMProviderException(
                f"Anthropic generation failed: {str(e)}",
                provider="anthropic",
                model=self.config.model,
                error_code="GENERATION_FAILED"
            )
    
    async def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate text with conversation context"""
        try:
            messages = context + [{"role": "user", "content": prompt}]
            
            def _call_api():
                return asyncio.create_task(
                    self.client.messages.create(
                        model=self.config.model,
                        max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                        temperature=kwargs.get('temperature', self.config.temperature),
                        messages=messages,
                    )
                )
            
            response = await self.circuit_breaker.call(_call_api)
            return response.content[0].text
            
        except Exception as e:
            logger.error(
                f"Anthropic generation with context failed: {e}",
                extra={'provider': 'anthropic', 'model': self.config.model}
            )
            raise LLMProviderException(
                f"Anthropic generation failed: {str(e)}",
                provider="anthropic",
                model=self.config.model,
                error_code="GENERATION_FAILED"
            )


class OllamaProvider(LLMProvider):
    """Ollama (local) LLM provider implementation"""
    
    def __init__(self, config: LLMProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using Ollama API"""
        try:
            import aiohttp
            
            async def _call_api():
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": self.config.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": kwargs.get('temperature', self.config.temperature),
                            "num_predict": kwargs.get('max_tokens', self.config.max_tokens),
                        }
                    }
                    if system_prompt:
                        payload["system"] = system_prompt
                    
                    async with session.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                    ) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result.get("response", "")
            
            return await self.circuit_breaker.call(_call_api)
            
        except Exception as e:
            logger.error(
                f"Ollama generation failed: {e}",
                extra={'provider': 'ollama', 'model': self.config.model}
            )
            raise LLMProviderException(
                f"Ollama generation failed: {str(e)}",
                provider="ollama",
                model=self.config.model,
                error_code="GENERATION_FAILED"
            )
    
    async def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate text with conversation context"""
        # Ollama doesn't have native context support, concatenate messages
        context_str = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in context
        ])
        full_prompt = f"{context_str}\nuser: {prompt}\nassistant:"
        return await self.generate(full_prompt, **kwargs)



class LLMOrchestrator:
    """
    Orchestrates multiple LLM providers with automatic failover.
    
    Validates Requirements: 1.7, 3.7
    """
    
    def __init__(self, providers: List[LLMProviderConfig]):
        """
        Initialize LLM orchestrator.
        
        Args:
            providers: List of provider configurations (ordered by priority)
        """
        if not providers:
            raise ValueError("At least one provider configuration is required")
        
        # Sort providers by priority (lower = higher priority)
        sorted_providers = sorted(providers, key=lambda p: p.priority)
        
        # Initialize provider instances
        self.providers: List[LLMProvider] = []
        for config in sorted_providers:
            try:
                provider = self._create_provider(config)
                self.providers.append(provider)
                logger.info(
                    f"Initialized LLM provider: {provider.get_provider_name()}",
                    extra={'provider': config.provider_type.value, 'model': config.model}
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize provider {config.provider_type.value}/{config.model}: {e}",
                    extra={'provider': config.provider_type.value, 'model': config.model}
                )
        
        if not self.providers:
            raise LLMProviderException(
                "No LLM providers could be initialized",
                provider="orchestrator",
                error_code="NO_PROVIDERS"
            )
        
        logger.info(
            f"LLM Orchestrator initialized with {len(self.providers)} provider(s)",
            extra={'provider_count': len(self.providers)}
        )
    
    def _create_provider(self, config: LLMProviderConfig) -> LLMProvider:
        """Create provider instance based on type"""
        if config.provider_type == LLMProviderType.OPENAI:
            return OpenAIProvider(config)
        elif config.provider_type == LLMProviderType.ANTHROPIC:
            return AnthropicProvider(config)
        elif config.provider_type == LLMProviderType.OLLAMA:
            return OllamaProvider(config)
        else:
            raise ValueError(f"Unsupported provider type: {config.provider_type}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text with automatic failover.
        
        Tries providers in priority order until one succeeds.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated text
            
        Raises:
            LLMProviderException: If all providers fail
            
        Validates Requirements: 1.7, 3.7
        """
        errors = []
        
        for provider in self.providers:
            try:
                logger.debug(
                    f"Attempting generation with {provider.get_provider_name()}",
                    extra={'provider': provider.config.provider_type.value}
                )
                
                result = await provider.generate(prompt, system_prompt, **kwargs)
                
                logger.info(
                    f"Successfully generated with {provider.get_provider_name()}",
                    extra={'provider': provider.config.provider_type.value}
                )
                
                return result
                
            except Exception as e:
                error_msg = f"{provider.get_provider_name()}: {str(e)}"
                errors.append(error_msg)
                
                logger.warning(
                    f"Provider {provider.get_provider_name()} failed, trying next",
                    extra={
                        'provider': provider.config.provider_type.value,
                        'error': str(e)
                    }
                )
                continue
        
        # All providers failed
        error_summary = "; ".join(errors)
        logger.error(
            f"All LLM providers failed: {error_summary}",
            extra={'provider_count': len(self.providers)}
        )
        
        raise LLMProviderException(
            f"All LLM providers failed: {error_summary}",
            provider="orchestrator",
            error_code="ALL_PROVIDERS_FAILED",
            details={'errors': errors}
        )
    
    async def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate text with context and automatic failover.
        
        Args:
            prompt: User prompt
            context: Conversation context
            **kwargs: Additional parameters
            
        Returns:
            Generated text
            
        Raises:
            LLMProviderException: If all providers fail
            
        Validates Requirements: 1.7, 3.7
        """
        errors = []
        
        for provider in self.providers:
            try:
                logger.debug(
                    f"Attempting generation with context using {provider.get_provider_name()}",
                    extra={'provider': provider.config.provider_type.value}
                )
                
                result = await provider.generate_with_context(prompt, context, **kwargs)
                
                logger.info(
                    f"Successfully generated with context using {provider.get_provider_name()}",
                    extra={'provider': provider.config.provider_type.value}
                )
                
                return result
                
            except Exception as e:
                error_msg = f"{provider.get_provider_name()}: {str(e)}"
                errors.append(error_msg)
                
                logger.warning(
                    f"Provider {provider.get_provider_name()} failed, trying next",
                    extra={
                        'provider': provider.config.provider_type.value,
                        'error': str(e)
                    }
                )
                continue
        
        # All providers failed
        error_summary = "; ".join(errors)
        logger.error(
            f"All LLM providers failed: {error_summary}",
            extra={'provider_count': len(self.providers)}
        )
        
        raise LLMProviderException(
            f"All LLM providers failed: {error_summary}",
            provider="orchestrator",
            error_code="ALL_PROVIDERS_FAILED",
            details={'errors': errors}
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [provider.get_provider_name() for provider in self.providers]
    
    def get_provider_count(self) -> int:
        """Get number of configured providers"""
        return len(self.providers)
