"""
Unit Tests for LLM Response Parser

Tests parsing of LLM responses into structured review comments.

Validates Requirements: 1.4
"""

import pytest
from app.services.llm.response_parser import (
    Severity,
    ReviewComment,
    ParseResult,
    ResponseParser,
    parse_llm_response
)


class TestSeverity:
    """Test Severity enum"""
    
    def test_severity_values(self):
        """Test severity enum values"""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"
    
    def test_from_string_exact_match(self):
        """Test parsing severity from exact string match"""
        assert Severity.from_string("critical") == Severity.CRITICAL
        assert Severity.from_string("high") == Severity.HIGH
        assert Severity.from_string("medium") == Severity.MEDIUM
        assert Severity.from_string("low") == Severity.LOW
        assert Severity.from_string("info") == Severity.INFO
    
    def test_from_string_case_insensitive(self):
        """Test parsing severity is case-insensitive"""
        assert Severity.from_string("CRITICAL") == Severity.CRITICAL
        assert Severity.from_string("High") == Severity.HIGH
        assert Severity.from_string("MeDiUm") == Severity.MEDIUM
    
    def test_from_string_with_whitespace(self):
        """Test parsing severity with whitespace"""
        assert Severity.from_string("  critical  ") == Severity.CRITICAL
        assert Severity.from_string("\thigh\n") == Severity.HIGH
    
    def test_from_string_unknown_defaults_to_medium(self):
        """Test unknown severity defaults to MEDIUM"""
        assert Severity.from_string("unknown") == Severity.MEDIUM
        assert Severity.from_string("invalid") == Severity.MEDIUM
        assert Severity.from_string("") == Severity.MEDIUM


class TestReviewComment:
    """Test ReviewComment dataclass"""
    
    def test_comment_creation(self):
        """Test creating a review comment"""
        comment = ReviewComment(
            severity=Severity.HIGH,
            file_path="src/auth.py",
            line_start=42,
            line_end=45,
            issue="SQL injection vulnerability",
            suggestion="Use parameterized queries",
            rationale="Prevents SQL injection attacks",
            category="security"
        )
        
        assert comment.severity == Severity.HIGH
        assert comment.file_path == "src/auth.py"
        assert comment.line_start == 42
        assert comment.line_end == 45
        assert comment.issue == "SQL injection vulnerability"
        assert comment.suggestion == "Use parameterized queries"
        assert comment.rationale == "Prevents SQL injection attacks"
        assert comment.category == "security"
    
    def test_comment_optional_fields(self):
        """Test comment with optional fields omitted"""
        comment = ReviewComment(
            severity=Severity.MEDIUM,
            file_path="test.py",
            issue="Code smell",
            suggestion="Refactor",
            rationale="Improves maintainability"
        )
        
        assert comment.line_start is None
        assert comment.line_end is None
        assert comment.category is None
        assert comment.raw_text is None
    
    def test_to_dict(self):
        """Test converting comment to dictionary"""
        comment = ReviewComment(
            severity=Severity.CRITICAL,
            file_path="api.py",
            line_start=10,
            issue="Security issue",
            suggestion="Fix it",
            rationale="Important"
        )
        
        result = comment.to_dict()
        
        assert result["severity"] == "critical"
        assert result["file_path"] == "api.py"
        assert result["line_start"] == 10
        assert result["issue"] == "Security issue"
        assert result["suggestion"] == "Fix it"
        assert result["rationale"] == "Important"
    
    def test_str_representation_with_single_line(self):
        """Test string representation with single line number"""
        comment = ReviewComment(
            severity=Severity.HIGH,
            file_path="test.py",
            line_start=42,
            issue="Issue here",
            suggestion="Fix this",
            rationale="Because reasons"
        )
        
        result = str(comment)
        
        assert "[HIGH]" in result
        assert "test.py:42" in result
        assert "Issue: Issue here" in result
        assert "Suggestion: Fix this" in result
        assert "Rationale: Because reasons" in result
    
    def test_str_representation_with_line_range(self):
        """Test string representation with line range"""
        comment = ReviewComment(
            severity=Severity.MEDIUM,
            file_path="test.py",
            line_start=10,
            line_end=20,
            issue="Issue",
            suggestion="Fix",
            rationale="Reason"
        )
        
        result = str(comment)
        
        assert "test.py:10-20" in result
    
    def test_str_representation_without_lines(self):
        """Test string representation without line numbers"""
        comment = ReviewComment(
            severity=Severity.LOW,
            file_path="test.py",
            issue="Issue",
            suggestion="Fix",
            rationale="Reason"
        )
        
        result = str(comment)
        
        assert "test.py\n" in result
        assert "test.py:" not in result


