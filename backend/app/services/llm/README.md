# LLM Client - Multi-Provider Support

A clean, well-structured LLM client implementation supporting multiple providers (GPT-4 and Claude 3.5) with a unified interface.

**Validates Requirements: 1.4**

## Overview

This module provides a multi-provider LLM client with:

- **Abstract Provider Interface**: Clean abstraction for all LLM providers
- **GPT-4 Support**: OpenAI GPT-4 and GPT-4 Turbo integration
- **Claude 3.5 Support**: Anthropic Claude 3.5 Sonnet integration
- **Automatic Retry**: Exponential backoff for transient failures
- **Usage Tracking**: Token usage and cost tracking per provider
- **Factory Pattern**: Easy provider instantiation and management
- **Error Handling**: Comprehensive error handling with logging

## Architecture

```
app/services/llm/
├── __init__.py           # Module exports
├── base.py               # Abstract base class and data models
├── openai_provider.py    # OpenAI GPT-4 implementation
├── anthropic_provider.py # Anthropic Claude 3.5 implementation
├── factory.py            # Provider factory and management
└── README.md             # This file
```

## Usage

### Basic Usage

```python
from app.services.llm import (
    get_llm_provider,
    LLMProviderType,
    LLMRequest
)

# Get OpenAI provider
provider = get_llm_provider(LLMProviderType.OPENAI, model="gpt-4")

# Create request
request = LLMRequest(
    prompt="Analyze this code for security issues",
    system_prompt="You are a security expert",
    temperature=0.3,
    max_tokens=2000,
    json_mode=False
)

# Generate response
response = await provider.generate(request)

print(f"Response: {response.content}")
print(f"Tokens used: {response.tokens['total']}")
print(f"Cost: ${response.cost:.4f}")
```

### Using Anthropic Claude

```python
# Get Anthropic provider
provider = get_llm_provider(
    LLMProviderType.ANTHROPIC,
    model="claude-3-5-sonnet-20241022"
)

request = LLMRequest(
    prompt="Review this pull request",
    temperature=0.2,
    max_tokens=4000
)

response = await provider.generate(request)
```

### Using the Factory Directly

```python
from app.services.llm import LLMProviderFactory, LLMProviderType

# Create provider with custom configuration
provider = LLMProviderFactory.create_provider(
    provider_type=LLMProviderType.OPENAI,
    model="gpt-4-turbo-preview",
    api_key="your-api-key",
    timeout=60
)

# Get cached provider instance
provider = LLMProviderFactory.get_provider(
    LLMProviderType.OPENAI,
    model="gpt-4",
    use_cache=True
)
```

### JSON Mode

```python
# Request JSON output (OpenAI native, Anthropic via prompt)
request = LLMRequest(
    prompt="List the security issues in JSON format",
    json_mode=True
)

response = await provider.generate(request)
# Response will be in JSON format
```

### Usage Tracking

```python
# Track token usage and costs
provider = get_llm_provider(LLMProviderType.OPENAI)

# Make multiple requests
for prompt in prompts:
    request = LLMRequest(prompt=prompt)
    response = await provider.generate(request)

# Get cumulative statistics
stats = provider.get_usage_stats()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']:.4f}")

# Reset tracking
provider.reset_usage()
```

## Provider Details

### OpenAI Provider

**Supported Models:**
- `gpt-4-turbo-preview` (default)
- `gpt-4`
- `gpt-4-1106-preview`

**Features:**
- Native JSON mode support
- Automatic retry on rate limits and connection errors
- Accurate cost calculation based on model pricing

**Pricing (as of 2024):**
- GPT-4 Turbo: $0.01/1K prompt tokens, $0.03/1K completion tokens
- GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens

### Anthropic Provider

**Supported Models:**
- `claude-3-5-sonnet-20241022` (default)
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

**Features:**
- JSON mode via prompt instruction
- Automatic retry on rate limits and connection errors
- Accurate cost calculation based on model pricing

**Pricing (as of 2024):**
- Claude 3.5 Sonnet: $3/MTok input, $15/MTok output
- Claude 3 Opus: $15/MTok input, $75/MTok output
- Claude 3 Sonnet: $3/MTok input, $15/MTok output
- Claude 3 Haiku: $0.25/MTok input, $1.25/MTok output

## Error Handling

The client implements comprehensive error handling:

