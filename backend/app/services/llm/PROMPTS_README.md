# Code Analysis Prompts

A comprehensive prompt library for LLM-based code analysis supporting code quality review, architectural analysis, and security vulnerability detection.

**Validates Requirements: 1.4**

## Overview

The prompt manager provides well-designed, structured prompts for different types of code analysis:

- **Code Quality Review**: Readability, maintainability, best practices
- **Architectural Analysis**: Design patterns, dependencies, structure
- **Security Vulnerability Detection**: OWASP Top 10, secure coding practices

All prompts are designed to produce consistent, actionable feedback that can be parsed and displayed to developers.

## Architecture

```
app/services/llm/
├── prompts.py           # Prompt manager and templates
├── PROMPTS_README.md    # This file
└── ...
```

## Quick Start

### Basic Usage

```python
from app.services.llm import get_prompt_manager, AnalysisType

# Get prompt manager
manager = get_prompt_manager()

# Generate code quality review prompt
prompt = manager.generate_code_quality_prompt(
    file_path="src/auth.py",
    language="python",
    code_diff="def login(user, password): ...",
    context="Authentication module review"
)

print(prompt["system_prompt"])  # System instructions for LLM
print(prompt["user_prompt"])    # User request with code
```

### Using with LLM Orchestrator

```python
from app.services.llm import (
    get_prompt_manager,
    create_orchestrator,
    LLMProviderType,
    LLMRequest
)

# Create prompt manager and orchestrator
manager = get_prompt_manager()
orchestrator = create_orchestrator(
    primary_provider=LLMProviderType.OPENAI,
    fallback_provider=LLMProviderType.ANTHROPIC
)

# Generate security analysis prompt
prompt = manager.generate_security_prompt(
    file_path="src/api.py",
    language="python",
    code_diff="query = f'SELECT * FROM users WHERE id={user_id}'",
    exposure_level="public-facing"
)

# Create LLM request
request = LLMRequest(
    prompt=prompt["user_prompt"],
    system_prompt=prompt["system_prompt"],
    temperature=0.3,
    max_tokens=2000
)

# Generate analysis
response = await orchestrator.generate(request)
print(response.content)
```

## Prompt Types

### 1. Code Quality Review

Analyzes code for readability, maintainability, and best practices.

**Focus Areas:**
- Code readability and clarity
- Language-specific best practices and idioms
- Maintainability and code organization
- Error handling and edge cases
- Code duplication and refactoring opportunities
- Naming conventions and documentation
- Performance considerations (critical issues only)

**Usage:**

```python
prompt = manager.generate_code_quality_prompt(
    file_path="src/service.py",
    language="python",
    code_diff="""
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] != None:
            result.append(data[i] * 2)
    return result
""",
    context="Data processing function review"
)
```

**Output Format:**

The LLM will provide structured findings with:
1. Severity: critical/high/medium/low
2. Location: File path and line number(s)
3. Issue: Clear description of the problem
4. Suggestion: Specific recommendation
5. Rationale: Why this matters

### 2. Architectural Analysis

Analyzes code from an architectural perspective, focusing on design patterns, dependencies, and structure.

**Focus Areas:**
- Design patterns and architectural principles (SOLID, DRY, KISS)
- Component coupling and cohesion
- Dependency management and circular dependencies
- Separation of concerns and layering
- API design and interface contracts
- Scalability and extensibility
- Architectural consistency
- Technical debt and refactoring opportunities

**Usage:**

```python
prompt = manager.generate_architecture_prompt(
    file_path="src/services/user_service.py",
    language="python",
    code_diff="""
class UserService:
    def __init__(self):
        self.db = Database()
        self.cache = Cache()
        self.email = EmailService()
        self.payment = PaymentService()
""",
    dependencies="Database, Cache, EmailService, PaymentService",
    context="Service layer architectural review"
)
```

**Output Format:**

The LLM will provide architectural findings with:
1. Severity: critical/high/medium/low
2. Location: Component/module/file affected
3. Issue: Architectural concern description
4. Impact: How this affects system architecture
5. Suggestion: Recommended improvement
6. Rationale: Why this architectural change matters

### 3. Security Vulnerability Detection

