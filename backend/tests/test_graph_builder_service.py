"""
Unit Tests for Graph Builder Service

Tests the graph builder service that creates and updates code entity nodes
and dependency relationships in Neo4j.

Validates Requirement 1.3: Update Graph_Database with new dependencies
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.graph_builder.service import GraphBuilderService
from app.services.code_entity_extractor import CodeEntity
from app.schemas.ast_models import DependencyGraph, DependencyEdge
from app.services.graph_builder.models import GraphUpdateResult


@pytest.fixture
def graph_builder():
    """Create graph builder service instance"""
    return GraphBuilderService()


@pytest.fixture
def sample_entity():
    """Create sample code entity"""
    return CodeEntity(
        name="test_function",
        entity_type="function",
        file_path="/path/to/file.py",
        complexity=5,
        lines_of_code=20,
        dependencies=["other_function"]
    )


@pytest.fixture
def sample_entities():
    """Create list of sample entities"""
    return [
        CodeEntity(
            name="function_a",
            entity_type="function",
            file_path="/path/to/file1.py",
            complexity=3,
            lines_of_code=10,
            dependencies=[]
        ),
        CodeEntity(
            name="function_b",
            entity_type="function",
            file_path="/path/to/file1.py",
            complexity=7,
            lines_of_code=25,
            dependencies=["function_a"]
        ),
        CodeEntity(
            name="ClassA",
            entity_type="class",
            file_path="/path/to/file2.py",
            complexity=15,
            lines_of_code=100,
            dependencies=[]
        )
    ]


@pytest.fixture
def sample_dependency_graph():
    """Create sample dependency graph"""
    graph = DependencyGraph()
    graph.nodes = ["function_a", "function_b", "ClassA"]
    graph.edges = [
        DependencyEdge(
            source="function_b",
            target="function_a",
            type="call",
            weight=1.0
        )
    ]
    graph.metrics = {
        "total_nodes": 3,
        "total_edges": 1
    }
    return graph


@pytest.fixture
def mock_neo4j_driver():
    """Create mock Neo4j driver"""
    driver = AsyncMock()
    session = AsyncMock()
    
    # Create async context manager for session
    async_context = AsyncMock()
    async_context.__aenter__ = AsyncMock(return_value=session)
    async_context.__aexit__ = AsyncMock(return_value=None)
    driver.session = MagicMock(return_value=async_context)
    
    return driver, session


class TestGraphBuilderService:
    """Test graph builder service functionality"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, graph_builder):
        """Test graph builder service initialization"""
        assert graph_builder is not None
        assert graph_builder.batch_size == 1000
    
    @pytest.mark.asyncio
    async def test_create_entity_node_success(self, graph_builder, sample_entity, mock_neo4j_driver):
        """Test successful entity node creation"""
        driver, session = mock_neo4j_driver
        
        # Mock query result
        mock_result = AsyncMock()
        mock_record = {"operation": "created"}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_or_update_entity_node(sample_entity)
        
        assert result.nodes_created == 1
        assert result.nodes_updated == 0
        assert len(result.errors) == 0
        session.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_entity_node_success(self, graph_builder, sample_entity, mock_neo4j_driver):
        """Test successful entity node update"""
        driver, session = mock_neo4j_driver
        
        # Mock query result for update
        mock_result = AsyncMock()
        mock_record = {"operation": "updated"}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_or_update_entity_node(sample_entity)
        
        assert result.nodes_created == 0
        assert result.nodes_updated == 1
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_create_entity_node_with_project_id(self, graph_builder, sample_entity, mock_neo4j_driver):
        """Test entity node creation with project ID"""
        driver, session = mock_neo4j_driver
        
        mock_result = AsyncMock()
        mock_record = {"operation": "created"}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_or_update_entity_node(
                sample_entity,
                project_id="project-123"
            )
        
        assert result.nodes_created == 1
        # Verify project_id was included in the call
        call_args = session.run.call_args
        assert "properties" in call_args.kwargs
    
    @pytest.mark.asyncio
    async def test_create_entity_node_error_handling(self, graph_builder, sample_entity, mock_neo4j_driver):
        """Test error handling in entity node creation"""
        driver, session = mock_neo4j_driver
        
        # Mock query failure
        session.run = AsyncMock(side_effect=Exception("Database error"))
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_or_update_entity_node(sample_entity)
        
        assert result.nodes_created == 0
        assert result.nodes_updated == 0
        assert len(result.errors) == 1
        assert "Database error" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_batch_create_entities(self, graph_builder, sample_entities, mock_neo4j_driver):
        """Test batch entity creation"""
        driver, session = mock_neo4j_driver
        
        # Mock query result
        mock_result = AsyncMock()
        mock_record = {"count": len(sample_entities)}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_or_update_entity_nodes_batch(sample_entities)
        
        # Should have created or updated all entities
        assert result.nodes_created + result.nodes_updated == len(sample_entities)
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_batch_create_large_dataset(self, graph_builder, mock_neo4j_driver):
        """Test batch creation with dataset larger than batch size"""
        driver, session = mock_neo4j_driver
        
        # Create 2500 entities (more than 2 batches)
        large_entity_list = [
            CodeEntity(
                name=f"entity_{i}",
                entity_type="function",
                file_path=f"/path/file_{i}.py",
                complexity=1,
                lines_of_code=10,
                dependencies=[]
            )
            for i in range(2500)
        ]
        
        # Mock query result
        mock_result = AsyncMock()
        mock_record = {"count": 1000}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_or_update_entity_nodes_batch(large_entity_list)
        
        # Should have processed all entities
        assert result.nodes_created + result.nodes_updated == len(large_entity_list)
        # Should have made 3 batch calls (1000, 1000, 500)
        assert session.run.call_count == 3
    
    @pytest.mark.asyncio
    async def test_create_dependency_relationship(self, graph_builder, sample_entities, mock_neo4j_driver):
        """Test creating a dependency relationship"""
        driver, session = mock_neo4j_driver
        
        source = sample_entities[1]  # function_b
        target = sample_entities[0]  # function_a
        
        # Mock query result
        mock_result = AsyncMock()
        mock_record = {"operation": "created"}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_dependency_relationship(
                source,
                target,
                relationship_type="CALLS"
            )
        
        assert result.relationships_created == 1
        assert result.relationships_updated == 0
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_create_relationship_with_properties(self, graph_builder, sample_entities, mock_neo4j_driver):
        """Test creating relationship with custom properties"""
        driver, session = mock_neo4j_driver
        
        source = sample_entities[1]
        target = sample_entities[0]
        
        mock_result = AsyncMock()
        mock_record = {"operation": "created"}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        properties = {
            "weight": 0.8,
            "call_count": 5
        }
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_dependency_relationship(
                source,
                target,
                relationship_type="CALLS",
                properties=properties
            )
        
        assert result.relationships_created == 1
        # Verify properties were passed
        call_args = session.run.call_args
        assert "properties" in call_args.kwargs
    
    @pytest.mark.asyncio
    async def test_batch_create_relationships(self, graph_builder, sample_entities, mock_neo4j_driver):
        """Test batch relationship creation"""
        driver, session = mock_neo4j_driver
        
        relationships = [
            (sample_entities[1], sample_entities[0], "CALLS", {"weight": 1.0}),
            (sample_entities[2], sample_entities[0], "USES", {"weight": 0.5})
        ]
        
        # Mock query result
        mock_result = AsyncMock()
        mock_record = {"count": len(relationships)}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.create_dependency_relationships_batch(relationships)
        
        assert result.relationships_created == len(relationships)
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_build_complete_dependency_graph(
        self,
        graph_builder,
        sample_entities,
        sample_dependency_graph,
        mock_neo4j_driver
    ):
        """Test building complete dependency graph from entities"""
        driver, session = mock_neo4j_driver
        
        # Mock query results
        mock_result = AsyncMock()
        mock_record = {"count": 3}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.build_dependency_graph_from_entities(
                sample_entities,
                sample_dependency_graph
            )
        
        # Should have created nodes and relationships
        assert result.nodes_created + result.nodes_updated > 0
        assert result.relationships_created > 0
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_update_entity_metrics(self, graph_builder, mock_neo4j_driver):
        """Test updating entity metrics"""
        driver, session = mock_neo4j_driver
        
        # Mock query result
        mock_result = AsyncMock()
        mock_record = {"n": {"name": "test_function"}}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        metrics = {
            "complexity": 10,
            "maintainability_index": 75.5
        }
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.update_entity_metrics(
                "test_function",
                "/path/to/file.py",
                metrics
            )
        
        assert result.nodes_updated == 1
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_update_metrics_entity_not_found(self, graph_builder, mock_neo4j_driver):
        """Test updating metrics for non-existent entity"""
        driver, session = mock_neo4j_driver
        
        # Mock query result with no record
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=None)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.update_entity_metrics(
                "nonexistent",
                "/path/to/file.py",
                {"complexity": 5}
            )
        
        assert result.nodes_updated == 0
        assert len(result.errors) == 1
        assert "not found" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_delete_entities_by_file(self, graph_builder, mock_neo4j_driver):
        """Test deleting all entities from a file"""
        driver, session = mock_neo4j_driver
        
        # Mock query result
        mock_result = AsyncMock()
        mock_record = {"deleted_count": 5}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.delete_entities_by_file("/path/to/file.py")
        
        assert result.nodes_updated == 5  # Deleted count
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_delete_entities_with_project_filter(self, graph_builder, mock_neo4j_driver):
        """Test deleting entities with project ID filter"""
        driver, session = mock_neo4j_driver
        
        mock_result = AsyncMock()
        mock_record = {"deleted_count": 3}
        mock_result.single = AsyncMock(return_value=mock_record)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            result = await graph_builder.delete_entities_by_file(
                "/path/to/file.py",
                project_id="project-123"
            )
        
        assert result.nodes_updated == 3
        # Verify project_id was used in query
        call_args = session.run.call_args
        assert "project_id" in call_args.kwargs
    
    @pytest.mark.asyncio
    async def test_get_entity_dependencies(self, graph_builder, mock_neo4j_driver):
        """Test getting entity dependencies"""
        driver, session = mock_neo4j_driver
        
        # Mock query result with dependencies
        mock_records = [
            {
                "name": "dependency_1",
                "type": "function",
                "file_path": "/path/to/dep1.py",
                "distance": 1,
                "relationship_types": ["CALLS"]
            },
            {
                "name": "dependency_2",
                "type": "class",
                "file_path": "/path/to/dep2.py",
                "distance": 2,
                "relationship_types": ["CALLS", "USES"]
            }
        ]
        
        # Create async iterator
        class AsyncIterator:
            def __init__(self, items):
                self.items = items
                self.index = 0
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                if self.index >= len(self.items):
                    raise StopAsyncIteration
                item = self.items[self.index]
                self.index += 1
                return item
        
        mock_result = AsyncIterator(mock_records)
        session.run = AsyncMock(return_value=mock_result)
        
        with patch('app.services.graph_builder.service.get_neo4j_driver', return_value=driver):
            dependencies = await graph_builder.get_entity_dependencies(
                "test_function",
                "/path/to/file.py",
                depth=2
            )
        
        assert len(dependencies) == 2
        assert dependencies[0]["name"] == "dependency_1"
        assert dependencies[1]["distance"] == 2
    
    @pytest.mark.asyncio
    async def test_get_node_label_mapping(self, graph_builder):
        """Test entity type to node label mapping"""
        assert graph_builder._get_node_label("function") == "Function"
        assert graph_builder._get_node_label("class") == "Class"
        assert graph_builder._get_node_label("method") == "Method"
        assert graph_builder._get_node_label("module") == "Module"
        assert graph_builder._get_node_label("unknown") == "CodeEntity"
    
    @pytest.mark.asyncio
    async def test_map_edge_type_to_relationship(self, graph_builder):
        """Test edge type to relationship type mapping"""
        assert graph_builder._map_edge_type_to_relationship("import") == "IMPORTS"
        assert graph_builder._map_edge_type_to_relationship("call") == "CALLS"
        assert graph_builder._map_edge_type_to_relationship("inheritance") == "INHERITS"
        assert graph_builder._map_edge_type_to_relationship("uses") == "USES"
        assert graph_builder._map_edge_type_to_relationship("unknown") == "DEPENDS_ON"
    
    @pytest.mark.asyncio
    async def test_graph_update_result_addition(self):
        """Test GraphUpdateResult addition operation"""
        result1 = GraphUpdateResult(
            nodes_created=5,
            nodes_updated=3,
            relationships_created=10,
            relationships_updated=2,
            errors=["error1"]
        )
        
        result2 = GraphUpdateResult(
            nodes_created=2,
            nodes_updated=1,
            relationships_created=5,
            relationships_updated=1,
            errors=["error2"]
        )
        
        combined = result1 + result2
        
        assert combined.nodes_created == 7
        assert combined.nodes_updated == 4
        assert combined.relationships_created == 15
        assert combined.relationships_updated == 3
        assert len(combined.errors) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
