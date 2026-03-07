"""
LLM Resilience Patterns Demo

Demonstrates circuit breaker and primary/fallback provider patterns.
"""
import logging
logger = logging.getLogger(__name__)


import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.llm import (
    create_orchestrator,
    LLMRequest,
    LLMProviderType,
    CircuitBreakerConfig,
    OrchestratorConfig,
    CircuitState
)


async def demo_basic_usage():
    """Demo 1: Basic usage with automatic failover"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 1: Basic Usage with Automatic Failover")
    logger.info("="*70)
    
    # Create orchestrator with default configuration
    orchestrator = create_orchestrator()
    
    # Create request
    request = LLMRequest(
        prompt="What is the capital of France?",
        temperature=0.3,
        max_tokens=100
    )
    
    logger.info("\nMaking request to LLM orchestrator...")
    logger.info("Primary provider: {orchestrator.config.primary_provider.value}")
    logger.info("Fallback provider: {orchestrator.config.fallback_provider.value}")
    
    try:
        response = await orchestrator.generate(request)
        
        logger.info("\n✓ Success!")
        logger.info("Provider used: {response.provider}")
        logger.info("Model: {response.model}")
        logger.info("Tokens: {response.tokens['total']}")
        logger.info("Cost: ${response.cost:.4f}")
        logger.info("\nResponse: {response.content[:200]}...")
        
    except Exception as e:
        logger.info("\n✗ Error: {e}")
    
    # Show statistics
    stats = orchestrator.get_stats()
    logger.info("\nStatistics:")
    logger.info("  Primary calls: {stats['primary_calls']}")
    logger.info("  Fallback calls: {stats['fallback_calls']}")
    logger.info("  Total failures: {stats['total_failures']}")


async def demo_circuit_breaker():
    """Demo 2: Circuit breaker behavior"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 2: Circuit Breaker Behavior")
    logger.info("="*70)
    
    # Create orchestrator with fast circuit breaker for demo
    config = OrchestratorConfig(
        circuit_breaker_config=CircuitBreakerConfig(
            failure_threshold=0.5,
            window_size=4,  # Small window for demo
            timeout=5  # Short timeout for demo
        )
    )
    orchestrator = LLMOrchestrator(config)
    
    logger.info("\nCircuit breaker configuration:")
    logger.info("  Failure threshold: 50%")
    logger.info("  Window size: 4 calls")
    logger.info("  Timeout: 5 seconds")
    
    # Simulate failures by using invalid API key
    orchestrator.primary_provider.api_key = "invalid_key"
    
    logger.info("\n\nSimulating failures with invalid API key...")
    
    request = LLMRequest(prompt="Test", max_tokens=10)
    
    for i in range(6):
        logger.info("\nAttempt {i+1}:")
        try:
            response = await orchestrator.generate(request)
            logger.info("  ✓ Success from {response.provider}")
        except Exception as e:
            error_msg = str(e)[:100]
            logger.info("  ✗ Failed: {error_msg}...")
        
        # Show circuit state
        primary_stats = orchestrator.primary_circuit.get_stats()
        logger.info("  Primary circuit: {primary_stats['state']}")
        logger.info("  Failure rate: {primary_stats['failure_rate']:.1%}")
    
    logger.info("\n\nCircuit breaker opened after reaching failure threshold!")
    logger.info("Subsequent requests fail fast without calling the API.")