Analyzes code for security vulnerabilities, focusing on OWASP Top 10 and secure coding practices.

**Focus Areas:**

**OWASP Top 10:**
1. Injection flaws (SQL, NoSQL, Command, LDAP, XPath)
2. Broken authentication and session management
3. Sensitive data exposure
4. XML External Entities (XXE)
5. Broken access control
6. Security misconfiguration
7. Cross-Site Scripting (XSS)
8. Insecure deserialization
9. Using components with known vulnerabilities
10. Insufficient logging and monitoring

**Additional Security Concerns:**
- Input validation and sanitization
- Output encoding
- Cryptographic issues
- Race conditions
- Information disclosure
- CSRF vulnerabilities
- Security headers

**Usage:**

```python
prompt = manager.generate_security_prompt(
    file_path="src/api/user_api.py",
    language="python",
    code_diff="""
@app.route('/api/user/<user_id>')
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id={user_id}"
    result = db.execute(query)
    return jsonify(result)
""",
    context="API endpoint security review",
    exposure_level="public-facing"
)
```

**Exposure Levels:**
- `public-facing`: Accessible from the internet
- `internal`: Accessible within organization
- `private`: Restricted access

**Output Format:**

The LLM will provide security findings with:
1. Severity: critical/high/medium/low
2. Vulnerability Type: OWASP category or CWE identifier
3. Location: File path and line number(s)
4. Issue: Security vulnerability description
5. Attack Vector: How this could be exploited
6. Impact: Potential consequences
7. Remediation: Steps to fix the vulnerability
8. References: Links to OWASP/CWE documentation

## API Reference

### PromptManager

Main interface for generating code analysis prompts.

#### Methods

##### `generate_prompt(analysis_type, file_path, language, code_diff, **kwargs)`

Generate a prompt for any analysis type.

**Parameters:**
- `analysis_type` (AnalysisType): Type of analysis
- `file_path` (str): Path to the file being analyzed
- `language` (str): Programming language
- `code_diff` (str): Code changes to analyze
- `**kwargs`: Additional context variables

**Returns:** `Dict[str, str]` with 'system_prompt' and 'user_prompt'

**Example:**

```python
prompt = manager.generate_prompt(
    analysis_type=AnalysisType.CODE_QUALITY,
    file_path="src/auth.py",
    language="python",
    code_diff="def login(): pass",
    context="Authentication review"
)
```

##### `generate_code_quality_prompt(file_path, language, code_diff, context=None)`

Generate code quality review prompt.

**Parameters:**
- `file_path` (str): Path to the file
- `language` (str): Programming language
- `code_diff` (str): Code changes
- `context` (str, optional): Additional context

**Returns:** `Dict[str, str]` with 'system_prompt' and 'user_prompt'

##### `generate_architecture_prompt(file_path, language, code_diff, dependencies=None, context=None)`

Generate architectural analysis prompt.

**Parameters:**
- `file_path` (str): Path to the file
- `language` (str): Programming language
- `code_diff` (str): Code changes
- `dependencies` (str, optional): Dependencies information
- `context` (str, optional): Architectural context

**Returns:** `Dict[str, str]` with 'system_prompt' and 'user_prompt'

##### `generate_security_prompt(file_path, language, code_diff, context=None, exposure_level=None)`

Generate security vulnerability detection prompt.

**Parameters:**
- `file_path` (str): Path to the file
- `language` (str): Programming language
- `code_diff` (str): Code changes
- `context` (str, optional): Security context
- `exposure_level` (str, optional): Exposure level (public-facing, internal, private)

**Returns:** `Dict[str, str]` with 'system_prompt' and 'user_prompt'

##### `get_available_analysis_types()`

Get list of available analysis types.

**Returns:** `List[str]` of analysis type names

### AnalysisType

Enum defining types of code analysis.

**Values:**
- `CODE_QUALITY`: Code quality review
- `ARCHITECTURE`: Architectural analysis
- `SECURITY`: Security vulnerability detection

### PromptTemplate

Template for code analysis prompts with variable substitution.

**Attributes:**
- `system_prompt` (str): System instructions for LLM
- `user_prompt_template` (str): User prompt template with variables
- `analysis_type` (AnalysisType): Type of analysis

**Methods:**

