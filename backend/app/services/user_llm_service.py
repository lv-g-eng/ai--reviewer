"""
用户 LLM 服务

根据用户配置动态选择 LLM 提供者和 API 密钥
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.auth import User
from app.services.llm.factory import LLMProviderFactory
from app.services.llm.base import BaseLLMProvider, LLMProviderType

logger = logging.getLogger(__name__)


class UserLLMService:
    """
    用户 LLM 服务
    
    根据用户配置动态创建 LLM 提供者实例
    优先级：用户配置 > 系统默认配置
    """
    
    @staticmethod
    async def get_user_llm_provider(
        db: AsyncSession,
        user_id: str,
        provider_type: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        获取用户的 LLM 提供者实例
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            provider_type: 可选的提供者类型，如果未指定则使用用户默认配置
            model: 可选的模型名称，如果未指定则使用用户默认配置
            
        Returns:
            配置好的 LLM 提供者实例
        """
        # 获取用户信息
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User {user_id} not found, using system default LLM provider")
            return UserLLMService._get_system_default_provider(provider_type, model)
        
        # 获取用户的 API 设置
        metadata = user.metadata or {}
        api_settings = metadata.get('api_settings', {})
        
        # 确定使用的提供者类型
        if not provider_type:
            provider_type = api_settings.get('default_llm_provider') or settings.DEFAULT_LLM_PROVIDER
        
        # 确定使用的模型
        if not model:
            model = api_settings.get('default_llm_model') or settings.DEFAULT_LLM_MODEL
        
        # 获取用户配置的 API 密钥
        user_api_key = None
        if provider_type == 'openrouter':
            user_api_key = api_settings.get('openrouter_api_key')
        elif provider_type == 'openai':
            user_api_key = api_settings.get('openai_api_key')
        elif provider_type == 'anthropic':
            user_api_key = api_settings.get('anthropic_api_key')
        
        # 如果用户有配置 API 密钥，使用用户的密钥
        if user_api_key:
            logger.info(
                f"Using user-configured API key for {provider_type}",
                extra={"user_id": user_id, "provider": provider_type}
            )
            return UserLLMService._create_provider_with_key(
                provider_type, model, user_api_key
            )
        
        # 否则使用系统默认配置
        logger.info(
            f"Using system default API key for {provider_type}",
            extra={"user_id": user_id, "provider": provider_type}
        )
        return UserLLMService._get_system_default_provider(provider_type, model)
    
    @staticmethod
    def _create_provider_with_key(
        provider_type: str,
        model: str,
        api_key: str
    ) -> BaseLLMProvider:
        """
        使用指定的 API 密钥创建提供者实例
        
        Args:
            provider_type: 提供者类型
            model: 模型名称
            api_key: API 密钥
            
        Returns:
            LLM 提供者实例
        """
        # 转换提供者类型
        provider_enum = {
            'openrouter': LLMProviderType.OPENROUTER,
            'openai': LLMProviderType.OPENAI,
            'anthropic': LLMProviderType.ANTHROPIC,
        }.get(provider_type.lower())
        
        if not provider_enum:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        # 创建提供者实例（不使用缓存，因为每个用户的密钥不同）
        return LLMProviderFactory.create_provider(
            provider_type=provider_enum,
            model=model,
            api_key=api_key
        )
    
    @staticmethod
    def _get_system_default_provider(
        provider_type: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        获取系统默认的 LLM 提供者
        
        Args:
            provider_type: 可选的提供者类型
            model: 可选的模型名称
            
        Returns:
            LLM 提供者实例
        """
        provider_type = provider_type or settings.DEFAULT_LLM_PROVIDER
        model = model or settings.DEFAULT_LLM_MODEL
        
        # 转换提供者类型
        provider_enum = {
            'openrouter': LLMProviderType.OPENROUTER,
            'openai': LLMProviderType.OPENAI,
            'anthropic': LLMProviderType.ANTHROPIC,
        }.get(provider_type.lower())
        
        if not provider_enum:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        # 使用工厂创建提供者（使用系统配置的 API 密钥）
        return LLMProviderFactory.get_provider(
            provider_type=provider_enum,
            model=model
        )
    
    @staticmethod
    async def get_user_api_settings(
        db: AsyncSession,
        user_id: str
    ) -> dict:
        """
        获取用户的 API 设置
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            
        Returns:
            用户的 API 设置字典
        """
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {}
        
        metadata = user.metadata or {}
        return metadata.get('api_settings', {})
