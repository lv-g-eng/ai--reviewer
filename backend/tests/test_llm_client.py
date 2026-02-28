"""
Unit tests for LLM client with multi-provider support

Tests the LLM client implementation including:
- OpenAI GPT-4 provider
- Anthropic Claude 3.5 provider
- Provider factory
- Error handling

Validates Requirements: 1.4
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from app.services.llm import (
    BaseLLMProvider,
    LLMProviderType,
    LLMRequest,
    LLMResponse,
    OpenAIProvider,
    AnthropicProvider,
    LLMProviderFactory,
    get_llm_provider
)


class TestLLMRequest:
    """Test LLMRequest dataclass"""
    
    def test_valid_request(self):
        """Test creating a valid LLM request"""
        request = LLMRequest(
            prompt="Test prompt",
            system_prompt="System instruction",
            temperature=0.5,
            max_tokens=1000,
            json_mode=True
        )
        
        assert request.prompt == "Test prompt"
        assert request.system_prompt == "System instruction"
        assert request.temperature == 0.5
        assert request.max_tokens == 1000
        assert request.json_mode is True
    
    def test_default_values(self):
        """Test default values in LLM request"""
        request = LLMRequest(prompt="Test")
        
        assert request.prompt == "Test"
        assert request.system_prompt is None
        assert request.temperature == 0.3
        assert request.max_tokens == 4000
        assert request.json_mode is False
    
    def test_invalid_temperature(self):
        """Test validation of temperature parameter"""
        with pytest.raises(ValueError, match="temperature must be between 0 and 2"):
            LLMRequest(prompt="Test", temperature=3.0)
        
        with pytest.raises(ValueError, match="temperature must be between 0 and 2"):
            LLMRequest(prompt="Test", temperature=-0.1)
    
    def test_invalid_max_tokens(self):
        """Test validation of max_tokens parameter"""
        with pytest.raises(ValueError, match="max_tokens must be >= 1"):
            LLMRequest(prompt="Test", max_tokens=0)


class TestLLMResponse:
    """Test LLMResponse dataclass"""
    
    def test_response_creation(self):
        """Test creating an LLM response"""
        response = LLMResponse(
            content="Generated text",
            provider="openai",
            model="gpt-4",
            tokens={"prompt": 10, "completion": 20, "total": 30},
            cost=0.001
        )
        
        assert response.content == "Generated text"
        assert response.provider == "openai"
        assert response.model == "gpt-4"
        assert response.tokens["total"] == 30
        assert response.cost == 0.001
    
    def test_to_dict(self):
        """Test converting response to dictionary"""
        response = LLMResponse(
            content="Test",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            tokens={"prompt": 5, "completion": 10, "total": 15},
            cost=0.0005
        )
        
        result = response.to_dict()
        
        assert isinstance(result, dict)
        assert result["content"] == "Test"
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-3-5-sonnet-20241022"
        assert result["tokens"]["total"] == 15
        assert result["cost"] == 0.0005


class TestOpenAIProvider:
    """Test OpenAI provider implementation"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create mock OpenAI client"""
        with patch('app.services.llm.openai_provider.AsyncOpenAI') as mock:
            yield mock
    
    @pytest.mark.asyncio
    async def test_generate_success(self, mock_openai_client):
        """Test successful generation with OpenAI"""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated response"))]
        mock_response.usage = Mock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client_instance
        
        # Create provider and generate
        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        request = LLMRequest(prompt="Test prompt")
        
        response = await provider.generate(request)
        
        # Verify response
        assert response.content == "Generated response"
        assert response.provider == "openai"
        assert response.model == "gpt-4"
        assert response.tokens["total"] == 30
        assert response.cost > 0
        
        # Verify API call
        mock_client_instance.chat.completions.create.assert_called_once()
        call_kwargs = mock_client_instance.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4"
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["messages"][0]["content"] == "Test prompt"
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_openai_client):
        """Test generation with system prompt"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client_instance
        
        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        request = LLMRequest(
            prompt="User prompt",
            system_prompt="System instruction"
        )
        
        await provider.generate(request)
        
        # Verify system prompt is included
        call_kwargs = mock_client_instance.chat.completions.create.call_args[1]
        assert len(call_kwargs["messages"]) == 2
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][0]["content"] == "System instruction"
        assert call_kwargs["messages"][1]["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_generate_with_json_mode(self, mock_openai_client):
        """Test generation with JSON mode enabled"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"key": "value"}'))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client_instance
        
        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        request = LLMRequest(prompt="Test", json_mode=True)
        
        await provider.generate(request)
        
        # Verify JSON mode is enabled
        call_kwargs = mock_client_instance.chat.completions.create.call_args[1]
        assert "response_format" in call_kwargs
        assert call_kwargs["response_format"]["type"] == "json_object"
    
    @pytest.mark.asyncio
    async def test_usage_tracking(self, mock_openai_client):
        """Test token usage and cost tracking"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200, total_tokens=300)
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client_instance
        
        provider = OpenAIProvider(model="gpt-4-turbo", api_key="test-key")
        request = LLMRequest(prompt="Test")
        
        # Generate twice
        await provider.generate(request)
        await provider.generate(request)
        
        # Check cumulative usage
        stats = provider.get_usage_stats()
        assert stats["total_tokens"] == 600
        assert stats["total_cost"] > 0
        assert stats["provider"] == "openai"
        assert stats["model"] == "gpt-4-turbo"
    
    @pytest.mark.asyncio
    async def test_reset_usage(self, mock_openai_client):
        """Test resetting usage statistics"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client_instance
        
        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        request = LLMRequest(prompt="Test")
        
        await provider.generate(request)
        assert provider.total_tokens > 0
        
        provider.reset_usage()
        assert provider.total_tokens == 0
        assert provider.total_cost == 0.0
    
    def test_get_provider_type(self):
        """Test getting provider type"""
        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        assert provider.get_provider_type() == LLMProviderType.OPENAI
    
    def test_cost_calculation_gpt4_turbo(self):
        """Test cost calculation for GPT-4 Turbo"""
        provider = OpenAIProvider(model="gpt-4-turbo", api_key="test-key")
        
        # 1000 prompt tokens + 1000 completion tokens
        cost = provider._calculate_cost(1000, 1000)
        
        # Expected: (1000/1000 * 0.01) + (1000/1000 * 0.03) = 0.04
        assert cost == pytest.approx(0.04, rel=1e-6)
    
    def test_cost_calculation_gpt4(self):
        """Test cost calculation for standard GPT-4"""
        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        
        # 1000 prompt tokens + 1000 completion tokens
        cost = provider._calculate_cost(1000, 1000)
        
        # Expected: (1000/1000 * 0.03) + (1000/1000 * 0.06) = 0.09
        assert cost == pytest.approx(0.09, rel=1e-6)


