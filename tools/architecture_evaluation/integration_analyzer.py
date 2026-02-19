"""
Integration analyzer for evaluating cross-layer integration points.

This module provides the IntegrationAnalyzer class which analyzes integration
points between architectural layers, traces data flows, and identifies
integration issues.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import (
    LayerAnalysisResult,
    IntegrationPoint,
    DataFlowTrace,
    IntegrationAnalysisResult
)


class IntegrationAnalyzer:
    """
    Analyzes integration points between architectural layers.
    
    This class evaluates interfaces between layers (Frontend-Backend,
    Backend-Data, Backend-AI, Backend-Integration), assesses error handling,
    traces data flows, and identifies bottlenecks.
    """
    
    def __init__(self):
        """Initialize the integration analyzer."""
        self.integration_point_counter = 0
    
    def analyze_integration_points(
        self,
        layer_results: Dict[str, LayerAnalysisResult]
    ) -> IntegrationAnalysisResult:
        """
        Analyze integration between layers.
        
        Args:
            layer_results: Analysis results for all layers
            
        Returns:
            IntegrationAnalysisResult with integration issues
        """
        integration_points = self.identify_integration_points(layer_results)
        
        # Assess error handling for each integration point
        for point in integration_points:
            self.assess_error_handling(point, layer_results)
        
        # Trace key data flows
        data_flows = self.evaluate_data_flow(layer_results, integration_points)
        
        # Identify bottlenecks across all integration points
        bottlenecks = self.identify_bottlenecks(integration_points, data_flows)
        
        # Collect all issues
        issues = []
        for point in integration_points:
            issues.extend(point.issues)
        
        # Add bottleneck issues
        for bottleneck in bottlenecks:
            if bottleneck not in issues:
                issues.append(bottleneck)
        
        return IntegrationAnalysisResult(
            integration_points=integration_points,
            data_flows=data_flows,
            issues=issues,
            timestamp=datetime.now()
        )
    
    def identify_integration_points(
        self,
        layer_results: Dict[str, LayerAnalysisResult]
    ) -> List[IntegrationPoint]:
        """
        Find all layer interfaces.
        
        Identifies integration points between:
        - Frontend and Backend API
        - Backend API and Data Persistence
        - Backend API and AI Reasoning
        - Backend API and Integration
        
        Args:
            layer_results: Analysis results for all layers
            
        Returns:
            List of IntegrationPoint objects
        """
        integration_points = []
        
        # Frontend <-> Backend API integration points
        if "Frontend" in layer_results and "Backend API" in layer_results:
            # REST API integration
            integration_points.append(self._create_integration_point(
                source_layer="Frontend",
                target_layer="Backend API",
                interface_type="REST API",
                data_flow_direction="Bidirectional",
                layer_results=layer_results
            ))
            
            # WebSocket integration
            integration_points.append(self._create_integration_point(
                source_layer="Frontend",
                target_layer="Backend API",
                interface_type="WebSocket",
                data_flow_direction="Bidirectional",
                layer_results=layer_results
            ))
        
        # Backend API <-> Data Persistence integration points
        if "Backend API" in layer_results and "Data Persistence" in layer_results:
            # PostgreSQL integration
            integration_points.append(self._create_integration_point(
                source_layer="Backend API",
                target_layer="Data Persistence",
                interface_type="PostgreSQL Query",
                data_flow_direction="Bidirectional",
                layer_results=layer_results
            ))
            
            # Neo4j integration
            integration_points.append(self._create_integration_point(
                source_layer="Backend API",
                target_layer="Data Persistence",
                interface_type="Neo4j Query",
                data_flow_direction="Bidirectional",
                layer_results=layer_results
            ))
            
            # Redis integration
            integration_points.append(self._create_integration_point(
                source_layer="Backend API",
                target_layer="Data Persistence",
                interface_type="Redis Cache",
                data_flow_direction="Bidirectional",
                layer_results=layer_results
            ))
        
        # Backend API <-> AI Reasoning integration points
        if "Backend API" in layer_results and "AI Reasoning" in layer_results:
            # LLM API integration
            integration_points.append(self._create_integration_point(
                source_layer="Backend API",
                target_layer="AI Reasoning",
                interface_type="LLM API",
                data_flow_direction="Bidirectional",
                layer_results=layer_results
            ))
        
        # Backend API <-> Integration Layer integration points
        if "Backend API" in layer_results and "Integration" in layer_results:
            # GitHub API integration
            integration_points.append(self._create_integration_point(
                source_layer="Backend API",
                target_layer="Integration",
                interface_type="GitHub API",
                data_flow_direction="Bidirectional",
                layer_results=layer_results
            ))
            
            # OAuth integration
            integration_points.append(self._create_integration_point(
                source_layer="Backend API",
                target_layer="Integration",
                interface_type="OAuth 2.0",
                data_flow_direction="Bidirectional",
                layer_results=layer_results
            ))
        
        return integration_points
    
    def _create_integration_point(
        self,
        source_layer: str,
        target_layer: str,
        interface_type: str,
        data_flow_direction: str,
        layer_results: Dict[str, LayerAnalysisResult]
    ) -> IntegrationPoint:
        """
        Create an integration point with initial assessment.
        
        Args:
            source_layer: Source layer name
            target_layer: Target layer name
            interface_type: Type of interface
            data_flow_direction: Direction of data flow
            layer_results: Layer analysis results for context
            
        Returns:
            IntegrationPoint object
        """
        self.integration_point_counter += 1
        point_id = f"INT-{self.integration_point_counter:03d}"
        
        # Initial assessment - will be updated by assess_error_handling
        return IntegrationPoint(
            point_id=point_id,
            source_layer=source_layer,
            target_layer=target_layer,
            interface_type=interface_type,
            data_flow_direction=data_flow_direction,
            error_handling_present=False,  # Will be assessed
            retry_mechanism_present=False,  # Will be assessed
            issues=[]
        )
    
    def assess_error_handling(
        self,
        integration_point: IntegrationPoint,
        layer_results: Dict[str, LayerAnalysisResult]
    ) -> None:
        """
        Check error handling at boundaries.
        
        Assesses whether the integration point has:
        - Error handling mechanisms
        - Retry logic
        - Timeout handling
        - Circuit breakers
        
        Updates the integration_point object in place.
        
        Args:
            integration_point: The integration point to assess
            layer_results: Layer analysis results for context
        """
        # Check for error handling based on interface type
        interface_type = integration_point.interface_type
        source_layer = integration_point.source_layer
        target_layer = integration_point.target_layer
        
        # Get layer results for source and target
        source_result = layer_results.get(source_layer)
        target_result = layer_results.get(target_layer)
        
        # Assess error handling based on interface type
        if interface_type in ["REST API", "WebSocket"]:
            # Check for HTTP error handling, timeout configuration
            error_handling = self._check_api_error_handling(source_result, target_result)
            integration_point.error_handling_present = error_handling['has_error_handling']
            integration_point.retry_mechanism_present = error_handling['has_retry']
            
            if not error_handling['has_error_handling']:
                integration_point.issues.append(
                    f"Missing error handling for {interface_type} between {source_layer} and {target_layer}"
                )
            if not error_handling['has_retry']:
                integration_point.issues.append(
                    f"Missing retry mechanism for {interface_type} between {source_layer} and {target_layer}"
                )
        
        elif interface_type in ["PostgreSQL Query", "Neo4j Query", "Redis Cache"]:
            # Check for database error handling, connection pooling
            error_handling = self._check_database_error_handling(source_result, target_result)
            integration_point.error_handling_present = error_handling['has_error_handling']
            integration_point.retry_mechanism_present = error_handling['has_retry']
            
            if not error_handling['has_error_handling']:
                integration_point.issues.append(
                    f"Missing database error handling for {interface_type}"
                )
            if not error_handling['has_retry']:
                integration_point.issues.append(
                    f"Missing connection retry logic for {interface_type}"
                )
        
        elif interface_type == "LLM API":
            # Check for LLM-specific error handling (rate limits, timeouts, fallbacks)
            error_handling = self._check_llm_error_handling(source_result, target_result)
            integration_point.error_handling_present = error_handling['has_error_handling']
            integration_point.retry_mechanism_present = error_handling['has_retry']
            
            if not error_handling['has_error_handling']:
                integration_point.issues.append(
                    f"Missing LLM error handling (rate limits, timeouts)"
                )
            if not error_handling['has_retry']:
                integration_point.issues.append(
                    f"Missing LLM retry/fallback mechanism"
                )
        
        elif interface_type in ["GitHub API", "OAuth 2.0"]:
            # Check for external API error handling
            error_handling = self._check_external_api_error_handling(source_result, target_result)
            integration_point.error_handling_present = error_handling['has_error_handling']
            integration_point.retry_mechanism_present = error_handling['has_retry']
            
            if not error_handling['has_error_handling']:
                integration_point.issues.append(
                    f"Missing error handling for {interface_type}"
                )
            if not error_handling['has_retry']:
                integration_point.issues.append(
                    f"Missing retry mechanism for {interface_type}"
                )
    
    def _check_api_error_handling(
        self,
        source_result: Optional[LayerAnalysisResult],
        target_result: Optional[LayerAnalysisResult]
    ) -> Dict[str, bool]:
        """Check API error handling capabilities."""
        has_error_handling = False
        has_retry = False
        
        # Check source layer for error handling patterns
        if source_result:
            # Look for error handling in strengths or implemented capabilities
            for strength in source_result.strengths:
                if any(keyword in strength.lower() for keyword in ['error', 'exception', 'try', 'catch']):
                    has_error_handling = True
                if any(keyword in strength.lower() for keyword in ['retry', 'backoff', 'circuit']):
                    has_retry = True
        
        # Check target layer for error handling patterns
        if target_result:
            for strength in target_result.strengths:
                if any(keyword in strength.lower() for keyword in ['error', 'exception', 'middleware']):
                    has_error_handling = True
                if any(keyword in strength.lower() for keyword in ['retry', 'timeout']):
                    has_retry = True
        
        # If we can't determine from analysis, assume partial implementation
        # This is conservative - real implementation would do deeper code analysis
        if not has_error_handling and source_result and target_result:
            # If both layers exist and have reasonable completeness, assume basic error handling
            if source_result.completeness_score > 0.5 and target_result.completeness_score > 0.5:
                has_error_handling = True
        
        return {
            'has_error_handling': has_error_handling,
            'has_retry': has_retry
        }
    
    def _check_database_error_handling(
        self,
        source_result: Optional[LayerAnalysisResult],
        target_result: Optional[LayerAnalysisResult]
    ) -> Dict[str, bool]:
        """Check database error handling capabilities."""
        has_error_handling = False
        has_retry = False
        
        # Check for database-specific error handling
        if target_result:
            for strength in target_result.strengths:
                if any(keyword in strength.lower() for keyword in ['connection', 'pool', 'transaction']):
                    has_error_handling = True
                if any(keyword in strength.lower() for keyword in ['retry', 'reconnect']):
                    has_retry = True
        
        # Check source layer for database client error handling
        if source_result:
            for strength in source_result.strengths:
                if any(keyword in strength.lower() for keyword in ['database', 'query', 'transaction']):
                    has_error_handling = True
        
        return {
            'has_error_handling': has_error_handling,
            'has_retry': has_retry
        }
    
    def _check_llm_error_handling(
        self,
        source_result: Optional[LayerAnalysisResult],
        target_result: Optional[LayerAnalysisResult]
    ) -> Dict[str, bool]:
        """Check LLM API error handling capabilities."""
        has_error_handling = False
        has_retry = False
        
        # Check AI Reasoning layer for error handling
        if target_result:
            for strength in target_result.strengths:
                if any(keyword in strength.lower() for keyword in ['error', 'timeout', 'rate limit']):
                    has_error_handling = True
                if any(keyword in strength.lower() for keyword in ['retry', 'fallback', 'circuit']):
                    has_retry = True
            
            # Check for fallback mechanisms in capabilities
            for cap in target_result.implemented_capabilities:
                if 'fallback' in cap.name.lower():
                    has_retry = True
        
        return {
            'has_error_handling': has_error_handling,
            'has_retry': has_retry
        }
    
    def _check_external_api_error_handling(
        self,
        source_result: Optional[LayerAnalysisResult],
        target_result: Optional[LayerAnalysisResult]
    ) -> Dict[str, bool]:
        """Check external API error handling capabilities."""
        has_error_handling = False
        has_retry = False
        
        # Check Integration layer for error handling
        if target_result:
            for strength in target_result.strengths:
                if any(keyword in strength.lower() for keyword in ['error', 'webhook', 'signature']):
                    has_error_handling = True
                if any(keyword in strength.lower() for keyword in ['retry', 'backoff', 'queue']):
                    has_retry = True
        
        return {
            'has_error_handling': has_error_handling,
            'has_retry': has_retry
        }
    
    def evaluate_data_flow(
        self,
        layer_results: Dict[str, LayerAnalysisResult],
        integration_points: List[IntegrationPoint]
    ) -> List[DataFlowTrace]:
        """
        Trace end-to-end flows.
        
        Traces key data flows through the system:
        - PR Review Request: Frontend → Backend → AI → Data → Backend → Frontend
        - Authentication: Frontend → Backend → Data
        - Webhook Processing: Integration → Backend → Data
        
        Args:
            layer_results: Layer analysis results
            integration_points: Identified integration points
            
        Returns:
            List of DataFlowTrace objects
        """
        data_flows = []
        
        # Trace 1: PR Review Request Flow
        pr_review_flow = self._trace_pr_review_flow(layer_results, integration_points)
        if pr_review_flow:
            data_flows.append(pr_review_flow)
        
        # Trace 2: Authentication Flow
        auth_flow = self._trace_authentication_flow(layer_results, integration_points)
        if auth_flow:
            data_flows.append(auth_flow)
        
        # Trace 3: Webhook Processing Flow
        webhook_flow = self._trace_webhook_flow(layer_results, integration_points)
        if webhook_flow:
            data_flows.append(webhook_flow)
        
        return data_flows
    
    def _trace_pr_review_flow(
        self,
        layer_results: Dict[str, LayerAnalysisResult],
        integration_points: List[IntegrationPoint]
    ) -> Optional[DataFlowTrace]:
        """Trace PR review request flow."""
        flow_name = "PR Review Request"
        layers_traversed = []
        flow_integration_points = []
        bottlenecks = []
        failure_points = []
        
        # Expected flow: Frontend → Backend API → AI Reasoning → Data Persistence → Backend API → Frontend
        expected_layers = ["Frontend", "Backend API", "AI Reasoning", "Data Persistence"]
        
        # Check which layers exist
        for layer in expected_layers:
            if layer in layer_results:
                layers_traversed.append(layer)
            else:
                failure_points.append(f"Missing layer: {layer}")
        
        # If we don't have at least Frontend and Backend, flow is not possible
        if "Frontend" not in layers_traversed or "Backend API" not in layers_traversed:
            return None
        
        # Find relevant integration points
        for point in integration_points:
            if (point.source_layer in layers_traversed and 
                point.target_layer in layers_traversed):
                # Check if this point is part of the PR review flow
                if (point.interface_type in ["REST API", "LLM API", "PostgreSQL Query", "Neo4j Query"]):
                    flow_integration_points.append(point)
                    
                    # Check for issues that could be bottlenecks
                    if point.issues:
                        bottlenecks.extend([
                            f"{point.interface_type}: {issue}" 
                            for issue in point.issues
                        ])
        
        # Identify potential bottlenecks based on layer completeness
        for layer in layers_traversed:
            result = layer_results[layer]
            if result.completeness_score < 0.7:
                bottlenecks.append(
                    f"{layer} layer incomplete ({result.completeness_score:.0%}) - may cause delays"
                )
        
        # Check for AI layer bottlenecks specifically
        if "AI Reasoning" in layer_results:
            ai_result = layer_results["AI Reasoning"]
            # AI calls are typically the slowest part
            bottlenecks.append(
                f"AI Reasoning layer - LLM API calls are typically high latency (2-10s)"
            )
        
        return DataFlowTrace(
            flow_name=flow_name,
            layers_traversed=layers_traversed,
            integration_points=flow_integration_points,
            bottlenecks=bottlenecks,
            failure_points=failure_points,
            total_latency_estimate=None  # Would require performance metrics
        )
    
    def _trace_authentication_flow(
        self,
        layer_results: Dict[str, LayerAnalysisResult],
        integration_points: List[IntegrationPoint]
    ) -> Optional[DataFlowTrace]:
        """Trace authentication flow."""
        flow_name = "Authentication"
        layers_traversed = []
        flow_integration_points = []
        bottlenecks = []
        failure_points = []
        
        # Expected flow: Frontend → Backend API → Data Persistence
        expected_layers = ["Frontend", "Backend API", "Data Persistence"]
        
        # Check which layers exist
        for layer in expected_layers:
            if layer in layer_results:
                layers_traversed.append(layer)
            else:
                failure_points.append(f"Missing layer: {layer}")
        
        # If we don't have the core layers, flow is not possible
        if len(layers_traversed) < 2:
            return None
        
        # Find relevant integration points
        for point in integration_points:
            if (point.source_layer in layers_traversed and 
                point.target_layer in layers_traversed):
                # Check if this point is part of auth flow
                if point.interface_type in ["REST API", "PostgreSQL Query", "OAuth 2.0"]:
                    flow_integration_points.append(point)
                    
                    if point.issues:
                        bottlenecks.extend([
                            f"{point.interface_type}: {issue}" 
                            for issue in point.issues
                        ])
        
        # Check for security-related gaps that could be failure points
        for layer in layers_traversed:
            result = layer_results[layer]
            for gap in result.gaps:
                if any(keyword in gap.category.lower() for keyword in ['auth', 'security', 'jwt']):
                    failure_points.append(
                        f"{layer}: {gap.description}"
                    )
        
        return DataFlowTrace(
            flow_name=flow_name,
            layers_traversed=layers_traversed,
            integration_points=flow_integration_points,
            bottlenecks=bottlenecks,
            failure_points=failure_points,
            total_latency_estimate=None
        )
    
    def _trace_webhook_flow(
        self,
        layer_results: Dict[str, LayerAnalysisResult],
        integration_points: List[IntegrationPoint]
    ) -> Optional[DataFlowTrace]:
        """Trace webhook processing flow."""
        flow_name = "Webhook Processing"
        layers_traversed = []
        flow_integration_points = []
        bottlenecks = []
        failure_points = []
        
        # Expected flow: Integration → Backend API → Data Persistence
        expected_layers = ["Integration", "Backend API", "Data Persistence"]
        
        # Check which layers exist
        for layer in expected_layers:
            if layer in layer_results:
                layers_traversed.append(layer)
            else:
                failure_points.append(f"Missing layer: {layer}")
        
        # If we don't have Integration layer, this flow doesn't exist
        if "Integration" not in layers_traversed:
            return None
        
        # Find relevant integration points
        for point in integration_points:
            if (point.source_layer in layers_traversed and 
                point.target_layer in layers_traversed):
                # Check if this point is part of webhook flow
                if point.interface_type in ["GitHub API", "PostgreSQL Query", "Neo4j Query"]:
                    flow_integration_points.append(point)
                    
                    if point.issues:
                        bottlenecks.extend([
                            f"{point.interface_type}: {issue}" 
                            for issue in point.issues
                        ])
        
        # Webhook processing should be fast - check for potential delays
        if "Integration" in layer_results:
            integration_result = layer_results["Integration"]
            if integration_result.completeness_score < 0.8:
                bottlenecks.append(
                    f"Integration layer incomplete - webhook processing may be unreliable"
                )
        
        return DataFlowTrace(
            flow_name=flow_name,
            layers_traversed=layers_traversed,
            integration_points=flow_integration_points,
            bottlenecks=bottlenecks,
            failure_points=failure_points,
            total_latency_estimate=None
        )
    
    def identify_bottlenecks(
        self,
        integration_points: List[IntegrationPoint],
        data_flows: List[DataFlowTrace]
    ) -> List[str]:
        """
        Find performance bottlenecks.
        
        Identifies bottlenecks by analyzing:
        - Integration points with many issues
        - Missing error handling or retry mechanisms
        - Data flows with multiple failure points
        - Layers with low completeness scores in critical paths
        
        Args:
            integration_points: All integration points
            data_flows: All traced data flows
            
        Returns:
            List of bottleneck descriptions
        """
        bottlenecks = []
        
        # Analyze integration points for bottlenecks
        for point in integration_points:
            # Points without error handling are bottlenecks
            if not point.error_handling_present:
                bottlenecks.append(
                    f"Bottleneck: {point.interface_type} between {point.source_layer} and "
                    f"{point.target_layer} lacks error handling - failures will cascade"
                )
            
            # Points without retry mechanisms are bottlenecks
            if not point.retry_mechanism_present:
                bottlenecks.append(
                    f"Bottleneck: {point.interface_type} between {point.source_layer} and "
                    f"{point.target_layer} lacks retry mechanism - transient failures will cause errors"
                )
            
            # Points with multiple issues are bottlenecks
            if len(point.issues) >= 2:
                bottlenecks.append(
                    f"Bottleneck: {point.interface_type} has multiple issues - "
                    f"high risk of integration failures"
                )
        
        # Analyze data flows for bottlenecks
        for flow in data_flows:
            # Flows with many failure points are bottlenecks
            if len(flow.failure_points) > 0:
                bottlenecks.append(
                    f"Bottleneck: {flow.flow_name} flow has {len(flow.failure_points)} "
                    f"failure points - reliability at risk"
                )
            
            # Flows with many bottlenecks are critical
            if len(flow.bottlenecks) >= 3:
                bottlenecks.append(
                    f"Critical bottleneck: {flow.flow_name} flow has {len(flow.bottlenecks)} "
                    f"identified bottlenecks - performance will be severely impacted"
                )
        
        # Deduplicate bottlenecks
        return list(set(bottlenecks))