async def demo_custom_configuration():
    """Demo 3: Custom configuration"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 3: Custom Configuration")
    logger.info("="*70)
    
    # Custom circuit breaker config
    cb_config = CircuitBreakerConfig(
        failure_threshold=0.6,  # More tolerant
        success_threshold=3,     # Need 3 successes to close
        timeout=30,
        window_size=20
    )
    
    # Custom orchestrator config
    config = OrchestratorConfig(
        primary_provider=LLMProviderType.ANTHROPIC,  # Claude as primary
        fallback_provider=LLMProviderType.OPENAI,    # GPT-4 as fallback
        primary_model="claude-3-5-sonnet-20241022",
        fallback_model="gpt-4-turbo-preview",
        circuit_breaker_config=cb_config,
        timeout=30
    )
    
    logger.info("\nCustom configuration:")
    logger.info("  Primary: {config.primary_provider.value} ({config.primary_model})")
    logger.info("  Fallback: {config.fallback_provider.value} ({config.fallback_model})")
    logger.info("  Failure threshold: {cb_config.failure_threshold:.0%}")
    logger.info("  Success threshold: {cb_config.success_threshold}")
    logger.info("  Timeout: {config.timeout}s")
    
    orchestrator = LLMOrchestrator(config)
    
    request = LLMRequest(
        prompt="Explain quantum computing in one sentence",
        temperature=0.3,
        max_tokens=100
    )
    
    logger.info("\nMaking request...")
    try:
        response = await orchestrator.generate(request)
        logger.info("\n✓ Success from {response.provider}")
        logger.info("Response: {response.content}")
    except Exception as e:
        logger.info("\n✗ Error: {e}")


async def demo_statistics_monitoring():
    """Demo 4: Statistics and monitoring"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 4: Statistics and Monitoring")
    logger.info("="*70)
    
    orchestrator = create_orchestrator()
    
    # Make multiple requests
    prompts = [
        "What is 2+2?",
        "Name a color",
        "What day comes after Monday?"
    ]
    
    logger.info("\nMaking multiple requests...")
    for i, prompt in enumerate(prompts, 1):
        logger.info("\nRequest {i}: {prompt}")
        try:
            request = LLMRequest(prompt=prompt, max_tokens=50)
            response = await orchestrator.generate(request)
            logger.info("  ✓ {response.provider}: {response.content[:50]}...")
        except Exception as e:
            logger.info("  ✗ Error: {e}")
    
    # Get comprehensive statistics
    stats = orchestrator.get_stats()
    
    logger.info("\n" + "-"*70)
    logger.info("COMPREHENSIVE STATISTICS")
    logger.info("-"*70)
    
    logger.info("\nRequest Statistics:")
    logger.info("  Primary calls: {stats['primary_calls']}")
    logger.info("  Fallback calls: {stats['fallback_calls']}")
    logger.info("  Total failures: {stats['total_failures']}")
    
    logger.info("\nPrimary Circuit Breaker:")
    primary_cb = stats['primary_circuit']
    logger.info("  State: {primary_cb['state']}")
    logger.info("  Failure count: {primary_cb['failure_count']}")
    logger.info("  Success count: {primary_cb['success_count']}")
    logger.info("  Failure rate: {primary_cb['failure_rate']:.1%}")
    logger.info("  Recent calls: {primary_cb['recent_calls']}")
    
    logger.info("\nFallback Circuit Breaker:")
    fallback_cb = stats['fallback_circuit']
    logger.info("  State: {fallback_cb['state']}")
    logger.info("  Failure count: {fallback_cb['failure_count']}")
    logger.info("  Success count: {fallback_cb['success_count']}")
    logger.info("  Failure rate: {fallback_cb['failure_rate']:.1%}")
    logger.info("  Recent calls: {fallback_cb['recent_calls']}")
    
    logger.info("\nPrimary Provider Usage:")
    primary_usage = stats['primary_usage']
    logger.info("  Total tokens: {primary_usage['total_tokens']}")
    logger.info("  Total cost: ${primary_usage['total_cost']:.4f}")
    logger.info("  Provider: {primary_usage['provider']}")
    logger.info("  Model: {primary_usage['model']}")
    
    logger.info("\nFallback Provider Usage:")
    fallback_usage = stats['fallback_usage']
    logger.info("  Total tokens: {fallback_usage['total_tokens']}")
    logger.info("  Total cost: ${fallback_usage['total_cost']:.4f}")
    logger.info("  Provider: {fallback_usage['provider']}")
    logger.info("  Model: {fallback_usage['model']}")


