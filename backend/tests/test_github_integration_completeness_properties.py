"""
Property-based tests for GitHub integration completeness

Tests Property 2: GitHub Integration Completeness
For any completed code review, actionable comments SHALL be posted to the 
corresponding GitHub PR, ensuring developers receive feedback in their workflow.

Validates Requirements: 1.5
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from app.services.github_comment_generator import (
    GitHubCommentGenerator,
    CommentResult,
    CommentBatchResult,
)
from app.services.security_scanner import SecurityFinding
from app.services.standards_classifier import ClassifiedFinding


# Strategy for generating security findings
@st.composite
def security_finding_strategy(draw):
    """Generate valid security findings"""
    severities = ["critical", "high", "medium", "low", "info"]
    issue_types = [
        "sql_injection_risk",
        "hardcoded_secret",
        "dangerous_function_call",
        "insecure_deserialization",
        "missing_authentication",
        "xss_risk",
        "csrf_risk",
    ]
    
    file_path = draw(st.sampled_from([
        "app/main.py",
        "app/services/auth.py",
        "app/api/endpoints.py",
        "app/models/user.py",
        "tests/test_security.py",
    ]))
    
    line_number = draw(st.integers(min_value=1, max_value=500))
    
    return SecurityFinding(
        severity=draw(st.sampled_from(severities)),
        issue_type=draw(st.sampled_from(issue_types)),
        description=draw(st.text(min_size=20, max_size=200)),
        location=f"{file_path}:{line_number}",
        suggestion=draw(st.text(min_size=20, max_size=200)),
        code_snippet=draw(st.text(min_size=10, max_size=100)),
        confidence=draw(st.floats(min_value=0.5, max_value=1.0)),
        owasp_reference=draw(st.sampled_from([
            "A01:2021", "A02:2021", "A03:2021", "A07:2021", "A08:2021", None
        ])),
        owasp_name=draw(st.text(min_size=10, max_size=50)) if draw(st.booleans()) else None,
        owasp_description=draw(st.text(min_size=20, max_size=100)) if draw(st.booleans()) else None,
        owasp_mitigations=draw(st.lists(st.text(min_size=10, max_size=50), min_size=0, max_size=3)),
        iso_25010_characteristic=draw(st.sampled_from(["security", "reliability", "maintainability"])),
        iso_25010_sub_characteristic=draw(st.text(min_size=5, max_size=30)) if draw(st.booleans()) else None,
        iso_23396_practice=draw(st.sampled_from(["SE-6", "SE-3", "SE-4"])),
    )


# Strategy for generating classified findings
@st.composite
def classified_finding_strategy(draw):
    """Generate valid classified findings"""
    severities = ["critical", "high", "medium", "low", "info"]
    categories = ["security", "performance", "maintainability", "reliability"]
    
    file_path = draw(st.sampled_from([
        "app/main.py",
        "app/services/auth.py",
        "app/api/endpoints.py",
        "app/models/user.py",
        "tests/test_security.py",
    ]))
    
    line_number = draw(st.integers(min_value=1, max_value=500))
    
    return ClassifiedFinding(
        severity=draw(st.sampled_from(severities)),
        category=draw(st.sampled_from(categories)),
        message=draw(st.text(min_size=20, max_size=200)),
        file_path=file_path,
        line_number=line_number,
        suggested_fix=draw(st.text(min_size=20, max_size=200)) if draw(st.booleans()) else None,
        iso_25010_characteristic=draw(st.sampled_from(["security", "reliability", "maintainability"])),
        iso_25010_sub_characteristic=draw(st.text(min_size=5, max_size=30)) if draw(st.booleans()) else None,
        iso_23396_practice=draw(st.sampled_from(["SE-6", "SE-3", "SE-4"])),
        owasp_reference=draw(st.sampled_from(["A01:2021", "A02:2021", "A03:2021", None])),
        rule_id=draw(st.text(min_size=3, max_size=20)) if draw(st.booleans()) else None,
        rule_name=draw(st.text(min_size=5, max_size=50)) if draw(st.booleans()) else None,
    )


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(2, "GitHub Integration Completeness")
@settings(
    max_examples=15,  # Using 15 examples as specified
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    findings=st.lists(security_finding_strategy(), min_size=1, max_size=10),
)
@pytest.mark.asyncio
async def test_property_github_integration_completeness_security(findings):
    """
    Property 2: GitHub Integration Completeness
    
    For any completed code review, actionable comments SHALL be posted to the
    corresponding GitHub PR, ensuring developers receive feedback in their workflow.
    
    **Validates: Requirements 1.5**
    """
    # Create mock GitHub client
    mock_github_client = MagicMock()
    mock_github_client.post_review_comment = AsyncMock(
        return_value={"id": 12345, "body": "test", "path": "test.py", "line": 1, "created_at": "2024-01-01T00:00:00Z"}
    )
    
    # Create comment generator with mock client
    generator = GitHubCommentGenerator(
        github_client=mock_github_client,
        max_retries=1,
        batch_size=5,
        batch_delay=0.01  # Small delay for testing
    )
    
    # Post findings
    result = await generator.post_security_findings(
        repo_full_name="test/repo",
        pr_number=123,
        commit_sha="abc123",
        findings=findings
    )
    
    # PROPERTY: All findings should result in comment attempts
    assert result.total_comments == len(findings), \
        f"Should attempt to post {len(findings)} comments, got {result.total_comments}"
    
    # PROPERTY: For successful GitHub API, all comments should succeed
    # (In this test, we mock successful API responses)
    assert result.successful_comments == len(findings), \
        f"All {len(findings)} comments should succeed with working API, " \
        f"got {result.successful_comments} successful"
    
    # PROPERTY: Failed comments should be zero with working API
    assert result.failed_comments == 0, \
        f"Should have 0 failed comments with working API, got {result.failed_comments}"
    
    # PROPERTY: Results list should match total comments
    assert len(result.results) == len(findings), \
        f"Results list should have {len(findings)} entries, got {len(result.results)}"
    
    # PROPERTY: All results should be successful
    for i, comment_result in enumerate(result.results):
        assert comment_result.success, \
            f"Comment {i} should be successful"
        
        assert comment_result.comment_id is not None, \
            f"Successful comment {i} should have comment_id"
        
        assert comment_result.error is None, \
            f"Successful comment {i} should not have error"
    
    # PROPERTY: GitHub API should be called for each finding
    assert mock_github_client.post_review_comment.call_count == len(findings), \
        f"GitHub API should be called {len(findings)} times, " \
        f"got {mock_github_client.post_review_comment.call_count} calls"
    
    # PROPERTY: Each comment should have proper formatting
    for call in mock_github_client.post_review_comment.call_args_list:
        kwargs = call[1]
        
        # Check required parameters
        assert "repo_full_name" in kwargs, "Comment should have repo_full_name"
        assert "pr_number" in kwargs, "Comment should have pr_number"
        assert "body" in kwargs, "Comment should have body"
        assert "commit_id" in kwargs, "Comment should have commit_id"
        assert "path" in kwargs, "Comment should have path"
        assert "line" in kwargs, "Comment should have line"
        
        # Check body is not empty
        assert len(kwargs["body"]) > 0, "Comment body should not be empty"
        
        # Check body contains key information
        body = kwargs["body"]
        assert "Security Issue" in body or "Code Quality Issue" in body, \
            "Comment should indicate issue type"
        
        assert "Severity" in body, "Comment should include severity"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(2, "GitHub Integration Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    findings=st.lists(classified_finding_strategy(), min_size=1, max_size=10),
)
@pytest.mark.asyncio
async def test_property_github_integration_completeness_classified(findings):
    """
    Property 2: GitHub Integration Completeness (classified findings)
    
    For any completed code review with classified findings, actionable comments
    SHALL be posted to the corresponding GitHub PR.
    
    **Validates: Requirements 1.5**
    """
    # Create mock GitHub client
    mock_github_client = MagicMock()
    mock_github_client.post_review_comment = AsyncMock(
        return_value={"id": 12345, "body": "test", "path": "test.py", "line": 1, "created_at": "2024-01-01T00:00:00Z"}
    )
    
    # Create comment generator with mock client
    generator = GitHubCommentGenerator(
        github_client=mock_github_client,
        max_retries=1,
        batch_size=5,
        batch_delay=0.01
    )
    
    # Post findings
    result = await generator.post_classified_findings(
        repo_full_name="test/repo",
        pr_number=123,
        commit_sha="abc123",
        findings=findings
    )
    
    # PROPERTY: All findings should result in comment attempts
    assert result.total_comments == len(findings), \
        f"Should attempt to post {len(findings)} comments"
    
    # PROPERTY: All comments should succeed with working API
    assert result.successful_comments == len(findings), \
        f"All {len(findings)} comments should succeed"
    
    # PROPERTY: No failed comments with working API
    assert result.failed_comments == 0, \
        f"Should have 0 failed comments"
    
    # PROPERTY: GitHub API called for each finding
    assert mock_github_client.post_review_comment.call_count == len(findings), \
        f"GitHub API should be called {len(findings)} times"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(2, "GitHub Integration Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    num_findings=st.integers(min_value=1, max_value=20),
)
@pytest.mark.asyncio
async def test_property_comment_formatting_completeness(num_findings):
    """
    Property 2 (formatting): All comments should be properly formatted
    
    **Validates: Requirements 1.5**
    """
    # Create mock GitHub client
    mock_github_client = MagicMock()
    mock_github_client.post_review_comment = AsyncMock(
        return_value={"id": 12345, "body": "test", "path": "test.py", "line": 1, "created_at": "2024-01-01T00:00:00Z"}
    )
    
    generator = GitHubCommentGenerator(github_client=mock_github_client)
    
    # Generate findings
    findings = []
    for i in range(num_findings):
        findings.append(SecurityFinding(
            severity="high",
            issue_type="sql_injection_risk",
            description=f"SQL injection vulnerability {i}",
            location=f"app/file{i}.py:{(i+1)*10}",  # Fixed: Start from line 10, 20, 30...
            suggestion=f"Use parameterized queries {i}",
            code_snippet=f"query = 'SELECT * FROM users WHERE id = ' + user_id",
            confidence=0.9,
            owasp_reference="A03:2021",
            owasp_name="Injection",
            owasp_description="SQL injection vulnerability",
            owasp_mitigations=["Use parameterized queries", "Validate input"],
            iso_25010_characteristic="security",
            iso_25010_sub_characteristic="confidentiality",
            iso_23396_practice="SE-6",
        ))
    
    # Post findings
    result = await generator.post_security_findings(
        repo_full_name="test/repo",
        pr_number=123,
        commit_sha="abc123",
        findings=findings
    )
    
    # PROPERTY: All comments should be formatted
    assert mock_github_client.post_review_comment.call_count == num_findings
    
    # PROPERTY: Each comment should contain required sections
    for call in mock_github_client.post_review_comment.call_args_list:
        body = call[1]["body"]
        
        # Required sections
        assert "Security Issue" in body, "Comment should have Security Issue header"
        assert "Severity" in body, "Comment should have Severity section"
        assert "Description" in body, "Comment should have Description section"
        assert "Suggestion" in body or "💡" in body, "Comment should have Suggestion section"
        assert "OWASP Top 10 Reference" in body or "🛡️" in body, "Comment should have OWASP section"
        assert "Standards Classification" in body or "📋" in body, "Comment should have Standards section"
        assert "Generated by AI Code Review Platform" in body, "Comment should have footer"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(2, "GitHub Integration Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    num_findings=st.integers(min_value=1, max_value=10),
    num_failures=st.integers(min_value=0, max_value=5),
)
@pytest.mark.asyncio
async def test_property_partial_failure_handling(num_findings, num_failures):
    """
    Property 2 (resilience): System should handle partial failures gracefully
    
    **Validates: Requirements 1.5**
    """
    # Ensure failures don't exceed findings
    num_failures = min(num_failures, num_findings)
    
    # Create mock GitHub client with some failures
    call_count = 0
    
    async def mock_post_with_failures(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        # Fail the first num_failures calls
        if call_count <= num_failures:
            from github import GithubException
            raise GithubException(422, {"message": "Line not in diff"}, None)
        
        return {"id": call_count, "body": "test", "path": "test.py", "line": 1, "created_at": "2024-01-01T00:00:00Z"}
    
    mock_github_client = MagicMock()
    mock_github_client.post_review_comment = AsyncMock(side_effect=mock_post_with_failures)
    
    generator = GitHubCommentGenerator(
        github_client=mock_github_client,
        max_retries=1,
        batch_delay=0.01
    )
    
    # Generate findings
    findings = []
    for i in range(num_findings):
        findings.append(ClassifiedFinding(  # Fixed: Use ClassifiedFinding instead of SecurityFinding
            severity="medium",
            category="security",
            message=f"Hardcoded secret {i}",
            file_path=f"app/file{i}.py",
            line_number=(i+1)*10,  # Fixed: Start from line 10, 20, 30...
            suggested_fix=f"Use environment variables {i}",
            iso_25010_characteristic="security",
            iso_25010_sub_characteristic="confidentiality",
            iso_23396_practice="SE-6",
            owasp_reference="A02:2021",
            rule_id="hardcoded-secret",
            rule_name="Hardcoded Secret Detection",
        ))
    
    # Post findings
    result = await generator.post_classified_findings(
        repo_full_name="test/repo",
        pr_number=123,
        commit_sha="abc123",
        findings=findings
    )
    
    # PROPERTY: Total comments should match findings
    assert result.total_comments == num_findings
    
    # PROPERTY: Failed comments should match expected failures
    assert result.failed_comments == num_failures, \
        f"Should have {num_failures} failed comments, got {result.failed_comments}"
    
    # PROPERTY: Successful comments should be total minus failures
    expected_successful = num_findings - num_failures
    assert result.successful_comments == expected_successful, \
        f"Should have {expected_successful} successful comments, got {result.successful_comments}"
    
    # PROPERTY: Results should include both successes and failures
    successful_results = [r for r in result.results if r.success]
    failed_results = [r for r in result.results if not r.success]
    
    assert len(successful_results) == expected_successful
    assert len(failed_results) == num_failures


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(2, "GitHub Integration Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    findings=st.lists(security_finding_strategy(), min_size=1, max_size=5),
)
@pytest.mark.asyncio
async def test_property_comment_content_actionability(findings):
    """
    Property 2 (actionability): Comments should be actionable with clear guidance
    
    **Validates: Requirements 1.5**
    """
    # Create mock GitHub client
    mock_github_client = MagicMock()
    mock_github_client.post_review_comment = AsyncMock(
        return_value={"id": 12345, "body": "test", "path": "test.py", "line": 1, "created_at": "2024-01-01T00:00:00Z"}
    )
    
    generator = GitHubCommentGenerator(github_client=mock_github_client)
    
    # Post findings
    await generator.post_security_findings(
        repo_full_name="test/repo",
        pr_number=123,
        commit_sha="abc123",
        findings=findings
    )
    
    # PROPERTY: Each comment should be actionable
    for call in mock_github_client.post_review_comment.call_args_list:
        body = call[1]["body"]
        
        # Actionable comments should have:
        # 1. Clear description of the issue
        assert "Description" in body, "Comment should describe the issue"
        
        # 2. Severity indication
        assert any(sev in body.upper() for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]), \
            "Comment should indicate severity"
        
        # 3. Suggestion or mitigation
        has_suggestion = "Suggestion" in body or "💡" in body
        has_mitigation = "Mitigation" in body or "Recommended" in body
        assert has_suggestion or has_mitigation, \
            "Comment should provide suggestions or mitigations"
        
        # 4. Standards reference for context
        has_standards = "ISO/IEC 25010" in body or "ISO/IEC 23396" in body or "OWASP" in body
        assert has_standards, \
            "Comment should reference relevant standards"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(2, "GitHub Integration Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    num_findings=st.integers(min_value=1, max_value=15),
)
@pytest.mark.asyncio
async def test_property_batch_processing_completeness(num_findings):
    """
    Property 2 (batch): Batch processing should handle all findings
    
    **Validates: Requirements 1.5**
    """
    # Create mock GitHub client
    mock_github_client = MagicMock()
    mock_github_client.post_review_comment = AsyncMock(
        return_value={"id": 12345, "body": "test", "path": "test.py", "line": 1, "created_at": "2024-01-01T00:00:00Z"}
    )
    
    # Use small batch size to test batching
    generator = GitHubCommentGenerator(
        github_client=mock_github_client,
        batch_size=3,
        batch_delay=0.01
    )
    
    # Generate findings
    findings = []
    for i in range(num_findings):
        findings.append(SecurityFinding(
            severity="medium",
            issue_type="hardcoded_secret",
            description=f"Issue {i}",
            location=f"app/file{i}.py:{(i+1)*10}",  # Fixed: Start from line 10, 20, 30...
            suggestion=f"Fix {i}",
            code_snippet="code",
            confidence=0.8,
            owasp_reference="A02:2021",
            owasp_name="Cryptographic Failures",
            owasp_description="Description",
            owasp_mitigations=["Mitigation"],
            iso_25010_characteristic="security",
            iso_25010_sub_characteristic="confidentiality",
            iso_23396_practice="SE-6",
        ))
    
    # Post findings
    result = await generator.post_security_findings(
        repo_full_name="test/repo",
        pr_number=123,
        commit_sha="abc123",
        findings=findings
    )
    
    # PROPERTY: All findings should be processed regardless of batch size
    assert result.total_comments == num_findings, \
        f"Should process all {num_findings} findings"
    
    # PROPERTY: All should succeed with working API
    assert result.successful_comments == num_findings, \
        f"All {num_findings} should succeed"
    
    # PROPERTY: API should be called for each finding
    assert mock_github_client.post_review_comment.call_count == num_findings


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(2, "GitHub Integration Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    findings=st.lists(security_finding_strategy(), min_size=1, max_size=5),
)
@pytest.mark.asyncio
async def test_property_comment_location_accuracy(findings):
    """
    Property 2 (location): Comments should be posted to correct file locations
    
    **Validates: Requirements 1.5**
    """
    # Create mock GitHub client
    mock_github_client = MagicMock()
    mock_github_client.post_review_comment = AsyncMock(
        return_value={"id": 12345, "body": "test", "path": "test.py", "line": 1, "created_at": "2024-01-01T00:00:00Z"}
    )
    
    generator = GitHubCommentGenerator(github_client=mock_github_client)
    
    # Post findings
    await generator.post_security_findings(
        repo_full_name="test/repo",
        pr_number=123,
        commit_sha="abc123",
        findings=findings
    )
    
    # PROPERTY: Each comment should be posted to correct location
    for i, call in enumerate(mock_github_client.post_review_comment.call_args_list):
        kwargs = call[1]
        
        # Extract expected location from finding
        finding = findings[i]
        expected_path, expected_line = generator._parse_location(finding.location)
        
        # PROPERTY: Path should match finding location
        assert kwargs["path"] == expected_path, \
            f"Comment path should match finding location"
        
        # PROPERTY: Line should match finding location
        assert kwargs["line"] == expected_line, \
            f"Comment line should match finding location"
        
        # PROPERTY: Line number should be positive
        assert kwargs["line"] > 0, \
            f"Line number should be positive"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(2, "GitHub Integration Completeness")
def test_property_comment_format_consistency():
    """
    Property 2 (consistency): Comment formatting should be consistent
    
    **Validates: Requirements 1.5**
    """
    generator = GitHubCommentGenerator()
    
    # Create multiple findings
    findings = [
        SecurityFinding(
            severity="high",
            issue_type="sql_injection_risk",
            description="SQL injection detected",
            location="app/main.py:42",
            suggestion="Use parameterized queries",
            code_snippet="query = 'SELECT * FROM users'",
            confidence=0.9,
            owasp_reference="A03:2021",
            owasp_name="Injection",
            owasp_description="SQL injection",
            owasp_mitigations=["Use parameterized queries"],
            iso_25010_characteristic="security",
            iso_25010_sub_characteristic="confidentiality",
            iso_23396_practice="SE-6",
        ),
        SecurityFinding(
            severity="critical",
            issue_type="hardcoded_secret",
            description="Hardcoded API key",
            location="app/config.py:10",
            suggestion="Use environment variables",
            code_snippet="API_KEY = 'secret'",
            confidence=1.0,
            owasp_reference="A02:2021",
            owasp_name="Cryptographic Failures",
            owasp_description="Hardcoded credentials",
            owasp_mitigations=["Use environment variables"],
            iso_25010_characteristic="security",
            iso_25010_sub_characteristic="confidentiality",
            iso_23396_practice="SE-6",
        ),
    ]
    
    # Format comments
    comments = [generator.format_security_finding(f) for f in findings]
    
    # PROPERTY: All comments should have consistent structure
    for comment in comments:
        # Check for consistent sections
        assert "## " in comment, "Comment should have header"
        assert "**Severity:**" in comment, "Comment should have severity"
        assert "### Description" in comment, "Comment should have description"
        assert "### 💡 Suggestion" in comment or "Suggestion" in comment, "Comment should have suggestion"
        assert "### 🛡️ OWASP Top 10 Reference" in comment or "OWASP" in comment, "Comment should have OWASP"
        assert "### 📋 Standards Classification" in comment or "Standards" in comment, "Comment should have standards"
        assert "---" in comment, "Comment should have separator"
        assert "Generated by AI Code Review Platform" in comment, "Comment should have footer"
    
    # PROPERTY: Comments should use consistent emoji
    for comment in comments:
        # Severity emojis
        assert any(emoji in comment for emoji in ["🔴", "🟠", "🟡", "🔵", "ℹ️"]), \
            "Comment should use severity emoji"
        
        # Section emojis
        assert "💡" in comment, "Comment should use suggestion emoji"
        assert "🛡️" in comment, "Comment should use OWASP emoji"
        assert "📋" in comment, "Comment should use standards emoji"
