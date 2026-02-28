# LLM Resilience Patterns

This document describes the resilience patterns implemented for the LLM service to handle API failures gracefully and prevent cascading failures.

## Overview

The LLM service implements comprehensive resilience patterns to ensure reliable operation even when external LLM APIs experience issues:

1. **Exponential Backoff Retry** - Automatic retry with increasing delays for transient failures
2. **Primary/Fallback Provider Pattern** - Automatic failover to secondary provider when primary fails
3. **Circuit Breaker Pattern** - Prevents cascading failures by failing fast when services are down
4. **Timeout Enforcement** - 30-second timeout for all API calls to prevent hanging requests

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Orchestrator                         │
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────┐     │
│  │  Primary Provider    │    │  Fallback Provider   │     │
│  │  (OpenAI GPT-4)      │    │  (Anthropic Claude)  │     │
│  │                      │    │                      │     │
│  │  ┌────────────────┐  │    │  ┌────────────────┐  │     │
│  │  │ Circuit Breaker│  │    │  │ Circuit Breaker│  │     │
│  │  │  - 50% threshold│  │    │  │  - 50% threshold│  │     │
│  │  │  - 60s timeout  │  │    │  │  - 60s timeout  │  │     │
│  │  └────────────────┘  │    │  └────────────────┘  │     │
│  │                      │    │                      │     │
│  │  ┌────────────────┐  │    │  ┌────────────────┐  │     │
│  │  │ Retry Logic    │  │    │  │ Retry Logic    │  │     │
│  │  │  - Max 3 tries │  │    │  │  - Max 3 tries │  │     │
│  │  │  - Exp backoff │  │    │  │  - Exp backoff │  │     │
│  │  └────────────────┘  │    │  └────────────────┘  │     │
│  └──────────────────────┘    └──────────────────────┘     │
│                                                             │
│  Flow: Primary → (if fails) → Fallback → (if fails) → Error│
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Circuit Breaker (`circuit_breaker.py`)

The circuit breaker prevents cascading failures by tracking failure rates and "opening" the circuit when failures exceed a threshold.

**States:**
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Too many failures, requests fail fast without calling the service
- **HALF_OPEN**: Testing if service has recovered, limited requests allowed

**Configuration:**
```python
CircuitBreakerConfig(
    failure_threshold=0.5,    # Open circuit at 50% failure rate
    success_threshold=2,       # Successes needed to close from half-open
    timeout=60,                # Seconds before trying half-open
    window_size=10             # Number of recent calls to track
)
```

**Example:**
```python
from app.services.llm import CircuitBreaker

cb = CircuitBreaker("my_service")

try:
    result = await cb.call_async(my_async_function, arg1, arg2)
except CircuitBreakerOpenError:
    # Circuit is open, service is down
    return cached_result
```

### 2. LLM Orchestrator (`orchestrator.py`)

The orchestrator manages multiple LLM providers with automatic failover and circuit breaker protection.

**Features:**
- Primary/fallback provider pattern
- Circuit breaker for each provider
- Automatic failover on primary failure
- 30-second timeout enforcement
- Usage statistics and monitoring

**Configuration:**
```python
OrchestratorConfig(
    primary_provider=LLMProviderType.OPENAI,
    fallback_provider=LLMProviderType.ANTHROPIC,
    primary_model="gpt-4-turbo-preview",
    fallback_model="claude-3-5-sonnet-20241022",
    timeout=30
)
```

**Example:**
```python
from app.services.llm import create_orchestrator, LLMRequest

# Create orchestrator
orchestrator = create_orchestrator(
    primary_provider=LLMProviderType.OPENAI,
    fallback_provider=LLMProviderType.ANTHROPIC,
    timeout=30
)

# Make request with automatic failover
request = LLMRequest(
    prompt="Analyze this code",
    system_prompt="You are a code reviewer",
    temperature=0.3,
    max_tokens=2000
)

response = await orchestrator.generate(request)
print(f"Response from {response.provider}: {response.content}")
```

## Resilience Patterns in Detail

### Pattern 1: Exponential Backoff Retry

Implemented in individual providers (`openai_provider.py`, `anthropic_provider.py`).

**Behavior:**
- Automatically retries on transient failures (rate limits, connection errors, server errors)
- Maximum 3 retry attempts
- Exponential backoff: 2s → 4s → 8s
- Logs warnings before each retry

**Retryable Errors:**
- `APIConnectionError` - Network connectivity issues
- `RateLimitError` - API rate limit exceeded
- `InternalServerError` - Temporary server issues

**Example:**
```python
# Automatic retry is built into providers
provider = get_llm_provider(LLMProviderType.OPENAI)
response = await provider.generate(request)
# If rate limited, will automatically retry with backoff
```

### Pattern 2: Primary/Fallback Provider

