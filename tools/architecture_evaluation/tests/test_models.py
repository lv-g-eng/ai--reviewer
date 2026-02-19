"""
Unit tests for data models.
"""

import pytest
from datetime import datetime
from tools.architecture_evaluation.models import (
    Capability,
    Gap,
    LayerAnalysisResult,
    IntegrationPoint,
    DataFlowTrace,
    SecurityFinding,
    PerformanceIssue,
    TestingGap,
    Improvement,
    EvaluationReport,
    IntegrationAnalysisResult,
    SecurityEvaluationResult,
    PerformanceEvaluationResult,
    TestingEvaluationResult,
    PartialCapability,
)


@pytest.mark.unit
class TestCapability:
    """Test Capability data model."""

    def test_capability_creation(self):
        """Test that Capability can be created with required fields."""
        capability = Capability(
            name="Authentication",
            description="JWT-based authentication",
            category="Security",
            required=True,
            verification_method="Code inspection"
        )
        
        assert capability.name == "Authentication"
        assert capability.description == "JWT-based authentication"
        assert capability.category == "Security"
        assert capability.required is True
        assert capability.verification_method == "Code inspection"


@pytest.mark.unit
class TestGap:
    """Test Gap data model."""

    def test_gap_creation(self):
        """Test that Gap can be created with required fields."""
        gap = Gap(
            gap_id="GAP-001",
            layer="Backend API",
            category="Authentication",
            description="Missing rate limiting",
            expected_state="Rate limiting implemented",
            current_state="No rate limiting",
            impact="High",
            affected_requirements=["REQ-4.2"],
            related_capabilities=["API Security"]
        )
        
        assert gap.gap_id == "GAP-001"
        assert gap.layer == "Backend API"
        assert gap.impact == "High"
        assert len(gap.affected_requirements) == 1
        assert len(gap.related_capabilities) == 1


@pytest.mark.unit
class TestLayerAnalysisResult:
    """Test LayerAnalysisResult data model."""

    def test_layer_analysis_result_creation(self):
        """Test that LayerAnalysisResult can be created."""
        capability = Capability(
            name="Test",
            description="Test capability",
            category="Test",
            required=True,
            verification_method="Test"
        )
        
        result = LayerAnalysisResult(
            layer_name="Frontend",
            completeness_score=0.75,
            capabilities_assessed=[capability],
            implemented_capabilities=[capability],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=["Good test coverage"],
            timestamp=datetime.now()
        )
        
        assert result.layer_name == "Frontend"
        assert result.completeness_score == 0.75
        assert 0.0 <= result.completeness_score <= 1.0
        assert len(result.capabilities_assessed) == 1
        assert len(result.strengths) == 1

    def test_completeness_score_range(self):
        """Test that completeness score is within valid range."""
        result = LayerAnalysisResult(
            layer_name="Backend",
            completeness_score=0.5,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=[],
            timestamp=datetime.now()
        )
        
        assert 0.0 <= result.completeness_score <= 1.0


@pytest.mark.unit
class TestIntegrationPoint:
    """Test IntegrationPoint data model."""

    def test_integration_point_creation(self):
        """Test that IntegrationPoint can be created."""
        point = IntegrationPoint(
            point_id="INT-001",
            source_layer="Frontend",
            target_layer="Backend API",
            interface_type="REST API",
            data_flow_direction="Bidirectional",
            error_handling_present=True,
            retry_mechanism_present=False,
            issues=["Missing retry logic"]
        )
        
        assert point.point_id == "INT-001"
        assert point.source_layer == "Frontend"
        assert point.target_layer == "Backend API"
        assert point.error_handling_present is True
        assert point.retry_mechanism_present is False
        assert len(point.issues) == 1


@pytest.mark.unit
class TestDataFlowTrace:
    """Test DataFlowTrace data model."""

    def test_data_flow_trace_creation(self):
        """Test that DataFlowTrace can be created."""
        trace = DataFlowTrace(
            flow_name="PR Review Flow",
            layers_traversed=["Frontend", "Backend API", "AI Reasoning", "Data Persistence"],
            integration_points=[],
            bottlenecks=["AI API latency"],
            failure_points=["Network timeout"],
            total_latency_estimate=2.5
        )
        
        assert trace.flow_name == "PR Review Flow"
        assert len(trace.layers_traversed) == 4
        assert trace.layers_traversed[0] == "Frontend"
        assert trace.layers_traversed[-1] == "Data Persistence"
        assert len(trace.bottlenecks) == 1
        assert trace.total_latency_estimate == 2.5