class TestParseResult:
    """Test ParseResult dataclass"""
    
    def test_parse_result_creation(self):
        """Test creating a parse result"""
        comments = [
            ReviewComment(
                severity=Severity.HIGH,
                file_path="test.py",
                issue="Issue",
                suggestion="Fix",
                rationale="Reason"
            )
        ]
        
        result = ParseResult(
            comments=comments,
            errors=["Error 1"],
            raw_response="Raw text",
            success=True
        )
        
        assert len(result.comments) == 1
        assert len(result.errors) == 1
        assert result.raw_response == "Raw text"
        assert result.success is True
    
    def test_to_dict(self):
        """Test converting parse result to dictionary"""
        comments = [
            ReviewComment(
                severity=Severity.MEDIUM,
                file_path="test.py",
                issue="Issue",
                suggestion="Fix",
                rationale="Reason"
            )
        ]
        
        result = ParseResult(
            comments=comments,
            errors=[],
            raw_response="Raw",
            success=True
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["comment_count"] == 1
        assert result_dict["error_count"] == 0
        assert result_dict["success"] is True
        assert len(result_dict["comments"]) == 1
        assert result_dict["comments"][0]["severity"] == "medium"


class TestResponseParser:
    """Test ResponseParser class"""
    
    def test_parser_initialization(self):
        """Test creating a parser"""
        parser = ResponseParser()
        assert parser.default_file_path == "unknown"
        
        parser = ResponseParser(default_file_path="test.py")
        assert parser.default_file_path == "test.py"
    
    def test_parse_empty_response(self):
        """Test parsing empty response"""
        parser = ResponseParser()
        result = parser.parse("")
        
        assert result.success is False
        assert len(result.comments) == 0
        assert len(result.errors) == 1
        assert "Empty response" in result.errors[0]
    
    def test_parse_well_formatted_response(self):
        """Test parsing well-formatted response"""
        response = """
Severity: high
Location: src/auth.py line 42
Issue: SQL injection vulnerability detected
Suggestion: Use parameterized queries instead of string concatenation
Rationale: Prevents SQL injection attacks which could compromise the database
"""
        
        parser = ResponseParser()
        result = parser.parse(response, "src/auth.py")
        
        assert result.success is True
        assert len(result.comments) == 1
        
        comment = result.comments[0]
        assert comment.severity == Severity.HIGH
        assert comment.file_path == "src/auth.py"
        assert comment.line_start == 42
        assert "SQL injection" in comment.issue
        assert "parameterized queries" in comment.suggestion
        assert "Prevents SQL injection" in comment.rationale
    
    def test_parse_multiple_findings(self):
        """Test parsing response with multiple findings"""
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
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) == 2
        
        assert result.comments[0].severity == Severity.CRITICAL
        assert "Hardcoded API key" in result.comments[0].issue
        
        assert result.comments[1].severity == Severity.MEDIUM
        assert "Missing error handling" in result.comments[1].issue
    
    def test_parse_with_line_range(self):
        """Test parsing location with line range"""
        response = """
Severity: high
Location: src/test.py lines 10-20
Issue: Complex function
Suggestion: Break into smaller functions
Rationale: Improves readability
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) == 1
        
        comment = result.comments[0]
        assert comment.line_start == 10
        assert comment.line_end == 20
    
    def test_parse_with_category(self):
        """Test parsing response with category"""
        response = """
