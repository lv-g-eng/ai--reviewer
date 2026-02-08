"""
Unit tests for Standards Classifier Service

Tests the classification logic for ISO/IEC 25010, ISO/IEC 23396, and OWASP Top 10.
"""
import pytest
from app.services.standards_classifier import StandardsClassifier, ClassifiedFinding, get_standards_classifier


class TestStandardsClassifier:
    """Test suite for StandardsClassifier"""
    
    @pytest.fixture
    def classifier(self):
        """Create a StandardsClassifier instance"""
        return StandardsClassifier()
    
    def test_classify_security_finding_with_owasp(self, classifier):
        """Test classification of security finding with OWASP mapping"""
        finding = classifier.classify_finding(
            category="security",
            message="SQL injection vulnerability detected in user input handling",
            severity="critical",
            file_path="app/api/users.py",
            line_number=42
        )
        
        assert finding.iso_25010_characteristic == "security"
        assert finding.iso_25010_sub_characteristic == "Integrity"
        assert finding.iso_23396_practice == "SE-6"
        assert finding.owasp_reference == "A03:2021"  # Injection
    
    def test_classify_performance_finding(self, classifier):
        """Test classification of performance finding"""
        finding = classifier.classify_finding(
            category="performance",
            message="Slow database query detected, consider adding index",
            severity="medium",
            file_path="app/models/user.py",
            line_number=100
        )
        
        assert finding.iso_25010_characteristic == "performance_efficiency"
        assert finding.iso_25010_sub_characteristic == "Time Behaviour"
        assert finding.iso_23396_practice == "SE-3"
        assert finding.owasp_reference is None  # Not a security issue
    
    def test_classify_maintainability_finding(self, classifier):
        """Test classification of maintainability finding"""
        finding = classifier.classify_finding(
            category="maintainability",
            message="High complexity detected, consider refactoring",
            severity="medium",
            file_path="app/services/processor.py",
            line_number=250
        )
        
        assert finding.iso_25010_characteristic == "maintainability"
        assert finding.iso_25010_sub_characteristic == "Analyzability"
        assert finding.iso_23396_practice == "SE-3"
        assert finding.owasp_reference is None
    
    def test_classify_authentication_security_finding(self, classifier):
        """Test classification of authentication security finding"""
        finding = classifier.classify_finding(
            category="security",
            message="Weak password policy detected, missing MFA",
            severity="high",
            file_path="app/auth/password.py",
            line_number=15
        )
        
        assert finding.iso_25010_characteristic == "security"
        assert finding.iso_25010_sub_characteristic == "Authenticity"
        assert finding.iso_23396_practice == "SE-6"
        assert finding.owasp_reference == "A07:2021"  # Authentication Failures
    
    def test_classify_access_control_finding(self, classifier):
        """Test classification of access control finding"""
        finding = classifier.classify_finding(
            category="security",
            message="Missing authorization check for admin endpoint",
            severity="critical",
            file_path="app/api/admin.py",
            line_number=30
        )
        
        assert finding.iso_25010_characteristic == "security"
        assert finding.iso_25010_sub_characteristic == "Confidentiality"
        assert finding.iso_23396_practice == "SE-6"
        assert finding.owasp_reference == "A01:2021"  # Broken Access Control
    
    def test_classify_code_quality_finding(self, classifier):
        """Test classification of code quality finding"""
        finding = classifier.classify_finding(
            category="code_quality",
            message="Duplicate code detected across multiple files",
            severity="low",
            file_path="app/utils/helpers.py",
            line_number=75
        )
        
        assert finding.iso_25010_characteristic == "maintainability"
        assert finding.iso_23396_practice == "SE-3"
        assert finding.owasp_reference is None
    
    def test_classify_reliability_finding(self, classifier):
        """Test classification of reliability finding"""
        finding = classifier.classify_finding(
            category="reliability",
            message="Missing error handling for network request",
            severity="medium",
            file_path="app/services/api_client.py",
            line_number=120
        )
        
        assert finding.iso_25010_characteristic == "reliability"
        assert finding.iso_25010_sub_characteristic == "Fault Tolerance"
        assert finding.iso_23396_practice == "SE-3"
        assert finding.owasp_reference is None
    
    def test_classify_cryptographic_finding(self, classifier):
        """Test classification of cryptographic finding"""
        finding = classifier.classify_finding(
            category="security",
            message="Hardcoded encryption key detected",
            severity="critical",
            file_path="app/config/secrets.py",
            line_number=10
        )
        
        assert finding.iso_25010_characteristic == "security"
        assert finding.iso_25010_sub_characteristic == "Confidentiality"
        assert finding.iso_23396_practice == "SE-6"
        assert finding.owasp_reference == "A02:2021"  # Cryptographic Failures
    
    def test_classify_dependency_finding(self, classifier):
        """Test classification of dependency finding"""
        finding = classifier.classify_finding(
            category="security",
            message="Outdated dependency with known CVE detected",
            severity="high",
            file_path="requirements.txt",
            line_number=5
        )
        
        assert finding.iso_25010_characteristic == "security"
        assert finding.iso_23396_practice == "SE-6"
        assert finding.owasp_reference == "A06:2021"  # Vulnerable Components
    
    def test_classify_logging_finding(self, classifier):
        """Test classification of logging finding"""
        finding = classifier.classify_finding(
            category="security",
            message="Missing audit logging for sensitive operation",
            severity="medium",
            file_path="app/api/transactions.py",
            line_number=88
        )
        
        assert finding.iso_25010_characteristic == "security"
        assert finding.iso_25010_sub_characteristic == "Accountability"
        assert finding.iso_23396_practice == "SE-6"
        assert finding.owasp_reference == "A09:2021"  # Logging Failures
    
    def test_classify_findings_batch(self, classifier):
        """Test batch classification of multiple findings"""
        findings = [
            {
                "category": "security",
                "message": "SQL injection vulnerability",
                "severity": "critical",
                "file_path": "app/api/users.py",
                "line_number": 42
            },
            {
                "category": "performance",
                "message": "Slow query detected",
                "severity": "medium",
                "file_path": "app/models/user.py",
                "line_number": 100
            },
            {
                "category": "maintainability",
                "message": "High complexity",
                "severity": "low",
                "file_path": "app/services/processor.py",
                "line_number": 250
            }
        ]
        
        classified = classifier.classify_findings_batch(findings)
        
        assert len(classified) == 3
        assert classified[0].owasp_reference == "A03:2021"
        assert classified[1].iso_25010_characteristic == "performance_efficiency"
        assert classified[2].iso_25010_characteristic == "maintainability"
    
    def test_get_standards_summary(self, classifier):
        """Test generation of standards compliance summary"""
        findings = [
            classifier.classify_finding("security", "SQL injection", "critical"),
            classifier.classify_finding("security", "XSS vulnerability", "high"),
            classifier.classify_finding("performance", "Slow query", "medium"),
            classifier.classify_finding("maintainability", "High complexity", "low"),
        ]
        
        summary = classifier.get_standards_summary(findings)
        
        assert summary["total_findings"] == 4
        assert "security" in summary["iso_25010_distribution"]
        assert summary["iso_25010_distribution"]["security"] == 2
        assert "SE-6" in summary["iso_23396_distribution"]
        assert summary["iso_23396_distribution"]["SE-6"] == 2
        assert len(summary["owasp_distribution"]) >= 1
    
    def test_classify_unknown_category_defaults_to_maintainability(self, classifier):
        """Test that unknown categories default to maintainability"""
        finding = classifier.classify_finding(
            category="unknown_category",
            message="Some issue",
            severity="medium"
        )
        
        assert finding.iso_25010_characteristic == "maintainability"
        assert finding.iso_23396_practice == "SE-3"
    
    def test_classify_with_suggested_fix(self, classifier):
        """Test classification with suggested fix"""
        finding = classifier.classify_finding(
            category="security",
            message="SQL injection vulnerability",
            severity="critical",
            suggested_fix="Use parameterized queries"
        )
        
        assert finding.suggested_fix == "Use parameterized queries"
        assert finding.owasp_reference == "A03:2021"
    
    def test_classify_with_rule_info(self, classifier):
        """Test classification with rule ID and name"""
        finding = classifier.classify_finding(
            category="security",
            message="SQL injection vulnerability",
            severity="critical",
            rule_id="SEC-001",
            rule_name="SQL Injection Detection"
        )
        
        assert finding.rule_id == "SEC-001"
        assert finding.rule_name == "SQL Injection Detection"
    
    def test_singleton_instance(self):
        """Test that get_standards_classifier returns singleton instance"""
        classifier1 = get_standards_classifier()
        classifier2 = get_standards_classifier()
        
        assert classifier1 is classifier2
    
    def test_ssrf_detection(self, classifier):
        """Test SSRF vulnerability detection"""
        finding = classifier.classify_finding(
            category="security",
            message="Unvalidated URL input allows server-side request forgery",
            severity="high",
            file_path="app/api/proxy.py",
            line_number=45
        )
        
        assert finding.owasp_reference == "A10:2021"  # SSRF
    
    def test_deserialization_detection(self, classifier):
        """Test insecure deserialization detection"""
        finding = classifier.classify_finding(
            category="security",
            message="Insecure deserialization of user input",
            severity="critical",
            file_path="app/api/data.py",
            line_number=67
        )
        
        assert finding.owasp_reference == "A08:2021"  # Software and Data Integrity Failures
    
    def test_configuration_issue_detection(self, classifier):
        """Test security misconfiguration detection"""
        finding = classifier.classify_finding(
            category="security",
            message="Default credentials detected in configuration",
            severity="high",
            file_path="config/settings.py",
            line_number=12
        )
        
        assert finding.owasp_reference == "A05:2021"  # Security Misconfiguration
    
    def test_architecture_category_mapping(self, classifier):
        """Test architecture category maps to design practice"""
        finding = classifier.classify_finding(
            category="architecture",
            message="Circular dependency detected",
            severity="high",
            file_path="app/services/service_a.py",
            line_number=20
        )
        
        assert finding.iso_25010_characteristic == "maintainability"
        assert finding.iso_23396_practice == "SE-2"  # Software Design
    
    def test_testing_category_mapping(self, classifier):
        """Test testing category maps to testing practice"""
        finding = classifier.classify_finding(
            category="testing",
            message="Missing unit tests for critical function",
            severity="medium",
            file_path="app/services/payment.py",
            line_number=150
        )
        
        assert finding.iso_25010_characteristic == "maintainability"
        assert finding.iso_23396_practice == "SE-4"  # Testing Practices
