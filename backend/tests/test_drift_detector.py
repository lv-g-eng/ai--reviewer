"""
Unit Tests for Architectural Drift Detector

Tests baseline creation, drift detection, metrics calculation, and severity assignment.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from app.services.architecture_analyzer.baseline import (
    BaselineManager,
    ArchitectureBaseline
)
from app.services.architecture_analyzer.drift_detector import (
    DriftDetector,
    DriftSeverity,
    DriftMetrics,
    DriftResult,
    DriftDetail
)


# Test Fixtures

@pytest.fixture
def temp_storage_path(tmp_path):
    """Create temporary storage path for baselines"""
    storage_path = tmp_path / "baselines"
    storage_path.mkdir()
    return str(storage_path)


@pytest.fixture
def baseline_manager(temp_storage_path):
    """Create BaselineManager with temporary storage"""
    return BaselineManager(storage_path=temp_storage_path)


@pytest.fixture
def drift_detector(baseline_manager):
    """Create DriftDetector with the same baseline manager instance"""
    return DriftDetector(baseline_manager=baseline_manager)


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
                "file_path": "src/utils.py",
                "complexity": 5,
                "lines_of_code": 20
            }
        },
        {
            "node_id": 2,
            "labels": ["CodeEntity", "Class"],
            "properties": {
                "name": "UserService",
                "type": "class",
                "file_path": "src/services.py",
                "complexity": 10,
                "lines_of_code": 50
            }
        },
        {
            "node_id": 3,
            "labels": ["CodeEntity", "Function"],
            "properties": {
                "name": "validate_input",
                "type": "function",
                "file_path": "src/validators.py",
                "complexity": 3,
                "lines_of_code": 15
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
            "target_name": "UserService",
            "rel_type": "CALLS",
            "properties": {"weight": 1}
        },
        {
            "rel_id": 2,
            "source_id": 2,
            "target_id": 3,
            "source_name": "UserService",
            "target_name": "validate_input",
            "rel_type": "DEPENDS_ON",
            "properties": {"weight": 1}
        }
    ]


@pytest.fixture
def sample_baseline(sample_nodes, sample_relationships, baseline_manager):
    """Create a sample baseline with correct ID"""
    # Generate the correct baseline ID using the manager's method
    baseline_id = baseline_manager._generate_baseline_id("test_project", "v1.0.0")
    
    return ArchitectureBaseline(
        baseline_id=baseline_id,
        project_id="test_project",
        version="v1.0.0",
        timestamp="2024-01-01T00:00:00",
        nodes=sample_nodes,
        relationships=sample_relationships,
        metrics={
            "total_nodes": 3,
            "total_relationships": 2,
            "node_types": {"function": 2, "class": 1},
            "relationship_types": {"CALLS": 1, "DEPENDS_ON": 1},
            "total_complexity": 18,
            "average_complexity": 6.0,
            "total_lines_of_code": 85
        },
        metadata={
            "description": "Test baseline",
            "node_count": 3,
            "relationship_count": 2
        }
    )


# BaselineManager Tests

class TestBaselineManager:
    """Tests for BaselineManager"""
    
    @pytest.mark.asyncio
    async def test_create_baseline(self, baseline_manager, sample_nodes, sample_relationships):
        """Test baseline creation"""
        # Mock Neo4j driver
        mock_driver = AsyncMock()
        mock_session = AsyncMock()
        mock_driver.session.return_value.__aenter__.return_value = mock_session
        
        # Mock node query
        mock_node_result = AsyncMock()
        mock_node_result.__aiter__.return_value = iter([
            {"node_id": n["node_id"], "labels": n["labels"], "properties": n["properties"]}
            for n in sample_nodes
        ])
        mock_session.run.return_value = mock_node_result
        
        with patch('app.services.architecture_analyzer.baseline.get_neo4j_driver', return_value=mock_driver):
            # Override capture methods to return sample data
            baseline_manager._capture_nodes = AsyncMock(return_value=sample_nodes)
            baseline_manager._capture_relationships = AsyncMock(return_value=sample_relationships)
            
            baseline = await baseline_manager.create_baseline(
                project_id="test_project",
                version="v1.0.0",
                description="Test baseline"
            )
            
            assert baseline.project_id == "test_project"
            assert baseline.version == "v1.0.0"
            assert len(baseline.nodes) == 3
            assert len(baseline.relationships) == 2
            assert baseline.metrics["total_nodes"] == 3
            assert baseline.metrics["total_relationships"] == 2
    
    @pytest.mark.asyncio
    async def test_store_and_load_baseline(self, baseline_manager, sample_baseline):
        """Test storing and loading a baseline"""
        # Store baseline
        await baseline_manager._store_baseline(sample_baseline)
        
        # Load baseline
        loaded = await baseline_manager._load_baseline_by_id(sample_baseline.baseline_id)
        
        assert loaded is not None
        assert loaded.baseline_id == sample_baseline.baseline_id
        assert loaded.project_id == sample_baseline.project_id
        assert loaded.version == sample_baseline.version
        assert len(loaded.nodes) == len(sample_baseline.nodes)
        assert len(loaded.relationships) == len(sample_baseline.relationships)
    
    @pytest.mark.asyncio
    async def test_list_baselines(self, baseline_manager, sample_baseline):
        """Test listing baselines for a project"""
        # Store multiple baselines
        await baseline_manager._store_baseline(sample_baseline)
        
        baseline2 = ArchitectureBaseline(
            baseline_id="test_project_v2.0.0_def456",
            project_id="test_project",
            version="v2.0.0",
            timestamp="2024-01-02T00:00:00",
            nodes=sample_baseline.nodes,
            relationships=sample_baseline.relationships,
            metrics=sample_baseline.metrics,
            metadata=sample_baseline.metadata
        )
        await baseline_manager._store_baseline(baseline2)
        
        # List baselines
        baselines = await baseline_manager.list_baselines("test_project")
        
        assert len(baselines) == 2
        assert baselines[0]["version"] == "v2.0.0"  # Newest first
        assert baselines[1]["version"] == "v1.0.0"
    
    @pytest.mark.asyncio
    async def test_delete_baseline(self, baseline_manager, sample_baseline):
        """Test deleting a baseline"""
        # Store baseline
        await baseline_manager._store_baseline(sample_baseline)
        
        # Verify it exists
        loaded = await baseline_manager._load_baseline_by_id(sample_baseline.baseline_id)
        assert loaded is not None
        
        # Delete baseline
        result = await baseline_manager.delete_baseline(sample_baseline.baseline_id)
        assert result is True
        
        # Verify it's gone
        loaded = await baseline_manager._load_baseline_by_id(sample_baseline.baseline_id)
        assert loaded is None
    
    @pytest.mark.asyncio
    async def test_get_latest_baseline(self, baseline_manager, sample_baseline):
        """Test getting the latest baseline"""
        # Store multiple baselines
        await baseline_manager._store_baseline(sample_baseline)
        
        baseline2 = ArchitectureBaseline(
            baseline_id="test_project_v2.0.0_def456",
            project_id="test_project",
            version="v2.0.0",
            timestamp="2024-01-02T00:00:00",
            nodes=sample_baseline.nodes,
            relationships=sample_baseline.relationships,
            metrics=sample_baseline.metrics,
            metadata=sample_baseline.metadata
        )
        await baseline_manager._store_baseline(baseline2)
        
        # Get latest
        latest = await baseline_manager._get_latest_baseline("test_project")
        
        assert latest is not None
        assert latest.version == "v2.0.0"


# DriftDetector Tests

class TestDriftDetector:
    """Tests for DriftDetector"""
    
    @pytest.mark.asyncio
    async def test_detect_no_drift(self, drift_detector, baseline_manager, sample_baseline, sample_nodes, sample_relationships):
        """Test drift detection when there are no changes"""
        # Store baseline - ensure it's stored with the correct ID
        await baseline_manager._store_baseline(sample_baseline)
        
        # Verify baseline was stored
        loaded_baseline = await baseline_manager.get_baseline(
            project_id="test_project",
            version="v1.0.0"
        )
        assert loaded_baseline is not None, "Baseline should be stored"
        
        # Mock current state to be same as baseline
        mock_driver = AsyncMock()
        
        with patch('app.services.architecture_analyzer.drift_detector.get_neo4j_driver', return_value=mock_driver):
            drift_detector._get_current_nodes = AsyncMock(return_value=sample_nodes)
            drift_detector._get_current_relationships = AsyncMock(return_value=sample_relationships)
            
            result = await drift_detector.detect_drift(
                project_id="test_project",
                baseline_version="v1.0.0"
            )
            
            assert result.severity == DriftSeverity.LOW
            assert result.metrics.total_changes == 0
            assert result.metrics.drift_percentage == 0.0
            assert result.metrics.new_dependencies == 0
            assert result.metrics.removed_dependencies == 0
    
    @pytest.mark.asyncio
    async def test_detect_new_dependencies(self, drift_detector, baseline_manager, sample_baseline, sample_nodes, sample_relationships):
        """Test detection of new dependencies"""
        # Store baseline
        await baseline_manager._store_baseline(sample_baseline)
        
        # Add new relationship
        current_relationships = sample_relationships + [
            {
                "rel_id": 3,
                "source_id": 1,
                "target_id": 3,
                "source_name": "calculate_total",
                "target_name": "validate_input",
                "rel_type": "CALLS",
                "properties": {"weight": 1}
            }
        ]
        
        mock_driver = AsyncMock()
        
        with patch('app.services.architecture_analyzer.drift_detector.get_neo4j_driver', return_value=mock_driver):
            drift_detector._get_current_nodes = AsyncMock(return_value=sample_nodes)
            drift_detector._get_current_relationships = AsyncMock(return_value=current_relationships)
            
            result = await drift_detector.detect_drift(
                project_id="test_project",
                baseline_version="v1.0.0"
            )
            
            assert result.metrics.new_dependencies == 1
            assert result.metrics.total_changes == 1
            assert result.severity == DriftSeverity.MEDIUM  # 1/5 = 20% drift
            
            # Check details
            added_deps = [d for d in result.details if d.change_type == "added" and d.entity_type == "relationship"]
            assert len(added_deps) == 1
            assert "calculate_total" in added_deps[0].entity_name
            assert "validate_input" in added_deps[0].entity_name
    
    @pytest.mark.asyncio
    async def test_detect_removed_dependencies(self, drift_detector, baseline_manager, sample_baseline, sample_nodes, sample_relationships):
        """Test detection of removed dependencies"""
        # Store baseline
        await baseline_manager._store_baseline(sample_baseline)
        
        # Remove a relationship
        current_relationships = [sample_relationships[0]]  # Keep only first relationship
        
        mock_driver = AsyncMock()
        
        with patch('app.services.architecture_analyzer.drift_detector.get_neo4j_driver', return_value=mock_driver):
            drift_detector._get_current_nodes = AsyncMock(return_value=sample_nodes)
            drift_detector._get_current_relationships = AsyncMock(return_value=current_relationships)
            
            result = await drift_detector.detect_drift(
                project_id="test_project",
                baseline_version="v1.0.0"
            )
            
            assert result.metrics.removed_dependencies == 1
            assert result.metrics.total_changes == 1
            
            # Check details
            removed_deps = [d for d in result.details if d.change_type == "removed" and d.entity_type == "relationship"]
            assert len(removed_deps) == 1
    
    @pytest.mark.asyncio
    async def test_detect_new_nodes(self, drift_detector, baseline_manager, sample_baseline, sample_nodes, sample_relationships):
        """Test detection of new nodes"""
        # Store baseline
        await baseline_manager._store_baseline(sample_baseline)
        
        # Add new node
        current_nodes = sample_nodes + [
            {
                "node_id": 4,
                "labels": ["CodeEntity", "Function"],
                "properties": {
                    "name": "new_function",
                    "type": "function",
                    "file_path": "src/new_module.py",
                    "complexity": 2,
                    "lines_of_code": 10
                }
            }
        ]
        
        mock_driver = AsyncMock()
        
        with patch('app.services.architecture_analyzer.drift_detector.get_neo4j_driver', return_value=mock_driver):
            drift_detector._get_current_nodes = AsyncMock(return_value=current_nodes)
            drift_detector._get_current_relationships = AsyncMock(return_value=sample_relationships)
            
            result = await drift_detector.detect_drift(
                project_id="test_project",
                baseline_version="v1.0.0"
            )
            
            assert result.metrics.new_nodes == 1
            assert result.metrics.total_changes == 1
            
            # Check details
            added_nodes = [d for d in result.details if d.change_type == "added" and d.entity_type == "node"]
            assert len(added_nodes) == 1
            assert added_nodes[0].entity_name == "new_function"
    
    @pytest.mark.asyncio
    async def test_detect_complexity_changes(self, drift_detector, baseline_manager, sample_baseline, sample_nodes, sample_relationships):
        """Test detection of complexity changes"""
        # Store baseline
        await baseline_manager._store_baseline(sample_baseline)
        
        # Modify node complexity
        current_nodes = [
            {
                **sample_nodes[0],
                "properties": {
                    **sample_nodes[0]["properties"],
                    "complexity": 15  # Increased from 5
                }
            },
            sample_nodes[1],
            sample_nodes[2]
        ]
        
        mock_driver = AsyncMock()
        
        with patch('app.services.architecture_analyzer.drift_detector.get_neo4j_driver', return_value=mock_driver):
            drift_detector._get_current_nodes = AsyncMock(return_value=current_nodes)
            drift_detector._get_current_relationships = AsyncMock(return_value=sample_relationships)
            
            result = await drift_detector.detect_drift(
                project_id="test_project",
                baseline_version="v1.0.0"
            )
            
            assert result.metrics.modified_nodes == 1
            assert result.metrics.complexity_delta == 10  # 28 - 18
            
            # Check details
            modified_nodes = [d for d in result.details if d.change_type == "modified" and d.entity_type == "node"]
            assert len(modified_nodes) == 1
            assert modified_nodes[0].details["delta"] == 10
    
    @pytest.mark.asyncio
    async def test_severity_calculation(self, drift_detector):
        """Test severity level calculation"""
        # Test LOW severity (<10% drift)
        metrics_low = DriftMetrics(
            new_dependencies=1,
            removed_dependencies=0,
            modified_relationships=0,
            new_nodes=0,
            removed_nodes=0,
            modified_nodes=0,
            total_changes=1,
            drift_percentage=5.0,
            complexity_delta=0
        )
        assert drift_detector._calculate_severity(metrics_low) == DriftSeverity.LOW
        
        # Test MEDIUM severity (10-25% drift)
        metrics_medium = DriftMetrics(
            new_dependencies=3,
            removed_dependencies=2,
            modified_relationships=0,
            new_nodes=0,
            removed_nodes=0,
            modified_nodes=0,
            total_changes=5,
            drift_percentage=15.0,
            complexity_delta=0
        )
        assert drift_detector._calculate_severity(metrics_medium) == DriftSeverity.MEDIUM
        
        # Test HIGH severity (25-50% drift)
        metrics_high = DriftMetrics(
            new_dependencies=10,
            removed_dependencies=5,
            modified_relationships=0,
            new_nodes=0,
            removed_nodes=0,
            modified_nodes=0,
            total_changes=15,
            drift_percentage=35.0,
            complexity_delta=0
        )
        assert drift_detector._calculate_severity(metrics_high) == DriftSeverity.HIGH
        
        # Test CRITICAL severity (>50% drift)
        metrics_critical = DriftMetrics(
            new_dependencies=20,
            removed_dependencies=15,
            modified_relationships=0,
            new_nodes=10,
            removed_nodes=5,
            modified_nodes=0,
            total_changes=50,
            drift_percentage=60.0,
            complexity_delta=0
        )
        assert drift_detector._calculate_severity(metrics_critical) == DriftSeverity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, drift_detector):
        """Test recommendation generation"""
        metrics = DriftMetrics(
            new_dependencies=15,
            removed_dependencies=5,
            modified_relationships=0,
            new_nodes=25,
            removed_nodes=12,
            modified_nodes=0,
            total_changes=57,
            drift_percentage=35.0,
            complexity_delta=150
        )
        
        recommendations = drift_detector._generate_recommendations(
            metrics=metrics,
            severity=DriftSeverity.HIGH,
            drift_details=[]
        )
        
        assert len(recommendations) > 0
        assert any("HIGH" in rec for rec in recommendations)
        assert any("dependencies" in rec for rec in recommendations)
        assert any("complexity" in rec.lower() for rec in recommendations)
        assert any("baseline" in rec.lower() for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_drift_result_serialization(self, drift_detector, baseline_manager, sample_baseline, sample_nodes, sample_relationships):
        """Test that DriftResult can be serialized to dict/JSON"""
        # Store baseline
        await baseline_manager._store_baseline(sample_baseline)
        
        mock_driver = AsyncMock()
        
        with patch('app.services.architecture_analyzer.drift_detector.get_neo4j_driver', return_value=mock_driver):
            drift_detector._get_current_nodes = AsyncMock(return_value=sample_nodes)
            drift_detector._get_current_relationships = AsyncMock(return_value=sample_relationships)
            
            result = await drift_detector.detect_drift(
                project_id="test_project",
                baseline_version="v1.0.0"
            )
            
            # Convert to dict
            result_dict = result.to_dict()
            
            assert "project_id" in result_dict
            assert "severity" in result_dict
            assert "metrics" in result_dict
            assert "details" in result_dict
            assert "recommendations" in result_dict
            
            # Verify it can be JSON serialized
            json_str = json.dumps(result_dict)
            assert len(json_str) > 0


# Integration Tests

class TestDriftDetectorIntegration:
    """Integration tests for drift detection workflow"""
    
    @pytest.mark.asyncio
    async def test_full_drift_detection_workflow(self, drift_detector, baseline_manager, sample_nodes, sample_relationships):
        """Test complete workflow: create baseline, make changes, detect drift"""
        # Step 1: Create baseline
        baseline_manager._capture_nodes = AsyncMock(return_value=sample_nodes)
        baseline_manager._capture_relationships = AsyncMock(return_value=sample_relationships)
        
        mock_driver = AsyncMock()
        
        with patch('app.services.architecture_analyzer.baseline.get_neo4j_driver', return_value=mock_driver):
            baseline = await baseline_manager.create_baseline(
                project_id="test_project",
                version="v1.0.0"
            )
        
        # Step 2: Simulate changes
        current_nodes = sample_nodes + [
            {
                "node_id": 4,
                "labels": ["CodeEntity", "Function"],
                "properties": {
                    "name": "new_feature",
                    "type": "function",
                    "file_path": "src/features.py",
                    "complexity": 8,
                    "lines_of_code": 30
                }
            }
        ]
        
        current_relationships = sample_relationships + [
            {
                "rel_id": 3,
                "source_id": 4,
                "target_id": 2,
                "source_name": "new_feature",
                "target_name": "UserService",
                "rel_type": "DEPENDS_ON",
                "properties": {"weight": 1}
            }
        ]
        
        # Step 3: Detect drift
        with patch('app.services.architecture_analyzer.drift_detector.get_neo4j_driver', return_value=mock_driver):
            drift_detector._get_current_nodes = AsyncMock(return_value=current_nodes)
            drift_detector._get_current_relationships = AsyncMock(return_value=current_relationships)
            
            result = await drift_detector.detect_drift(
                project_id="test_project",
                baseline_version="v1.0.0"
            )
        
        # Step 4: Verify results
        assert result.project_id == "test_project"
        assert result.baseline_version == "v1.0.0"
        assert result.metrics.new_nodes == 1
        assert result.metrics.new_dependencies == 1
        assert result.metrics.total_changes == 2
        # 2 changes out of 5 total items (3 nodes + 2 rels) = 40% drift = HIGH severity
        assert result.severity in [DriftSeverity.MEDIUM, DriftSeverity.HIGH]
        assert len(result.recommendations) > 0
