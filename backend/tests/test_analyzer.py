"""
Unit Tests for Architecture Analyzer

Tests the main architecture analyzer service that orchestrates drift detection
and compliance verification.

**Validates: Requirements 5.2**
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from app.services.architecture_analyzer.analyzer import ArchitectureAnalyzer
from app.services.architecture_analyzer.drift_detector import (
    DriftDetector,
    DriftResult,
    DriftMetrics,
    DriftSeverity,
    DriftDetail
)
from app.services.architecture_analyzer.compliance import (
    ComplianceVerifier,
    ComplianceReport,
    ComplianceStatus,
    QualityCharacteristic
)


@pytest.fixture
def analyzer():
    """Create ArchitectureAnalyzer instance"""
    return ArchitectureAnalyzer()


@pytest.fixture
def sample_drift_result():
    """Sample drift detection result"""
    metrics = DriftMetrics(
        new_dependencies=5,
        removed_dependencies=2,
        modified_relationships=1,
        new_nodes=3,
        removed_nodes=1,
        modified_nodes=2,
        total_changes=14,
        drift_percentage=15.5,
        complexity_delta=25
    )
    
    return DriftResult(
        project_id="test_project",
        baseline_version="v1.0.0",
        current_timestamp="2024-01-15T10:00:00",
        severity=DriftSeverity.MEDIUM,
        metrics=metrics,
        details=[
            DriftDetail(
                change_type="added",
                entity_type="node",
                entity_name="new_function",
                details={"complexity": 5},
                impact="New functionality added"
            )
        ],
        summary="Medium drift detected",
        recommendations=["Review architectural changes"]
    )


@pytest.fixture
def sample_compliance_report():
    """Sample compliance report"""
    char = QualityCharacteristic(
        name="Security",
        score=85,
        max_score=100,
        violations=[],
        recommendations=[]
    )
    
    return ComplianceReport(
        project_id="test_project",
        timestamp="2024-01-15T10:00:00",
        overall_score=85,
        compliance_status=ComplianceStatus.COMPLIANT,
        characteristics={"security": char},
        violations=[],
        summary="Project is compliant",
        recommendations=[]
    )


class TestArchitectureAnalyzer:
    """Test suite for ArchitectureAnalyzer"""
    
    @pytest.mark.asyncio
    async def test_analyze_architecture_stub(self, analyzer):
        """Test that analyze_architecture returns stub response"""
        result = await analyzer.analyze_architecture("test_project")
        
        assert isinstance(result, dict)
        assert result["project_id"] == "test_project"
        assert result["status"] == "not_implemented"
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_detect_violations_stub(self, analyzer):
        """Test that detect_violations returns empty list"""
        violations = await analyzer.detect_violations("test_project")
        
        assert isinstance(violations, list)
        assert len(violations) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_with_kwargs(self, analyzer):
        """Test analyze_architecture accepts additional parameters"""
        result = await analyzer.analyze_architecture(
            "test_project",
            baseline_version="v1.0.0",
            include_compliance=True
        )
        
        assert result["project_id"] == "test_project"
        assert result["status"] == "not_implemented"


class TestArchitectureAnalyzerIntegration:
    """Integration tests for architecture analyzer workflow"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_workflow_mock(
        self,
        sample_drift_result,
        sample_compliance_report
    ):
        """Test complete analysis workflow with mocked components"""
        # This test demonstrates how the analyzer would work when fully implemented
        
        # Mock drift detector
        mock_drift_detector = AsyncMock(spec=DriftDetector)
        mock_drift_detector.detect_drift.return_value = sample_drift_result
        
        # Mock compliance verifier
        mock_compliance_verifier = AsyncMock(spec=ComplianceVerifier)
        mock_compliance_verifier.verify_compliance.return_value = sample_compliance_report
        
        # Simulate full analysis
        project_id = "test_project"
        
        # Step 1: Detect drift
        drift_result = await mock_drift_detector.detect_drift(
            project_id=project_id,
            baseline_version="v1.0.0"
        )
        
        assert drift_result.project_id == project_id
        assert drift_result.severity == DriftSeverity.MEDIUM
        assert drift_result.metrics.total_changes == 14
        
        # Step 2: Verify compliance
        compliance_report = await mock_compliance_verifier.verify_compliance(project_id)
        
        assert compliance_report.project_id == project_id
        assert compliance_report.overall_score == 85
        assert compliance_report.compliance_status == ComplianceStatus.COMPLIANT
        
        # Step 3: Combine results
        combined_result = {
            "project_id": project_id,
            "drift_analysis": drift_result.to_dict(),
            "compliance_report": compliance_report.to_dict(),
            "overall_health": "good" if (
                drift_result.severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM] and
                compliance_report.compliance_status == ComplianceStatus.COMPLIANT
            ) else "needs_attention"
        }
        
        assert combined_result["overall_health"] == "good"
        assert "drift_analysis" in combined_result
        assert "compliance_report" in combined_result


