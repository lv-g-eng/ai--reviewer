"""
Property-based tests for Agentic AI Service multi-provider LLM support

Tests Property 13: Multi-Provider LLM Support
For any reasoning request, the Agentic AI Service SHALL successfully process it 
using any of the configured LLM providers (GPT-4, Claude 3.5, Ollama).

Validates Requirements: 3.1
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from app.shared.llm_provider import (
    LLMOrchestrator,
    LLMProviderConfig,
    LLMProviderType,
    OllamaProvider,
)
from app.shared.exceptions import LLMProviderException
from app.services.agentic_ai_service import AgenticAIService


# Strategy for generating prompts
@st.composite
def prompt_strategy(draw):
    """Generate valid prompts for testing"""
    prompt_types = [
        "Analyze this code for issues",
        "Explain this technical concept",
        "Suggest improvements for this function",
        "Identify security vulnerabilities",
        "Recommend refactoring strategies",
    ]
    
    base_prompt = draw(st.sampled_from(prompt_types))
    detail = draw(st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))))
    
    return f"{base_prompt}: {detail}"


# Strategy for generating system prompts
@st.composite
def system_prompt_strategy(draw):
    """Generate valid system prompts"""
    roles = [
        "You are an expert code reviewer",
        "You are a software architect",
        "You are a security analyst",
        "You are a clean code expert",
        "You are a refactoring specialist",
    ]
    
    return draw(st.sampled_from(roles))


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
@settings(
    max_examples=10,  # Reduced for LLM tests
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    prompt=prompt_strategy(),
    system_prompt=system_prompt_strategy(),
)
@pytest.mark.asyncio
async def test_property_multi_provider_support_ollama(prompt, system_prompt):
    """
    Property 13: Multi-Provider LLM Support
    
    For any reasoning request, the Agentic AI Service SHALL successfully process it
    using any of the configured LLM providers.
    
    This test validates Ollama provider support.
    
    **Validates: Requirements 3.1**
    """
    # Create mock Ollama provider
    mock_response = "This is a test response from the LLM."
    
    with patch('aiohttp.ClientSession') as mock_session_class:
        # Mock the HTTP response
        mock_response_obj = AsyncMock()
        mock_response_obj.raise_for_status = MagicMock()
        mock_response_obj.json = AsyncMock(return_value={"response": mock_response})
        
        # Mock the post method to return the response
        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_post.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session to return the post mock
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Make ClientSession() return the mock session
        mock_session_class.return_value = mock_session
        
        # Create Ollama provider
        config = LLMProviderConfig(
            provider_type=LLMProviderType.OLLAMA,
            model="qwen2.5-coder:14b",
            base_url="http://localhost:11434",
            max_tokens=1000,
            temperature=0.3,
            priority=1,
        )
        
        provider = OllamaProvider(config)
        
        # PROPERTY: Provider should successfully generate response
        result = await provider.generate(prompt, system_prompt=system_prompt)
        
        assert result is not None, "Provider should return a response"
        assert isinstance(result, str), "Response should be a string"
        assert len(result) > 0, "Response should not be empty"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    prompt=prompt_strategy(),
)
@pytest.mark.asyncio
async def test_property_orchestrator_failover(prompt):
    """
    Property 13: Multi-Provider LLM Support (Failover)
    
    When primary provider fails, orchestrator SHALL automatically try next provider.
    
    **Validates: Requirements 3.1, 3.7**
    """
    # Create mock providers - first fails, second succeeds
    mock_response = "Success from secondary provider"
    
    call_count = 0
    
    async def mock_generate_with_failover(self, prompt, system_prompt=None, **kwargs):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First provider fails
            raise LLMProviderException(
                "Primary provider failed",
                provider="ollama",
                error_code="CONNECTION_ERROR"
            )
        else:
            # Second provider succeeds
            return mock_response
    
    with patch.object(OllamaProvider, 'generate', mock_generate_with_failover):
        # Create orchestrator with multiple providers
        providers = [
            LLMProviderConfig(
                provider_type=LLMProviderType.OLLAMA,
                model="qwen2.5-coder:14b",
                priority=1,
            ),
            LLMProviderConfig(
                provider_type=LLMProviderType.OLLAMA,
                model="deepseek-r1:7b",
                priority=2,
            ),
        ]
        
        orchestrator = LLMOrchestrator(providers)
        
        # PROPERTY: Orchestrator should failover to second provider
        result = await orchestrator.generate(prompt)
        
        assert result == mock_response, "Should get response from secondary provider"
        assert call_count == 2, "Should have tried both providers"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    prompt=prompt_strategy(),
)
@pytest.mark.asyncio
async def test_property_all_providers_fail(prompt):
    """
    Property 13: Multi-Provider LLM Support (All Fail)
    
    When all providers fail, orchestrator SHALL raise appropriate exception.
    
    **Validates: Requirements 3.1, 3.7**
    """
    async def mock_generate_always_fail(self, prompt, system_prompt=None, **kwargs):
        raise LLMProviderException(
            "Provider failed",
            provider=self.config.provider_type.value,
            error_code="GENERATION_FAILED"
        )
    
    with patch.object(OllamaProvider, 'generate', mock_generate_always_fail):
        # Create orchestrator with multiple providers
        providers = [
            LLMProviderConfig(
                provider_type=LLMProviderType.OLLAMA,
                model="qwen2.5-coder:14b",
                priority=1,
            ),
            LLMProviderConfig(
                provider_type=LLMProviderType.OLLAMA,
                model="deepseek-r1:7b",
                priority=2,
            ),
        ]
        
        orchestrator = LLMOrchestrator(providers)
        
        # PROPERTY: Should raise exception when all providers fail
        with pytest.raises(LLMProviderException) as exc_info:
            await orchestrator.generate(prompt)
        
        assert "All LLM providers failed" in str(exc_info.value)
        assert exc_info.value.error_code == "ALL_PROVIDERS_FAILED"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    num_providers=st.integers(min_value=1, max_value=5),
)
@pytest.mark.asyncio
async def test_property_provider_priority_ordering(num_providers):
    """
    Property 13: Multi-Provider LLM Support (Priority)
    
    Orchestrator SHALL try providers in priority order (lower priority number first).
    
    **Validates: Requirements 3.1**
    """
    call_order = []
    
    async def mock_generate_track_order(self, prompt, system_prompt=None, **kwargs):
        call_order.append(self.config.priority)
        return f"Response from priority {self.config.priority}"
    
    with patch.object(OllamaProvider, 'generate', mock_generate_track_order):
        # Create providers with different priorities
        providers = []
        for i in range(num_providers):
            providers.append(
                LLMProviderConfig(
                    provider_type=LLMProviderType.OLLAMA,
                    model=f"model-{i}",
                    priority=i + 1,  # Priority 1, 2, 3, ...
                )
            )
        
        orchestrator = LLMOrchestrator(providers)
        
        # PROPERTY: Should try provider with lowest priority number first
        result = await orchestrator.generate("test prompt")
        
        assert len(call_order) >= 1, "Should have called at least one provider"
        assert call_order[0] == 1, "Should try priority 1 provider first"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    prompt=prompt_strategy(),
)
@pytest.mark.asyncio
async def test_property_agentic_ai_service_uses_orchestrator(prompt):
    """
    Property 13: Multi-Provider LLM Support (Service Integration)
    
    Agentic AI Service SHALL use LLM orchestrator for all LLM requests.
    
    **Validates: Requirements 3.1**
    """
    mock_response = "AI service response"
    
    # Create mock orchestrator
    mock_orchestrator = MagicMock()
    mock_orchestrator.generate = AsyncMock(return_value=mock_response)
    mock_orchestrator.get_provider_count = MagicMock(return_value=3)
    
    # Create service with mock orchestrator
    service = AgenticAIService(
        llm_orchestrator=mock_orchestrator,
        neo4j_client=None,
        redis_client=None,
    )
    
    # PROPERTY: Service should use orchestrator for generation
    result = await service.generate_natural_language_explanation(
        technical_finding="Test finding",
        context=None,
    )
    
    assert mock_orchestrator.generate.called, "Service should call orchestrator"
    assert mock_orchestrator.generate.call_count >= 1, "Should call orchestrator at least once"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=st.text(min_size=50, max_size=500, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))),
)
@pytest.mark.asyncio
async def test_property_service_handles_llm_failure_gracefully(code):
    """
    Property 13: Multi-Provider LLM Support (Error Handling)
    
    Service SHALL handle LLM failures gracefully and propagate errors appropriately.
    
    **Validates: Requirements 3.1, 3.7**
    """
    # Create mock orchestrator that fails
    mock_orchestrator = MagicMock()
    mock_orchestrator.generate = AsyncMock(
        side_effect=LLMProviderException(
            "All providers failed",
            provider="orchestrator",
            error_code="ALL_PROVIDERS_FAILED"
        )
    )
    mock_orchestrator.get_provider_count = MagicMock(return_value=3)
    
    # Create service with failing orchestrator
    service = AgenticAIService(
        llm_orchestrator=mock_orchestrator,
        neo4j_client=None,
        redis_client=None,
    )
    
    # PROPERTY: Service should propagate LLM exceptions
    with pytest.raises(LLMProviderException):
        await service.analyze_clean_code_violations(
            code=code,
            file_path="test.py",
            language="python",
        )


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
def test_property_provider_config_validation():
    """
    Property 13: Multi-Provider LLM Support (Configuration)
    
    Provider configuration SHALL validate parameters and reject invalid values.
    
    **Validates: Requirements 3.1**
    """
    # PROPERTY: Valid configuration should be accepted
    valid_config = LLMProviderConfig(
        provider_type=LLMProviderType.OLLAMA,
        model="qwen2.5-coder:14b",
        max_tokens=1000,
        temperature=0.5,
        timeout=60,
        priority=1,
    )
    
    assert valid_config.max_tokens == 1000
    assert valid_config.temperature == 0.5
    
    # PROPERTY: Invalid max_tokens should be rejected
    with pytest.raises(ValueError):
        LLMProviderConfig(
            provider_type=LLMProviderType.OLLAMA,
            model="test",
            max_tokens=0,  # Invalid
        )
    
    # PROPERTY: Invalid temperature should be rejected
    with pytest.raises(ValueError):
        LLMProviderConfig(
            provider_type=LLMProviderType.OLLAMA,
            model="test",
            temperature=3.0,  # Invalid (must be 0-2)
        )
    
    # PROPERTY: Invalid timeout should be rejected
    with pytest.raises(ValueError):
        LLMProviderConfig(
            provider_type=LLMProviderType.OLLAMA,
            model="test",
            timeout=0,  # Invalid
        )


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    context_messages=st.lists(
        st.fixed_dictionaries({
            'role': st.sampled_from(['user', 'assistant']),
            'content': st.text(min_size=10, max_size=100)
        }),
        min_size=1,
        max_size=5
    ),
    prompt=prompt_strategy(),
)
@pytest.mark.asyncio
async def test_property_context_support(context_messages, prompt):
    """
    Property 13: Multi-Provider LLM Support (Context)
    
    Providers SHALL support generation with conversation context.
    
    **Validates: Requirements 3.1, 3.2**
    """
    mock_response = "Response with context"
    
    with patch('aiohttp.ClientSession') as mock_session_class:
        # Mock the HTTP response
        mock_response_obj = AsyncMock()
        mock_response_obj.raise_for_status = MagicMock()
        mock_response_obj.json = AsyncMock(return_value={"response": mock_response})
        
        # Mock the post method to return the response
        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_post.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session to return the post mock
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Make ClientSession() return the mock session
        mock_session_class.return_value = mock_session
        
        # Create provider
        config = LLMProviderConfig(
            provider_type=LLMProviderType.OLLAMA,
            model="qwen2.5-coder:14b",
            priority=1,
        )
        
        provider = OllamaProvider(config)
        
        # PROPERTY: Provider should handle context
        result = await provider.generate_with_context(prompt, context_messages)
        
        assert result is not None, "Should return response with context"
        assert isinstance(result, str), "Response should be string"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
def test_property_orchestrator_requires_providers():
    """
    Property 13: Multi-Provider LLM Support (Validation)
    
    Orchestrator SHALL require at least one provider configuration.
    
    **Validates: Requirements 3.1**
    """
    # PROPERTY: Empty provider list should be rejected
    with pytest.raises(ValueError) as exc_info:
        LLMOrchestrator([])
    
    assert "at least one provider" in str(exc_info.value).lower()


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(13, "Multi-Provider LLM Support")
def test_property_provider_name_format():
    """
    Property 13: Multi-Provider LLM Support (Naming)
    
    Provider names SHALL follow format: provider_type/model
    
    **Validates: Requirements 3.1**
    """
    config = LLMProviderConfig(
        provider_type=LLMProviderType.OLLAMA,
        model="qwen2.5-coder:14b",
        priority=1,
    )
    
    provider = OllamaProvider(config)
    
    # PROPERTY: Provider name should include type and model
    name = provider.get_provider_name()
    
    assert "ollama" in name.lower(), "Name should include provider type"
    assert "qwen2.5-coder" in name.lower(), "Name should include model name"
    assert "/" in name, "Name should use / separator"