### Automatic Retry

Both providers automatically retry on transient failures:
- Connection errors
- Rate limit errors
- Internal server errors

**Retry Strategy:**
- Maximum 3 attempts
- Exponential backoff (2s, 4s, 8s)
- Logs warnings before each retry

### Error Propagation

Non-transient errors are propagated with detailed error messages:

```python
try:
    response = await provider.generate(request)
except Exception as e:
    # Handle error
    print(f"Generation failed: {e}")
```

## Configuration

### Environment Variables

Configure API keys in your environment or `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Settings

The factory uses `app.core.config.settings` for default configuration:

```python
from app.core.config import settings

# API keys are loaded from settings
provider = LLMProviderFactory.create_provider(
    LLMProviderType.OPENAI
    # api_key defaults to settings.OPENAI_API_KEY
)
```

## Testing

Comprehensive unit tests are provided in `backend/tests/test_llm_client.py`:

```bash
# Run all tests
pytest backend/tests/test_llm_client.py -v

# Run specific test class
pytest backend/tests/test_llm_client.py::TestOpenAIProvider -v

# Run with coverage
pytest backend/tests/test_llm_client.py --cov=app.services.llm
```

**Test Coverage:**
- Request/Response data models
- OpenAI provider (14 tests)
- Anthropic provider (7 tests)
- Provider factory (8 tests)
- Convenience functions (3 tests)

## Best Practices

### 1. Use Cached Instances

```python
# Good: Reuses provider instance
provider = get_llm_provider(LLMProviderType.OPENAI)

# Avoid: Creates new instance each time
provider = LLMProviderFactory.create_provider(
    LLMProviderType.OPENAI,
    use_cache=False
)
```

### 2. Set Appropriate Timeouts

```python
# For long-running requests
provider = LLMProviderFactory.create_provider(
    LLMProviderType.OPENAI,
    timeout=60  # 60 seconds
)
```

### 3. Monitor Costs

```python
# Track costs for budget management
provider = get_llm_provider(LLMProviderType.OPENAI)

# ... make requests ...

stats = provider.get_usage_stats()
if stats['total_cost'] > budget_limit:
    logger.warning(f"Budget exceeded: ${stats['total_cost']:.2f}")
```

### 4. Use Appropriate Temperature

```python
# For deterministic outputs (code analysis, security)
request = LLMRequest(prompt="...", temperature=0.1)

# For creative outputs (suggestions, explanations)
request = LLMRequest(prompt="...", temperature=0.7)
```

### 5. Handle Errors Gracefully

```python
try:
    response = await provider.generate(request)
except Exception as e:
    logger.error(f"LLM generation failed: {e}")
    # Implement fallback or retry logic
    response = await fallback_provider.generate(request)
```

## Integration with Existing Code

This new LLM client can be integrated with existing services:

### Replacing Old LLM Client

```python
# Old code
from app.services.llm_client import LLMClient, LLMProvider

client = LLMClient(provider=LLMProvider.OPENAI)
response = await client.generate_completion(
    system_prompt="...",
    user_prompt="...",
    temperature=0.3
)

# New code
from app.services.llm import get_llm_provider, LLMProviderType, LLMRequest

provider = get_llm_provider(LLMProviderType.OPENAI)
request = LLMRequest(
    prompt="...",
    system_prompt="...",
    temperature=0.3
)
response = await provider.generate(request)
```

## Future Enhancements

Potential improvements for future versions:

1. **Streaming Support**: Add streaming response support for real-time output
2. **Batch Processing**: Implement batch request processing for efficiency
3. **Caching**: Add response caching to reduce API calls and costs
4. **Rate Limiting**: Implement client-side rate limiting
5. **Metrics**: Add Prometheus metrics for monitoring
6. **Additional Providers**: Support for more providers (Cohere, AI21, etc.)

## Requirements Validation

This implementation validates the following requirements:

- **Requirement 1.4**: LLM Service integration for GPT-4 and Claude 3.5
- **Requirement 2.2**: Exponential backoff retry for LLM API rate limits
- **Requirement 2.3**: Automatic fallback to secondary provider (via orchestrator)
- **Requirement 2.5**: Standardized error responses
- **Requirement 2.8**: Request timeout for LLM API calls

## License

Part of the AI-Based Reviewer on Project Code and Architecture project.
