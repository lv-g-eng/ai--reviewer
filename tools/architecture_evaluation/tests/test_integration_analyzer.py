"""
Unit tests for IntegrationAnalyzer.

Tests the integration analysis functionality including integration point
identification, error handling assessment, data flow tracing, and bottleneck
identification.
"""

import pytest
from datetime import datetime

from tools.architecture_evaluation.integration_analyzer import IntegrationAnalyzer
from tools.architecture_evaluation.models import (
    LayerAnalysisResult,
    IntegrationPoint,
    DataFlowTrace,
    IntegrationAnalysisResult,
    Capability,
    Gap
)


@pytest.fixture
def sample_layer_results():
    """Create sample layer analysis results for testing."""
    return {
        "Frontend": LayerAnalysisResult(
            layer_name="Frontend",
            completeness_score=0.85,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=["React 19 configured", "WebSocket client implemented"],
            timestamp=datetime.now()
        ),
        "Backend API": LayerAnalysisResult(
            layer_name="Backend API",
            completeness_score=0.90,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=["FastAPI configured", "JWT authentication", "Error middleware"],
            timestamp=datetime.now()
        ),
        "Data Persistence": LayerAnalysisResult(
            layer_name="Data Persistence",
            completeness_score=0.75,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=["PostgreSQL configured", "Connection pooling"],
            timestamp=datetime.now()
        ),
        "AI Reasoning": LayerAnalysisResult(
            layer_name="AI Reasoning",
            completeness_score=0.80,
            capabilities_assessed=[],
            implemented_capabilities=[
                Capability("Fallback Mechanism", "LLM fallback", "Reliability", True, "Code")
            ],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=["Multi-LLM support", "Timeout handling"],
            timestamp=datetime.now()
        ),
        "Integration": LayerAnalysisResult(
            layer_name="Integration",
            completeness_score=0.70,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[
                Gap(
                    gap_id="GAP-INT-001",
                    layer="Integration",
                    category="Authentication",
                    description="OAuth signature verification incomplete",
                    expected_state="Full OAuth 2.0 implementation",
                    current_state="Partial implementation",
                    impact="High",
                    affected_requirements=["4.5"],
                    related_capabilities=["OAuth 2.0"]
                )
            ],
            strengths=["GitHub webhook handling"],
            timestamp=datetime.now()
        )
    }


@pytest.fixture
def integration_analyzer():
    """Create an IntegrationAnalyzer instance for testing."""
    return IntegrationAnalyzer()


def test_identify_integration_points_all_layers(integration_analyzer, sample_layer_results):
    """Test identification of integration points when all layers are present."""
    integration_points = integration_analyzer.identify_integration_points(sample_layer_results)
    
    # Should identify multiple integration points
    assert len(integration_points) > 0
    
    # Check for Frontend-Backend integration
    frontend_backend_points = [
        p for p in integration_points 
        if p.source_layer == "Frontend" and p.target_layer == "Backend API"
    ]
    assert len(frontend_backend_points) >= 1
    
    # Check for Backend-Data integration
    backend_data_points = [
        p for p in integration_points 
        if p.source_layer == "Backend API" and p.target_layer == "Data Persistence"
    ]
    assert len(backend_data_points) >= 1
    
    # Check for Backend-AI integration
    backend_ai_points = [
        p for p in integration_points 
        if p.source_layer == "Backend API" and p.target_layer == "AI Reasoning"
    ]
    assert len(backend_ai_points) >= 1
    
    # Check for Backend-Integration points
    backend_integration_points = [
        p for p in integration_points 
        if p.source_layer == "Backend API" and p.target_layer == "Integration"
    ]
    assert len(backend_integration_points) >= 1


def test_identify_integration_points_missing_layers(integration_analyzer):
    """Test integration point identification with missing layers."""
    # Only Frontend and Backend
    limited_results = {
        "Frontend": LayerAnalysisResult(
            layer_name="Frontend",
            completeness_score=0.85,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=[],
            timestamp=datetime.now()
        ),
        "Backend API": LayerAnalysisResult(
            layer_name="Backend API",
            completeness_score=0.90,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=[],
            timestamp=datetime.now()
        )
    }
    
    integration_points = integration_analyzer.identify_integration_points(limited_results)
    
    # Should only have Frontend-Backend points
    assert len(integration_points) >= 1
    assert all(
        (p.source_layer in ["Frontend", "Backend API"] and 
         p.target_layer in ["Frontend", "Backend API"])
        for p in integration_points
    )


