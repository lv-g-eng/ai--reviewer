# LLM Response Parser

## Overview

The Response Parser module provides robust parsing of unstructured LLM text responses into structured `ReviewComment` objects. It handles various response formats from different LLM providers (GPT-4, Claude, etc.) and gracefully handles malformed or incomplete responses.

**Validates Requirements:** 1.4

## Features

- **Multi-Format Support**: Parses numbered lists, markdown headings, and structured field formats
- **Severity Extraction**: Identifies and normalizes severity levels (critical, high, medium, low, info)
- **Location Parsing**: Extracts file paths and line numbers (single lines or ranges)
- **Graceful Degradation**: Handles malformed responses without crashing
- **Flexible Patterns**: Supports various formatting styles (colons, bold text, bullet points)
- **Unicode Support**: Handles international characters and Chinese colons (：)
- **Error Reporting**: Provides detailed error messages for debugging

## Core Components

### Severity Enum

```python
class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
```

### ReviewComment

Structured representation of a code review comment:

```python
@dataclass
class ReviewComment:
    severity: Severity
    file_path: str
    issue: str
    suggestion: str
    rationale: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    category: Optional[str] = None
    raw_text: Optional[str] = None
```

### ParseResult

Result of parsing operation:

```python
@dataclass
class ParseResult:
    comments: List[ReviewComment]
    errors: List[str]
    raw_response: str
    success: bool
```

### ResponseParser

Main parser class with configurable default file path:

```python
class ResponseParser:
    def __init__(self, default_file_path: Optional[str] = None)
    def parse(self, response: str, file_path: Optional[str] = None) -> ParseResult
```

## Usage Examples

### Basic Usage

```python
from app.services.llm.response_parser import parse_llm_response

# Parse LLM response
response = """
Severity: high
Location: src/auth.py line 42
Issue: SQL injection vulnerability detected
Suggestion: Use parameterized queries
Rationale: Prevents SQL injection attacks
"""

result = parse_llm_response(response, "src/auth.py")

if result.success:
    for comment in result.comments:
        print(f"{comment.severity}: {comment.issue}")
        print(f"  Location: {comment.file_path}:{comment.line_start}")
        print(f"  Fix: {comment.suggestion}")
else:
    print(f"Parsing errors: {result.errors}")
```

### Using ResponseParser Class

```python
from app.services.llm.response_parser import ResponseParser

parser = ResponseParser(default_file_path="src/unknown.py")
result = parser.parse(llm_response, "src/auth.py")

# Access structured data
for comment in result.comments:
    comment_dict = comment.to_dict()
    # Store in database, send to API, etc.
```

### Handling Multiple Findings

```python
response = """
1. Severity: critical
   Location: src/api.py line 10
   Issue: Hardcoded API key
   Suggestion: Use environment variables
   Rationale: Prevents credential exposure

2. Severity: medium
   Location: src/utils.py line 25
   Issue: Missing error handling
   Suggestion: Add try-except block
   Rationale: Improves robustness
"""

result = parse_llm_response(response)

print(f"Found {len(result.comments)} issues")
for comment in result.comments:
    print(f"[{comment.severity.value.upper()}] {comment.file_path}:{comment.line_start}")
    print(f"  {comment.issue}")
```

## Supported Response Formats

### Format 1: Structured Fields

```
Severity: high
Location: src/auth.py line 42
Issue: SQL injection vulnerability
Suggestion: Use parameterized queries
Rationale: Prevents SQL injection attacks
```

### Format 2: Numbered List

```
1. Severity: critical
   Location: src/api.py line 10-15
   Issue: Security vulnerability
   Suggestion: Fix immediately
   Rationale: Critical security risk

2. Severity: medium
   Location: src/utils.py line 25
   Issue: Code smell
   Suggestion: Refactor
   Rationale: Improves maintainability
```

### Format 3: Markdown Headings

```
## Finding 1

**Severity:** high
**Location:** src/api.py:42
**Issue:** Missing input validation
**Suggestion:** Add validation
**Rationale:** Prevents injection attacks
```

### Format 4: Markdown Bold

```
**Finding 1: Security Vulnerability**
- Severity: Critical
- Location: src/auth.py, lines 42-45
- Issue: Hardcoded secret key
- Suggestion: Use environment variables
- Rationale: Prevents credential exposure
```

## Parsing Logic

### 1. Finding Splitting