class TestAnthropicProvider:
    """Test Anthropic provider implementation"""
    
    @pytest.fixture
    def mock_anthropic_client(self):
        """Create mock Anthropic client"""
        with patch('app.services.llm.anthropic_provider.AsyncAnthropic') as mock:
            yield mock
    
    @pytest.mark.asyncio
    async def test_generate_success(self, mock_anthropic_client):
        """Test successful generation with Anthropic"""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = [Mock(text="Generated response")]
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)
        
        mock_client_instance = AsyncMock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_anthropic_client.return_value = mock_client_instance
        
        # Create provider and generate
        provider = AnthropicProvider(model="claude-3-5-sonnet-20241022", api_key="test-key")
        request = LLMRequest(prompt="Test prompt")
        
        response = await provider.generate(request)
        
        # Verify response
        assert response.content == "Generated response"
        assert response.provider == "anthropic"
        assert response.model == "claude-3-5-sonnet-20241022"
        assert response.tokens["total"] == 30
        assert response.cost > 0
        
        # Verify API call
        mock_client_instance.messages.create.assert_called_once()
        call_kwargs = mock_client_instance.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["messages"][0]["content"] == "Test prompt"
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_anthropic_client):
        """Test generation with system prompt"""
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)
        
        mock_client_instance = AsyncMock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_anthropic_client.return_value = mock_client_instance
        
        provider = AnthropicProvider(model="claude-3-5-sonnet-20241022", api_key="test-key")
        request = LLMRequest(
            prompt="User prompt",
            system_prompt="System instruction"
        )
        
        await provider.generate(request)
        
        # Verify system prompt is passed
        call_kwargs = mock_client_instance.messages.create.call_args[1]
        assert call_kwargs["system"] == "System instruction"
    
    @pytest.mark.asyncio
    async def test_generate_with_json_mode(self, mock_anthropic_client):
        """Test generation with JSON mode (adds instruction to prompt)"""
        mock_response = Mock()
        mock_response.content = [Mock(text='{"key": "value"}')]
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)
        
        mock_client_instance = AsyncMock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_anthropic_client.return_value = mock_client_instance
        
        provider = AnthropicProvider(model="claude-3-5-sonnet-20241022", api_key="test-key")
        request = LLMRequest(prompt="Test", json_mode=True)
        
        await provider.generate(request)
        
        # Verify JSON instruction is added to prompt
        call_kwargs = mock_client_instance.messages.create.call_args[1]
        assert "valid JSON only" in call_kwargs["messages"][0]["content"]
    
    def test_get_provider_type(self):
        """Test getting provider type"""
        provider = AnthropicProvider(model="claude-3-5-sonnet-20241022", api_key="test-key")
        assert provider.get_provider_type() == LLMProviderType.ANTHROPIC
    
    def test_cost_calculation_sonnet(self):
        """Test cost calculation for Claude Sonnet"""
        provider = AnthropicProvider(model="claude-3-5-sonnet-20241022", api_key="test-key")
        
        # 1,000,000 input tokens + 1,000,000 output tokens
        cost = provider._calculate_cost(1_000_000, 1_000_000)
        
        # Expected: (1M/1M * 3) + (1M/1M * 15) = 18
        assert cost == pytest.approx(18.0, rel=1e-6)
    
    def test_cost_calculation_opus(self):
        """Test cost calculation for Claude Opus"""
        provider = AnthropicProvider(model="claude-3-opus-20240229", api_key="test-key")
        
        # 1,000,000 input tokens + 1,000,000 output tokens
        cost = provider._calculate_cost(1_000_000, 1_000_000)
        
        # Expected: (1M/1M * 15) + (1M/1M * 75) = 90
        assert cost == pytest.approx(90.0, rel=1e-6)
    
    def test_cost_calculation_haiku(self):
        """Test cost calculation for Claude Haiku"""
        provider = AnthropicProvider(model="claude-3-haiku-20240307", api_key="test-key")
        
        # 1,000,000 input tokens + 1,000,000 output tokens
        cost = provider._calculate_cost(1_000_000, 1_000_000)
        
        # Expected: (1M/1M * 0.25) + (1M/1M * 1.25) = 1.5
        assert cost == pytest.approx(1.5, rel=1e-6)


