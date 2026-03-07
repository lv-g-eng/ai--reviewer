"""
LLM Client Demo

Demonstrates the usage of the multi-provider LLM client.

Usage:
    python -m backend.examples.llm_client_demo

Requirements:
    - Set OPENAI_API_KEY or ANTHROPIC_API_KEY in environment
"""
import logging
logger = logging.getLogger(__name__)


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
    logger.info("\n" + "="*60)
    logger.info("OpenAI GPT-4 Provider Demo")
    logger.info("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.info("⚠️  OPENAI_API_KEY not set. Skipping OpenAI demo.")
        return
    
    try:
        # Get provider
        provider = get_llm_provider(LLMProviderType.OPENAI, model="gpt-4-turbo-preview")
        logger.info("✓ Provider initialized: {provider.get_provider_type().value}/{provider.model}")
        
        # Create request
        request = LLMRequest(
            prompt="Write a Python function to calculate fibonacci numbers.",
            system_prompt="You are a helpful Python programming assistant.",
            temperature=0.3,
            max_tokens=500
        )
        
        logger.info("\n📝 Generating response...")
        response = await provider.generate(request)
        
        logger.info("\n✓ Response generated successfully!")
        logger.info("  - Tokens: {response.tokens['total']} (prompt: {response.tokens['prompt']}, completion: {response.tokens['completion']})")
        logger.info("  - Cost: ${response.cost:.4f}")
        logger.info("\n📄 Content:\n{response.content[:200]}...")
        
        # Show usage stats
        stats = provider.get_usage_stats()
        logger.info("\n📊 Usage Statistics:")
        logger.info("  - Total tokens: {stats['total_tokens']}")
        logger.info("  - Total cost: ${stats['total_cost']:.4f}")
        
    except Exception as e:
        logger.info("❌ Error: {e}")


async def demo_anthropic_provider():
    """Demonstrate Anthropic provider usage"""
    logger.info("\n" + "="*60)
    logger.info("Anthropic Claude 3.5 Provider Demo")
    logger.info("="*60)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        logger.info("⚠️  ANTHROPIC_API_KEY not set. Skipping Anthropic demo.")
        return
    
    try:
        # Get provider
        provider = get_llm_provider(
            LLMProviderType.ANTHROPIC,
            model="claude-3-5-sonnet-20241022"
        )
        logger.info("✓ Provider initialized: {provider.get_provider_type().value}/{provider.model}")
        
        # Create request with JSON mode
        request = LLMRequest(
            prompt="List 3 best practices for Python code review in JSON format with 'practice' and 'description' fields.",
            system_prompt="You are a code review expert.",
            temperature=0.2,
            max_tokens=500,
            json_mode=True
        )
        
        logger.info("\n📝 Generating response (JSON mode)...")
        response = await provider.generate(request)
        
        logger.info("\n✓ Response generated successfully!")
        logger.info("  - Tokens: {response.tokens['total']} (input: {response.tokens['prompt']}, output: {response.tokens['completion']})")
        logger.info("  - Cost: ${response.cost:.6f}")
        logger.info("\n📄 Content:\n{response.content[:300]}...")
        
        # Show usage stats
        stats = provider.get_usage_stats()
        logger.info("\n📊 Usage Statistics:")
        logger.info("  - Total tokens: {stats['total_tokens']}")
        logger.info("  - Total cost: ${stats['total_cost']:.6f}")
        
    except Exception as e:
        logger.info("❌ Error: {e}")


async def demo_provider_comparison():
    """Compare responses from different providers"""
    logger.info("\n" + "="*60)
    logger.info("Provider Comparison Demo")
    logger.info("="*60)
    
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if not (has_openai and has_anthropic):
        logger.info("⚠️  Both OPENAI_API_KEY and ANTHROPIC_API_KEY required for comparison.")
        return
    
    prompt = "Explain the concept of dependency injection in 2 sentences."
    
    try:
        # OpenAI
        logger.info("\n🤖 OpenAI GPT-4:")
        openai_provider = get_llm_provider(LLMProviderType.OPENAI)
        openai_request = LLMRequest(prompt=prompt, temperature=0.3, max_tokens=200)
        openai_response = await openai_provider.generate(openai_request)
        logger.info("  Response: {openai_response.content}")
        logger.info("  Cost: ${openai_response.cost:.4f}")
        
        # Anthropic
        logger.info("\n🤖 Anthropic Claude:")
        anthropic_provider = get_llm_provider(LLMProviderType.ANTHROPIC)
        anthropic_request = LLMRequest(prompt=prompt, temperature=0.3, max_tokens=200)
        anthropic_response = await anthropic_provider.generate(anthropic_request)
        logger.info("  Response: {anthropic_response.content}")
        logger.info("  Cost: ${anthropic_response.cost:.6f}")
        
    except Exception as e:
        logger.info("❌ Error: {e}")


async def demo_usage_tracking():
    """Demonstrate usage tracking across multiple requests"""
    logger.info("\n" + "="*60)
    logger.info("Usage Tracking Demo")
    logger.info("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.info("⚠️  OPENAI_API_KEY not set. Skipping usage tracking demo.")
        return
    
    try:
        provider = get_llm_provider(LLMProviderType.OPENAI)
        
        prompts = [
            "What is Python?",
            "What is JavaScript?",
            "What is TypeScript?"
        ]
        
        logger.info("\n📝 Making {len(prompts)} requests...")
        
        for i, prompt in enumerate(prompts, 1):
            request = LLMRequest(prompt=prompt, max_tokens=100)
            response = await provider.generate(request)
            logger.info("  {i}. {prompt[:30]}... - {response.tokens['total']} tokens, ${response.cost:.4f}")
        
        # Show cumulative stats
        stats = provider.get_usage_stats()
        logger.info("\n📊 Cumulative Statistics:")
        logger.info("  - Total requests: {len(prompts)}")
        logger.info("  - Total tokens: {stats['total_tokens']}")
        logger.info("  - Total cost: ${stats['total_cost']:.4f}")
        logger.info("  - Average tokens per request: {stats['total_tokens'] / len(prompts):.0f}")
        logger.info("  - Average cost per request: ${stats['total_cost'] / len(prompts):.4f}")
        
        # Reset usage
        logger.info("\n🔄 Resetting usage statistics...")
        provider.reset_usage()
        stats = provider.get_usage_stats()
        logger.info("  - Total tokens after reset: {stats['total_tokens']}")
        logger.info("  - Total cost after reset: ${stats['total_cost']:.4f}")
        
    except Exception as e:
        logger.info("❌ Error: {e}")


async def demo_factory_pattern():
    """Demonstrate factory pattern usage"""
    logger.info("\n" + "="*60)
    logger.info("Factory Pattern Demo")
    logger.info("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.info("⚠️  OPENAI_API_KEY not set. Skipping factory demo.")
        return
    
    try:
        # Create provider with custom configuration
        logger.info("\n🏭 Creating provider with custom configuration...")
        provider = LLMProviderFactory.create_provider(
            provider_type=LLMProviderType.OPENAI,
            model="gpt-4",
            timeout=60
        )
        logger.info("  ✓ Created: {provider.model} with 60s timeout")
        
        # Get cached provider
        logger.info("\n📦 Getting cached provider...")
        cached_provider = LLMProviderFactory.get_provider(
            LLMProviderType.OPENAI,
            model="gpt-4",
            use_cache=True
        )
        logger.info("  ✓ Same instance: {provider is cached_provider}")
        
        # Get new instance without cache
        logger.info("\n🆕 Getting new provider without cache...")
        new_provider = LLMProviderFactory.get_provider(
            LLMProviderType.OPENAI,
            model="gpt-4",
            use_cache=False
        )
        logger.info("  ✓ Different instance: {provider is not new_provider}")
        
        # Clear cache
        logger.info("\n🗑️  Clearing provider cache...")
        LLMProviderFactory.clear_cache()
        logger.info("  ✓ Cache cleared")
        
    except Exception as e:
        logger.info("❌ Error: {e}")


async def main():
    """Run all demos"""
    logger.info("\n" + "="*60)
    logger.info("LLM Client Multi-Provider Demo")
    logger.info("="*60)
    logger.info("\nThis demo showcases the multi-provider LLM client capabilities.")
    logger.info("Make sure to set OPENAI_API_KEY and/or ANTHROPIC_API_KEY in your environment.")
    
    # Run demos
    await demo_openai_provider()
    await demo_anthropic_provider()
    await demo_provider_comparison()
    await demo_usage_tracking()
    await demo_factory_pattern()
    
    logger.info("\n" + "="*60)
    logger.info("Demo Complete!")
    logger.info("="*60)


if __name__ == "__main__":
    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if not (has_openai or has_anthropic):
        logger.info("\n⚠️  Warning: No API keys found!")
        logger.info("Please set at least one of the following environment variables:")
        logger.info("  - OPENAI_API_KEY")
        logger.info("  - ANTHROPIC_API_KEY")
        logger.info("\nExample:")
        logger.info("  export OPENAI_API_KEY='sk-...'")
        logger.info("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)
    
    # Run demos
    asyncio.run(main())