The parser attempts to split responses into individual findings using:
- Numbered lists (1., 2., 3., etc.)
- Markdown headings (##, ###)
- Bold finding markers (**Finding 1:**, **Finding 2:**)
- Severity-based splitting

### 2. Field Extraction

For each finding, the parser extracts:

**Severity**: 
- Looks for "Severity:", "Level:", "Priority:" keywords
- Supports brackets: `[critical]`, `[high]`
- Infers from keywords if not explicit (e.g., "critical security vulnerability")
- Defaults to MEDIUM if unknown

**Location**:
- Extracts file path from "Location:", "File:", "Path:" keywords
- Parses line numbers: "line 42", "lines 10-20", "line 42-45"
- Cleans formatting (backticks, quotes, trailing punctuation)
- Handles N/A, none, unknown as missing values

**Issue**:
- Extracts from "Issue:", "Problem:", "Concern:" keywords
- Combines multi-line descriptions
- Falls back to first substantial sentence if no keyword found

**Suggestion**:
- Extracts from "Suggestion:", "Recommendation:", "Fix:", "Remediation:" keywords
- Defaults to "No specific suggestion provided" if missing

**Rationale**:
- Extracts from "Rationale:", "Reason:", "Why:", "Explanation:", "Impact:" keywords
- Defaults to "No rationale provided" if missing

**Category** (optional):
- Extracts from "Category:", "Type:", "Vulnerability Type:" keywords

### 3. Validation

- Requires at least an issue description
- Filters out very short findings (< 20 characters)
- Filters out introductory text without structured content

## Error Handling

The parser handles errors gracefully:

```python
result = parse_llm_response(malformed_response)

if not result.success:
    print(f"Parsing failed with {len(result.errors)} errors:")
    for error in result.errors:
        print(f"  - {error}")
    
    # Still may have partial results
    if result.comments:
        print(f"But found {len(result.comments)} valid comments")
```

Common error scenarios:
- Empty or whitespace-only responses
- Responses without any structured fields
- Malformed field formats
- Missing required fields (issue description)

## Integration with LLM Service

### Complete Workflow

```python
from app.services.llm import (
    create_orchestrator,
    LLMRequest,
    get_prompt_manager,
    parse_llm_response
)

# 1. Create orchestrator
orchestrator = create_orchestrator()

# 2. Generate prompt
prompt_manager = get_prompt_manager()
prompts = prompt_manager.generate_code_quality_prompt(
    file_path="src/auth.py",
    language="python",
    code_diff="def login(user, password): ..."
)

# 3. Call LLM
request = LLMRequest(
    prompt=prompts["user_prompt"],
    system_prompt=prompts["system_prompt"],
    temperature=0.3
)
llm_response = await orchestrator.generate(request)

# 4. Parse response
parse_result = parse_llm_response(llm_response.content, "src/auth.py")

# 5. Process comments
for comment in parse_result.comments:
    # Store in database
    # Post to GitHub PR
    # Send notifications
    pass
```

## Testing

Comprehensive test suite in `backend/tests/test_response_parser.py`:

```bash
# Run all response parser tests
pytest backend/tests/test_response_parser.py -v

# Run specific test class
pytest backend/tests/test_response_parser.py::TestResponseParser -v

# Run with coverage
pytest backend/tests/test_response_parser.py --cov=app.services.llm.response_parser
```

Test coverage includes:
- Severity parsing (exact match, case-insensitive, inference)
- Location extraction (file paths, line numbers, ranges)
- Multiple finding formats (numbered, markdown, structured)
- Edge cases (empty responses, malformed data, unicode)
- Real-world LLM responses (GPT-4, Claude styles)

## Performance Considerations

- **Regex Compilation**: Patterns are compiled once at class definition
- **Lazy Evaluation**: Only parses what's needed
- **Memory Efficient**: Streams through findings without loading all into memory
- **Fast Parsing**: Typical response (3-5 findings) parses in < 10ms

## Best Practices

1. **Always check success flag**:
   ```python
   result = parse_llm_response(response)
   if result.success:
       # Process comments
   else:
       # Handle errors
   ```

2. **Provide file path context**:
   ```python
   # Better: provides context for default file path
   result = parse_llm_response(response, file_path="src/auth.py")
   
   # Works but less informative
   result = parse_llm_response(response)
   ```

3. **Handle partial results**:
   ```python
   result = parse_llm_response(response)
   if result.comments:
       # Process what we got
       for comment in result.comments:
           process(comment)
   
   if result.errors:
       # Log errors for debugging
       logger.warning(f"Parsing errors: {result.errors}")
   ```

4. **Store raw response**:
   ```python
   # Keep raw response for debugging
   result = parse_llm_response(response)
   store_in_db(
       comments=result.comments,
       raw_response=result.raw_response,
       errors=result.errors
   )
   ```

## Limitations

1. **Bullet Point Format**: Markdown bullet points (- Item) are harder to parse than structured fields
2. **Nested Structures**: Doesn't handle deeply nested findings
3. **Code Blocks**: Code blocks in suggestions are preserved but not specially handled
4. **Language Detection**: Doesn't detect or validate programming language
5. **Confidence Scores**: Doesn't provide confidence scores for extracted fields

## Future Enhancements

Potential improvements (not currently implemented):

1. **JSON Mode**: Support for LLMs that can output structured JSON
2. **Confidence Scores**: Assign confidence to each extracted field
3. **Field Validation**: Validate file paths exist, line numbers are reasonable
4. **Custom Patterns**: Allow users to register custom extraction patterns
5. **Streaming Parser**: Parse responses as they stream from LLM
6. **Multi-Language**: Better support for non-English responses

## Related Documentation

- [LLM Client README](./README.md) - Multi-provider LLM client
- [Prompts README](./PROMPTS_README.md) - Code analysis prompts
- [Resilience Patterns](./RESILIENCE_PATTERNS.md) - Circuit breaker and failover

## Requirements Validation

This module validates **Requirement 1.4**:
- ✅ Parses LLM responses into structured review comments
- ✅ Extracts severity levels (critical, high, medium, low)
- ✅ Extracts line numbers and file locations
- ✅ Handles malformed responses gracefully
- ✅ Provides detailed error reporting
- ✅ Supports multiple response formats
