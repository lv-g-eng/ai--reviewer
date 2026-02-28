"""
LLM Client Demo

Demonstrates the usage of the multi-provider LLM client.

Usage:
    python -m backend.examples.llm_client_demo

Requirements:
    - Set OPENAI_API_KEY or ANTHROPIC_API_KEY in environment
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.llm import (
    get_llm_provider,
    LLMProviderType,
    LLMRequest,
    LLMProviderFactory
)


async def demo_openai_provider():
    """Demonstrate OpenAI provider usage"""
    print("\n" + "="*60)
    print("OpenAI GPT-4 Provider Demo")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Skipping OpenAI demo.")
        return
    
    try:
        # Get provider
        provider = get_llm_provider(LLMProviderType.OPENAI, model="gpt-4-turbo-preview")
        print(f"✓ Provider initialized: {provider.get_provider_type().value}/{provider.model}")
        
        # Create request
        request = LLMRequest(
            prompt="Write a Python function to calculate fibonacci numbers.",
            system_prompt="You are a helpful Python programming assistant.",
            temperature=0.3,
            max_tokens=500
        )
        
        print("\n📝 Generating response...")
        response = await provider.generate(request)
        
        print(f"\n✓ Response generated successfully!")
        print(f"  - Tokens: {response.tokens['total']} (prompt: {response.tokens['prompt']}, completion: {response.tokens['completion']})")
        print(f"  - Cost: ${response.cost:.4f}")
        print(f"\n📄 Content:\n{response.content[:200]}...")
        
        # Show usage stats
        stats = provider.get_usage_stats()
        print(f"\n📊 Usage Statistics:")
        print(f"  - Total tokens: {stats['total_tokens']}")
        print(f"  - Total cost: ${stats['total_cost']:.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_anthropic_provider():
    """Demonstrate Anthropic provider usage"""
    print("\n" + "="*60)
    print("Anthropic Claude 3.5 Provider Demo")
    print("="*60)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set. Skipping Anthropic demo.")
        return
    
    try:
        # Get provider
        provider = get_llm_provider(
            LLMProviderType.ANTHROPIC,
            model="claude-3-5-sonnet-20241022"
        )
        print(f"✓ Provider initialized: {provider.get_provider_type().value}/{provider.model}")
        
        # Create request with JSON mode
        request = LLMRequest(
            prompt="List 3 best practices for Python code review in JSON format with 'practice' and 'description' fields.",
            system_prompt="You are a code review expert.",
            temperature=0.2,
            max_tokens=500,
            json_mode=True
        )
        
        print("\n📝 Generating response (JSON mode)...")
        response = await provider.generate(request)
        
        print(f"\n✓ Response generated successfully!")
        print(f"  - Tokens: {response.tokens['total']} (input: {response.tokens['prompt']}, output: {response.tokens['completion']})")
        print(f"  - Cost: ${response.cost:.6f}")
        print(f"\n📄 Content:\n{response.content[:300]}...")
        
        # Show usage stats
        stats = provider.get_usage_stats()
        print(f"\n📊 Usage Statistics:")
        print(f"  - Total tokens: {stats['total_tokens']}")
        print(f"  - Total cost: ${stats['total_cost']:.6f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_provider_comparison():
    """Compare responses from different providers"""
    print("\n" + "="*60)
    print("Provider Comparison Demo")
    print("="*60)
    
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if not (has_openai and has_anthropic):
        print("⚠️  Both OPENAI_API_KEY and ANTHROPIC_API_KEY required for comparison.")
        return
    
    prompt = "Explain the concept of dependency injection in 2 sentences."
    
    try:
        # OpenAI
        print("\n🤖 OpenAI GPT-4:")
        openai_provider = get_llm_provider(LLMProviderType.OPENAI)
        openai_request = LLMRequest(prompt=prompt, temperature=0.3, max_tokens=200)
        openai_response = await openai_provider.generate(openai_request)
        print(f"  Response: {openai_response.content}")
        print(f"  Cost: ${openai_response.cost:.4f}")
        
        # Anthropic
        print("\n🤖 Anthropic Claude:")
        anthropic_provider = get_llm_provider(LLMProviderType.ANTHROPIC)
        anthropic_request = LLMRequest(prompt=prompt, temperature=0.3, max_tokens=200)
        anthropic_response = await anthropic_provider.generate(anthropic_request)
        print(f"  Response: {anthropic_response.content}")
        print(f"  Cost: ${anthropic_response.cost:.6f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_usage_tracking():
    """Demonstrate usage tracking across multiple requests"""
    print("\n" + "="*60)
    print("Usage Tracking Demo")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Skipping usage tracking demo.")
        return
    
    try:
        provider = get_llm_provider(LLMProviderType.OPENAI)
        
        prompts = [
            "What is Python?",
            "What is JavaScript?",
            "What is TypeScript?"
        ]
        
        print(f"\n📝 Making {len(prompts)} requests...")
        
        for i, prompt in enumerate(prompts, 1):
            request = LLMRequest(prompt=prompt, max_tokens=100)
            response = await provider.generate(request)
            print(f"  {i}. {prompt[:30]}... - {response.tokens['total']} tokens, ${response.cost:.4f}")
        
        # Show cumulative stats
        stats = provider.get_usage_stats()
        print(f"\n📊 Cumulative Statistics:")
        print(f"  - Total requests: {len(prompts)}")
        print(f"  - Total tokens: {stats['total_tokens']}")
        print(f"  - Total cost: ${stats['total_cost']:.4f}")
        print(f"  - Average tokens per request: {stats['total_tokens'] / len(prompts):.0f}")
        print(f"  - Average cost per request: ${stats['total_cost'] / len(prompts):.4f}")
        
        # Reset usage
        print("\n🔄 Resetting usage statistics...")
        provider.reset_usage()
        stats = provider.get_usage_stats()
        print(f"  - Total tokens after reset: {stats['total_tokens']}")
        print(f"  - Total cost after reset: ${stats['total_cost']:.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_factory_pattern():
    """Demonstrate factory pattern usage"""
    print("\n" + "="*60)
    print("Factory Pattern Demo")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Skipping factory demo.")
        return
    
    try:
        # Create provider with custom configuration
        print("\n🏭 Creating provider with custom configuration...")
        provider = LLMProviderFactory.create_provider(
            provider_type=LLMProviderType.OPENAI,
            model="gpt-4",
            timeout=60
        )
        print(f"  ✓ Created: {provider.model} with 60s timeout")
        
        # Get cached provider
        print("\n📦 Getting cached provider...")
        cached_provider = LLMProviderFactory.get_provider(
            LLMProviderType.OPENAI,
            model="gpt-4",
            use_cache=True
        )
        print(f"  ✓ Same instance: {provider is cached_provider}")
        
        # Get new instance without cache
        print("\n🆕 Getting new provider without cache...")
        new_provider = LLMProviderFactory.get_provider(
            LLMProviderType.OPENAI,
            model="gpt-4",
            use_cache=False
        )
        print(f"  ✓ Different instance: {provider is not new_provider}")
        
        # Clear cache
        print("\n🗑️  Clearing provider cache...")
        LLMProviderFactory.clear_cache()
        print("  ✓ Cache cleared")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("LLM Client Multi-Provider Demo")
    print("="*60)
    print("\nThis demo showcases the multi-provider LLM client capabilities.")
    print("Make sure to set OPENAI_API_KEY and/or ANTHROPIC_API_KEY in your environment.")
    
    # Run demos
    await demo_openai_provider()
    await demo_anthropic_provider()
    await demo_provider_comparison()
    await demo_usage_tracking()
    await demo_factory_pattern()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)


if __name__ == "__main__":
    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if not (has_openai or has_anthropic):
        print("\n⚠️  Warning: No API keys found!")
        print("Please set at least one of the following environment variables:")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        print("\nExample:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)
    
    # Run demos
    asyncio.run(main())
