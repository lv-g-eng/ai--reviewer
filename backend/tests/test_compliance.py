"""
Unit Tests for ISO/IEC 25010 Compliance Verification

Tests compliance verification against ISO/IEC 25010 quality standards.

**Validates: Requirements 1.9, 15.8**
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.architecture_analyzer.compliance import (
    ComplianceVerifier,
    ComplianceReport,
    ComplianceStatus,
    QualityCharacteristic,
    ComplianceViolation,
    ViolationSeverity
)


@pytest.fixture
def sample_nodes():
    """Sample nodes for testing"""
    return [
        {
            "node_id": 1,
            "labels": ["CodeEntity", "Function"],
            "properties": {
                "name": "calculate_total",
                "type": "function",
                "complexity": 5,
                "lines_of_code": 25,
                "has_error_handling": True,
                "has_docstring": True,
                "file_path": "src/calculator.py"
            }
        },
        {
            "node_id": 2,
            "labels": ["CodeEntity", "Function"],
            "properties": {
                "name": "process_data",
                "type": "function",
                "complexity": 15,
                "lines_of_code": 150,
                "has_error_handling": False,
                "has_docstring": False,
                "file_path": "src/processor.py"
            }
        },
        {
            "node_id": 3,
            "labels": ["CodeEntity", "Class"],
            "properties": {
                "name": "UserManager",
                "type": "class",
                "complexity": 8,
                "lines_of_code": 200,
                "has_error_handling": True,
                "has_docstring": True,
                "file_path": "src/user.py"
            }
        }
    ]



@pytest.fixture
def sample_relationships():
    """Sample relationships for testing"""
    return [
        {
            "rel_id": 1,
            "source_id": 1,
            "target_id": 2,
            "source_name": "calculate_total",
            "target_name": "process_data",
            "rel_type": "CALLS",
            "properties": {}
        },
        {
            "rel_id": 2,
            "source_id": 2,
            "target_id": 3,
            "source_name": "process_data",
            "target_name": "UserManager",
            "rel_type": "USES",
            "properties": {}
        }
    ]


@pytest.fixture
def high_complexity_nodes():
    """Nodes with high complexity for testing"""
    return [
        {
            "node_id": 1,
            "labels": ["CodeEntity", "Function"],
            "properties": {
                "name": "complex_function",
                "type": "function",
                "complexity": 25,
                "lines_of_code": 400,
                "has_error_handling": False,
                "has_docstring": False,
                "file_path": "src/complex.py"
            }
        }
    ]


@pytest.fixture
def security_sensitive_nodes():
    """Nodes with security-sensitive names"""
    return [
        {
            "node_id": 1,
            "labels": ["CodeEntity", "Function"],
            "properties": {
                "name": "validate_password",
                "type": "function",
                "complexity": 5,
                "lines_of_code": 20,
                "has_error_handling": False,
                "has_validation": False,
                "file_path": "src/auth.py"
            }
        },
        {
            "node_id": 2,
            "labels": ["CodeEntity", "Function"],
            "properties": {
                "name": "encrypt_token",
                "type": "function",
                "complexity": 3,
                "lines_of_code": 15,
                "has_error_handling": True,
                "has_validation": True,
                "file_path": "src/crypto.py"
            }
        }
    ]


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver"""
    driver = AsyncMock()
    session = AsyncMock()
    result = AsyncMock()
    
    driver.session.return_value.__aenter__.return_value = session
    session.run.return_value = result
    
    return driver, session, result



