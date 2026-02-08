# Shared Infrastructure and Utilities

This module provides shared infrastructure components used across all platform services.

## Components

### 1. Standards Models (`standards.py`)

Structured representations of software quality standards for classification and compliance reporting.

**Standards Supported:**
- **ISO/IEC 25010**: Software quality characteristics (8 characteristics, 31 sub-characteristics)
- **ISO/IEC 23396**: Software engineering practices (6 common practices)
- **OWASP Top 10 2021**: Web application security vulnerabilities

**Usage:**
```python
from app.shared import StandardsMapper, ISO25010CharacteristicType

mapper = StandardsMapper()

# Map finding to ISO/IEC 25010
characteristic = mapper.map_to_iso25010("security")
print(characteristic.name)  # "Security"

# Map to ISO/IEC 23396
practice = mapper.map_to_iso23396("code_quality")
print(practice.id)  # "SE-3"

# Map to OWASP Top 10
vuln = mapper.map_to_owasp("sql injection")
print(vuln.rank)  # 3
```

**Validates Requirements:** 1.3, 1.4, 1.6, 8.1, 8.2, 8.3

### 2. Custom Exceptions (`exceptions.py`)

Structured exception hierarchy for better error handling and reporting.

**Exception Types:**
- `ServiceException`: Base exception for all service errors
- `LLMProviderException`: LLM provider errors
- `CircuitBreakerException`: Circuit breaker open errors
- `CacheException`: Cache operation errors
- `DatabaseException`: Database operation errors
- `ValidationException`: Validation errors
- `AuthenticationException`: Authentication errors
- `AuthorizationException`: Authorization errors

**Usage:**
```python
from app.shared import LLMProviderException

raise LLMProviderException(
    "Provider timeout",
    provider="openai",
    model="gpt-4",
    error_code="TIMEOUT"
)
```

**Validates Requirements:** 1.8, 7.6

### 3. Circuit Breaker (`circuit_breaker.py`)

Prevents cascading failures by stopping requests to failing services.

**States:**
- `CLOSED`: Normal operation, requests pass through
- `OPEN`: Failure threshold exceeded, requests fail immediately
- `HALF_OPEN`: Testing if service recovered

**Usage:**
```python
from app.shared import get_circuit_breaker, CircuitBreakerConfig

# Get or create circuit breaker
breaker = get_circuit_breaker(
    "external_api",
    CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=2,
        timeout=60
    )
)

# Use circuit breaker
try:
    result = breaker.call(external_api_call, arg1, arg2)
except CircuitBreakerException:
    # Circuit is open, service unavailable
    pass
```

**Validates Requirements:** 7.7

### 4. LLM Provider Abstraction (`llm_provider.py`)

Unified interface for multiple LLM providers with automatic failover.

**Supported Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5)
- Ollama (local models)

**Usage:**
```python
from app.shared import LLMOrchestrator, LLMProviderConfig, LLMProviderType

# Configure providers
providers = [
    LLMProviderConfig(
        provider_type=LLMProviderType.OPENAI,
        model="gpt-4",
        api_key="sk-...",
        priority=1
    ),
    LLMProviderConfig(
        provider_type=LLMProviderType.ANTHROPIC,
        model="claude-3.5-sonnet",
        api_key="sk-ant-...",
        priority=2
    ),
]

# Create orchestrator
orchestrator = LLMOrchestrator(providers)

# Generate with automatic failover
response = await orchestrator.generate(
    "Explain this code",
    system_prompt="You are a code reviewer"
)
```

**Validates Requirements:** 1.7, 3.1, 3.7

### 5. Cache Manager (`cache_manager.py`)

Enhanced Redis cache utilities with connection pooling.

**Features:**
- Connection pooling
- Automatic serialization/deserialization
- Pattern-based deletion
- Batch operations
- Standard key prefixes

**Usage:**
```python
from app.shared import CacheManager, CacheKey

# Initialize cache manager
cache = CacheManager(
    host="localhost",
    port=6379,
    max_connections=50
)
await cache.connect()

# Set cache value
await cache.set(
    CacheKey.session("user123"),
    {"user_id": "user123", "role": "admin"},
    expiration=3600
)

# Get cache value
session = await cache.get(CacheKey.session("user123"))

# Delete pattern
await cache.delete_pattern("session:*")
```

**Validates Requirements:** 7.3, 10.4, 10.5

### 6. Task Priority (`task_priority.py`)

Celery task queue enhancements with priority support.

**Priority Levels:**
- `CRITICAL` (0): Security issues, critical errors
- `HIGH` (3): Important analysis tasks
- `NORMAL` (5): Regular tasks
- `LOW` (7): Background tasks
- `VERY_LOW` (9): Non-urgent maintenance

**Usage:**
```python
from app.shared import TaskPriority, PriorityTaskRouter
from celery import Celery

# Configure Celery with priorities
app = Celery('myapp')
app.conf.update(
    task_routes=(PriorityTaskRouter.route_for_task,)
)

# Create priority task
@app.task(priority=TaskPriority.HIGH)
def important_task():
    pass

# Tasks are automatically routed to appropriate queues
```

**Validates Requirements:** 10.6

## Integration

All shared components are designed to work together:

```python
from app.shared import (
    StandardsMapper,
    LLMOrchestrator,
    CacheManager,
    get_circuit_breaker,
)

# Standards mapping with caching
mapper = StandardsMapper()
cache = CacheManager()

async def get_cached_standard(category: str):
    cache_key = f"standard:{category}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # Map to standard
    standard = mapper.map_to_iso25010(category)
    
    # Cache result
    await cache.set(cache_key, standard, expiration=3600)
    return standard

# LLM with circuit breaker
breaker = get_circuit_breaker("llm_service")
orchestrator = LLMOrchestrator(providers)

async def safe_llm_call(prompt: str):
    try:
        return breaker.call(
            lambda: orchestrator.generate(prompt)
        )
    except CircuitBreakerException:
        # Fallback to cached response or default
        return await cache.get(f"llm_fallback:{prompt}")
```

## Testing

All components include comprehensive error handling and logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Components log important events
# - Circuit breaker state changes
# - LLM provider failovers
# - Cache hits/misses
# - Task routing decisions
```

## Configuration

Environment variables for shared components:

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Requirements Validation

This module validates the following requirements:

- **1.3, 1.4**: Standards compliance mapping (ISO/IEC 25010, ISO/IEC 23396)
- **1.6**: OWASP Top 10 security references
- **1.7, 3.7**: LLM provider failover
- **1.8, 7.6**: Error logging completeness
- **7.2, 7.3**: Asynchronous message queues and caching
- **7.7**: Circuit breaker patterns
- **10.4, 10.5**: Cache hit rates and connection pooling
- **10.6**: Task priority ordering