##### `format(**kwargs)`

Format the template with provided variables.

**Parameters:**
- `**kwargs`: Variables to substitute

**Returns:** `Dict[str, str]` with 'system_prompt' and 'user_prompt'

**Raises:** `KeyError` if required variables are missing

**Example:**

```python
from app.services.llm.prompts import PromptTemplate, AnalysisType

template = PromptTemplate(
    system_prompt="You are a code reviewer.",
    user_prompt_template="Review this code: {code}",
    analysis_type=AnalysisType.CODE_QUALITY
)

prompt = template.format(code="def hello(): pass")
```

### CodeAnalysisPrompts

Low-level prompt library with class methods for generating prompts.

**Class Methods:**
- `get_code_quality_prompt(file_path, language, code_diff, context)`
- `get_architecture_prompt(file_path, language, code_diff, dependencies, context)`
- `get_security_prompt(file_path, language, code_diff, context, exposure_level)`
- `get_prompt_by_type(analysis_type, **kwargs)`

### Convenience Functions

##### `get_prompt_manager()`

Get a prompt manager instance.

**Returns:** `PromptManager`

**Example:**

```python
from app.services.llm import get_prompt_manager

manager = get_prompt_manager()
```

## Supported Languages

The prompts are language-agnostic and work with any programming language. Common languages include:

- Python
- JavaScript/TypeScript
- Java
- Go
- C/C++
- C#
- Ruby
- PHP
- Rust
- Swift
- Kotlin

## Best Practices

### 1. Provide Context

Always provide meaningful context to help the LLM understand the purpose of the code:

```python
# Good
prompt = manager.generate_code_quality_prompt(
    file_path="src/auth.py",
    language="python",
    code_diff="...",
    context="Authentication module - handles user login and session management"
)

# Less helpful
prompt = manager.generate_code_quality_prompt(
    file_path="src/auth.py",
    language="python",
    code_diff="..."
)
```

### 2. Use Appropriate Analysis Type

Choose the right analysis type for your needs:

- **Code Quality**: For general code review, refactoring, best practices
- **Architecture**: For design decisions, dependencies, structural changes
- **Security**: For security-sensitive code, authentication, data handling

### 3. Specify Exposure Level for Security

For security analysis, always specify the exposure level:

```python
# Public-facing API
prompt = manager.generate_security_prompt(
    file_path="src/api/public.py",
    language="python",
    code_diff="...",
    exposure_level="public-facing"
)

# Internal service
prompt = manager.generate_security_prompt(
    file_path="src/services/internal.py",
    language="python",
    code_diff="...",
    exposure_level="internal"
)
```

### 4. Include Dependencies for Architecture

For architectural analysis, include dependency information:

```python
prompt = manager.generate_architecture_prompt(
    file_path="src/service.py",
    language="python",
    code_diff="...",
    dependencies="Database, Cache, EmailService, PaymentService",
    context="Service layer with multiple dependencies"
)
```

### 5. Use Appropriate Temperature

When using prompts with LLM orchestrator:

```python
# For deterministic analysis (recommended)
request = LLMRequest(
    prompt=prompt["user_prompt"],
    system_prompt=prompt["system_prompt"],
    temperature=0.3,  # Low temperature for consistent analysis
    max_tokens=2000
)

# For creative suggestions (use sparingly)
request = LLMRequest(
    prompt=prompt["user_prompt"],
    system_prompt=prompt["system_prompt"],
    temperature=0.7,  # Higher temperature for varied suggestions
    max_tokens=2000
)
```

## Integration Examples

### With GitHub Webhook Handler

```python
from app.services.llm import get_prompt_manager, create_orchestrator, LLMRequest

async def analyze_pull_request(pr_files):
    manager = get_prompt_manager()
    orchestrator = create_orchestrator()
    
    results = []
    
    for file in pr_files:
        # Generate security prompt for each file
        prompt = manager.generate_security_prompt(
            file_path=file.path,
            language=file.language,
            code_diff=file.diff,
            exposure_level="public-facing"
        )
        
        # Analyze with LLM
        request = LLMRequest(
            prompt=prompt["user_prompt"],
            system_prompt=prompt["system_prompt"],
            temperature=0.3
        )
        
        response = await orchestrator.generate(request)
        results.append({
            "file": file.path,
            "analysis": response.content
        })
    
    return results
```

