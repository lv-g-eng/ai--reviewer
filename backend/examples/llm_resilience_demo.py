"""
LLM Resilience Patterns Demo

Demonstrates circuit breaker and primary/fallback provider patterns.
"""

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
    print("\n" + "="*70)
    print("DEMO 1: Basic Usage with Automatic Failover")
    print("="*70)
    
    # Create orchestrator with default configuration
    orchestrator = create_orchestrator()
    
    # Create request
    request = LLMRequest(
        prompt="What is the capital of France?",
        temperature=0.3,
        max_tokens=100
    )
    
    print("\nMaking request to LLM orchestrator...")
    print(f"Primary provider: {orchestrator.config.primary_provider.value}")
    print(f"Fallback provider: {orchestrator.config.fallback_provider.value}")
    
    try:
        response = await orchestrator.generate(request)
        
        print(f"\n✓ Success!")
        print(f"Provider used: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Tokens: {response.tokens['total']}")
        print(f"Cost: ${response.cost:.4f}")
        print(f"\nResponse: {response.content[:200]}...")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # Show statistics
    stats = orchestrator.get_stats()
    print(f"\nStatistics:")
    print(f"  Primary calls: {stats['primary_calls']}")
    print(f"  Fallback calls: {stats['fallback_calls']}")
    print(f"  Total failures: {stats['total_failures']}")


async def demo_circuit_breaker():
    """Demo 2: Circuit breaker behavior"""
    print("\n" + "="*70)
    print("DEMO 2: Circuit Breaker Behavior")
    print("="*70)
    
    # Create orchestrator with fast circuit breaker for demo
    config = OrchestratorConfig(
        circuit_breaker_config=CircuitBreakerConfig(
            failure_threshold=0.5,
            window_size=4,  # Small window for demo
            timeout=5  # Short timeout for demo
        )
    )
    orchestrator = LLMOrchestrator(config)
    
    print("\nCircuit breaker configuration:")
    print(f"  Failure threshold: 50%")
    print(f"  Window size: 4 calls")
    print(f"  Timeout: 5 seconds")
    
    # Simulate failures by using invalid API key
    orchestrator.primary_provider.api_key = "invalid_key"
    
    print("\n\nSimulating failures with invalid API key...")
    
    request = LLMRequest(prompt="Test", max_tokens=10)
    
    for i in range(6):
        print(f"\nAttempt {i+1}:")
        try:
            response = await orchestrator.generate(request)
            print(f"  ✓ Success from {response.provider}")
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"  ✗ Failed: {error_msg}...")
        
        # Show circuit state
        primary_stats = orchestrator.primary_circuit.get_stats()
        print(f"  Primary circuit: {primary_stats['state']}")
        print(f"  Failure rate: {primary_stats['failure_rate']:.1%}")
    
    print("\n\nCircuit breaker opened after reaching failure threshold!")
    print("Subsequent requests fail fast without calling the API.")


