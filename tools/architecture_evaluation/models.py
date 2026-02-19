"""
Data models for architecture evaluation.

This module defines the core data structures used throughout the architecture
evaluation system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any


@dataclass
class Capability:
    """Represents a capability that a layer should provide."""
    name: str
    description: str
    category: str  # e.g., "Authentication", "Data Storage", "UI"
    required: bool
    verification_method: str  # How to verify implementation


@dataclass
class PartialCapability:
    """Represents a partially implemented capability."""
    capability: Capability
    implemented_aspects: List[str]
    missing_aspects: List[str]
    completeness_percentage: float


@dataclass
class Gap:
    """Represents a gap in implementation."""
    gap_id: str
    layer: str
    category: str
    description: str
    expected_state: str
    current_state: str
    impact: str  # "Critical", "High", "Medium", "Low"
    affected_requirements: List[str]
    related_capabilities: List[str]


@dataclass
class LayerAnalysisResult:
    """Result of analyzing a single layer."""
    layer_name: str
    completeness_score: float  # 0.0 to 1.0
    capabilities_assessed: List[Capability]
    implemented_capabilities: List[Capability]
    missing_capabilities: List[Capability]
    partial_capabilities: List[PartialCapability]
    gaps: List[Gap]
    strengths: List[str]
    timestamp: datetime


@dataclass
class IntegrationPoint:
    """Represents an integration between layers."""
    point_id: str
    source_layer: str
    target_layer: str
    interface_type: str  # "REST API", "WebSocket", "Database Query"
    data_flow_direction: str  # "Unidirectional", "Bidirectional"
    error_handling_present: bool
    retry_mechanism_present: bool
    issues: List[str]


@dataclass
class DataFlowTrace:
    """Represents a traced data flow across layers."""
    flow_name: str
    layers_traversed: List[str]
    integration_points: List[IntegrationPoint]
    bottlenecks: List[str]
    failure_points: List[str]
    total_latency_estimate: Optional[float]


@dataclass
class IntegrationAnalysisResult:
    """Result of analyzing integration between layers."""
    integration_points: List[IntegrationPoint]
    data_flows: List[DataFlowTrace]
    issues: List[str]
    timestamp: datetime


@dataclass
class SecurityFinding:
    """Represents a security issue or gap."""
    finding_id: str
    layer: str
    severity: str  # "Critical", "High", "Medium", "Low"
    category: str  # "Authentication", "Authorization", "Data Protection"
    description: str
    current_state: str
    recommended_fix: str
    references: List[str]  # Links to security standards


@dataclass
class SecurityEvaluationResult:
    """Result of security evaluation across layers."""
    findings: List[SecurityFinding]
    layers_assessed: List[str]
    timestamp: datetime


@dataclass
class PerformanceIssue:
    """Represents a performance or scalability issue."""
    issue_id: str
    layer: str
    severity: str
    category: str  # "Scalability", "Latency", "Resource Usage"
    description: str
    impact_estimate: str
    recommended_fix: str


@dataclass
class PerformanceEvaluationResult:
    """Result of performance evaluation across layers."""
    issues: List[PerformanceIssue]
    layers_assessed: List[str]
    timestamp: datetime


@dataclass
class TestingGap:
    """Represents a gap in testing coverage."""
    gap_id: str
    layer: str
    component: str
    test_type: str  # "Unit", "Integration", "Property-Based", "E2E"
    current_coverage: Optional[float]
    target_coverage: float
    missing_test_scenarios: List[str]


@dataclass
class TestingEvaluationResult:
    """Result of testing evaluation across layers."""
    gaps: List[TestingGap]
    layers_assessed: List[str]
    timestamp: datetime


@dataclass
class Improvement:
    """Represents a prioritized improvement recommendation."""
    improvement_id: str
    title: str
    description: str
    priority: str  # "Critical", "High", "Medium", "Low"
    category: str  # "Security", "Performance", "Testing", "Feature Gap"
    affected_layers: List[str]
    current_state: str
    desired_state: str
    implementation_guidance: str
    acceptance_criteria: List[str]
    estimated_effort: str  # "Small", "Medium", "Large"
    dependencies: List[str] = field(default_factory=list)  # IDs of other improvements
    impact_metrics: Dict[str, str] = field(default_factory=dict)


@dataclass
class EvaluationReport:
    """Complete evaluation report."""
    report_id: str
    generated_at: datetime
    executive_summary: str
    layer_results: Dict[str, LayerAnalysisResult]
    integration_analysis: IntegrationAnalysisResult
    security_evaluation: SecurityEvaluationResult
    performance_evaluation: PerformanceEvaluationResult
    testing_evaluation: TestingEvaluationResult
    improvements: List[Improvement]
    overall_completeness_score: float
    priority_improvements: List[Improvement]  # Critical and High only
    diagrams: Dict[str, str] = field(default_factory=dict)  # Diagram name -> Mermaid/SVG content