Implemented in the orchestrator.

**Behavior:**
1. Try primary provider first
2. If primary fails or circuit is open, automatically try fallback
3. If both fail, return error with details

**Example:**
```python
orchestrator = create_orchestrator()

# Primary (OpenAI) fails → automatically tries fallback (Anthropic)
response = await orchestrator.generate(request)

# Check which provider was used
if response.provider == "anthropic":
    print("Primary failed, used fallback")
```

### Pattern 3: Circuit Breaker

Prevents cascading failures by failing fast when a service is down.

**Behavior:**
1. Track success/failure rate in sliding window (default: 10 calls)
2. Open circuit when failure rate ≥ 50%
3. Reject requests immediately when circuit is open
4. After timeout (default: 60s), transition to half-open
5. In half-open, allow limited requests to test recovery
6. Close circuit after 2 consecutive successes

**Benefits:**
- Prevents wasting time on failing services
- Reduces load on struggling services
- Enables faster recovery
- Provides clear failure signals

**Example:**
```python
# Circuit breaker is automatic in orchestrator
orchestrator = create_orchestrator()

# If primary provider fails repeatedly, circuit opens
for _ in range(10):
    try:
        response = await orchestrator.generate(request)
    except Exception as e:
        print(f"Error: {e}")

# Check circuit state
stats = orchestrator.get_stats()
print(f"Primary circuit: {stats['primary_circuit']['state']}")
# Output: "open" if too many failures
```

### Pattern 4: Timeout Enforcement

All API calls have a 30-second timeout to prevent hanging requests.

**Configuration:**
```python
# Set timeout when creating orchestrator
orchestrator = create_orchestrator(timeout=30)

# Or when creating individual providers
provider = OpenAIProvider(model="gpt-4", timeout=30)
```

## Usage Examples

### Basic Usage with Automatic Failover

```python
from app.services.llm import create_orchestrator, LLMRequest, LLMProviderType

# Create orchestrator with default configuration
orchestrator = create_orchestrator()

# Make request
request = LLMRequest(
    prompt="Review this Python code for security issues",
    system_prompt="You are a security expert",
    temperature=0.3,
    max_tokens=2000
)

# Automatic failover if primary fails
response = await orchestrator.generate(request)
print(response.content)
```

### Custom Configuration

```python
from app.services.llm import (
    LLMOrchestrator,
    OrchestratorConfig,
    CircuitBreakerConfig,
    LLMProviderType
)

# Custom circuit breaker configuration
cb_config = CircuitBreakerConfig(
    failure_threshold=0.6,  # More tolerant (60% failure rate)
    success_threshold=3,     # Need 3 successes to close
    timeout=30,              # Shorter timeout (30s)
    window_size=20           # Larger window (20 calls)
)

# Custom orchestrator configuration
config = OrchestratorConfig(
    primary_provider=LLMProviderType.ANTHROPIC,  # Use Claude as primary
    fallback_provider=LLMProviderType.OPENAI,    # OpenAI as fallback
    primary_model="claude-3-5-sonnet-20241022",
    fallback_model="gpt-4-turbo-preview",
    circuit_breaker_config=cb_config,
    timeout=30
)

orchestrator = LLMOrchestrator(config)
```

### Monitoring and Statistics

```python
# Get comprehensive statistics
stats = orchestrator.get_stats()

print(f"Primary calls: {stats['primary_calls']}")
print(f"Fallback calls: {stats['fallback_calls']}")
print(f"Total failures: {stats['total_failures']}")

# Circuit breaker states
print(f"Primary circuit: {stats['primary_circuit']['state']}")
print(f"Primary failure rate: {stats['primary_circuit']['failure_rate']:.2%}")

print(f"Fallback circuit: {stats['fallback_circuit']['state']}")
print(f"Fallback failure rate: {stats['fallback_circuit']['failure_rate']:.2%}")

# Usage statistics
print(f"Primary tokens: {stats['primary_usage']['total_tokens']}")
print(f"Primary cost: ${stats['primary_usage']['total_cost']:.4f}")
print(f"Fallback tokens: {stats['fallback_usage']['total_tokens']}")
print(f"Fallback cost: ${stats['fallback_usage']['total_cost']:.4f}")
```

### Manual Circuit Control

```python
# Reset circuit breakers manually
orchestrator.reset_circuits()

# Reset statistics
orchestrator.reset_stats()

# Check individual circuit state
if orchestrator.primary_circuit.get_state() == CircuitState.OPEN:
    print("Primary circuit is open, using fallback only")
```

### Disable Fallback (Primary Only)

```python
# Use primary provider only, no fallback
try:
    response = await orchestrator.generate(request, use_fallback=False)
except Exception as e:
    print(f"Primary provider failed: {e}")
    # Handle error (e.g., return cached result, queue for later)
```

