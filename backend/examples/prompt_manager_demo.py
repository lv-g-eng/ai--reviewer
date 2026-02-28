"""
Prompt Manager Demo

Demonstrates how to use the prompt manager for code analysis.

This example shows:
1. Generating code quality review prompts
2. Generating architectural analysis prompts
3. Generating security vulnerability detection prompts
4. Using prompts with the LLM orchestrator

Validates Requirements: 1.4
"""

import asyncio
from app.services.llm import (
    get_prompt_manager,
    AnalysisType,
    create_orchestrator,
    LLMProviderType,
    LLMRequest
)


# Sample code for analysis
SAMPLE_CODE_QUALITY = """
def authenticate_user(username, password):
    # TODO: Add input validation
    user = db.query("SELECT * FROM users WHERE username='" + username + "'")
    if user and user.password == password:
        return user
    return None
"""

SAMPLE_CODE_ARCHITECTURE = """
class UserService:
    def __init__(self):
        self.db = Database()
        self.cache = Cache()
        self.email = EmailService()
        self.sms = SMSService()
        self.payment = PaymentService()
    
    def create_user(self, data):
        user = self.db.create_user(data)
        self.cache.set(user.id, user)
        self.email.send_welcome(user)
        self.sms.send_verification(user)
        self.payment.create_account(user)
        return user
"""

SAMPLE_CODE_SECURITY = """
@app.route('/api/user/<user_id>')
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id={user_id}"
    result = db.execute(query)
    return jsonify(result)
"""


def demo_code_quality_prompt():
    """Demonstrate code quality review prompt generation"""
    print("=" * 80)
    print("CODE QUALITY REVIEW PROMPT")
    print("=" * 80)
    
    manager = get_prompt_manager()
    
    prompt = manager.generate_code_quality_prompt(
        file_path="src/auth.py",
        language="python",
        code_diff=SAMPLE_CODE_QUALITY,
        context="Authentication module review - checking for security issues and code quality"
    )
    
    print("\n--- SYSTEM PROMPT ---")
    print(prompt["system_prompt"][:500] + "...\n")
    
    print("--- USER PROMPT ---")
    print(prompt["user_prompt"])
    print()


def demo_architecture_prompt():
    """Demonstrate architectural analysis prompt generation"""
    print("=" * 80)
    print("ARCHITECTURAL ANALYSIS PROMPT")
    print("=" * 80)
    
    manager = get_prompt_manager()
    
    prompt = manager.generate_architecture_prompt(
        file_path="src/services/user_service.py",
        language="python",
        code_diff=SAMPLE_CODE_ARCHITECTURE,
        dependencies="Database, Cache, EmailService, SMSService, PaymentService",
        context="Service layer review - checking for proper separation of concerns and dependency management"
    )
    
    print("\n--- SYSTEM PROMPT ---")
    print(prompt["system_prompt"][:500] + "...\n")
    
    print("--- USER PROMPT ---")
    print(prompt["user_prompt"])
    print()


def demo_security_prompt():
    """Demonstrate security vulnerability detection prompt generation"""
    print("=" * 80)
    print("SECURITY VULNERABILITY DETECTION PROMPT")
    print("=" * 80)
    
    manager = get_prompt_manager()
    
    prompt = manager.generate_security_prompt(
        file_path="src/api/user_api.py",
        language="python",
        code_diff=SAMPLE_CODE_SECURITY,
        context="API endpoint security review - checking for OWASP Top 10 vulnerabilities",
        exposure_level="public-facing"
    )
    
    print("\n--- SYSTEM PROMPT ---")
    print(prompt["system_prompt"][:500] + "...\n")
    
    print("--- USER PROMPT ---")
    print(prompt["user_prompt"])
    print()


def demo_prompt_by_type():
    """Demonstrate generating prompts by analysis type"""
    print("=" * 80)
    print("GENERATING PROMPTS BY TYPE")
    print("=" * 80)
    
    manager = get_prompt_manager()
    
    # Get available analysis types
    types = manager.get_available_analysis_types()
    print(f"\nAvailable analysis types: {types}\n")
    
    # Generate prompt for each type
    for analysis_type in [AnalysisType.CODE_QUALITY, AnalysisType.ARCHITECTURE, AnalysisType.SECURITY]:
        prompt = manager.generate_prompt(
            analysis_type=analysis_type,
            file_path="src/example.py",
            language="python",
            code_diff="def example(): pass",
            context=f"{analysis_type.value} analysis"
        )
        
        print(f"--- {analysis_type.value.upper()} ---")
        print(f"System prompt length: {len(prompt['system_prompt'])} chars")
        print(f"User prompt length: {len(prompt['user_prompt'])} chars")
        print()


