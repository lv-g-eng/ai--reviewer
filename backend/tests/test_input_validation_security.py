"""
Security Tests for Input Validation and Sanitization

Tests SQL injection prevention, XSS prevention, and input validation.

Requirements:
- 5.10: Implement security tests scanning for OWASP Top 10 vulnerabilities
- 2.10: Sanitize all user input to prevent SQL injection and XSS attacks
- 8.7: Validate and sanitize all user input to prevent injection attacks
"""
import pytest
from app.utils.validators import (
    sanitize_html,
    sanitize_string,
    validate_url,
    validate_github_url,
    validate_file_path,
    sanitize_sql_identifier,
)
from app.utils.xss_prevention import XSSProtection, sanitize_user_input
from app.database.sql_injection_prevention import (
    validate_sql_identifier,
    validate_order_by,
    validate_limit_offset,
    build_safe_where_clause,
    SafeQueryBuilder,
    SQLInjectionError,
)


class TestSQLInjectionPrevention:
    """
    Test SQL injection prevention mechanisms
    
    **Validates: Requirements 2.10, 8.7, 5.10**
    """
    
    def test_sql_identifier_validation_blocks_injection(self):
        """Test that SQL identifier validation blocks injection attempts"""
        # Valid identifiers should pass
        assert validate_sql_identifier("user_id") == "user_id"
        assert validate_sql_identifier("table_name") == "table_name"
        assert validate_sql_identifier("_private") == "_private"
        
        # Invalid identifiers should raise error
        with pytest.raises(SQLInjectionError):
            validate_sql_identifier("user_id; DROP TABLE users--")
        
        with pytest.raises(SQLInjectionError):
            validate_sql_identifier("user_id' OR '1'='1")
        
        with pytest.raises(SQLInjectionError):
            validate_sql_identifier("user_id--")
        
        with pytest.raises(SQLInjectionError):
            validate_sql_identifier("user_id/*comment*/")
    
    def test_sql_identifier_blocks_keywords(self):
        """Test that SQL keywords are blocked as identifiers"""
        sql_keywords = ['select', 'insert', 'update', 'delete', 'drop', 'union']
        
        for keyword in sql_keywords:
            with pytest.raises(SQLInjectionError):
                validate_sql_identifier(keyword)
    
    def test_order_by_validation_prevents_injection(self):
        """Test that ORDER BY validation prevents SQL injection"""
        allowed_columns = ['name', 'created_at', 'status']
        
        # Valid ORDER BY clauses
        assert validate_order_by("name ASC", allowed_columns) == "name ASC"
        assert validate_order_by("created_at DESC", allowed_columns) == "created_at DESC"
        
        # Invalid column names should raise error
        with pytest.raises(SQLInjectionError):
            validate_order_by("name; DROP TABLE users--", allowed_columns)
        
        with pytest.raises(SQLInjectionError):
            validate_order_by("malicious_column", allowed_columns)
        
        # Invalid direction should raise error
        with pytest.raises(SQLInjectionError):
            validate_order_by("name UNION SELECT", allowed_columns)
    
    def test_limit_offset_validation(self):
        """Test that LIMIT and OFFSET validation prevents injection"""
        # Valid values
        limit, offset = validate_limit_offset(10, 0)
        assert limit == 10
        assert offset == 0
        
        # Negative values should raise error
        with pytest.raises(SQLInjectionError):
            validate_limit_offset(-1, 0)
        
        with pytest.raises(SQLInjectionError):
            validate_limit_offset(10, -1)
        
        # Excessive limit should raise error
        with pytest.raises(SQLInjectionError):
            validate_limit_offset(100000, 0)
    
    def test_safe_where_clause_builder(self):
        """Test that WHERE clause builder uses parameterized queries"""
        allowed_columns = ['user_id', 'status', 'email']
        filters = {
            'user_id': 123,
            'status': 'active'
        }
        
        where_clause, params = build_safe_where_clause(filters, allowed_columns)
        
        # Should use parameterized queries
        assert ':user_id' in where_clause
        assert ':status' in where_clause
        assert params['user_id'] == 123
        assert params['status'] == 'active'
        
        # Should not contain raw values
        assert '123' not in where_clause
        assert 'active' not in where_clause
    
    def test_safe_where_clause_blocks_invalid_columns(self):
        """Test that WHERE clause builder blocks invalid columns"""
        allowed_columns = ['user_id', 'status']
        filters = {
            'user_id': 123,
            'malicious_column': 'value'
        }
        
        with pytest.raises(SQLInjectionError):
            build_safe_where_clause(filters, allowed_columns)
    
    def test_safe_query_builder_select(self):
        """Test that SafeQueryBuilder creates parameterized SELECT queries"""
        builder = SafeQueryBuilder('users', ['id', 'email', 'status'])
        
        query, params = builder.build_select(
            columns=['email', 'status'],
            filters={'status': 'active'},
            order_by='email ASC',
            limit=10,
            offset=0
        )
        
        # Should use parameterized queries
        assert ':status' in query
        assert params['status'] == 'active'
        
        # Should not contain SQL injection vectors
        assert 'DROP' not in query.upper()
        assert 'UNION' not in query.upper()
        assert '--' not in query
    
    def test_safe_query_builder_blocks_injection_in_columns(self):
        """Test that SafeQueryBuilder blocks injection in column names"""
        builder = SafeQueryBuilder('users', ['id', 'email'])
        
        with pytest.raises(SQLInjectionError):
            builder.build_select(columns=['id; DROP TABLE users--'])
    
    def test_parameterized_queries_prevent_string_injection(self):
        """Test that parameterized queries prevent string-based injection"""
        builder = SafeQueryBuilder('users', ['id', 'email', 'password'])
        
        # Attempt injection through filter value
        malicious_value = "' OR '1'='1"
        query, params = builder.build_select(
            filters={'email': malicious_value}
        )
        
        # Value should be parameterized, not interpolated
        assert malicious_value not in query
        assert ':email' in query
        assert params['email'] == malicious_value