### With Celery Task Queue

```python
from celery import shared_task
from app.services.llm import get_prompt_manager, create_orchestrator, LLMRequest

@shared_task
async def analyze_code_quality(file_path, language, code_diff):
    manager = get_prompt_manager()
    orchestrator = create_orchestrator()
    
    # Generate code quality prompt
    prompt = manager.generate_code_quality_prompt(
        file_path=file_path,
        language=language,
        code_diff=code_diff,
        context="Automated code quality review"
    )
    
    # Analyze with LLM
    request = LLMRequest(
        prompt=prompt["user_prompt"],
        system_prompt=prompt["system_prompt"],
        temperature=0.3
    )
    
    response = await orchestrator.generate(request)
    
    return {
        "file": file_path,
        "analysis": response.content,
        "tokens": response.tokens["total"],
        "cost": response.cost
    }
```

## Testing

Comprehensive unit tests are provided in `backend/tests/test_prompts.py`:

```bash
# Run all prompt tests
pytest backend/tests/test_prompts.py -v

# Run specific test class
pytest backend/tests/test_prompts.py::TestPromptManager -v

# Run with coverage
pytest backend/tests/test_prompts.py --cov=app.services.llm.prompts
```

**Test Coverage:**
- PromptTemplate class (3 tests)
- CodeAnalysisPrompts class (11 tests)
- PromptManager class (15 tests)
- Convenience functions (1 test)
- Prompt content quality (3 tests)
- Variable substitution (3 tests)
- AnalysisType enum (2 tests)

## Demo

Run the demo to see all features in action:

```bash
cd backend
python examples/prompt_manager_demo.py
```

The demo shows:
1. Code quality review prompt generation
2. Architectural analysis prompt generation
3. Security vulnerability detection prompt generation
4. Generating prompts by type
5. Using prompts with LLM orchestrator (requires API keys)
6. Creating custom prompt templates

## Customization

### Creating Custom Prompts

You can create custom prompt templates for specialized analysis:

```python
from app.services.llm.prompts import PromptTemplate, AnalysisType

# Create custom performance analysis template
performance_template = PromptTemplate(
    system_prompt="""You are a performance optimization expert.
    
Focus on:
- Time complexity (Big O notation)
- Space complexity
- Database query optimization
- Caching opportunities
- Algorithmic improvements""",
    
    user_prompt_template="""Analyze this code for performance:

File: {file_path}
Language: {language}

Code:
```{language}
{code}
```

Provide specific optimization recommendations.""",
    
    analysis_type=AnalysisType.CODE_QUALITY
)

# Use the custom template
prompt = performance_template.format(
    file_path="src/processor.py",
    language="python",
    code="def process(items): ..."
)
```

### Extending PromptManager

You can extend the PromptManager class to add custom analysis types:

```python
from app.services.llm.prompts import PromptManager

class CustomPromptManager(PromptManager):
    def generate_performance_prompt(self, file_path, language, code_diff):
        # Custom performance analysis prompt
        template = PromptTemplate(...)
        return template.format(
            file_path=file_path,
            language=language,
            code_diff=code_diff
        )
```

## Requirements Validation

This implementation validates the following requirements:

- **Requirement 1.4**: LLM Service SHALL analyze code changes and generate review comments
  - Provides structured prompts for code quality, architecture, and security analysis
  - Designed to produce consistent, actionable feedback
  - Integrates with LLM orchestrator for actual analysis

## Future Enhancements

Potential improvements for future versions:

1. **Multi-Language Prompts**: Localized prompts in different languages
2. **Custom Analysis Types**: Support for domain-specific analysis (e.g., accessibility, performance)
3. **Prompt Versioning**: Track and manage different versions of prompts
4. **Prompt A/B Testing**: Compare effectiveness of different prompt variations
5. **Response Parsing**: Structured parsing of LLM responses into standardized format
6. **Prompt Optimization**: Automatic optimization based on feedback
7. **Context-Aware Prompts**: Adapt prompts based on codebase context

## License

Part of the AI-Based Reviewer on Project Code and Architecture project.