def test_assess_error_handling_with_strengths(integration_analyzer, sample_layer_results):
    """Test error handling assessment when layers have error handling strengths."""
    integration_point = IntegrationPoint(
        point_id="INT-001",
        source_layer="Frontend",
        target_layer="Backend API",
        interface_type="REST API",
        data_flow_direction="Bidirectional",
        error_handling_present=False,
        retry_mechanism_present=False,
        issues=[]
    )
    
    integration_analyzer.assess_error_handling(integration_point, sample_layer_results)
    
    # Backend has "Error middleware" in strengths, so error handling should be detected
    assert integration_point.error_handling_present is True


def test_assess_error_handling_missing(integration_analyzer):
    """Test error handling assessment when error handling is missing."""
    layer_results = {
        "Frontend": LayerAnalysisResult(
            layer_name="Frontend",
            completeness_score=0.50,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=[],  # No error handling strengths
            timestamp=datetime.now()
        ),
        "Backend API": LayerAnalysisResult(
            layer_name="Backend API",
            completeness_score=0.50,
            capabilities_assessed=[],
            implemented_capabilities=[],
            missing_capabilities=[],
            partial_capabilities=[],
            gaps=[],
            strengths=[],  # No error handling strengths
            timestamp=datetime.now()
        )
    }
    
    integration_point = IntegrationPoint(
        point_id="INT-001",
        source_layer="Frontend",
        target_layer="Backend API",
        interface_type="REST API",
        data_flow_direction="Bidirectional",
        error_handling_present=False,
        retry_mechanism_present=False,
        issues=[]
    )
    
    integration_analyzer.assess_error_handling(integration_point, layer_results)
    
    # Should flag missing error handling
    assert len(integration_point.issues) > 0
    assert any("error handling" in issue.lower() for issue in integration_point.issues)


def test_evaluate_data_flow_pr_review(integration_analyzer, sample_layer_results):
    """Test data flow tracing for PR review flow."""
    integration_points = integration_analyzer.identify_integration_points(sample_layer_results)
    data_flows = integration_analyzer.evaluate_data_flow(sample_layer_results, integration_points)
    
    # Should have PR review flow
    pr_flows = [f for f in data_flows if "PR Review" in f.flow_name]
    assert len(pr_flows) > 0
    
    pr_flow = pr_flows[0]
    # Should traverse multiple layers
    assert len(pr_flow.layers_traversed) >= 2
    # Should include Frontend and Backend at minimum
    assert "Frontend" in pr_flow.layers_traversed
    assert "Backend API" in pr_flow.layers_traversed


def test_evaluate_data_flow_authentication(integration_analyzer, sample_layer_results):
    """Test data flow tracing for authentication flow."""
    integration_points = integration_analyzer.identify_integration_points(sample_layer_results)
    data_flows = integration_analyzer.evaluate_data_flow(sample_layer_results, integration_points)
    
    # Should have authentication flow
    auth_flows = [f for f in data_flows if "Authentication" in f.flow_name]
    assert len(auth_flows) > 0
    
    auth_flow = auth_flows[0]
    # Should traverse Frontend, Backend, and Data layers
    assert "Frontend" in auth_flow.layers_traversed
    assert "Backend API" in auth_flow.layers_traversed


def test_evaluate_data_flow_webhook(integration_analyzer, sample_layer_results):
    """Test data flow tracing for webhook flow."""
    integration_points = integration_analyzer.identify_integration_points(sample_layer_results)
    data_flows = integration_analyzer.evaluate_data_flow(sample_layer_results, integration_points)
    
    # Should have webhook flow
    webhook_flows = [f for f in data_flows if "Webhook" in f.flow_name]
    assert len(webhook_flows) > 0
    
    webhook_flow = webhook_flows[0]
    # Should start with Integration layer
    assert "Integration" in webhook_flow.layers_traversed


def test_identify_bottlenecks_no_error_handling(integration_analyzer):
    """Test bottleneck identification when error handling is missing."""
    integration_points = [
        IntegrationPoint(
            point_id="INT-001",
            source_layer="Frontend",
            target_layer="Backend API",
            interface_type="REST API",
            data_flow_direction="Bidirectional",
            error_handling_present=False,  # Missing error handling
            retry_mechanism_present=False,  # Missing retry
            issues=["Missing error handling", "Missing retry mechanism"]
        )
    ]
    
    data_flows = []
    
    bottlenecks = integration_analyzer.identify_bottlenecks(integration_points, data_flows)
    
    # Should identify bottlenecks for missing error handling and retry
    assert len(bottlenecks) >= 2
    assert any("error handling" in b.lower() for b in bottlenecks)
    assert any("retry" in b.lower() for b in bottlenecks)