class TestXSSPrevention:
    """
    Test XSS prevention mechanisms
    
    **Validates: Requirements 2.10, 8.7, 5.10**
    """
    
    def test_html_sanitization_removes_script_tags(self):
        """Test that HTML sanitization removes script tags"""
        malicious_html = '<p>Hello</p><script>alert("XSS")</script>'
        sanitized = sanitize_html(malicious_html)
        
        assert '<script>' not in sanitized
        assert 'alert' not in sanitized
        assert '<p>Hello</p>' in sanitized
    
    def test_html_sanitization_removes_event_handlers(self):
        """Test that HTML sanitization removes event handlers"""
        malicious_html = '<img src="x" onerror="alert(\'XSS\')">'
        sanitized = sanitize_html(malicious_html)
        
        assert 'onerror' not in sanitized
        assert 'alert' not in sanitized
    
    def test_html_sanitization_removes_javascript_urls(self):
        """Test that HTML sanitization removes javascript: URLs"""
        malicious_html = '<a href="javascript:alert(\'XSS\')">Click</a>'
        sanitized = sanitize_html(malicious_html)
        
        assert 'javascript:' not in sanitized.lower()
        assert 'alert' not in sanitized
    
    def test_html_sanitization_allows_safe_tags(self):
        """Test that HTML sanitization allows safe tags"""
        safe_html = '<p>Hello <strong>World</strong></p>'
        sanitized = sanitize_html(safe_html)
        
        assert '<p>' in sanitized
        assert '<strong>' in sanitized
        assert 'Hello' in sanitized
        assert 'World' in sanitized
    
    def test_string_sanitization_escapes_html_entities(self):
        """Test that string sanitization escapes HTML entities"""
        malicious_string = '<script>alert("XSS")</script>'
        sanitized = sanitize_string(malicious_string)
        
        assert '&lt;script&gt;' in sanitized
        assert '<script>' not in sanitized
    
    def test_xss_protection_escape_javascript(self):
        """Test JavaScript escaping"""
        xss = XSSProtection()
        
        malicious_string = '"; alert("XSS"); //'
        escaped = xss.escape_javascript(malicious_string)
        
        # Should escape quotes and special characters
        assert '"' not in escaped or '\\"' in escaped
        assert 'alert' in escaped  # Content preserved but escaped
    
    def test_xss_protection_validate_safe_url(self):
        """Test URL validation for XSS vectors"""
        xss = XSSProtection()
        
        # Safe URLs should pass
        assert xss.validate_safe_url('https://example.com')
        assert xss.validate_safe_url('http://example.com/path')
        assert xss.validate_safe_url('mailto:user@example.com')
        
        # Dangerous URLs should fail
        assert not xss.validate_safe_url('javascript:alert("XSS")')
        assert not xss.validate_safe_url('data:text/html,<script>alert("XSS")</script>')
        assert not xss.validate_safe_url('vbscript:msgbox("XSS")')
    
    def test_xss_protection_sanitize_markdown(self):
        """Test Markdown sanitization"""
        xss = XSSProtection()
        
        # Markdown should be preserved
        markdown = '# Heading\n\n**Bold** and *italic*'
        sanitized = xss.sanitize_markdown(markdown)
        
        assert '#' in sanitized
        assert '**' in sanitized
        assert '*' in sanitized
        
        # HTML should be escaped
        markdown_with_html = '# Heading\n\n<script>alert("XSS")</script>'
        sanitized = xss.sanitize_markdown(markdown_with_html)
        
        assert '<script>' not in sanitized
        assert '&lt;script&gt;' in sanitized
    
    def test_context_aware_sanitization(self):
        """Test context-aware sanitization"""
        malicious_input = '<script>alert("XSS")</script>'
        
        # HTML context
        html_sanitized = sanitize_user_input(malicious_input, context='html')
        assert '<script>' not in html_sanitized
        
        # Plain text context
        plain_sanitized = sanitize_user_input(malicious_input, context='plain')
        assert '&lt;script&gt;' in plain_sanitized
        
        # JavaScript context
        js_sanitized = sanitize_user_input(malicious_input, context='javascript')
        assert '\\' in js_sanitized or '&' in js_sanitized