class TestComplianceVerifier:
    """Test suite for ComplianceVerifier"""
    
    @pytest.mark.asyncio
    async def test_verify_compliance_basic(self, sample_nodes, sample_relationships):
        """Test basic compliance verification"""
        verifier = ComplianceVerifier()
        
        with patch.object(verifier, '_get_project_nodes', return_value=sample_nodes), \
             patch.object(verifier, '_get_project_relationships', return_value=sample_relationships), \
             patch('app.services.architecture_analyzer.compliance.get_neo4j_driver', new_callable=AsyncMock):
            
            report = await verifier.verify_compliance("test_project")
            
            assert isinstance(report, ComplianceReport)
            assert report.project_id == "test_project"
            assert 0 <= report.overall_score <= 100
            assert report.compliance_status in [
                ComplianceStatus.COMPLIANT,
                ComplianceStatus.PARTIALLY_COMPLIANT,
                ComplianceStatus.NON_COMPLIANT
            ]
            assert len(report.characteristics) == 8
            assert "functional_suitability" in report.characteristics
            assert "performance_efficiency" in report.characteristics
            assert "compatibility" in report.characteristics
            assert "usability" in report.characteristics
            assert "reliability" in report.characteristics
            assert "security" in report.characteristics
            assert "maintainability" in report.characteristics
            assert "portability" in report.characteristics
    
    @pytest.mark.asyncio
    async def test_functional_suitability_check(self, sample_nodes, sample_relationships):
        """Test functional suitability characteristic check"""
        verifier = ComplianceVerifier()
        
        result = await verifier._check_functional_suitability(sample_nodes, sample_relationships)
        
        assert isinstance(result, QualityCharacteristic)
        assert result.name == "Functional Suitability"
        assert 0 <= result.score <= 100
        assert result.max_score == 100
        assert isinstance(result.violations, list)
        assert isinstance(result.recommendations, list)
    
    @pytest.mark.asyncio
    async def test_performance_efficiency_high_complexity(self, high_complexity_nodes, sample_relationships):
        """Test performance efficiency detects high complexity"""
        verifier = ComplianceVerifier()
        
        result = await verifier._check_performance_efficiency(high_complexity_nodes, sample_relationships)
        
        assert result.score < 100  # Should have violations
        assert len(result.violations) > 0
        # Check for complexity violation
        complexity_violations = [v for v in result.violations if "complexity" in v["issue"].lower()]
        assert len(complexity_violations) > 0
    
    @pytest.mark.asyncio
    async def test_security_check_sensitive_functions(self, security_sensitive_nodes, sample_relationships):
        """Test security check identifies security-sensitive functions"""
        verifier = ComplianceVerifier()
        
        result = await verifier._check_security(security_sensitive_nodes, sample_relationships)
        
        assert isinstance(result, QualityCharacteristic)
        # Should detect missing error handling in validate_password
        assert len(result.violations) > 0
        critical_violations = [v for v in result.violations if v["severity"] == "critical"]
        assert len(critical_violations) > 0

    
    @pytest.mark.asyncio
    async def test_reliability_check_error_handling(self, sample_nodes, sample_relationships):
        """Test reliability check evaluates error handling"""
        verifier = ComplianceVerifier()
        
        result = await verifier._check_reliability(sample_nodes, sample_relationships)
        
        assert isinstance(result, QualityCharacteristic)
        assert result.name == "Reliability"
        # Should detect missing error handling in process_data
        error_handling_violations = [v for v in result.violations 
                                     if "error handling" in v["issue"].lower()]
        assert len(error_handling_violations) > 0
    
    @pytest.mark.asyncio
    async def test_maintainability_check(self, high_complexity_nodes, sample_relationships):
        """Test maintainability check"""
        verifier = ComplianceVerifier()
        
        result = await verifier._check_maintainability(high_complexity_nodes, sample_relationships)
        
        assert isinstance(result, QualityCharacteristic)
        assert result.name == "Maintainability"
        # Should detect high complexity and large size
        assert len(result.violations) > 0
        assert result.score < 100
    
    @pytest.mark.asyncio
    async def test_usability_check_naming_conventions(self):
        """Test usability check for naming conventions"""
        verifier = ComplianceVerifier()
        
        nodes = [
            {
                "node_id": 1,
                "labels": ["CodeEntity", "Class"],
                "properties": {
                    "name": "myclass",  # Should start with uppercase
                    "type": "class",
                    "complexity": 5,
                    "lines_of_code": 50,
                    "has_docstring": False,
                    "file_path": "src/test.py"
                }
            }
        ]
        
        result = await verifier._check_usability(nodes, [])
        
        assert len(result.violations) > 0
        naming_violations = [v for v in result.violations if "uppercase" in v["issue"].lower()]
        assert len(naming_violations) > 0
    
    @pytest.mark.asyncio
    async def test_compatibility_circular_dependencies(self):
        """Test compatibility check detects circular dependencies"""
        verifier = ComplianceVerifier()
        
        # Create circular dependency: A -> B -> C -> A
        relationships = [
            {
                "rel_id": 1,
                "source_name": "A",
                "target_name": "B",
                "rel_type": "DEPENDS_ON",
                "properties": {}
            },
            {
                "rel_id": 2,
                "source_name": "B",
                "target_name": "C",
                "rel_type": "DEPENDS_ON",
                "properties": {}
            },
            {
                "rel_id": 3,
                "source_name": "C",
                "target_name": "A",
                "rel_type": "DEPENDS_ON",
                "properties": {}
            }
        ]
        
        result = await verifier._check_compatibility([], relationships)
        
        assert len(result.violations) > 0
        circular_violations = [v for v in result.violations 
                              if "circular" in v["issue"].lower()]
        assert len(circular_violations) > 0

    
    @pytest.mark.asyncio
    async def test_portability_check_platform_specific(self):
        """Test portability check detects platform-specific code"""
        verifier = ComplianceVerifier()
        
        nodes = [
            {
                "node_id": 1,
                "labels": ["CodeEntity", "Function"],
                "properties": {
                    "name": "windows_specific_function",
                    "type": "function",
                    "complexity": 5,
                    "lines_of_code": 30,
                    "file_path": "c:\\users\\test\\file.py"
                }
            }
        ]
        
        result = await verifier._check_portability(nodes, [])
        
        assert len(result.violations) > 0
        platform_violations = [v for v in result.violations 
                              if "platform" in v["issue"].lower() or "path" in v["issue"].lower()]
        assert len(platform_violations) > 0
    
    def test_calculate_overall_score(self):
        """Test overall score calculation"""
        verifier = ComplianceVerifier()
        
        characteristics = {
            "char1": QualityCharacteristic("Char1", 80, 100, [], []),
            "char2": QualityCharacteristic("Char2", 90, 100, [], []),
            "char3": QualityCharacteristic("Char3", 70, 100, [], [])
        }
        
        score = verifier._calculate_overall_score(characteristics)
        
        assert score == 80  # (80 + 90 + 70) / 3 = 80
    
    def test_determine_compliance_status(self):
        """Test compliance status determination"""
        verifier = ComplianceVerifier()
        
        assert verifier._determine_compliance_status(85) == ComplianceStatus.COMPLIANT
        assert verifier._determine_compliance_status(70) == ComplianceStatus.PARTIALLY_COMPLIANT
        assert verifier._determine_compliance_status(50) == ComplianceStatus.NON_COMPLIANT
    
    def test_extract_violations(self):
        """Test violation extraction from quality characteristic"""
        verifier = ComplianceVerifier()
        
        char = QualityCharacteristic(
            name="Test Characteristic",
            score=80,
            max_score=100,
            violations=[
                {
                    "entity": "test_function",
                    "type": "function",
                    "issue": "High complexity",
                    "severity": "high",
                    "metric": "Complexity: 20"
                }
            ],
            recommendations=["Refactor function"]
        )
        
        violations = verifier._extract_violations(char, "test_characteristic")
        
        assert len(violations) == 1
        assert isinstance(violations[0], ComplianceViolation)
        assert violations[0].characteristic == "test_characteristic"
        assert violations[0].severity == ViolationSeverity.HIGH
        assert violations[0].entity_name == "test_function"
    
    def test_generate_summary(self):
        """Test summary generation"""
        verifier = ComplianceVerifier()
        
        characteristics = {
            "char1": QualityCharacteristic("Char1", 80, 100, 
                [{"severity": "high", "issue": "test"}], []),
            "char2": QualityCharacteristic("Char2", 90, 100, [], [])
        }
        
        summary = verifier._generate_summary(85, ComplianceStatus.COMPLIANT, characteristics)
        
        assert "COMPLIANT" in summary
        assert "85/100" in summary
        assert "Char1" in summary
        assert "Char2" in summary

    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        verifier = ComplianceVerifier()
        
        characteristics = {
            "char1": QualityCharacteristic("Char1", 70, 100, [], 
                ["Improve code quality"]),
            "char2": QualityCharacteristic("Char2", 90, 100, [], [])
        }
        
        violations = [
            ComplianceViolation(
                characteristic="char1",
                severity=ViolationSeverity.CRITICAL,
                entity_name="test",
                entity_type="function",
                description="Critical issue",
                metric_value="N/A",
                threshold="N/A",
                recommendation="Fix immediately"
            )
        ]
        
        recommendations = verifier._generate_recommendations(characteristics, violations)
        
        assert len(recommendations) > 0
        assert any("URGENT" in rec or "critical" in rec.lower() for rec in recommendations)
    
    def test_compliance_report_to_dict(self):
        """Test ComplianceReport serialization"""
        char = QualityCharacteristic("Test", 80, 100, [], [])
        violation = ComplianceViolation(
            characteristic="test",
            severity=ViolationSeverity.HIGH,
            entity_name="test_entity",
            entity_type="function",
            description="Test violation",
            metric_value="10",
            threshold="5",
            recommendation="Fix it"
        )
        
        report = ComplianceReport(
            project_id="test_project",
            timestamp=datetime.utcnow().isoformat(),
            overall_score=80,
            compliance_status=ComplianceStatus.COMPLIANT,
            characteristics={"test": char},
            violations=[violation],
            summary="Test summary",
            recommendations=["Test recommendation"]
        )
        
        report_dict = report.to_dict()
        
        assert report_dict["project_id"] == "test_project"
        assert report_dict["overall_score"] == 80
        assert report_dict["compliance_status"] == "compliant"
        assert "test" in report_dict["characteristics"]
        assert len(report_dict["violations"]) == 1
        assert report_dict["summary"] == "Test summary"


