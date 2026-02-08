"""
Property-based tests for LLM provider failover

Tests Property 4: LLM Provider Failover
For any LLM request where the primary provider fails, the system SHALL 
automatically attempt the request with the next available provider in the 
priority list, ensuring service continuity.

Validates Requirements: 1.7, 3.7
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from app.shared.llm_provider import (
    LLMOrchestrator,
    LLMProviderConfig,
    LLMProviderType,
    LLMProviderException,
)


# Strategy for generating provider configurations
@st.composite
def provider_config_strategy(draw):
    """Generate valid provider configurations"""
    provider_type = draw(st.sampled_from([
        LLMProviderType.OPENAI,
        LLMProviderType.ANTHROPIC,
        LLMProviderType.OLLAMA,
    ]))
    
    models = {
        LLMProviderType.OPENAI: ["gpt-4", "gpt-3.5-turbo"],
        LLMProviderType.ANTHROPIC: ["claude-3.5-sonnet", "claude-3-opus"],
        LLMProviderType.OLLAMA: ["llama2", "codellama"],
    }
    
    return LLMProviderConfig(
        provider_type=provider_type,
        model=draw(st.sampled_from(models[provider_type])),
        api_key="test-key",
        priority=draw(st.integers(min_value=1, max_value=10)),
        max_tokens=draw(st.integers(min_value=100, max_value=4000)),
        temperature=draw(st.floats(min_value=0.0, max_value=1.0)),
    )


@st.composite
def prompt_strategy(draw):
    """Generate test prompts"""
    return draw(st.text(min_size=10, max_size=200))


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(4, "LLM Provider Failover")
@pytest.mark.asyncio
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    prompt=prompt_strategy(),
    num_providers=st.integers(min_value=2, max_value=5),
    failing_provider_index=st.integers(min_value=0, max_value=4),
)
async def test_property_llm_provider_failover(prompt, num_providers, failing_provider_index):
    """
    Property 4: LLM Provider Failover
    
    For any LLM request where the primary provider fails, the system SHALL
    automatically attempt the request with the next available provider in the
    priority list, ensuring service continuity.
    
    **Validates: Requirements 1.7, 3.7**
    """
    # Ensure failing index is within bounds
    if failing_provider_index >= num_providers:
        failing_provider_index = num_providers - 1
    
    # Create provider configurations with different priorities
    configs = []
    for i in range(num_providers):
        config = LLMProviderConfig(
            provider_type=LLMProviderType.OPENAI,
            model=f"test-model-{i}",
            api_key="test-key",
            priority=i + 1,  # Priority 1, 2, 3, etc.
        )
        configs.append(config)
    
    # Mock the provider implementations
    with patch('app.shared.llm_provider.OpenAIProvider') as MockProvider:
        # Track which providers were called
        call_order = []
        
        def create_mock_provider(config):
            mock = MagicMock()
            mock.config = config
            mock.get_provider_name.return_value = f"{config.provider_type.value}/{config.model}"
            
            async def mock_generate(prompt_text, system_prompt=None, **kwargs):
                call_order.append(config.priority)
                
                # Fail the specified provider
                if config.priority == failing_provider_index + 1:
                    raise LLMProviderException(
                        "Provider failed",
                        provider=config.provider_type.value,
                        model=config.model
                    )
                
                # Succeed for other providers
                return f"Response from provider {config.priority}"
            
            mock.generate = mock_generate
            mock.circuit_breaker = MagicMock()
            mock.circuit_breaker.call = lambda func: func()
            
            return mock
        
        MockProvider.side_effect = create_mock_provider
        
        # Create orchestrator
        orchestrator = LLMOrchestrator(configs)
        
        # Execute request
        try:
            result = await orchestrator.generate(prompt)
            
            # PROPERTY: If any provider succeeds, request should succeed
            assert result is not None
            assert isinstance(result, str)
            
            # PROPERTY: Providers should be tried in priority order
            assert len(call_order) >= 1
            for i in range(len(call_order) - 1):
                assert call_order[i] < call_order[i + 1], \
                    "Providers should be tried in priority order (lower priority number first)"
            
            # PROPERTY: If primary provider fails, next provider should be tried
            if failing_provider_index == 0:
                # Primary provider failed, should have tried at least 2 providers
                assert len(call_order) >= 2, \
                    "Should try next provider when primary fails"
                assert call_order[0] == 1, "Should try primary provider first"
                assert call_order[1] == 2, "Should try second provider after primary fails"
            
            # PROPERTY: Result should come from a working provider
            assert "Response from provider" in result
            
        except LLMProviderException as e:
            # All providers failed - this is acceptable if all providers were set to fail
            # But in our test, only one provider fails, so this shouldn't happen
            if num_providers > 1:
                pytest.fail(f"Failover should have succeeded with {num_providers} providers, "
                          f"but got exception: {e}")


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(4, "LLM Provider Failover")
@pytest.mark.asyncio
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    prompt=prompt_strategy(),
    num_providers=st.integers(min_value=1, max_value=3),
)
async def test_property_all_providers_fail(prompt, num_providers):
    """
    Property 4 (failure case): When all providers fail, exception should be raised
    
    **Validates: Requirements 1.7, 3.7**
    """
    # Create provider configurations
    configs = []
    for i in range(num_providers):
        config = LLMProviderConfig(
            provider_type=LLMProviderType.OPENAI,
            model=f"test-model-{i}",
            api_key="test-key",
            priority=i + 1,
        )
        configs.append(config)
    
    # Mock all providers to fail
    with patch('app.shared.llm_provider.OpenAIProvider') as MockProvider:
        call_count = [0]
        
        def create_mock_provider(config):
            mock = MagicMock()
            mock.config = config
            mock.get_provider_name.return_value = f"{config.provider_type.value}/{config.model}"
            
            async def mock_generate(prompt_text, system_prompt=None, **kwargs):
                call_count[0] += 1
                raise LLMProviderException(
                    "Provider failed",
                    provider=config.provider_type.value,
                    model=config.model
                )
            
            mock.generate = mock_generate
            mock.circuit_breaker = MagicMock()
            mock.circuit_breaker.call = lambda func: func()
            
            return mock
        
        MockProvider.side_effect = create_mock_provider
        
        # Create orchestrator
        orchestrator = LLMOrchestrator(configs)
        
        # Execute request - should fail
        with pytest.raises(LLMProviderException) as exc_info:
            await orchestrator.generate(prompt)
        
        # PROPERTY: All providers should have been tried
        assert call_count[0] == num_providers, \
            f"Should try all {num_providers} providers before failing"
        
        # PROPERTY: Exception should indicate all providers failed
        assert "All LLM providers failed" in str(exc_info.value)


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(4, "LLM Provider Failover")
@pytest.mark.asyncio
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    prompt=prompt_strategy(),
    success_provider_index=st.integers(min_value=0, max_value=2),
)
async def test_property_failover_stops_at_success(prompt, success_provider_index):
    """
    Property 4 (optimization): Failover should stop at first successful provider
    
    **Validates: Requirements 1.7, 3.7**
    """
    num_providers = 3
    
    # Create provider configurations
    configs = []
    for i in range(num_providers):
        config = LLMProviderConfig(
            provider_type=LLMProviderType.OPENAI,
            model=f"test-model-{i}",
            api_key="test-key",
            priority=i + 1,
        )
        configs.append(config)
    
    # Mock providers
    with patch('app.shared.llm_provider.OpenAIProvider') as MockProvider:
        call_order = []
        
        def create_mock_provider(config):
            mock = MagicMock()
            mock.config = config
            mock.get_provider_name.return_value = f"{config.provider_type.value}/{config.model}"
            
            async def mock_generate(prompt_text, system_prompt=None, **kwargs):
                call_order.append(config.priority)
                
                # Fail providers before success_provider_index
                if config.priority <= success_provider_index:
                    raise LLMProviderException(
                        "Provider failed",
                        provider=config.provider_type.value,
                        model=config.model
                    )
                
                # Succeed at success_provider_index
                return f"Response from provider {config.priority}"
            
            mock.generate = mock_generate
            mock.circuit_breaker = MagicMock()
            mock.circuit_breaker.call = lambda func: func()
            
            return mock
        
        MockProvider.side_effect = create_mock_provider
        
        # Create orchestrator
        orchestrator = LLMOrchestrator(configs)
        
        # Execute request
        result = await orchestrator.generate(prompt)
        
        # PROPERTY: Should stop at first successful provider
        expected_calls = success_provider_index + 1
        assert len(call_order) == expected_calls, \
            f"Should stop after first success (expected {expected_calls} calls, got {len(call_order)})"
        
        # PROPERTY: Should not call providers after successful one
        assert max(call_order) == success_provider_index + 1, \
            "Should not try providers after successful one"
