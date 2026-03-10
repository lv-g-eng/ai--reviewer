"""
Property-based tests for security finding OWASP reference

Tests Property 3: Security Finding OWASP Reference
For any finding classified as a security risk, it SHALL include a reference 
to the relevant OWASP Top 10 vulnerability category when applicable.

Validates Requirements: 1.6
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from app.services.security_scanner import get_security_scanner


# Strategy for generating security code samples
@st.composite
def security_code_strategy(draw):
    """Generate code samples with security issues"""
    templates = [
        # SQL Injection (A03:2021)
        '''
def query_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchall()
''',
        # Hardcoded Secret (A02:2021)
        '''
def connect_api():
    api_key = "sk-1234567890abcdef"
    password = get_test_password("admin")
    return connect(api_key, password)
''',
        # Dangerous Function - eval (A03:2021)
        '''
def process_input(user_input):
    result = eval(user_input)
    return result
''',
        # Dangerous Function - exec (A03:2021)
        '''
def execute_code(code):
    exec(code)
''',
        # Command Injection (A03:2021)
        '''
import os
def run_command(cmd):
    os.system(cmd)
''',
        # Insecure Deserialization (A08:2021)
        '''
import pickle
def load_data(data):
    obj = pickle.loads(data)
    return obj
''',
        # Subprocess without shell=False (A03:2021)
        '''
import subprocess
def execute(cmd):
    subprocess.call(cmd, shell=True)
''',
    ]
    return draw(st.sampled_from(templates))


# Strategy for generating OWASP vulnerability IDs
@st.composite
def owasp_id_strategy(draw):
    """Generate valid OWASP Top 10 2021 IDs"""
    return draw(st.sampled_from([
        "A01:2021",  # Broken Access Control
        "A02:2021",  # Cryptographic Failures
        "A03:2021",  # Injection
        "A04:2021",  # Insecure Design
        "A05:2021",  # Security Misconfiguration
        "A06:2021",  # Vulnerable and Outdated Components
        "A07:2021",  # Identification and Authentication Failures
        "A08:2021",  # Software and Data Integrity Failures
        "A09:2021",  # Security Logging and Monitoring Failures
        "A10:2021",  # Server-Side Request Forgery (SSRF)
    ]))


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(3, "Security Finding OWASP Reference")
@settings(
    max_examples=20,  # Using 15-20 examples as specified
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=security_code_strategy(),
)
def test_property_security_finding_owasp_reference(code):
    """
    Property 3: Security Finding OWASP Reference
    
    For any finding classified as a security risk, it SHALL include a reference
    to the relevant OWASP Top 10 vulnerability category when applicable.
    
    **Validates: Requirements 1.6**
    """
    scanner = get_security_scanner()
    
    # Scan code for security issues
    result = scanner.scan_code(code, filename="test_security.py")
    
    # PROPERTY: Security findings should have OWASP references
    security_findings = [
        f for f in result.findings 
        if f.severity in ['critical', 'high']  # Focus on critical/high severity
    ]
    
    if security_findings:
        for finding in security_findings:
            # PROPERTY: Security finding MUST have OWASP reference when applicable
            # "Applicable" means it's a recognized security vulnerability type
            applicable_types = [
                'dangerous_function_call',
                'sql_injection_risk',
                'hardcoded_secret',
                'insecure_deserialization',
                'missing_authentication',
                'missing_authorization',
                'xss_risk',
                'csrf_risk',
                'ssrf_risk',
                'weak_crypto',
                'path_traversal',
                'outdated_dependency',
            ]
            
            if finding.issue_type in applicable_types:
                assert finding.owasp_reference is not None, \
                    f"Security finding of type '{finding.issue_type}' must have OWASP reference. " \
                    f"Description: {finding.description}"
                
                # PROPERTY: OWASP reference must be in valid format
                assert finding.owasp_reference.startswith("A"), \
                    f"OWASP reference must start with 'A', got: {finding.owasp_reference}"
                
                assert ":2021" in finding.owasp_reference, \
                    f"OWASP reference must include ':2021', got: {finding.owasp_reference}"
                
                # PROPERTY: OWASP reference must be one of the Top 10
                valid_owasp_ids = [
                    "A01:2021", "A02:2021", "A03:2021", "A04:2021", "A05:2021",
                    "A06:2021", "A07:2021", "A08:2021", "A09:2021", "A10:2021"
                ]
                assert finding.owasp_reference in valid_owasp_ids, \
                    f"OWASP reference must be valid Top 10 ID, got: {finding.owasp_reference}"
                
                # PROPERTY: If OWASP reference exists, OWASP name should also exist
                assert finding.owasp_name is not None, \
                    f"Finding with OWASP reference must have OWASP name"
                
                # PROPERTY: If OWASP reference exists, OWASP description should exist
                assert finding.owasp_description is not None, \
                    f"Finding with OWASP reference must have OWASP description"
                
                # PROPERTY: If OWASP reference exists, mitigations should be provided
                assert finding.owasp_mitigations is not None, \
                    f"Finding with OWASP reference must have mitigations"
                
                assert len(finding.owasp_mitigations) > 0, \
                    f"Finding with OWASP reference must have at least one mitigation"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(3, "Security Finding OWASP Reference")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    num_files=st.integers(min_value=1, max_value=5),
)
def test_property_multiple_files_owasp_reference(num_files):
    """
    Property 3 (batch): Security findings across multiple files should have OWASP references
    
    **Validates: Requirements 1.6**
    """
    scanner = get_security_scanner()
    
    # Create multiple files with security issues
    files = {}
    for i in range(num_files):
        files[f"file{i}.py"] = f'''
import os
from backend.tests.utils.secure_test_data import get_test_password, get_test_jwt_secret, get_test_api_key
def dangerous_function_{i}():
    # SQL injection
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    
    # Hardcoded secret
    api_key = "sk-secret{i}"
    
    # Dangerous eval
    result = eval("1+1")
    
    return result
'''
    
    # Scan all files
    result = scanner.scan_multiple_files(files)
    
    # PROPERTY: All security findings should have OWASP references
    security_findings = [
        f for f in result.findings 
        if f.severity in ['critical', 'high']
    ]
    
    if security_findings:
        findings_with_owasp = [
            f for f in security_findings 
            if f.owasp_reference is not None
        ]
        
        # At least some security findings should have OWASP references
        assert len(findings_with_owasp) > 0, \
            f"At least some security findings should have OWASP references"
        
        # Most applicable security findings should have OWASP references
        applicable_findings = [
            f for f in security_findings
            if f.issue_type in [
                'dangerous_function_call', 'sql_injection_risk', 
                'hardcoded_secret', 'insecure_deserialization'
            ]
        ]
        
        if applicable_findings:
            owasp_coverage_rate = len(findings_with_owasp) / len(applicable_findings)
            assert owasp_coverage_rate >= 0.5, \
                f"At least 50% of applicable security findings should have OWASP references. " \
                f"Got {owasp_coverage_rate:.1%}"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(3, "Security Finding OWASP Reference")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=security_code_strategy(),
)
def test_property_owasp_reference_consistency(code):
    """
    Property 3 (consistency): Same security issue should map to same OWASP reference
    
    **Validates: Requirements 1.6**
    """
    scanner = get_security_scanner()
    
    # Scan same code twice
    result1 = scanner.scan_code(code, filename="test1.py")
    result2 = scanner.scan_code(code, filename="test2.py")
    
    # PROPERTY: Same security issues should have same OWASP references
    if result1.findings and result2.findings:
        # Match findings by issue type and description
        for finding1 in result1.findings:
            matching_findings = [
                f for f in result2.findings
                if f.issue_type == finding1.issue_type
            ]
            
            if matching_findings:
                finding2 = matching_findings[0]
                
                # PROPERTY: OWASP reference should be consistent
                assert finding1.owasp_reference == finding2.owasp_reference, \
                    f"Same security issue should have same OWASP reference. " \
                    f"Issue type: {finding1.issue_type}, " \
                    f"Got: {finding1.owasp_reference} vs {finding2.owasp_reference}"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(3, "Security Finding OWASP Reference")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=security_code_strategy(),
)
def test_property_owasp_coverage_tracking(code):
    """
    Property 3 (coverage): OWASP coverage should accurately track affected categories
    
    **Validates: Requirements 1.6**
    """
    scanner = get_security_scanner()
    
    # Scan code
    result = scanner.scan_code(code, filename="test.py")
    
    # PROPERTY: OWASP coverage should match findings
    if result.owasp_coverage:
        # Count findings per OWASP category
        manual_coverage = {}
        for finding in result.findings:
            if finding.owasp_reference:
                owasp_id = finding.owasp_reference
                manual_coverage[owasp_id] = manual_coverage.get(owasp_id, 0) + 1
        
        # PROPERTY: Coverage should match manual count
        assert result.owasp_coverage == manual_coverage, \
            f"OWASP coverage should match actual findings. " \
            f"Expected: {manual_coverage}, Got: {result.owasp_coverage}"
        
        # PROPERTY: Coverage count should not exceed total findings
        total_coverage = sum(result.owasp_coverage.values())
        assert total_coverage <= result.total_issues, \
            f"OWASP coverage count should not exceed total issues"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(3, "Security Finding OWASP Reference")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=security_code_strategy(),
)
def test_property_owasp_summary_completeness(code):
    """
    Property 3 (summary): OWASP summary should provide complete information
    
    **Validates: Requirements 1.6**
    """
    scanner = get_security_scanner()
    
    # Scan code
    result = scanner.scan_code(code, filename="test.py")
    
    # Get OWASP summary
    summary = scanner.get_owasp_summary(result)
    
    # PROPERTY: Summary should include all required fields
    assert 'total_owasp_categories_affected' in summary, \
        "Summary must include total_owasp_categories_affected"
    
    assert 'owasp_details' in summary, \
        "Summary must include owasp_details"
    
    assert 'security_score' in summary, \
        "Summary must include security_score"
    
    # PROPERTY: Total categories should match coverage
    assert summary['total_owasp_categories_affected'] == len(result.owasp_coverage), \
        "Total OWASP categories should match coverage length"
    
    # PROPERTY: OWASP details should include complete information
    for owasp_id, details in summary['owasp_details'].items():
        assert 'rank' in details, \
            f"OWASP details for {owasp_id} must include rank"
        
        assert 'name' in details, \
            f"OWASP details for {owasp_id} must include name"
        
        assert 'description' in details, \
            f"OWASP details for {owasp_id} must include description"
        
        assert 'finding_count' in details, \
            f"OWASP details for {owasp_id} must include finding_count"
        
        assert 'mitigations' in details, \
            f"OWASP details for {owasp_id} must include mitigations"
        
        # PROPERTY: Rank should be between 1 and 10
        assert 1 <= details['rank'] <= 10, \
            f"OWASP rank should be between 1 and 10, got {details['rank']}"
        
        # PROPERTY: Finding count should match coverage
        assert details['finding_count'] == result.owasp_coverage[owasp_id], \
            f"Finding count in details should match coverage"
    
    # PROPERTY: Security score should be between 0 and 100
    assert 0 <= summary['security_score'] <= 100, \
        f"Security score should be between 0 and 100, got {summary['security_score']}"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(3, "Security Finding OWASP Reference")
def test_property_specific_vulnerability_mapping():
    """
    Property 3 (specific): Specific vulnerability types should map to correct OWASP categories
    
    **Validates: Requirements 1.6**
    """
    scanner = get_security_scanner()
    
    # Test specific vulnerability mappings
    test_cases = [
        # (code, expected_owasp_id, description)
        (
            'query = "SELECT * FROM users WHERE id = " + user_id\ncursor.execute(query)',
            "A03:2021",
            "SQL injection"
        ),
        (
            'api_key = "sk-1234567890abcdef"',
            "A02:2021",
            "Hardcoded secret"
        ),
        (
            'result = eval(user_input)',
            "A03:2021",
            "Dangerous eval"
        ),
        (
            'import pickle\nobj = pickle.loads(data)',
            "A08:2021",
            "Insecure deserialization"
        ),
    ]
    
    for code, expected_owasp, description in test_cases:
        result = scanner.scan_code(code, filename="test.py")
        
        # PROPERTY: Specific vulnerability should map to expected OWASP category
        if result.findings:
            security_findings = [
                f for f in result.findings
                if f.severity in ['critical', 'high']
            ]
            
            if security_findings:
                # At least one finding should have the expected OWASP reference
                owasp_refs = [f.owasp_reference for f in security_findings if f.owasp_reference]
                
                assert expected_owasp in owasp_refs, \
                    f"{description} should map to {expected_owasp}, got {owasp_refs}"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(3, "Security Finding OWASP Reference")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=security_code_strategy(),
)
def test_property_iso25010_security_mapping(code):
    """
    Property 3 (standards): Security findings should map to ISO 25010 Security characteristic
    
    **Validates: Requirements 1.6**
    """
    scanner = get_security_scanner()
    
    # Scan code
    result = scanner.scan_code(code, filename="test.py")
    
    # PROPERTY: Security findings should map to ISO 25010 Security
    security_findings = [
        f for f in result.findings
        if f.severity in ['critical', 'high']
    ]
    
    if security_findings:
        for finding in security_findings:
            # PROPERTY: Security finding should have ISO 25010 security characteristic
            assert finding.iso_25010_characteristic == "security", \
                f"Security finding should map to ISO 25010 'security' characteristic, " \
                f"got: {finding.iso_25010_characteristic}"
            
            # PROPERTY: Security finding should have ISO 23396 SE-6 practice
            assert finding.iso_23396_practice == "SE-6", \
                f"Security finding should map to ISO 23396 'SE-6' practice, " \
                f"got: {finding.iso_23396_practice}"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(3, "Security Finding OWASP Reference")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=security_code_strategy(),
)
def test_property_non_security_no_owasp(code):
    """
    Property 3 (exclusion): Non-security findings should not have OWASP references
    
    **Validates: Requirements 1.6**
    """
    scanner = get_security_scanner()
    
    # Scan code
    result = scanner.scan_code(code, filename="test.py")
    
    # PROPERTY: Non-security findings should not have OWASP references
    non_security_findings = [
        f for f in result.findings
        if f.issue_type in [
            'high_complexity', 'large_class', 'deep_nesting',
            'suspicious_function_name', 'syntax_error', 'analysis_error'
        ]
    ]
    
    for finding in non_security_findings:
        assert finding.owasp_reference is None, \
            f"Non-security finding (type: {finding.issue_type}) should not have OWASP reference"