Severity: critical
Category: Security
Location: src/auth.py line 15
Issue: Weak password hashing
Suggestion: Use bcrypt with cost factor 12
Rationale: Protects against brute force attacks
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) == 1
        assert result.comments[0].category == "Security"
    
    def test_parse_missing_optional_fields(self):
        """Test parsing with missing optional fields"""
        response = """
Severity: low
Issue: Variable naming could be improved
"""
        
        parser = ResponseParser()
        result = parser.parse(response, "test.py")
        
        assert result.success is True
        assert len(result.comments) == 1
        
        comment = result.comments[0]
        assert comment.severity == Severity.LOW
        assert comment.file_path == "test.py"
        assert "Variable naming" in comment.issue
        assert "No specific suggestion" in comment.suggestion
        assert "No rationale" in comment.rationale
    
    def test_parse_infers_severity_from_keywords(self):
        """Test parser infers severity from keywords"""
        response = """
Issue: This is a critical security vulnerability
Suggestion: Fix immediately
Rationale: Could lead to data breach
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert result.comments[0].severity == Severity.CRITICAL
    
    def test_parse_handles_malformed_response(self):
        """Test parser handles malformed response gracefully"""
        response = "This is just some random text without structure"
        
        parser = ResponseParser()
        result = parser.parse(response, "test.py")
        
        # Should still try to extract something
        assert result.success is True or len(result.errors) > 0
    
    def test_parse_markdown_format(self):
        """Test parsing markdown-formatted response"""
        response = """
## Finding 1

**Severity:** high
**Location:** src/api.py:42
**Issue:** Missing input validation
**Suggestion:** Add validation for user input
**Rationale:** Prevents injection attacks

## Finding 2

**Severity:** medium
**Location:** src/utils.py:10
**Issue:** Inefficient algorithm
**Suggestion:** Use more efficient data structure
**Rationale:** Improves performance
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) >= 1
    
    def test_parse_with_chinese_colon(self):
        """Test parsing with Chinese colon (：)"""
        response = """
Severity：high
Location：src/test.py line 10
Issue：Code issue here
Suggestion：Fix this way
Rationale：Because reasons
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) == 1
        assert result.comments[0].severity == Severity.HIGH
    
    def test_parse_filters_short_findings(self):
        """Test parser filters out very short findings"""
        response = """
1. x
2. Severity: high
   Issue: Real issue here
   Suggestion: Fix it
   Rationale: Important
3. y
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        # Should only parse the substantial finding
        assert len(result.comments) == 1
        assert "Real issue" in result.comments[0].issue
    
    def test_extract_location_cleans_formatting(self):
        """Test location extraction cleans up formatting"""
        parser = ResponseParser()
        
        # Test with backticks
        file_path, line_start, line_end = parser._extract_location(
            "Location: `src/test.py` line 10",
            "default.py"
        )
        assert file_path == "src/test.py"
        assert line_start == 10
        
        # Test with quotes
        file_path, line_start, line_end = parser._extract_location(
            'Location: "src/test.py" line 20',
            "default.py"
        )
        assert file_path == "src/test.py"
        assert line_start == 20
        
        # Test with trailing punctuation
        file_path, line_start, line_end = parser._extract_location(
            "Location: src/test.py:, line 30",
            "default.py"
        )
        assert file_path == "src/test.py"
        assert line_start == 30
    
    def test_extract_location_handles_na(self):
        """Test location extraction handles N/A values"""
        parser = ResponseParser()
        
        file_path, _, _ = parser._extract_location(
            "Location: N/A",
            "default.py"
        )
        assert file_path == "default.py"
        
        file_path, _, _ = parser._extract_location(
            "Location: none",
            "default.py"
        )
        assert file_path == "default.py"
    
    def test_extract_issue_multiline(self):
        """Test extracting multi-line issue"""
        parser = ResponseParser()
        
        text = """
Issue: This is a long issue description
that spans multiple lines
and should be combined
Suggestion: Fix it
"""
        
        issue = parser._extract_issue(text)
        assert issue is not None
        assert "long issue description" in issue
        assert "spans multiple lines" in issue
        assert "\n" not in issue  # Should be combined into single line