def test_identify_bottlenecks_multiple_issues(integration_analyzer):
    """Test bottleneck identification when integration point has multiple issues."""
    integration_points = [
        IntegrationPoint(
            point_id="INT-001",
            source_layer="Backend API",
            target_layer="Data Persistence",
            interface_type="PostgreSQL Query",
            data_flow_direction="Bidirectional",
            error_handling_present=True,
            retry_mechanism_present=True,
            issues=["Slow queries", "Missing indexes", "Connection pool exhaustion"]
        )
    ]
    
    data_flows = []
    
    bottlenecks = integration_analyzer.identify_bottlenecks(integration_points, data_flows)
    
    # Should identify bottleneck due to multiple issues
    assert len(bottlenecks) > 0
    assert any("multiple issues" in b.lower() for b in bottlenecks)


def test_identify_bottlenecks_flow_failure_points(integration_analyzer):
    """Test bottleneck identification from data flow failure points."""
    integration_points = []
    
    data_flows = [
        DataFlowTrace(
            flow_name="Test Flow",
            layers_traversed=["Frontend", "Backend API"],
            integration_points=[],
            bottlenecks=["Slow API", "No caching", "Large payload"],
            failure_points=["Missing layer: AI Reasoning", "Database timeout"],
            total_latency_estimate=None
        )
    ]
    
    bottlenecks = integration_analyzer.identify_bottlenecks(integration_points, data_flows)
    
    # Should identify bottlenecks from flow failure points
    assert len(bottlenecks) > 0
    assert any("failure points" in b.lower() for b in bottlenecks)


def test_analyze_integration_points_complete(integration_analyzer, sample_layer_results):
    """Test complete integration analysis workflow."""
    result = integration_analyzer.analyze_integration_points(sample_layer_results)
    
    # Should return IntegrationAnalysisResult
    assert isinstance(result, IntegrationAnalysisResult)
    
    # Should have integration points
    assert len(result.integration_points) > 0
    
    # Should have data flows
    assert len(result.data_flows) > 0
    
    # Should have timestamp
    assert result.timestamp is not None
    
    # Issues should be collected from integration points
    assert isinstance(result.issues, list)


def test_integration_point_ids_unique(integration_analyzer, sample_layer_results):
    """Test that integration point IDs are unique."""
    integration_points = integration_analyzer.identify_integration_points(sample_layer_results)
    
    point_ids = [p.point_id for p in integration_points]
    
    # All IDs should be unique
    assert len(point_ids) == len(set(point_ids))
    
    # IDs should follow format INT-XXX
    assert all(p.startswith("INT-") for p in point_ids)


def test_data_flow_trace_layer_order(integration_analyzer, sample_layer_results):
    """Test that data flow traces maintain proper layer order."""
    integration_points = integration_analyzer.identify_integration_points(sample_layer_results)
    data_flows = integration_analyzer.evaluate_data_flow(sample_layer_results, integration_points)
    
    for flow in data_flows:
        # Each flow should have at least 2 layers
        assert len(flow.layers_traversed) >= 2
        
        # Layers should be from the available layer results
        for layer in flow.layers_traversed:
            assert layer in sample_layer_results


def test_assess_llm_error_handling_with_fallback(integration_analyzer, sample_layer_results):
    """Test LLM error handling assessment when fallback is implemented."""
    integration_point = IntegrationPoint(
        point_id="INT-001",
        source_layer="Backend API",
        target_layer="AI Reasoning",
        interface_type="LLM API",
        data_flow_direction="Bidirectional",
        error_handling_present=False,
        retry_mechanism_present=False,
        issues=[]
    )
    
    integration_analyzer.assess_error_handling(integration_point, sample_layer_results)
    
    # AI Reasoning layer has fallback capability, so retry should be detected
    assert integration_point.retry_mechanism_present is True


def test_bottleneck_deduplication(integration_analyzer):
    """Test that bottlenecks are deduplicated."""
    integration_points = [
        IntegrationPoint(
            point_id="INT-001",
            source_layer="Frontend",
            target_layer="Backend API",
            interface_type="REST API",
            data_flow_direction="Bidirectional",
            error_handling_present=False,
            retry_mechanism_present=False,
            issues=[]
        ),
        IntegrationPoint(
            point_id="INT-002",
            source_layer="Frontend",
            target_layer="Backend API",
            interface_type="WebSocket",
            data_flow_direction="Bidirectional",
            error_handling_present=False,
            retry_mechanism_present=False,
            issues=[]
        )
    ]
    
    data_flows = []
    
    bottlenecks = integration_analyzer.identify_bottlenecks(integration_points, data_flows)
    
    # Should have unique bottlenecks (no duplicates)
    assert len(bottlenecks) == len(set(bottlenecks))