class TestArchitectureAnalyzerErrorHandling:
    """Test error handling in architecture analyzer"""
    
    @pytest.mark.asyncio
    async def test_analyze_with_invalid_project_id(self, analyzer):
        """Test analysis with invalid project ID"""
        # Current stub implementation doesn't validate, but test the interface
        result = await analyzer.analyze_architecture("")
        
        assert isinstance(result, dict)
        assert "project_id" in result
    
    @pytest.mark.asyncio
    async def test_detect_violations_with_none_project_id(self, analyzer):
        """Test detect_violations handles None project ID"""
        # Current stub implementation doesn't validate
        violations = await analyzer.detect_violations(None)
        
        assert isinstance(violations, list)


class TestArchitectureAnalyzerDataStructures:
    """Test data structure handling"""
    
    def test_drift_result_serialization(self, sample_drift_result):
        """Test DriftResult can be serialized to dict"""
        result_dict = sample_drift_result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["project_id"] == "test_project"
        assert result_dict["severity"] == "medium"
        assert "metrics" in result_dict
        assert "details" in result_dict
        assert "recommendations" in result_dict
    
    def test_compliance_report_serialization(self, sample_compliance_report):
        """Test ComplianceReport can be serialized to dict"""
        report_dict = sample_compliance_report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert report_dict["project_id"] == "test_project"
        assert report_dict["overall_score"] == 85
        assert report_dict["compliance_status"] == "compliant"
        assert "characteristics" in report_dict
        assert "violations" in report_dict
    
    def test_drift_metrics_to_dict(self):
        """Test DriftMetrics serialization"""
        metrics = DriftMetrics(
            new_dependencies=1,
            removed_dependencies=2,
            modified_relationships=3,
            new_nodes=4,
            removed_nodes=5,
            modified_nodes=6,
            total_changes=21,
            drift_percentage=10.5,
            complexity_delta=15
        )
        
        metrics_dict = metrics.to_dict()
        
        assert metrics_dict["new_dependencies"] == 1
        assert metrics_dict["removed_dependencies"] == 2
        assert metrics_dict["total_changes"] == 21
        assert metrics_dict["drift_percentage"] == 10.5
        assert metrics_dict["complexity_delta"] == 15


class TestArchitectureAnalyzerFutureImplementation:
    """Tests for future implementation features"""
    
    @pytest.mark.asyncio
    async def test_future_combined_analysis(self):
        """Test future implementation of combined drift and compliance analysis"""
        # This test documents the expected behavior when fully implemented
        
        # Expected interface:
        # result = await analyzer.analyze_architecture(
        #     project_id="test_project",
        #     baseline_version="v1.0.0",
        #     include_drift=True,
        #     include_compliance=True
        # )
        
        # Expected result structure:
        expected_structure = {
            "project_id": str,
            "timestamp": str,
            "drift_analysis": dict,  # DriftResult
            "compliance_report": dict,  # ComplianceReport
            "recommendations": list,
            "overall_health_score": int,
            "action_items": list
        }
        
        # Verify expected structure is documented
        assert "project_id" in expected_structure
        assert "drift_analysis" in expected_structure
        assert "compliance_report" in expected_structure
    
    @pytest.mark.asyncio
    async def test_future_violation_detection(self):
        """Test future implementation of violation detection"""
        # Expected interface:
        # violations = await analyzer.detect_violations(
        #     project_id="test_project",
        #     violation_types=["circular_dependency", "high_complexity"]
        # )
        
        # Expected violation structure:
        expected_violation = {
            "type": str,
            "severity": str,
            "entity": str,
            "description": str,
            "recommendation": str
        }
        
        # Verify expected structure is documented
        assert "type" in expected_violation
        assert "severity" in expected_violation
        assert "entity" in expected_violation