async def demo_with_llm_orchestrator():
    """Demonstrate using prompts with LLM orchestrator"""
    print("=" * 80)
    print("USING PROMPTS WITH LLM ORCHESTRATOR")
    print("=" * 80)
    print("\nNOTE: This demo requires valid API keys to run.\n")
    
    try:
        # Create prompt manager and orchestrator
        manager = get_prompt_manager()
        orchestrator = create_orchestrator(
            primary_provider=LLMProviderType.OPENAI,
            fallback_provider=LLMProviderType.ANTHROPIC,
            timeout=30
        )
        
        # Generate security analysis prompt
        prompt = manager.generate_security_prompt(
            file_path="src/api.py",
            language="python",
            code_diff=SAMPLE_CODE_SECURITY,
            context="Security review of API endpoint",
            exposure_level="public-facing"
        )
        
        print("Generated security analysis prompt")
        print(f"System prompt: {len(prompt['system_prompt'])} chars")
        print(f"User prompt: {len(prompt['user_prompt'])} chars")
        
        # Create LLM request
        request = LLMRequest(
            prompt=prompt["user_prompt"],
            system_prompt=prompt["system_prompt"],
            temperature=0.3,
            max_tokens=2000
        )
        
        print("\nSending request to LLM orchestrator...")
        
        # Generate analysis (this will fail without valid API keys)
        response = await orchestrator.generate(request)
        
        print("\n--- LLM ANALYSIS RESPONSE ---")
        print(response.content)
        print(f"\nTokens used: {response.tokens['total']}")
        print(f"Cost: ${response.cost:.4f}")
        print(f"Provider: {response.provider}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nThis is expected if API keys are not configured.")
        print("To run this demo with actual LLM calls:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Set ANTHROPIC_API_KEY environment variable")
        print("3. Run this script again")


def demo_custom_prompt_template():
    """Demonstrate creating custom prompt templates"""
    print("=" * 80)
    print("CUSTOM PROMPT TEMPLATE")
    print("=" * 80)
    
    from app.services.llm.prompts import PromptTemplate
    
    # Create a custom template
    template = PromptTemplate(
        system_prompt="You are a performance optimization expert.",
        user_prompt_template="""Analyze the following code for performance issues:

File: {file_path}
Language: {language}

Code:
```{language}
{code}
```

Focus on:
- Time complexity
- Space complexity
- Database query optimization
- Caching opportunities

Provide specific optimization recommendations.""",
        analysis_type=AnalysisType.CODE_QUALITY
    )
    
    # Format the template
    prompt = template.format(
        file_path="src/data_processor.py",
        language="python",
        code="""
def process_data(items):
    results = []
    for item in items:
        if item.is_valid():
            processed = expensive_operation(item)
            results.append(processed)
    return results
"""
    )
    
    print("\n--- CUSTOM SYSTEM PROMPT ---")
    print(prompt["system_prompt"])
    
    print("\n--- CUSTOM USER PROMPT ---")
    print(prompt["user_prompt"])
    print()


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PROMPT MANAGER DEMONSTRATION" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Run synchronous demos
    demo_code_quality_prompt()
    demo_architecture_prompt()
    demo_security_prompt()
    demo_prompt_by_type()
    demo_custom_prompt_template()
    
    # Run async demo
    print("\n--- ASYNC DEMO ---")
    asyncio.run(demo_with_llm_orchestrator())
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("1. Use get_prompt_manager() to get a prompt manager instance")
    print("2. Generate prompts using convenience methods or generate_prompt()")
    print("3. Prompts include both system and user prompts")
    print("4. All prompts support variable substitution")
    print("5. Integrate with LLM orchestrator for actual analysis")
    print()


if __name__ == "__main__":
    main()