class TestComplianceDataClasses:
    """Test compliance data classes"""
    
    def test_quality_characteristic_to_dict(self):
        """Test QualityCharacteristic serialization"""
        char = QualityCharacteristic(
            name="Test",
            score=85,
            max_score=100,
            violations=[{"test": "violation"}],
            recommendations=["Test recommendation"]
        )
        
        char_dict = char.to_dict()
        
        assert char_dict["name"] == "Test"
        assert char_dict["score"] == 85
        assert char_dict["max_score"] == 100
        assert len(char_dict["violations"]) == 1
        assert len(char_dict["recommendations"]) == 1
    
    def test_compliance_violation_to_dict(self):
        """Test ComplianceViolation serialization"""
        violation = ComplianceViolation(
            characteristic="security",
            severity=ViolationSeverity.CRITICAL,
            entity_name="validate_password",
            entity_type="function",
            description="Missing error handling",
            metric_value="No error handling",
            threshold="Required",
            recommendation="Add try-catch blocks"
        )
        
        violation_dict = violation.to_dict()
        
        assert violation_dict["characteristic"] == "security"
        assert violation_dict["severity"] == "critical"
        assert violation_dict["entity_name"] == "validate_password"
        assert violation_dict["entity_type"] == "function"
        assert "error handling" in violation_dict["description"]

    
    def test_compliance_status_enum(self):
        """Test ComplianceStatus enum values"""
        assert ComplianceStatus.COMPLIANT.value == "compliant"
        assert ComplianceStatus.PARTIALLY_COMPLIANT.value == "partially_compliant"
        assert ComplianceStatus.NON_COMPLIANT.value == "non_compliant"
    
    def test_violation_severity_enum(self):
        """Test ViolationSeverity enum values"""
        assert ViolationSeverity.CRITICAL.value == "critical"
        assert ViolationSeverity.HIGH.value == "high"
        assert ViolationSeverity.MEDIUM.value == "medium"
        assert ViolationSeverity.LOW.value == "low"