class TestInputValidation:
    """
    Test input validation mechanisms
    
    **Validates: Requirements 2.9, 8.7, 5.10**
    """
    
    def test_url_validation_blocks_malicious_urls(self):
        """Test that URL validation blocks malicious URLs"""
        # Valid URLs should pass
        assert validate_url('https://example.com')
        assert validate_url('http://example.com/path')
        
        # Invalid URLs should fail
        assert not validate_url('javascript:alert("XSS")')
        assert not validate_url('data:text/html,<script>')
        assert not validate_url('file:///etc/passwd')
    
    def test_github_url_validation(self):
        """Test GitHub URL validation"""
        # Valid GitHub URLs
        is_valid, error = validate_github_url('https://github.com/owner/repo.git')
        assert is_valid
        
        is_valid, error = validate_github_url('git@github.com:owner/repo.git')
        assert is_valid
        
        # Invalid GitHub URLs
        is_valid, error = validate_github_url('https://evil.com/malicious')
        assert not is_valid
        
        is_valid, error = validate_github_url('javascript:alert("XSS")')
        assert not is_valid
    
    def test_file_path_validation_prevents_traversal(self):
        """Test that file path validation prevents directory traversal"""
        # Valid paths should pass
        is_valid, error = validate_file_path('src/main.py')
        assert is_valid
        
        is_valid, error = validate_file_path('docs/README.md')
        assert is_valid
        
        # Directory traversal should fail
        is_valid, error = validate_file_path('../../../etc/passwd')
        assert not is_valid
        
        is_valid, error = validate_file_path('src/../../../etc/passwd')
        assert not is_valid
        
        # Null bytes should fail
        is_valid, error = validate_file_path('file.txt\x00.jpg')
        assert not is_valid
    
    def test_filename_sanitization(self):
        """Test filename sanitization"""
        xss = XSSProtection()
        
        # Normal filename
        assert xss.sanitize_filename('document.pdf') == 'document.pdf'
        
        # Filename with path separators
        assert '/' not in xss.sanitize_filename('../../etc/passwd')
        assert '\\' not in xss.sanitize_filename('..\\..\\windows\\system32')
        
        # Filename with HTML
        sanitized = xss.sanitize_filename('<script>alert("XSS")</script>.txt')
        assert '<script>' not in sanitized
        
        # Filename with null bytes
        sanitized = xss.sanitize_filename('file\x00.txt')
        assert '\x00' not in sanitized


class TestMalformedInputRejection:
    """
    Test that malformed input is properly rejected
    
    **Validates: Requirements 2.9, 5.10**
    """
    
    def test_empty_sql_identifier_rejected(self):
        """Test that empty SQL identifiers are rejected"""
        with pytest.raises(SQLInjectionError):
            validate_sql_identifier("")
    
    def test_invalid_limit_offset_types_rejected(self):
        """Test that invalid LIMIT/OFFSET types are rejected"""
        with pytest.raises(SQLInjectionError):
            validate_limit_offset("10", 0)  # String instead of int
        
        with pytest.raises(SQLInjectionError):
            validate_limit_offset(10, "0")  # String instead of int
    
    def test_malformed_order_by_rejected(self):
        """Test that malformed ORDER BY clauses are rejected"""
        allowed_columns = ['name', 'created_at']
        
        # Too many parts
        with pytest.raises(SQLInjectionError):
            validate_order_by("name ASC LIMIT 10", allowed_columns)
        
        # Invalid direction
        with pytest.raises(SQLInjectionError):
            validate_order_by("name INVALID", allowed_columns)
    
    def test_oversized_input_rejected(self):
        """Test that oversized input is rejected"""
        # Very long string
        long_string = "A" * 100000
        sanitized = sanitize_string(long_string, max_length=1000)
        
        # Should be truncated
        assert len(sanitized) <= 1000


class TestOWASPTop10Coverage:
    """
    Test coverage for OWASP Top 10 vulnerabilities
    
    **Validates: Requirement 5.10**
    """
    
    def test_a03_injection_prevention(self):
        """Test A03:2021 - Injection prevention"""
        # SQL Injection
        with pytest.raises(SQLInjectionError):
            validate_sql_identifier("id' OR '1'='1")
        
        # XSS
        malicious = '<script>alert("XSS")</script>'
        sanitized = sanitize_html(malicious)
        assert '<script>' not in sanitized
    
    def test_a05_security_misconfiguration(self):
        """Test A05:2021 - Security Misconfiguration prevention"""
        # Ensure dangerous URL schemes are blocked
        xss = XSSProtection()
        assert not xss.validate_safe_url('javascript:alert(1)')
        assert not xss.validate_safe_url('data:text/html,<script>')
    
    def test_a07_identification_authentication_failures(self):
        """Test A07:2021 - Identification and Authentication Failures"""
        # Ensure SQL injection in auth queries is prevented
        builder = SafeQueryBuilder('users', ['id', 'email', 'password_hash'])
        
        # Attempt SQL injection in email field
        query, params = builder.build_select(
            filters={'email': "admin' OR '1'='1"}
        )
        
        # Should use parameterized query
        assert ':email' in query
        assert "admin' OR '1'='1" not in query


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