class TestLLMProviderFactory:
    """Test LLM provider factory"""
    
    def setup_method(self):
        """Clear factory cache before each test"""
        LLMProviderFactory.clear_cache()
    
    @patch('app.services.llm.factory.settings')
    def test_create_openai_provider(self, mock_settings):
        """Test creating OpenAI provider"""
        mock_settings.OPENAI_API_KEY = "test-openai-key"
        
        provider = LLMProviderFactory.create_provider(
            LLMProviderType.OPENAI,
            model="gpt-4"
        )
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4"
        assert provider.get_provider_type() == LLMProviderType.OPENAI
    
    @patch('app.services.llm.factory.settings')
    def test_create_anthropic_provider(self, mock_settings):
        """Test creating Anthropic provider"""
        mock_settings.ANTHROPIC_API_KEY = "test-anthropic-key"
        
        provider = LLMProviderFactory.create_provider(
            LLMProviderType.ANTHROPIC,
            model="claude-3-5-sonnet-20241022"
        )
        
        assert isinstance(provider, AnthropicProvider)
        assert provider.model == "claude-3-5-sonnet-20241022"
        assert provider.get_provider_type() == LLMProviderType.ANTHROPIC
    
    @patch('app.services.llm.factory.settings')
    def test_create_provider_with_default_model(self, mock_settings):
        """Test creating provider with default model"""
        mock_settings.OPENAI_API_KEY = "test-key"
        
        provider = LLMProviderFactory.create_provider(LLMProviderType.OPENAI)
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4-turbo-preview"
    
    def test_create_provider_invalid_type(self):
        """Test creating provider with invalid type"""
        with pytest.raises(ValueError, match="Unsupported provider type"):
            LLMProviderFactory.create_provider("invalid_type")
    
    @patch('app.services.llm.factory.settings')
    def test_create_provider_missing_api_key(self, mock_settings):
        """Test creating provider without API key"""
        mock_settings.OPENAI_API_KEY = None
        
        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            LLMProviderFactory.create_provider(LLMProviderType.OPENAI)
    
    @patch('app.services.llm.factory.settings')
    def test_get_provider_with_cache(self, mock_settings):
        """Test getting provider with caching"""
        mock_settings.OPENAI_API_KEY = "test-key"
        
        # Get provider twice
        provider1 = LLMProviderFactory.get_provider(LLMProviderType.OPENAI, "gpt-4")
        provider2 = LLMProviderFactory.get_provider(LLMProviderType.OPENAI, "gpt-4")
        
        # Should return same instance
        assert provider1 is provider2
    
    @patch('app.services.llm.factory.settings')
    def test_get_provider_without_cache(self, mock_settings):
        """Test getting provider without caching"""
        mock_settings.OPENAI_API_KEY = "test-key"
        
        # Get provider twice without cache
        provider1 = LLMProviderFactory.get_provider(
            LLMProviderType.OPENAI, "gpt-4", use_cache=False
        )
        provider2 = LLMProviderFactory.get_provider(
            LLMProviderType.OPENAI, "gpt-4", use_cache=False
        )
        
        # Should return different instances
        assert provider1 is not provider2
    
    @patch('app.services.llm.factory.settings')
    def test_clear_cache(self, mock_settings):
        """Test clearing provider cache"""
        mock_settings.OPENAI_API_KEY = "test-key"
        
        # Get provider and cache it
        provider1 = LLMProviderFactory.get_provider(LLMProviderType.OPENAI, "gpt-4")
        
        # Clear cache
        LLMProviderFactory.clear_cache()
        
        # Get provider again
        provider2 = LLMProviderFactory.get_provider(LLMProviderType.OPENAI, "gpt-4")
        
        # Should be different instance
        assert provider1 is not provider2


class TestGetLLMProvider:
    """Test convenience function"""
    
    def setup_method(self):
        """Clear factory cache before each test"""
        LLMProviderFactory.clear_cache()
    
    @patch('app.services.llm.factory.settings')
    def test_get_llm_provider_default(self, mock_settings):
        """Test getting provider with defaults"""
        mock_settings.OPENAI_API_KEY = "test-key"
        
        provider = get_llm_provider()
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.get_provider_type() == LLMProviderType.OPENAI
    
    @patch('app.services.llm.factory.settings')
    def test_get_llm_provider_anthropic(self, mock_settings):
        """Test getting Anthropic provider"""
        mock_settings.ANTHROPIC_API_KEY = "test-key"
        
        provider = get_llm_provider(LLMProviderType.ANTHROPIC)
        
        assert isinstance(provider, AnthropicProvider)
        assert provider.get_provider_type() == LLMProviderType.ANTHROPIC
    
    @patch('app.services.llm.factory.settings')
    def test_get_llm_provider_with_model(self, mock_settings):
        """Test getting provider with specific model"""
        mock_settings.OPENAI_API_KEY = "test-key"
        
        provider = get_llm_provider(LLMProviderType.OPENAI, "gpt-4")
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4"
