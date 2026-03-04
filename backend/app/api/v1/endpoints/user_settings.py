"""
用户设置 API 端点

管理用户的个人设置，包括 API 密钥配置
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.database.postgresql import get_db
from app.auth import TokenPayload, get_current_user, User

router = APIRouter()


class UserAPISettings(BaseModel):
    """用户 API 设置模型"""
    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: Optional[str] = None
    default_llm_model: Optional[str] = None


class UpdateAPISettingsRequest(BaseModel):
    """更新 API 设置请求"""
    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: Optional[str] = None
    default_llm_model: Optional[str] = None


class APISettingsResponse(BaseModel):
    """API 设置响应"""
    openrouter_api_key_set: bool
    openai_api_key_set: bool
    anthropic_api_key_set: bool
    default_llm_provider: Optional[str]
    default_llm_model: Optional[str]
    message: str


@router.get("/api-settings", response_model=APISettingsResponse)
async def get_user_api_settings(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    获取用户的 API 设置
    
    返回 API 密钥是否已设置（不返回实际密钥）
    """
    # 获取用户信息
    result = await db.execute(
        select(User).filter(User.id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查用户的 metadata 中是否有 API 设置
    metadata = user.metadata or {}
    api_settings = metadata.get('api_settings', {})
    
    return APISettingsResponse(
        openrouter_api_key_set=bool(api_settings.get('openrouter_api_key')),
        openai_api_key_set=bool(api_settings.get('openai_api_key')),
        anthropic_api_key_set=bool(api_settings.get('anthropic_api_key')),
        default_llm_provider=api_settings.get('default_llm_provider'),
        default_llm_model=api_settings.get('default_llm_model'),
        message="API settings retrieved successfully"
    )


@router.put("/api-settings", response_model=APISettingsResponse)
async def update_user_api_settings(
    settings: UpdateAPISettingsRequest,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    更新用户的 API 设置
    
    允许用户配置自己的 API 密钥和默认 LLM 提供者
    """
    # 获取用户信息
    result = await db.execute(
        select(User).filter(User.id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 获取现有的 metadata
    metadata = user.metadata or {}
    api_settings = metadata.get('api_settings', {})
    
    # 更新 API 设置
    if settings.openrouter_api_key is not None:
        if settings.openrouter_api_key.strip():
            api_settings['openrouter_api_key'] = settings.openrouter_api_key.strip()
        else:
            api_settings.pop('openrouter_api_key', None)
    
    if settings.openai_api_key is not None:
        if settings.openai_api_key.strip():
            api_settings['openai_api_key'] = settings.openai_api_key.strip()
        else:
            api_settings.pop('openai_api_key', None)
    
    if settings.anthropic_api_key is not None:
        if settings.anthropic_api_key.strip():
            api_settings['anthropic_api_key'] = settings.anthropic_api_key.strip()
        else:
            api_settings.pop('anthropic_api_key', None)
    
    if settings.default_llm_provider is not None:
        if settings.default_llm_provider.strip():
            api_settings['default_llm_provider'] = settings.default_llm_provider.strip()
        else:
            api_settings.pop('default_llm_provider', None)
    
    if settings.default_llm_model is not None:
        if settings.default_llm_model.strip():
            api_settings['default_llm_model'] = settings.default_llm_model.strip()
        else:
            api_settings.pop('default_llm_model', None)
    
    # 更新 metadata
    metadata['api_settings'] = api_settings
    metadata['updated_at'] = datetime.utcnow().isoformat()
    
    # 保存到数据库
    await db.execute(
        update(User)
        .where(User.id == current_user.user_id)
        .values(metadata=metadata)
    )
    await db.commit()
    
    return APISettingsResponse(
        openrouter_api_key_set=bool(api_settings.get('openrouter_api_key')),
        openai_api_key_set=bool(api_settings.get('openai_api_key')),
        anthropic_api_key_set=bool(api_settings.get('anthropic_api_key')),
        default_llm_provider=api_settings.get('default_llm_provider'),
        default_llm_model=api_settings.get('default_llm_model'),
        message="API settings updated successfully"
    )


@router.delete("/api-settings/{provider}", response_model=APISettingsResponse)
async def delete_user_api_key(
    provider: str,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    删除指定提供者的 API 密钥
    
    provider: openrouter, openai, anthropic
    """
    if provider not in ['openrouter', 'openai', 'anthropic']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider: {provider}. Must be one of: openrouter, openai, anthropic"
        )
    
    # 获取用户信息
    result = await db.execute(
        select(User).filter(User.id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 获取现有的 metadata
    metadata = user.metadata or {}
    api_settings = metadata.get('api_settings', {})
    
    # 删除指定的 API 密钥
    key_name = f'{provider}_api_key'
    api_settings.pop(key_name, None)
    
    # 更新 metadata
    metadata['api_settings'] = api_settings
    metadata['updated_at'] = datetime.utcnow().isoformat()
    
    # 保存到数据库
    await db.execute(
        update(User)
        .where(User.id == current_user.user_id)
        .values(metadata=metadata)
    )
    await db.commit()
    
    return APISettingsResponse(
        openrouter_api_key_set=bool(api_settings.get('openrouter_api_key')),
        openai_api_key_set=bool(api_settings.get('openai_api_key')),
        anthropic_api_key_set=bool(api_settings.get('anthropic_api_key')),
        default_llm_provider=api_settings.get('default_llm_provider'),
        default_llm_model=api_settings.get('default_llm_model'),
        message=f"{provider.capitalize()} API key deleted successfully"
    )