@pytest.mark.unit
class TestSecurityFinding:
    """Test SecurityFinding data model."""

    def test_security_finding_creation(self):
        """Test that SecurityFinding can be created."""
        finding = SecurityFinding(
            finding_id="SEC-001",
            layer="Backend API",
            severity="Critical",
            category="Authentication",
            description="JWT secret exposed",
            current_state="Hardcoded in source",
            recommended_fix="Use environment variable",
            references=["OWASP A02:2021"]
        )
        
        assert finding.finding_id == "SEC-001"
        assert finding.severity == "Critical"
        assert finding.category == "Authentication"
        assert len(finding.references) == 1


@pytest.mark.unit
class TestPerformanceIssue:
    """Test PerformanceIssue data model."""

    def test_performance_issue_creation(self):
        """Test that PerformanceIssue can be created."""
        issue = PerformanceIssue(
            issue_id="PERF-001",
            layer="Data Persistence",
            severity="High",
            category="Latency",
            description="Missing database index",
            impact_estimate="50% slower queries",
            recommended_fix="Add index on user_id column"
        )
        
        assert issue.issue_id == "PERF-001"
        assert issue.layer == "Data Persistence"
        assert issue.severity == "High"
        assert issue.impact_estimate != ""


@pytest.mark.unit
class TestTestingGap:
    """Test TestingGap data model."""

    def test_testing_gap_creation(self):
        """Test that TestingGap can be created."""
        gap = TestingGap(
            gap_id="TEST-001",
            layer="Backend API",
            component="auth_service",
            test_type="Unit",
            current_coverage=0.45,
            target_coverage=0.80,
            missing_test_scenarios=["Token expiration", "Invalid credentials"]
        )
        
        assert gap.gap_id == "TEST-001"
        assert gap.test_type == "Unit"
        assert gap.current_coverage == 0.45
        assert gap.target_coverage == 0.80
        assert len(gap.missing_test_scenarios) == 2


@pytest.mark.unit
class TestImprovement:
    """Test Improvement data model."""

    def test_improvement_creation(self):
        """Test that Improvement can be created."""
        improvement = Improvement(
            improvement_id="IMP-001",
            title="Implement rate limiting",
            description="Add rate limiting to API endpoints",
            priority="High",
            category="Security",
            affected_layers=["Backend API"],
            current_state="No rate limiting",
            desired_state="Rate limiting on all endpoints",
            implementation_guidance="Use slowapi library",
            acceptance_criteria=[
                "Rate limit of 100 requests/minute per user",
                "Return 429 status code when exceeded"
            ],
            estimated_effort="Medium",
            dependencies=[],
            impact_metrics={"security": "High", "performance": "Medium"}
        )
        
        assert improvement.improvement_id == "IMP-001"
        assert improvement.priority == "High"
        assert len(improvement.acceptance_criteria) == 2
        assert improvement.estimated_effort == "Medium"
        assert len(improvement.dependencies) == 0
        assert "security" in improvement.impact_metrics


@pytest.mark.unit
class TestEvaluationReport:
    """Test EvaluationReport data model."""

    def test_evaluation_report_creation(self):
        """Test that EvaluationReport can be created."""
        layer_result = LayerAnalysisResult(
            layer_name="Frontend",
            completeness_score=0.8,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=[],
            timestamp=datetime.now()
        )
        
        integration_result = IntegrationAnalysisResult(
            integration_points=[],
            data_flows=[],
            issues=[],
            timestamp=datetime.now()
        )
        
        security_result = SecurityEvaluationResult(
            findings=[],
            layers_assessed=["Frontend"],
            timestamp=datetime.now()
        )
        
        performance_result = PerformanceEvaluationResult(
            issues=[],
            layers_assessed=["Frontend"],
            timestamp=datetime.now()
        )
        
        testing_result = TestingEvaluationResult(
            gaps=[],
            layers_assessed=["Frontend"],
            timestamp=datetime.now()
        )
        
        report = EvaluationReport(
            report_id="EVAL-001",
            generated_at=datetime.now(),
            executive_summary="Test summary",
            layer_results={"Frontend": layer_result},
            integration_analysis=integration_result,
            security_evaluation=security_result,
            performance_evaluation=performance_result,
            testing_evaluation=testing_result,
            improvements=[],
            overall_completeness_score=0.8,
            priority_improvements=[],
            diagrams={}
        )
        
        assert report.report_id == "EVAL-001"
        assert report.overall_completeness_score == 0.8
        assert "Frontend" in report.layer_results
        assert len(report.improvements) == 0