class TestCircularDependencyDetection:
    """Test circular dependency detection"""
    
    @pytest.mark.asyncio
    async def test_detect_simple_circular_dependency(self):
        """Test detection of simple circular dependency"""
        verifier = ComplianceVerifier()
        
        relationships = [
            {"source_name": "A", "target_name": "B", "rel_type": "DEPENDS_ON"},
            {"source_name": "B", "target_name": "A", "rel_type": "DEPENDS_ON"}
        ]
        
        cycles = await verifier._detect_circular_dependencies(relationships)
        
        assert len(cycles) > 0
        # Should detect A -> B -> A cycle
        assert any("A" in cycle and "B" in cycle for cycle in cycles)
    
    @pytest.mark.asyncio
    async def test_detect_complex_circular_dependency(self):
        """Test detection of complex circular dependency"""
        verifier = ComplianceVerifier()
        
        relationships = [
            {"source_name": "A", "target_name": "B", "rel_type": "DEPENDS_ON"},
            {"source_name": "B", "target_name": "C", "rel_type": "DEPENDS_ON"},
            {"source_name": "C", "target_name": "D", "rel_type": "DEPENDS_ON"},
            {"source_name": "D", "target_name": "A", "rel_type": "DEPENDS_ON"}
        ]
        
        cycles = await verifier._detect_circular_dependencies(relationships)
        
        assert len(cycles) > 0
        # Should detect A -> B -> C -> D -> A cycle
        assert any(len(cycle) >= 4 for cycle in cycles)
    
    @pytest.mark.asyncio
    async def test_no_circular_dependency(self):
        """Test when no circular dependencies exist"""
        verifier = ComplianceVerifier()
        
        relationships = [
            {"source_name": "A", "target_name": "B", "rel_type": "DEPENDS_ON"},
            {"source_name": "B", "target_name": "C", "rel_type": "DEPENDS_ON"},
            {"source_name": "C", "target_name": "D", "rel_type": "DEPENDS_ON"}
        ]
        
        cycles = await verifier._detect_circular_dependencies(relationships)
        
        assert len(cycles) == 0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_empty_project(self):
        """Test compliance verification with empty project"""
        verifier = ComplianceVerifier()
        
        with patch.object(verifier, '_get_project_nodes', return_value=[]), \
             patch.object(verifier, '_get_project_relationships', return_value=[]), \
             patch('app.services.architecture_analyzer.compliance.get_neo4j_driver', new_callable=AsyncMock):
            
            report = await verifier.verify_compliance("empty_project")
            
            assert isinstance(report, ComplianceReport)
            assert report.overall_score >= 0
            # Empty project should have high scores (no violations)
            assert report.overall_score >= 80
    
    @pytest.mark.asyncio
    async def test_minimal_node_properties(self):
        """Test handling nodes with minimal properties"""
        verifier = ComplianceVerifier()
        
        nodes = [
            {
                "node_id": 1,
                "labels": ["CodeEntity"],
                "properties": {
                    "name": "test",
                    "type": "function"
                    # Missing: complexity, lines_of_code, etc.
                }
            }
        ]
        
        # Should not crash with missing properties
        result = await verifier._check_performance_efficiency(nodes, [])
        assert isinstance(result, QualityCharacteristic)