## Error Handling

### Circuit Breaker Open

```python
from app.services.llm import CircuitBreakerOpenError

try:
    response = await orchestrator.generate(request)
except CircuitBreakerOpenError as e:
    # Circuit is open, service is down
    logger.warning(f"Circuit breaker open: {e}")
    # Return cached result or graceful degradation
    return get_cached_response(request)
```

### Both Providers Failed

```python
try:
    response = await orchestrator.generate(request)
except Exception as e:
    if "Both primary and fallback" in str(e):
        # Both providers failed
        logger.error("All LLM providers unavailable")
        # Queue request for later or return error to user
        return {"error": "LLM service temporarily unavailable"}
```

## Best Practices

1. **Use the Orchestrator**: Always use `LLMOrchestrator` instead of individual providers for production code
2. **Monitor Circuit States**: Regularly check circuit breaker states to detect issues early
3. **Set Appropriate Timeouts**: 30 seconds is reasonable for most LLM calls, adjust if needed
4. **Handle Errors Gracefully**: Always have a fallback plan when both providers fail
5. **Track Statistics**: Monitor usage statistics to optimize costs and detect patterns
6. **Test Failure Scenarios**: Regularly test failover behavior in staging environment
7. **Configure Alerts**: Set up alerts when circuits open or failure rates spike

## Performance Considerations

- **Circuit Breaker Overhead**: Minimal (~1ms per call for state checking)
- **Retry Delays**: Maximum 14 seconds total for 3 retries (2s + 4s + 8s)
- **Failover Time**: ~1-2 seconds to switch from primary to fallback
- **Memory Usage**: ~1KB per circuit breaker for tracking recent calls

## Requirements Validation

This implementation validates the following requirements:

✅ **Requirement 2.2**: Exponential backoff retry for LLM API rate limits
- Automatic retry with exponential backoff (2s, 4s, 8s)
- Maximum 3 retry attempts
- Retries on rate limits, connection errors, and server errors

✅ **Requirement 2.3**: Automatic fallback to secondary provider
- Primary/fallback provider pattern implemented
- Automatic failover when primary fails or circuit is open
- Seamless transition between providers

✅ **Requirement 2.6**: Circuit breaker pattern for external service calls
- Circuit breaker with 50% failure threshold
- Prevents cascading failures
- Automatic recovery testing

✅ **Requirement 2.8**: Request timeout for LLM API calls
- 30-second timeout enforced at provider level
- Configurable timeout per orchestrator
- Prevents hanging requests

## Testing

Comprehensive test suite with 26 tests covering:
- Circuit breaker state transitions
- Primary/fallback failover
- Timeout enforcement
- Statistics tracking
- Error handling
- Integration scenarios

Run tests:
```bash
pytest backend/tests/test_llm_resilience.py -v
```

## Troubleshooting

### Circuit Keeps Opening

**Symptoms**: Circuit breaker frequently opens, causing requests to fail fast

**Possible Causes**:
- API keys invalid or expired
- Rate limits too low for request volume
- Network connectivity issues
- Service outage

**Solutions**:
1. Check API key validity
2. Verify rate limits and adjust request rate
3. Check network connectivity
4. Monitor service status pages
5. Adjust circuit breaker threshold if needed

### High Fallback Usage

**Symptoms**: Most requests use fallback provider instead of primary

**Possible Causes**:
- Primary provider circuit is open
- Primary provider experiencing issues
- Primary provider rate limits exceeded

**Solutions**:
1. Check primary circuit state
2. Review primary provider logs
3. Verify rate limits
4. Consider increasing primary provider capacity
5. Manually reset circuit if issue is resolved

### Both Providers Failing

**Symptoms**: All requests fail with "Both primary and fallback" error

**Possible Causes**:
- Both circuits are open
- Network connectivity issues
- Both services experiencing outages
- Invalid API keys

**Solutions**:
1. Check both circuit states
2. Verify network connectivity
3. Check service status pages
4. Verify API keys
5. Implement request queuing for retry later

## Future Enhancements

Potential improvements for future iterations:

1. **Adaptive Timeouts**: Adjust timeout based on historical response times
2. **Priority Queuing**: Queue failed requests for retry when circuits close
3. **Cost Optimization**: Route to cheaper provider when both are available
4. **Response Caching**: Cache responses to reduce API calls
5. **Metrics Export**: Export metrics to Prometheus/CloudWatch
6. **Dynamic Configuration**: Update circuit breaker config without restart
7. **Multi-Region Failover**: Support multiple regions for each provider
8. **Request Hedging**: Send duplicate requests to both providers for critical calls

## References

- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
- [Resilience Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/category/resiliency)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Anthropic API Documentation](https://docs.anthropic.com/claude/reference)