async def demo_error_handling():
    """Demo 5: Error handling patterns"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 5: Error Handling Patterns")
    logger.info("="*70)
    
    orchestrator = create_orchestrator()
    
    logger.info("\nPattern 1: Disable fallback (primary only)")
    logger.info("-" * 50)
    
    request = LLMRequest(prompt="Test", max_tokens=10)
    
    try:
        response = await orchestrator.generate(request, use_fallback=False)
        logger.info("✓ Primary succeeded: {response.provider}")
    except Exception as e:
        logger.info("✗ Primary failed: {str(e)[:100]}...")
        logger.info("  → Could return cached result or queue for later")
    
    logger.info("\nPattern 2: Handle circuit breaker open")
    logger.info("-" * 50)
    
    # Manually open circuit for demo
    orchestrator.primary_circuit.state = CircuitState.OPEN
    orchestrator.primary_circuit.last_failure_time = 999999999999
    
    try:
        response = await orchestrator.generate(request)
        logger.info("✓ Fallback succeeded: {response.provider}")
    except Exception as e:
        logger.info("✗ Both providers unavailable: {str(e)[:100]}...")
        logger.info("  → Return graceful degradation response")
    
    # Reset for next demo
    orchestrator.reset_circuits()
    
    logger.info("\nPattern 3: Manual circuit control")
    logger.info("-" * 50)
    
    logger.info("Resetting all circuits...")
    orchestrator.reset_circuits()
    logger.info("✓ Circuits reset to CLOSED state")
    
    logger.info("\nResetting statistics...")
    orchestrator.reset_stats()
    logger.info("✓ Statistics reset")
    
    stats = orchestrator.get_stats()
    logger.info("\nVerification:")
    logger.info("  Primary calls: {stats['primary_calls']}")
    logger.info("  Fallback calls: {stats['fallback_calls']}")
    logger.info("  Primary circuit: {stats['primary_circuit']['state']}")
    logger.info("  Fallback circuit: {stats['fallback_circuit']['state']}")


async def main():
    """Run all demos"""
    logger.info("\n" + "="*70)
    logger.info("LLM RESILIENCE PATTERNS DEMONSTRATION")
    logger.info("="*70)
    logger.info("\nThis demo showcases the resilience patterns implemented for")
    logger.info("the LLM service, including circuit breakers and primary/fallback")
    logger.info("provider patterns.")
    
    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Circuit Breaker", demo_circuit_breaker),
        ("Custom Configuration", demo_custom_configuration),
        ("Statistics Monitoring", demo_statistics_monitoring),
        ("Error Handling", demo_error_handling)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            await demo_func()
        except KeyboardInterrupt:
            logger.info("\n\nDemo interrupted by user")
            break
        except Exception as e:
            logger.info("\n✗ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos):
            input("\nPress Enter to continue to next demo...")
    
    logger.info("\n" + "="*70)
    logger.info("DEMO COMPLETE")
    logger.info("="*70)
    logger.info("\nKey Takeaways:")
    logger.info("  1. Automatic failover from primary to fallback provider")
    logger.info("  2. Circuit breaker prevents cascading failures")
    logger.info("  3. Exponential backoff retry for transient failures")
    logger.info("  4. 30-second timeout enforcement")
    logger.info("  5. Comprehensive statistics and monitoring")
    logger.info("\nFor more information, see:")
    logger.info("  - backend/app/services/llm/RESILIENCE_PATTERNS.md")
    logger.info("  - backend/tests/test_llm_resilience.py")
    logger.info()


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        logger.info("\n⚠ Warning: No API keys found in environment")
        logger.info("Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY to run live demos")
        logger.info("\nSome demos will fail, but you can still see the resilience patterns")
        input("\nPress Enter to continue anyway...")
    
    asyncio.run(main())
