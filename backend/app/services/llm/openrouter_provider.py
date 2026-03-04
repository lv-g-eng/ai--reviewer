"""
OpenRouter Provider Implementation

OpenRouter 提供统一接口访问多个 LLM 提供商的模型。
支持 OpenAI、Anthropic、Google 等多个提供商。
"""

import logging
from typing import Optional
from openai import AsyncOpenAI
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from .base import BaseLLMProvider, LLMProviderType, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter 提供者实现
    
    OpenRouter 提供统一的 API 接口访问多个 LLM 提供商：
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
    - Google (Gemini Pro)
    - Meta (Llama 2, Llama 3)
    - 以及更多模型
    
    使用 OpenAI 兼容的 API 格式，便于集成。
    """
    
    def __init__(
        self,
        model: str = "anthropic/claude-3.5-sonnet",
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: int = 60,
        app_name: str = "AI Code Review Platform"
    ):
        """
        初始化 OpenRouter 提供者
        
        Args:
            model: 模型标识符 (例如: "anthropic/claude-3.5-sonnet", "openai/gpt-4")
            api_key: OpenRouter API 密钥
            base_url: OpenRouter API 基础 URL
            timeout: 请求超时时间（秒）
            app_name: 应用名称（用于 OpenRouter 统计）
        """
        super().__init__(model, api_key)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            default_headers={
                "HTTP-Referer": "https://github.com/ai-code-review",
                "X-Title": app_name
            }
        )
        self.timeout = timeout
        self.app_name = app_name
    
    @retry(
        retry=retry_if_exception_type((
            openai.APIConnectionError,
            openai.RateLimitError,
            openai.InternalServerError
        )),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        使用 OpenRouter API 生成响应
        
        对临时性错误（连接错误、速率限制、内部服务器错误）
        实现指数退避重试策略。
        
        Args:
            request: LLM 请求参数
            
        Returns:
            包含内容和元数据的 LLM 响应
            
        Raises:
            Exception: 重试后生成失败
        """
        try:
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
            
            # 如果请求 JSON 模式，添加响应格式
            if request.json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = await self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            usage = response.usage
            
            # 跟踪使用情况
            self.total_tokens += usage.total_tokens
            
            # OpenRouter 在响应头中返回实际成本
            # 这里使用估算值，实际成本可从响应头获取
            cost = self._estimate_cost(usage.prompt_tokens, usage.completion_tokens)
            self.total_cost += cost
            
            logger.info(
                f"OpenRouter 生成成功: {usage.total_tokens} tokens, 估算成本 ${cost:.4f}",
                extra={
                    "provider": "openrouter",
                    "model": self.model,
                    "tokens": usage.total_tokens,
                    "cost": cost
                }
            )
            
            return LLMResponse(
                content=content,
                provider="openrouter",
                model=self.model,
                tokens={
                    "prompt": usage.prompt_tokens,
                    "completion": usage.completion_tokens,
                    "total": usage.total_tokens
                },
                cost=cost
            )
            
        except Exception as e:
            logger.error(
                f"OpenRouter API 错误: {str(e)}",
                extra={"provider": "openrouter", "model": self.model},
                exc_info=True
            )
            raise Exception(f"OpenRouter API 错误: {str(e)}")
    
    def get_provider_type(self) -> LLMProviderType:
        """获取提供者类型"""
        return LLMProviderType.OPENROUTER
    
    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        估算 OpenRouter API 成本
        
        不同模型的定价不同，这里提供常见模型的估算：
        - Claude 3.5 Sonnet: $3/1M prompt tokens, $15/1M completion tokens
        - GPT-4 Turbo: $10/1M prompt tokens, $30/1M completion tokens
        - GPT-3.5 Turbo: $0.5/1M prompt tokens, $1.5/1M completion tokens
        
        注意：实际成本应从 OpenRouter 响应头中获取
        
        Args:
            prompt_tokens: 提示词 token 数量
            completion_tokens: 完成 token 数量
            
        Returns:
            估算的总成本（美元）
        """
        # 根据模型名称估算成本
        model_lower = self.model.lower()
        
        if "claude-3.5-sonnet" in model_lower or "claude-3-5-sonnet" in model_lower:
            prompt_cost_per_1m = 3.0
            completion_cost_per_1m = 15.0
        elif "claude-3-opus" in model_lower:
            prompt_cost_per_1m = 15.0
            completion_cost_per_1m = 75.0
        elif "gpt-4-turbo" in model_lower or "gpt-4-1106" in model_lower:
            prompt_cost_per_1m = 10.0
            completion_cost_per_1m = 30.0
        elif "gpt-4" in model_lower:
            prompt_cost_per_1m = 30.0
            completion_cost_per_1m = 60.0
        elif "gpt-3.5-turbo" in model_lower:
            prompt_cost_per_1m = 0.5
            completion_cost_per_1m = 1.5
        else:
            # 默认使用中等价格估算
            prompt_cost_per_1m = 5.0
            completion_cost_per_1m = 15.0
        
        prompt_cost = (prompt_tokens / 1_000_000) * prompt_cost_per_1m
        completion_cost = (completion_tokens / 1_000_000) * completion_cost_per_1m
        
        return prompt_cost + completion_cost