async def demo_custom_configuration():
    """Demo 3: Custom configuration"""
    print("\n" + "="*70)
    print("DEMO 3: Custom Configuration")
    print("="*70)
    
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
    
    print("\nCustom configuration:")
    print(f"  Primary: {config.primary_provider.value} ({config.primary_model})")
    print(f"  Fallback: {config.fallback_provider.value} ({config.fallback_model})")
    print(f"  Failure threshold: {cb_config.failure_threshold:.0%}")
    print(f"  Success threshold: {cb_config.success_threshold}")
    print(f"  Timeout: {config.timeout}s")
    
    orchestrator = LLMOrchestrator(config)
    
    request = LLMRequest(
        prompt="Explain quantum computing in one sentence",
        temperature=0.3,
        max_tokens=100
    )
    
    print("\nMaking request...")
    try:
        response = await orchestrator.generate(request)
        print(f"\n✓ Success from {response.provider}")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def demo_statistics_monitoring():
    """Demo 4: Statistics and monitoring"""
    print("\n" + "="*70)
    print("DEMO 4: Statistics and Monitoring")
    print("="*70)
    
    orchestrator = create_orchestrator()
    
    # Make multiple requests
    prompts = [
        "What is 2+2?",
        "Name a color",
        "What day comes after Monday?"
    ]
    
    print("\nMaking multiple requests...")
    for i, prompt in enumerate(prompts, 1):
        print(f"\nRequest {i}: {prompt}")
        try:
            request = LLMRequest(prompt=prompt, max_tokens=50)
            response = await orchestrator.generate(request)
            print(f"  ✓ {response.provider}: {response.content[:50]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Get comprehensive statistics
    stats = orchestrator.get_stats()
    
    print("\n" + "-"*70)
    print("COMPREHENSIVE STATISTICS")
    print("-"*70)
    
    print("\nRequest Statistics:")
    print(f"  Primary calls: {stats['primary_calls']}")
    print(f"  Fallback calls: {stats['fallback_calls']}")
    print(f"  Total failures: {stats['total_failures']}")
    
    print("\nPrimary Circuit Breaker:")
    primary_cb = stats['primary_circuit']
    print(f"  State: {primary_cb['state']}")
    print(f"  Failure count: {primary_cb['failure_count']}")
    print(f"  Success count: {primary_cb['success_count']}")
    print(f"  Failure rate: {primary_cb['failure_rate']:.1%}")
    print(f"  Recent calls: {primary_cb['recent_calls']}")
    
    print("\nFallback Circuit Breaker:")
    fallback_cb = stats['fallback_circuit']
    print(f"  State: {fallback_cb['state']}")
    print(f"  Failure count: {fallback_cb['failure_count']}")
    print(f"  Success count: {fallback_cb['success_count']}")
    print(f"  Failure rate: {fallback_cb['failure_rate']:.1%}")
    print(f"  Recent calls: {fallback_cb['recent_calls']}")
    
    print("\nPrimary Provider Usage:")
    primary_usage = stats['primary_usage']
    print(f"  Total tokens: {primary_usage['total_tokens']}")
    print(f"  Total cost: ${primary_usage['total_cost']:.4f}")
    print(f"  Provider: {primary_usage['provider']}")
    print(f"  Model: {primary_usage['model']}")
    
    print("\nFallback Provider Usage:")
    fallback_usage = stats['fallback_usage']
    print(f"  Total tokens: {fallback_usage['total_tokens']}")
    print(f"  Total cost: ${fallback_usage['total_cost']:.4f}")
    print(f"  Provider: {fallback_usage['provider']}")
    print(f"  Model: {fallback_usage['model']}")


async def demo_error_handling():
    """Demo 5: Error handling patterns"""
    print("\n" + "="*70)
    print("DEMO 5: Error Handling Patterns")
    print("="*70)
    
    orchestrator = create_orchestrator()
    
    print("\nPattern 1: Disable fallback (primary only)")
    print("-" * 50)
    
    request = LLMRequest(prompt="Test", max_tokens=10)
    
    try:
        response = await orchestrator.generate(request, use_fallback=False)
        print(f"✓ Primary succeeded: {response.provider}")
    except Exception as e:
        print(f"✗ Primary failed: {str(e)[:100]}...")
        print("  → Could return cached result or queue for later")
    
    print("\nPattern 2: Handle circuit breaker open")
    print("-" * 50)
    
    # Manually open circuit for demo
    orchestrator.primary_circuit.state = CircuitState.OPEN
    orchestrator.primary_circuit.last_failure_time = 999999999999
    
    try:
        response = await orchestrator.generate(request)
        print(f"✓ Fallback succeeded: {response.provider}")
    except Exception as e:
        print(f"✗ Both providers unavailable: {str(e)[:100]}...")
        print("  → Return graceful degradation response")
    
    # Reset for next demo
    orchestrator.reset_circuits()
    
    print("\nPattern 3: Manual circuit control")
    print("-" * 50)
    
    print("Resetting all circuits...")
    orchestrator.reset_circuits()
    print("✓ Circuits reset to CLOSED state")
    
    print("\nResetting statistics...")
    orchestrator.reset_stats()
    print("✓ Statistics reset")
    
    stats = orchestrator.get_stats()
    print(f"\nVerification:")
    print(f"  Primary calls: {stats['primary_calls']}")
    print(f"  Fallback calls: {stats['fallback_calls']}")
    print(f"  Primary circuit: {stats['primary_circuit']['state']}")
    print(f"  Fallback circuit: {stats['fallback_circuit']['state']}")


async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("LLM RESILIENCE PATTERNS DEMONSTRATION")
    print("="*70)
    print("\nThis demo showcases the resilience patterns implemented for")
    print("the LLM service, including circuit breakers and primary/fallback")
    print("provider patterns.")
    
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
            print("\n\nDemo interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos):
            input("\nPress Enter to continue to next demo...")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Automatic failover from primary to fallback provider")
    print("  2. Circuit breaker prevents cascading failures")
    print("  3. Exponential backoff retry for transient failures")
    print("  4. 30-second timeout enforcement")
    print("  5. Comprehensive statistics and monitoring")
    print("\nFor more information, see:")
    print("  - backend/app/services/llm/RESILIENCE_PATTERNS.md")
    print("  - backend/tests/test_llm_resilience.py")
    print()


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠ Warning: No API keys found in environment")
        print("Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY to run live demos")
        print("\nSome demos will fail, but you can still see the resilience patterns")
        input("\nPress Enter to continue anyway...")
    
    asyncio.run(main())
