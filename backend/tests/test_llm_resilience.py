"""
Integration Tests for LLM Resilience Patterns

Tests circuit breaker and orchestrator with primary/fallback pattern.
Validates Requirements: 2.2, 2.3, 2.6, 2.8
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from openai import RateLimitError, APIConnectionError, InternalServerError
from anthropic import RateLimitError as AnthropicRateLimitError

from app.services.llm import (
    LLMRequest,
    LLMResponse,
    LLMProviderType,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitBreakerOpenError,
    LLMOrchestrator,
    OrchestratorConfig,
    create_orchestrator
)


# ============================================================================
# Circuit Breaker Tests
# ============================================================================

class TestCircuitBreaker:
    """Test circuit breaker implementation"""
    
    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initializes correctly"""
        cb = CircuitBreaker("test_circuit")
        
        assert cb.name == "test_circuit"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
    
    def test_circuit_breaker_custom_config(self):
        """Test circuit breaker with custom configuration"""
        config = CircuitBreakerConfig(
            failure_threshold=0.6,
            success_threshold=3,
            timeout=30,
            window_size=20
        )
        cb = CircuitBreaker("test_circuit", config)
        
        assert cb.config.failure_threshold == 0.6
        assert cb.config.success_threshold == 3
        assert cb.config.timeout == 30
        assert cb.config.window_size == 20
    
    def test_circuit_breaker_successful_call(self):
        """Test circuit breaker with successful call"""
        cb = CircuitBreaker("test_circuit")
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert len(cb.recent_calls) == 1
        assert cb.recent_calls[0] is True
    
    def test_circuit_breaker_failed_call(self):
        """Test circuit breaker with failed call"""
        cb = CircuitBreaker("test_circuit")
        
        def failure_func():
            raise Exception("Test failure")
        
        with pytest.raises(Exception, match="Test failure"):
            cb.call(failure_func)
        
        assert cb.state == CircuitState.CLOSED  # Still closed after 1 failure
        assert cb.failure_count == 1
        assert len(cb.recent_calls) == 1
        assert cb.recent_calls[0] is False
    
    def test_circuit_breaker_opens_on_threshold(self):
        """Test circuit breaker opens when failure threshold is reached"""
        config = CircuitBreakerConfig(
            failure_threshold=0.5,
            window_size=10
        )
        cb = CircuitBreaker("test_circuit", config)
        
        def failure_func():
            raise Exception("Test failure")
        
        # Record calls in a pattern that will trigger the circuit breaker
        # We need to fill the window first, then have failures exceed threshold
        # Pattern: 5 successes, then 5 failures = 50% at call 10
        # Then one more failure pushes it over (6/11 = 54.5% but window is 10, so 6/10 = 60%)
        for i in range(11):
            try:
                if i < 5:
                    cb.call(lambda: "success")
                else:
                    cb.call(failure_func)
            except Exception:
                pass
        
        # Circuit should be OPEN after reaching >50% failure rate
        assert cb.state == CircuitState.OPEN
    
    def test_circuit_breaker_rejects_when_open(self):
        """Test circuit breaker rejects calls when open"""
        cb = CircuitBreaker("test_circuit")
        cb.state = CircuitState.OPEN
        cb.last_failure_time = 999999999999  # Far in the future to prevent reset
        
        def success_func():
            return "success"
        
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(success_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_async_call(self):
        """Test circuit breaker with async function"""
        cb = CircuitBreaker("test_circuit")
        
        async def async_success():
            await asyncio.sleep(0.01)
            return "async_success"
        
        result = await cb.call_async(async_success)
        
        assert result == "async_success"
        assert cb.state == CircuitState.CLOSED
        assert len(cb.recent_calls) == 1
        assert cb.recent_calls[0] is True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_async_failure(self):
        """Test circuit breaker with async failure"""
        cb = CircuitBreaker("test_circuit")
        
        async def async_failure():
            await asyncio.sleep(0.01)
            raise Exception("Async failure")
        
        with pytest.raises(Exception, match="Async failure"):
            await cb.call_async(async_failure)
        
        assert cb.failure_count == 1
        assert cb.recent_calls[0] is False
    
    def test_circuit_breaker_half_open_transition(self):
        """Test circuit breaker transitions to half-open after timeout"""
        config = CircuitBreakerConfig(timeout=0)  # Immediate timeout
        cb = CircuitBreaker("test_circuit", config)
        cb.state = CircuitState.OPEN
        cb.last_failure_time = 0  # Long time ago
        
        def success_func():
            return "success"
        
        # Should transition to HALF_OPEN and succeed
        result = cb.call(success_func)
        
        assert result == "success"
        assert cb.state == CircuitState.HALF_OPEN
    
    def test_circuit_breaker_closes_from_half_open(self):
        """Test circuit breaker closes after successful calls in half-open"""
        config = CircuitBreakerConfig(success_threshold=2)
        cb = CircuitBreaker("test_circuit", config)
        cb.state = CircuitState.HALF_OPEN
        
        def success_func():
            return "success"
        
        # First success
        cb.call(success_func)
        assert cb.state == CircuitState.HALF_OPEN
        
        # Second success should close circuit
        cb.call(success_func)
        assert cb.state == CircuitState.CLOSED
    
    def test_circuit_breaker_reopens_from_half_open(self):
        """Test circuit breaker reopens on failure in half-open state"""
        cb = CircuitBreaker("test_circuit")
        cb.state = CircuitState.HALF_OPEN
        
        def failure_func():
            raise Exception("Test failure")
        
        with pytest.raises(Exception):
            cb.call(failure_func)
        
        assert cb.state == CircuitState.OPEN
    
    def test_circuit_breaker_get_stats(self):
        """Test circuit breaker statistics"""
        cb = CircuitBreaker("test_circuit")
        
        # Record some calls
        cb.call(lambda: "success")
        try:
            cb.call(lambda: 1/0)
        except:
            pass
        
        stats = cb.get_stats()
        
        assert stats["name"] == "test_circuit"
        assert stats["state"] == CircuitState.CLOSED.value
        assert stats["failure_count"] == 1
        assert stats["recent_calls"] == 2
        assert 0 <= stats["failure_rate"] <= 1
    
    def test_circuit_breaker_manual_reset(self):
        """Test manual circuit breaker reset"""
        cb = CircuitBreaker("test_circuit")
        cb.state = CircuitState.OPEN
        cb.failure_count = 10
        
        cb.reset()
        
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert len(cb.recent_calls) == 0


# ============================================================================
# LLM Orchestrator Tests
# ============================================================================

class TestLLMOrchestrator:
    """Test LLM orchestrator with primary/fallback pattern"""
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI response"""
        return LLMResponse(
            content="OpenAI response",
            provider="openai",
            model="gpt-4",
            tokens={"prompt": 10, "completion": 20, "total": 30},
            cost=0.001
        )
    
    @pytest.fixture
    def mock_anthropic_response(self):
        """Mock Anthropic response"""
        return LLMResponse(
            content="Anthropic response",
            provider="anthropic",
            model="claude-3-5-sonnet",
            tokens={"prompt": 10, "completion": 20, "total": 30},
            cost=0.0015
        )
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_openai_key"
            mock_settings.ANTHROPIC_API_KEY = "test_anthropic_key"
            
            orchestrator = create_orchestrator()
            
            assert orchestrator.config.primary_provider == LLMProviderType.OPENAI
            assert orchestrator.config.fallback_provider == LLMProviderType.ANTHROPIC
            assert orchestrator.config.timeout == 30
            assert orchestrator.primary_calls == 0
            assert orchestrator.fallback_calls == 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_primary_success(self, mock_openai_response):
        """Test orchestrator uses primary provider successfully"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator()
            
            # Mock primary provider
            orchestrator.primary_provider.generate = AsyncMock(
                return_value=mock_openai_response
            )
            
            request = LLMRequest(prompt="Test prompt")
            response = await orchestrator.generate(request)
            
            assert response.content == "OpenAI response"
            assert response.provider == "openai"
            assert orchestrator.primary_calls == 1
            assert orchestrator.fallback_calls == 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_fallback_on_primary_failure(
        self,
        mock_anthropic_response
    ):
        """Test orchestrator falls back when primary fails"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator()
            
            # Mock primary to fail, fallback to succeed
            orchestrator.primary_provider.generate = AsyncMock(
                side_effect=Exception("Primary failed")
            )
            orchestrator.fallback_provider.generate = AsyncMock(
                return_value=mock_anthropic_response
            )
            
            request = LLMRequest(prompt="Test prompt")
            response = await orchestrator.generate(request)
            
            assert response.content == "Anthropic response"
            assert response.provider == "anthropic"
            assert orchestrator.primary_calls == 0  # Circuit breaker recorded failure
            assert orchestrator.fallback_calls == 1
    
    @pytest.mark.asyncio
    async def test_orchestrator_both_providers_fail(self):
        """Test orchestrator when both providers fail"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator()
            
            # Mock both to fail
            orchestrator.primary_provider.generate = AsyncMock(
                side_effect=Exception("Primary failed")
            )
            orchestrator.fallback_provider.generate = AsyncMock(
                side_effect=Exception("Fallback failed")
            )
            
            request = LLMRequest(prompt="Test prompt")
            
            with pytest.raises(Exception, match="Both primary and fallback"):
                await orchestrator.generate(request)
            
            assert orchestrator.total_failures == 1
    
    @pytest.mark.asyncio
    async def test_orchestrator_circuit_breaker_integration(
        self,
        mock_anthropic_response
    ):
        """Test orchestrator with circuit breaker opening"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            # Use small window for faster testing
            config = OrchestratorConfig(
                circuit_breaker_config=CircuitBreakerConfig(
                    failure_threshold=0.5,
                    window_size=4
                )
            )
            orchestrator = LLMOrchestrator(config)
            
            # Mock primary to fail, fallback to succeed
            orchestrator.primary_provider.generate = AsyncMock(
                side_effect=Exception("Primary failed")
            )
            orchestrator.fallback_provider.generate = AsyncMock(
                return_value=mock_anthropic_response
            )
            
            request = LLMRequest(prompt="Test prompt")
            
            # Make multiple requests to trigger circuit breaker
            for _ in range(4):
                response = await orchestrator.generate(request)
                assert response.provider == "anthropic"
            
            # Check circuit breaker state
            primary_stats = orchestrator.primary_circuit.get_stats()
            assert primary_stats["state"] == CircuitState.OPEN.value
    
    @pytest.mark.asyncio
    async def test_orchestrator_no_fallback_option(self):
        """Test orchestrator without fallback enabled"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator()
            
            # Mock primary to fail
            orchestrator.primary_provider.generate = AsyncMock(
                side_effect=Exception("Primary failed")
            )
            
            request = LLMRequest(prompt="Test prompt")
            
            with pytest.raises(Exception, match="Primary failed"):
                await orchestrator.generate(request, use_fallback=False)
            
            assert orchestrator.fallback_calls == 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_get_stats(self, mock_openai_response):
        """Test orchestrator statistics"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator()
            
            # Mock primary provider
            orchestrator.primary_provider.generate = AsyncMock(
                return_value=mock_openai_response
            )
            
            request = LLMRequest(prompt="Test prompt")
            await orchestrator.generate(request)
            
            stats = orchestrator.get_stats()
            
            assert stats["primary_calls"] == 1
            assert stats["fallback_calls"] == 0
            assert stats["total_failures"] == 0
            assert "primary_circuit" in stats
            assert "fallback_circuit" in stats
            assert "primary_usage" in stats
            assert "fallback_usage" in stats
    
    @pytest.mark.asyncio
    async def test_orchestrator_reset_stats(self, mock_openai_response):
        """Test orchestrator statistics reset"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator()
            
            # Mock primary provider
            orchestrator.primary_provider.generate = AsyncMock(
                return_value=mock_openai_response
            )
            
            request = LLMRequest(prompt="Test prompt")
            await orchestrator.generate(request)
            
            assert orchestrator.primary_calls == 1
            
            orchestrator.reset_stats()
            
            assert orchestrator.primary_calls == 0
            assert orchestrator.fallback_calls == 0
            assert orchestrator.total_failures == 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_reset_circuits(self):
        """Test orchestrator circuit breaker reset"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator()
            
            # Manually open circuits
            orchestrator.primary_circuit.state = CircuitState.OPEN
            orchestrator.fallback_circuit.state = CircuitState.OPEN
            
            orchestrator.reset_circuits()
            
            assert orchestrator.primary_circuit.state == CircuitState.CLOSED
            assert orchestrator.fallback_circuit.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_orchestrator_timeout_enforcement(self):
        """Test orchestrator enforces 30-second timeout"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator(timeout=30)
            
            # Verify timeout is set on providers
            assert orchestrator.primary_provider.timeout == 30
            assert orchestrator.fallback_provider.timeout == 30
    
    @pytest.mark.asyncio
    async def test_orchestrator_custom_models(self):
        """Test orchestrator with custom models"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator(
                primary_model="gpt-4-turbo-preview",
                fallback_model="claude-3-5-sonnet-20241022"
            )
            
            assert orchestrator.primary_provider.model == "gpt-4-turbo-preview"
            assert orchestrator.fallback_provider.model == "claude-3-5-sonnet-20241022"


# ============================================================================
# Integration Tests
# ============================================================================

class TestResilienceIntegration:
    """Integration tests for complete resilience patterns"""
    
    @pytest.mark.asyncio
    async def test_complete_resilience_flow(self):
        """Test complete resilience flow with retries and fallback"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            orchestrator = create_orchestrator()
            
            # Mock responses
            fallback_response = LLMResponse(
                content="Fallback response",
                provider="anthropic",
                model="claude-3-5-sonnet",
                tokens={"prompt": 10, "completion": 20, "total": 30},
                cost=0.0015
            )
            
            # Primary fails, fallback succeeds
            orchestrator.primary_provider.generate = AsyncMock(
                side_effect=Exception("Primary unavailable")
            )
            orchestrator.fallback_provider.generate = AsyncMock(
                return_value=fallback_response
            )
            
            request = LLMRequest(
                prompt="Analyze this code",
                system_prompt="You are a code reviewer",
                temperature=0.3,
                max_tokens=2000
            )
            
            response = await orchestrator.generate(request)
            
            # Verify fallback was used
            assert response.content == "Fallback response"
            assert response.provider == "anthropic"
            assert orchestrator.fallback_calls == 1
            
            # Verify statistics
            stats = orchestrator.get_stats()
            assert stats["fallback_calls"] == 1
            assert stats["primary_circuit"]["failure_count"] > 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_cascading_failures(self):
        """Test circuit breaker prevents cascading failures"""
        with patch('app.services.llm.factory.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.ANTHROPIC_API_KEY = "test_key"
            
            config = OrchestratorConfig(
                circuit_breaker_config=CircuitBreakerConfig(
                    failure_threshold=0.5,
                    window_size=4
                )
            )
            orchestrator = LLMOrchestrator(config)
            
            # Mock both providers to fail
            orchestrator.primary_provider.generate = AsyncMock(
                side_effect=Exception("Service unavailable")
            )
            orchestrator.fallback_provider.generate = AsyncMock(
                side_effect=Exception("Service unavailable")
            )
            
            request = LLMRequest(prompt="Test")
            
            # Make requests until circuit opens
            for _ in range(4):
                try:
                    await orchestrator.generate(request)
                except Exception:
                    pass
            
            # Verify circuits are open
            assert orchestrator.primary_circuit.state == CircuitState.OPEN
            assert orchestrator.fallback_circuit.state == CircuitState.OPEN
            
            # Next request should fail fast without calling providers
            with pytest.raises(Exception, match="circuits open"):
                await orchestrator.generate(request)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
