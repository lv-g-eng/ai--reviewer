"""
Property-based tests for standards compliance mapping

Tests Property 1: Standards Compliance Mapping
For any code violation or finding detected by the platform, it SHALL be mapped 
to at least one valid ISO/IEC 25010 quality characteristic or ISO/IEC 23396 
engineering practice, ensuring all findings are traceable to recognized standards.

Validates Requirements: 1.3, 1.4, 8.2, 8.3
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from app.services.standards_classifier import StandardsClassifier


# Strategy for generating finding categories
@st.composite
def finding_category_strategy(draw):
    """Generate valid finding categories"""
    return draw(st.sampled_from([
        "security",
        "performance",
        "reliability",
        "maintainability",
        "usability",
        "compatibility",
        "portability",
        "functionality",
        "code_quality",
        "style",
        "testing",
        "architecture",
        "design",
        "documentation",
    ]))


# Strategy for generating finding messages
@st.composite
def finding_message_strategy(draw):
    """Generate realistic finding messages with keywords"""
    keywords = [
        "SQL injection vulnerability detected",
        "Missing authentication check",
        "Weak password policy",
        "Slow database query",
        "High memory usage",
        "Missing error handling",
        "Exception not caught",
        "High complexity detected",
        "Duplicate code found",
        "Poor naming convention",
        "Missing documentation",
        "Hardcoded encryption key",
        "Outdated dependency",
        "Missing audit logging",
        "XSS vulnerability",
        "CSRF token missing",
        "Access control bypass",
        "Insecure deserialization",
        "SSRF vulnerability",
        "Default configuration",
        "Circular dependency",
        "Missing unit tests",
        "Poor cohesion",
        "Tight coupling",
    ]
    return draw(st.sampled_from(keywords))


# Strategy for generating severity levels
@st.composite
def severity_strategy(draw):
    """Generate valid severity levels"""
    return draw(st.sampled_from([
        "critical",
        "high",
        "medium",
        "low",
        "info",
    ]))


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(1, "Standards Compliance Mapping")
@settings(
    max_examples=20,  # Using 15-20 examples as specified
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    category=finding_category_strategy(),
    message=finding_message_strategy(),
    severity=severity_strategy(),
)
def test_property_standards_compliance_mapping(category, message, severity):
    """
    Property 1: Standards Compliance Mapping
    
    For any code violation or finding detected by the platform, it SHALL be
    mapped to at least one valid ISO/IEC 25010 quality characteristic or
    ISO/IEC 23396 engineering practice, ensuring all findings are traceable
    to recognized standards.
    
    **Validates: Requirements 1.3, 1.4, 8.2, 8.3**
    """
    classifier = StandardsClassifier()
    
    # Classify the finding
    finding = classifier.classify_finding(
        category=category,
        message=message,
        severity=severity,
        file_path="test/file.py",
        line_number=42
    )
    
    # PROPERTY: Every finding MUST be mapped to at least one standard
    assert finding.iso_25010_characteristic is not None or \
           finding.iso_23396_practice is not None, \
           f"Finding must be mapped to at least one standard (ISO 25010 or ISO 23396). " \
           f"Category: {category}, Message: {message}"
    
    # PROPERTY: ISO/IEC 25010 characteristic must be valid if present
    if finding.iso_25010_characteristic:
        valid_characteristics = [
            "security",
            "performance_efficiency",
            "reliability",
            "maintainability",
            "usability",
            "compatibility",
            "portability",
            "functional_suitability",
        ]
        assert finding.iso_25010_characteristic in valid_characteristics, \
            f"ISO 25010 characteristic must be valid. Got: {finding.iso_25010_characteristic}"
    
    # PROPERTY: ISO/IEC 23396 practice must be valid if present
    if finding.iso_23396_practice:
        valid_practices = [
            "SE-1",  # Requirements Engineering
            "SE-2",  # Software Design
            "SE-3",  # Code Quality
            "SE-4",  # Testing Practices
            "SE-5",  # Configuration Management
            "SE-6",  # Security Engineering
        ]
        assert finding.iso_23396_practice in valid_practices, \
            f"ISO 23396 practice must be valid. Got: {finding.iso_23396_practice}"
    
    # PROPERTY: Security findings should have OWASP reference when applicable
    if category.lower() == "security":
        # Security findings should have ISO 25010 security characteristic
        assert finding.iso_25010_characteristic == "security", \
            "Security findings must map to ISO 25010 security characteristic"
        
        # Security findings should have ISO 23396 SE-6 practice
        assert finding.iso_23396_practice == "SE-6", \
            "Security findings must map to ISO 23396 SE-6 (Security Engineering)"
        
        # Many security findings should have OWASP references
        # (not all, but common ones should)
        security_keywords = [
            "injection", "authentication", "encryption", "access control",
            "xss", "csrf", "deserialization", "ssrf", "logging", "dependency"
        ]
        if any(keyword in message.lower() for keyword in security_keywords):
            assert finding.owasp_reference is not None, \
                f"Security finding with common vulnerability keyword should have OWASP reference. " \
                f"Message: {message}"
            
            # OWASP reference should be in valid format
            assert finding.owasp_reference.startswith("A"), \
                "OWASP reference should start with 'A'"
            assert "2021" in finding.owasp_reference, \
                "OWASP reference should include year"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(1, "Standards Compliance Mapping")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    num_findings=st.integers(min_value=1, max_value=10),
)
def test_property_batch_classification_completeness(num_findings):
    """
    Property 1 (batch): All findings in batch should be mapped to standards
    
    **Validates: Requirements 1.3, 1.4, 8.2, 8.3**
    """
    classifier = StandardsClassifier()
    
    # Generate batch of findings
    findings = []
    for i in range(num_findings):
        findings.append({
            "category": ["security", "performance", "maintainability"][i % 3],
            "message": f"Test finding {i}",
            "severity": "medium",
            "file_path": f"test/file{i}.py",
            "line_number": i * 10,
        })
    
    # Classify batch
    classified = classifier.classify_findings_batch(findings)
    
    # PROPERTY: All findings should be classified
    assert len(classified) == num_findings, \
        f"Should classify all {num_findings} findings"
    
    # PROPERTY: Each finding should have at least one standard mapping
    for i, finding in enumerate(classified):
        assert finding.iso_25010_characteristic is not None or \
               finding.iso_23396_practice is not None, \
               f"Finding {i} must be mapped to at least one standard"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(1, "Standards Compliance Mapping")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    category=finding_category_strategy(),
    message=finding_message_strategy(),
)
def test_property_consistent_mapping(category, message):
    """
    Property 1 (consistency): Same finding should map to same standards
    
    **Validates: Requirements 1.3, 1.4, 8.2, 8.3**
    """
    classifier = StandardsClassifier()
    
    # Classify same finding multiple times
    finding1 = classifier.classify_finding(
        category=category,
        message=message,
        severity="medium"
    )
    
    finding2 = classifier.classify_finding(
        category=category,
        message=message,
        severity="medium"
    )
    
    # PROPERTY: Mappings should be consistent
    assert finding1.iso_25010_characteristic == finding2.iso_25010_characteristic, \
        "Same finding should map to same ISO 25010 characteristic"
    
    assert finding1.iso_25010_sub_characteristic == finding2.iso_25010_sub_characteristic, \
        "Same finding should map to same ISO 25010 sub-characteristic"
    
    assert finding1.iso_23396_practice == finding2.iso_23396_practice, \
        "Same finding should map to same ISO 23396 practice"
    
    assert finding1.owasp_reference == finding2.owasp_reference, \
        "Same finding should map to same OWASP reference"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(1, "Standards Compliance Mapping")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    num_findings=st.integers(min_value=5, max_value=20),
)
def test_property_standards_summary_accuracy(num_findings):
    """
    Property 1 (summary): Standards summary should accurately reflect findings
    
    **Validates: Requirements 1.3, 1.4, 8.2, 8.3**
    """
    classifier = StandardsClassifier()
    
    # Generate and classify findings
    categories = ["security", "performance", "maintainability", "reliability"]
    classified_findings = []
    
    for i in range(num_findings):
        finding = classifier.classify_finding(
            category=categories[i % len(categories)],
            message=f"Test finding {i}",
            severity="medium"
        )
        classified_findings.append(finding)
    
    # Get summary
    summary = classifier.get_standards_summary(classified_findings)
    
    # PROPERTY: Total findings should match
    assert summary["total_findings"] == num_findings, \
        f"Summary should report {num_findings} total findings"
    
    # PROPERTY: Distribution counts should sum correctly
    iso25010_total = sum(summary["iso_25010_distribution"].values())
    assert iso25010_total <= num_findings, \
        "ISO 25010 distribution count should not exceed total findings"
    
    iso23396_total = sum(summary["iso_23396_distribution"].values())
    assert iso23396_total <= num_findings, \
        "ISO 23396 distribution count should not exceed total findings"
    
    # PROPERTY: Unmapped findings should be minimal
    # (all findings should be mapped to at least one standard)
    assert summary["unmapped_findings"] == 0, \
        "All findings should be mapped to at least one standard"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(1, "Standards Compliance Mapping")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    category=st.sampled_from(["security", "performance", "maintainability"]),
    message=finding_message_strategy(),
)
def test_property_sub_characteristic_mapping(category, message):
    """
    Property 1 (detail): Findings should map to sub-characteristics when possible
    
    **Validates: Requirements 1.3, 1.4, 8.2, 8.3**
    """
    classifier = StandardsClassifier()
    
    finding = classifier.classify_finding(
        category=category,
        message=message,
        severity="medium"
    )
    
    # PROPERTY: If characteristic is mapped, try to map sub-characteristic
    if finding.iso_25010_characteristic:
        # Check if message contains keywords that should trigger sub-characteristic mapping
        keyword_mappings = {
            "security": ["authentication", "encryption", "injection", "xss", "audit"],
            "performance": ["slow", "memory", "cpu", "database", "cache"],
            "maintainability": ["complexity", "duplication", "coupling", "naming"],
        }
        
        if category in keyword_mappings:
            message_lower = message.lower()
            has_keyword = any(kw in message_lower for kw in keyword_mappings[category])
            
            if has_keyword:
                # If message has relevant keywords, sub-characteristic should be mapped
                assert finding.iso_25010_sub_characteristic is not None, \
                    f"Finding with keyword should have sub-characteristic. " \
                    f"Category: {category}, Message: {message}"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(1, "Standards Compliance Mapping")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    message=st.text(min_size=10, max_size=100),
)
def test_property_owasp_mapping_for_security(message):
    """
    Property 1 (OWASP): Security findings with OWASP keywords should map to OWASP
    
    **Validates: Requirements 1.3, 1.4, 8.2, 8.3**
    """
    classifier = StandardsClassifier()
    
    # Add OWASP-specific keywords to message
    owasp_keywords = [
        ("SQL injection", "A03:2021"),
        ("access control", "A01:2021"),
        ("encryption", "A02:2021"),
        ("authentication", "A07:2021"),
        ("logging", "A09:2021"),
        ("dependency", "A06:2021"),
    ]
    
    for keyword, expected_owasp in owasp_keywords:
        test_message = f"{message} {keyword} detected"
        
        finding = classifier.classify_finding(
            category="security",
            message=test_message,
            severity="high"
        )
        
        # PROPERTY: Security finding with OWASP keyword should have OWASP reference
        assert finding.owasp_reference is not None, \
            f"Security finding with '{keyword}' should have OWASP reference"
        
        # PROPERTY: OWASP reference should match expected category
        assert finding.owasp_reference == expected_owasp, \
            f"Finding with '{keyword}' should map to {expected_owasp}, got {finding.owasp_reference}"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(1, "Standards Compliance Mapping")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    category=finding_category_strategy(),
)
def test_property_non_security_no_owasp(category):
    """
    Property 1 (OWASP exclusion): Non-security findings should not have OWASP reference
    
    **Validates: Requirements 1.3, 1.4, 8.2, 8.3**
    """
    # Skip security category
    if category.lower() == "security":
        return
    
    classifier = StandardsClassifier()
    
    finding = classifier.classify_finding(
        category=category,
        message="Test finding without security implications",
        severity="medium"
    )
    
    # PROPERTY: Non-security findings should not have OWASP reference
    assert finding.owasp_reference is None, \
        f"Non-security finding (category: {category}) should not have OWASP reference"