class TestConvenienceFunction:
    """Test convenience function"""
    
    def test_parse_llm_response(self):
        """Test parse_llm_response convenience function"""
        response = """
Severity: high
Location: test.py line 10
Issue: Test issue
Suggestion: Test suggestion
Rationale: Test rationale
"""
        
        result = parse_llm_response(response, "test.py")
        
        assert isinstance(result, ParseResult)
        assert result.success is True
        assert len(result.comments) == 1
        assert result.comments[0].file_path == "test.py"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_parse_none_response(self):
        """Test parsing None response"""
        parser = ResponseParser()
        result = parser.parse(None)
        
        assert result.success is False
        assert len(result.errors) > 0
    
    def test_parse_whitespace_only_response(self):
        """Test parsing whitespace-only response"""
        parser = ResponseParser()
        result = parser.parse("   \n\t  \n  ")
        
        assert result.success is False
        assert len(result.errors) > 0
    
    def test_parse_response_without_issue(self):
        """Test parsing response without issue field"""
        response = """
Severity: high
Location: test.py
Suggestion: Do something
Rationale: Because
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        # Should fail to create comment without issue
        assert len(result.comments) == 0 or result.comments[0].issue
    
    def test_parse_very_long_response(self):
        """Test parsing very long response"""
        # Create a response with many findings
        findings = []
        for i in range(50):
            findings.append(f"""
{i+1}. Severity: medium
Location: file{i}.py line {i*10}
Issue: Issue number {i}
Suggestion: Fix number {i}
Rationale: Reason number {i}
""")
        
        response = "\n".join(findings)
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) > 0
    
    def test_parse_unicode_content(self):
        """Test parsing response with unicode characters"""
        response = """
Severity: high
Location: src/测试.py line 10
Issue: 代码质量问题
Suggestion: 改进代码结构
Rationale: 提高可维护性
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) == 1
    
    def test_parse_with_code_blocks(self):
        """Test parsing response with code blocks"""
        response = """
Severity: high
Location: src/auth.py line 42
Issue: SQL injection vulnerability
Suggestion: Use parameterized queries like this:
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```
Rationale: Prevents SQL injection attacks
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) == 1
        assert "parameterized queries" in result.comments[0].suggestion


class TestRealWorldResponses:
    """Test with realistic LLM responses"""
    
    def test_parse_gpt4_style_response(self):
        """Test parsing GPT-4 style response"""
        response = """
Based on my analysis of the code changes, here are my findings:

1. Severity: [critical]
   Location: src/auth.py line 45-48
   Issue: The password is being compared using == operator which is vulnerable to timing attacks
   Suggestion: Use a constant-time comparison function like `secrets.compare_digest()` for password verification
   Rationale: Timing attacks can be used to determine valid passwords by measuring response times

2. Severity: [high]
   Location: src/api.py line 120
   Issue: User input is directly interpolated into SQL query
   Suggestion: Replace string formatting with parameterized queries using SQLAlchemy's text() with bound parameters
   Rationale: This prevents SQL injection attacks which could compromise the entire database

3. Severity: [medium]
   Location: src/utils.py line 67-75
   Issue: Function has cyclomatic complexity of 15, exceeding recommended threshold of 10
   Suggestion: Break down the function into smaller, more focused functions with single responsibilities
   Rationale: Lower complexity improves code maintainability and testability
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) == 3
        
        assert result.comments[0].severity == Severity.CRITICAL
        assert result.comments[1].severity == Severity.HIGH
        assert result.comments[2].severity == Severity.MEDIUM
        
        assert result.comments[0].line_start == 45
        assert result.comments[0].line_end == 48
    
    def test_parse_claude_style_response(self):
        """Test parsing Claude style response"""
        response = """
I've reviewed the code changes and identified the following concerns:

**Finding 1: Security Vulnerability**
- Severity: Critical
- Location: src/auth.py, lines 42-45
- Issue: Hardcoded secret key in source code
- Suggestion: Move the secret key to environment variables and use a secrets management system
- Rationale: Hardcoded secrets can be exposed in version control and compromise system security

**Finding 2: Code Quality**
- Severity: Medium  
- Location: src/service.py, line 89
- Issue: Missing error handling for database connection
- Suggestion: Wrap database operations in try-except blocks and implement proper error recovery
- Rationale: Unhandled exceptions can crash the application and provide poor user experience
"""
        
        parser = ResponseParser()
        result = parser.parse(response)
        
        assert result.success is True
        assert len(result.comments) >= 1
        
        # Check that we found at least one critical finding
        assert any(c.severity == Severity.CRITICAL for c in result.comments)
        # Check that we found issues (may be in issue or raw_text)
        assert any(
            "secret" in c.issue.lower() or 
            (c.raw_text and "secret" in c.raw_text.lower())
            for c in result.comments
        )
