"""
Integration Tests for Neo4j Operations

Tests graph builder service and circular dependency detector with real Neo4j database
using testcontainers for isolated testing.

Validates Requirement 13.3: Integration tests for Neo4j graph operations

**Requirements:**
- Docker must be running to execute these tests
- Tests are automatically skipped if Docker is not available

**Running the tests:**
```bash
# Ensure Docker is running
docker ps

# Run all Neo4j integration tests
pytest backend/tests/test_neo4j_integration.py -v

# Run specific test class
pytest backend/tests/test_neo4j_integration.py::TestGraphBuilderIntegration -v

# Run with detailed output
pytest backend/tests/test_neo4j_integration.py -v -s
```
"""
import pytest
import asyncio
from typing import AsyncGenerator
from testcontainers.neo4j import Neo4jContainer

# Mark all tests in this module as requiring Docker
pytestmark = pytest.mark.requires_docker

from app.services.graph_builder.service import GraphBuilderService
from app.services.graph_builder.circular_dependency_detector import (
    CircularDependencyDetector,
    CycleSeverity
)
from app.services.code_entity_extractor import CodeEntity
from app.schemas.ast_models import DependencyGraph, DependencyEdge
from app.database.neo4j_db import init_neo4j, close_neo4j, get_neo4j_driver
from app.core.config import settings


@pytest.fixture(scope="module")
def neo4j_container():
    """Start Neo4j container for integration tests"""
    container = Neo4jContainer("neo4j:5.13.0")
    container.with_env("NEO4J_AUTH", "neo4j/testpassword")
    container.with_env("NEO4J_ACCEPT_LICENSE_AGREEMENT", "yes")
    container.start()
    
    yield container
    
    container.stop()


@pytest.fixture(scope="module")
async def neo4j_test_config(neo4j_container):
    """Configure Neo4j settings for test container"""
    # Override settings with container connection details
    original_uri = settings.NEO4J_URI
    original_user = settings.NEO4J_USER
    original_password = settings.NEO4J_PASSWORD
    original_database = settings.NEO4J_DATABASE
    
    settings.NEO4J_URI = neo4j_container.get_connection_url()
    settings.NEO4J_USER = "neo4j"
    settings.NEO4J_PASSWORD = "testpassword"
    settings.NEO4J_DATABASE = "neo4j"
    
    # Initialize connection
    await init_neo4j()
    
    yield
    
    # Cleanup
    await close_neo4j()
    
    # Restore original settings
    settings.NEO4J_URI = original_uri
    settings.NEO4J_USER = original_user
    settings.NEO4J_PASSWORD = original_password
    settings.NEO4J_DATABASE = original_database


@pytest.fixture
async def clean_database(neo4j_test_config):
    """Clean database before each test"""
    driver = await get_neo4j_driver()
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        await session.run("MATCH (n) DETACH DELETE n")
    yield


@pytest.fixture
def graph_builder():
    """Create graph builder service instance"""
    return GraphBuilderService()


@pytest.fixture
def cycle_detector():
    """Create circular dependency detector instance"""
    return CircularDependencyDetector()


@pytest.fixture
def sample_entities():
    """Create sample code entities for testing"""
    return [
        CodeEntity(
            name="module_a",
            entity_type="module",
            file_path="/project/module_a.py",
            complexity=5,
            lines_of_code=50,
            dependencies=["module_b"]
        ),
        CodeEntity(
            name="module_b",
            entity_type="module",
            file_path="/project/module_b.py",
            complexity=8,
            lines_of_code=80,
            dependencies=["module_c"]
        ),
        CodeEntity(
            name="module_c",
            entity_type="module",
            file_path="/project/module_c.py",
            complexity=3,
            lines_of_code=30,
            dependencies=[]
        ),
        CodeEntity(
            name="function_x",
            entity_type="function",
            file_path="/project/utils.py",
            complexity=2,
            lines_of_code=15,
            dependencies=[]
        )
    ]


class TestGraphBuilderIntegration:
    """Integration tests for graph builder service with real Neo4j"""
    
    @pytest.mark.asyncio
    async def test_create_single_entity_node(self, graph_builder, clean_database, sample_entities):
        """Test creating a single entity node in Neo4j"""
        entity = sample_entities[0]
        
        result = await graph_builder.create_or_update_entity_node(entity)
        
        assert result.nodes_created == 1
        assert result.nodes_updated == 0
        assert len(result.errors) == 0
        
        # Verify node exists in database
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run(
                "MATCH (n:CodeEntity {name: $name}) RETURN n",
                name=entity.name
            )
            record = await query_result.single()
            assert record is not None
            node = record["n"]
            assert node["name"] == entity.name
            assert node["file_path"] == entity.file_path
            assert node["complexity"] == entity.complexity
    
    @pytest.mark.asyncio
    async def test_update_existing_entity_node(self, graph_builder, clean_database, sample_entities):
        """Test updating an existing entity node"""
        entity = sample_entities[0]
        
        # Create initial node
        await graph_builder.create_or_update_entity_node(entity)
        
        # Update with modified entity
        updated_entity = CodeEntity(
            name=entity.name,
            entity_type=entity.entity_type,
            file_path=entity.file_path,
            complexity=10,  # Changed
            lines_of_code=100,  # Changed
            dependencies=entity.dependencies
        )
        
        result = await graph_builder.create_or_update_entity_node(updated_entity)
        
        assert result.nodes_created == 0
        assert result.nodes_updated == 1
        assert len(result.errors) == 0
        
        # Verify updated values
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run(
                "MATCH (n:CodeEntity {name: $name}) RETURN n",
                name=entity.name
            )
            record = await query_result.single()
            node = record["n"]
            assert node["complexity"] == 10
            assert node["lines_of_code"] == 100
    
    @pytest.mark.asyncio
    async def test_batch_create_entities(self, graph_builder, clean_database, sample_entities):
        """Test batch creation of multiple entities"""
        result = await graph_builder.create_or_update_entity_nodes_batch(sample_entities)
        
        assert result.nodes_created + result.nodes_updated == len(sample_entities)
        assert len(result.errors) == 0
        
        # Verify all nodes exist
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run("MATCH (n:CodeEntity) RETURN count(n) as count")
            record = await query_result.single()
            assert record["count"] == len(sample_entities)
    
    @pytest.mark.asyncio
    async def test_create_dependency_relationship(self, graph_builder, clean_database, sample_entities):
        """Test creating dependency relationships between entities"""
        # Create entities first
        await graph_builder.create_or_update_entity_nodes_batch(sample_entities[:2])
        
        # Create relationship
        source = sample_entities[0]
        target = sample_entities[1]
        
        result = await graph_builder.create_dependency_relationship(
            source,
            target,
            relationship_type="DEPENDS_ON"
        )
        
        assert result.relationships_created == 1
        assert len(result.errors) == 0
        
        # Verify relationship exists
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run(
                """
                MATCH (s:CodeEntity {name: $source})-[r:DEPENDS_ON]->(t:CodeEntity {name: $target})
                RETURN r
                """,
                source=source.name,
                target=target.name
            )
            record = await query_result.single()
            assert record is not None
    
    @pytest.mark.asyncio
    async def test_batch_create_relationships(self, graph_builder, clean_database, sample_entities):
        """Test batch creation of multiple relationships"""
        # Create entities first
        await graph_builder.create_or_update_entity_nodes_batch(sample_entities)
        
        # Create relationships
        relationships = [
            (sample_entities[0], sample_entities[1], "DEPENDS_ON", {"weight": 1.0}),
            (sample_entities[1], sample_entities[2], "DEPENDS_ON", {"weight": 0.8}),
            (sample_entities[0], sample_entities[3], "CALLS", {"weight": 0.5})
        ]
        
        result = await graph_builder.create_dependency_relationships_batch(relationships)
        
        assert result.relationships_created == len(relationships)
        assert len(result.errors) == 0
        
        # Verify all relationships exist
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run(
                "MATCH ()-[r]->() RETURN count(r) as count"
            )
            record = await query_result.single()
            assert record["count"] == len(relationships)
    
    @pytest.mark.asyncio
    async def test_build_complete_dependency_graph(self, graph_builder, clean_database, sample_entities):
        """Test building complete dependency graph from entities and edges"""
        # Create dependency graph
        dependency_graph = DependencyGraph()
        dependency_graph.nodes = [e.name for e in sample_entities]
        dependency_graph.edges = [
            DependencyEdge(
                source="module_a",
                target="module_b",
                type="import",
                weight=1.0
            ),
            DependencyEdge(
                source="module_b",
                target="module_c",
                type="import",
                weight=1.0
            )
        ]
        dependency_graph.metrics = {
            "total_nodes": len(sample_entities),
            "total_edges": 2
        }
        
        result = await graph_builder.build_dependency_graph_from_entities(
            sample_entities,
            dependency_graph
        )
        
        assert result.nodes_created + result.nodes_updated == len(sample_entities)
        assert result.relationships_created >= 2
        assert len(result.errors) == 0
        
        # Verify graph structure
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            # Check nodes
            node_result = await session.run("MATCH (n:CodeEntity) RETURN count(n) as count")
            node_record = await node_result.single()
            assert node_record["count"] == len(sample_entities)
            
            # Check relationships
            rel_result = await session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_record = await rel_result.single()
            assert rel_record["count"] >= 2
    
    @pytest.mark.asyncio
    async def test_update_entity_metrics(self, graph_builder, clean_database, sample_entities):
        """Test updating metrics for an existing entity"""
        entity = sample_entities[0]
        
        # Create entity
        await graph_builder.create_or_update_entity_node(entity)
        
        # Update metrics
        new_metrics = {
            "complexity": 15,
            "maintainability_index": 85.5,
            "test_coverage": 90.0
        }
        
        result = await graph_builder.update_entity_metrics(
            entity.name,
            entity.file_path,
            new_metrics
        )
        
        assert result.nodes_updated == 1
        assert len(result.errors) == 0
        
        # Verify metrics were updated
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run(
                "MATCH (n:CodeEntity {name: $name}) RETURN n",
                name=entity.name
            )
            record = await query_result.single()
            node = record["n"]
            assert node["complexity"] == 15
            assert node["maintainability_index"] == 85.5
            assert node["test_coverage"] == 90.0
    
    @pytest.mark.asyncio
    async def test_delete_entities_by_file(self, graph_builder, clean_database, sample_entities):
        """Test deleting all entities from a specific file"""
        # Create entities
        await graph_builder.create_or_update_entity_nodes_batch(sample_entities)
        
        # Delete entities from one file
        file_path = "/project/module_a.py"
        result = await graph_builder.delete_entities_by_file(file_path)
        
        assert result.nodes_updated == 1  # One entity deleted
        assert len(result.errors) == 0
        
        # Verify entity was deleted
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run(
                "MATCH (n:CodeEntity {file_path: $file_path}) RETURN count(n) as count",
                file_path=file_path
            )
            record = await query_result.single()
            assert record["count"] == 0
            
            # Verify other entities still exist
            all_result = await session.run("MATCH (n:CodeEntity) RETURN count(n) as count")
            all_record = await all_result.single()
            assert all_record["count"] == len(sample_entities) - 1
    
    @pytest.mark.asyncio
    async def test_get_entity_dependencies(self, graph_builder, clean_database, sample_entities):
        """Test retrieving entity dependencies"""
        # Build graph
        await graph_builder.create_or_update_entity_nodes_batch(sample_entities)
        
        relationships = [
            (sample_entities[0], sample_entities[1], "DEPENDS_ON", {}),
            (sample_entities[1], sample_entities[2], "DEPENDS_ON", {}),
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Get dependencies
        dependencies = await graph_builder.get_entity_dependencies(
            sample_entities[0].name,
            sample_entities[0].file_path,
            depth=2
        )
        
        assert len(dependencies) >= 1
        assert any(d["name"] == "module_b" for d in dependencies)


class TestCircularDependencyDetectorIntegration:
    """Integration tests for circular dependency detector with real Neo4j"""
    
    @pytest.mark.asyncio
    async def test_detect_no_cycles(self, cycle_detector, graph_builder, clean_database):
        """Test cycle detection when no cycles exist"""
        # Create linear dependency chain: A -> B -> C
        entities = [
            CodeEntity(name="A", entity_type="module", file_path="/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="B", entity_type="module", file_path="/b.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="C", entity_type="module", file_path="/c.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        relationships = [
            (entities[0], entities[1], "DEPENDS_ON", {}),
            (entities[1], entities[2], "DEPENDS_ON", {})
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles
        result = await cycle_detector.detect_cycles()
        
        assert result.total_cycles == 0
        assert len(result.cycles) == 0
        assert result.detection_time_ms >= 0
    
    @pytest.mark.asyncio
    async def test_detect_simple_cycle(self, cycle_detector, graph_builder, clean_database):
        """Test detection of a simple 2-node cycle"""
        # Create cycle: A -> B -> A
        entities = [
            CodeEntity(name="A", entity_type="module", file_path="/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="B", entity_type="module", file_path="/b.py", complexity=3, lines_of_code=30, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        relationships = [
            (entities[0], entities[1], "DEPENDS_ON", {}),
            (entities[1], entities[0], "DEPENDS_ON", {})
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles
        result = await cycle_detector.detect_cycles()
        
        assert result.total_cycles >= 1
        assert len(result.cycles) >= 1
        
        cycle = result.cycles[0]
        assert len(cycle.nodes) == 2
        assert set(cycle.nodes) == {"A", "B"}
        assert cycle.severity == CycleSeverity.LOW
        assert cycle.depth == 2
        assert cycle.total_complexity == 8
    
    @pytest.mark.asyncio
    async def test_detect_complex_cycle(self, cycle_detector, graph_builder, clean_database):
        """Test detection of a complex multi-node cycle"""
        # Create cycle: A -> B -> C -> D -> A
        entities = [
            CodeEntity(name="A", entity_type="module", file_path="/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="B", entity_type="module", file_path="/b.py", complexity=7, lines_of_code=70, dependencies=[]),
            CodeEntity(name="C", entity_type="module", file_path="/c.py", complexity=6, lines_of_code=60, dependencies=[]),
            CodeEntity(name="D", entity_type="module", file_path="/d.py", complexity=8, lines_of_code=80, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        relationships = [
            (entities[0], entities[1], "DEPENDS_ON", {}),
            (entities[1], entities[2], "DEPENDS_ON", {}),
            (entities[2], entities[3], "DEPENDS_ON", {}),
            (entities[3], entities[0], "DEPENDS_ON", {})
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles
        result = await cycle_detector.detect_cycles()
        
        assert result.total_cycles >= 1
        
        cycle = result.cycles[0]
        assert len(cycle.nodes) == 4
        assert set(cycle.nodes) == {"A", "B", "C", "D"}
        assert cycle.severity == CycleSeverity.MEDIUM
        assert cycle.depth == 4
        assert cycle.total_complexity == 26
    
    @pytest.mark.asyncio
    async def test_detect_multiple_cycles(self, cycle_detector, graph_builder, clean_database):
        """Test detection of multiple independent cycles"""
        # Create two separate cycles:
        # Cycle 1: A -> B -> A
        # Cycle 2: C -> D -> E -> C
        entities = [
            CodeEntity(name="A", entity_type="module", file_path="/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="B", entity_type="module", file_path="/b.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="C", entity_type="module", file_path="/c.py", complexity=8, lines_of_code=80, dependencies=[]),
            CodeEntity(name="D", entity_type="module", file_path="/d.py", complexity=7, lines_of_code=70, dependencies=[]),
            CodeEntity(name="E", entity_type="module", file_path="/e.py", complexity=6, lines_of_code=60, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        relationships = [
            # Cycle 1
            (entities[0], entities[1], "DEPENDS_ON", {}),
            (entities[1], entities[0], "DEPENDS_ON", {}),
            # Cycle 2
            (entities[2], entities[3], "DEPENDS_ON", {}),
            (entities[3], entities[4], "DEPENDS_ON", {}),
            (entities[4], entities[2], "DEPENDS_ON", {})
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles
        result = await cycle_detector.detect_cycles()
        
        assert result.total_cycles >= 2
        assert len(result.cycles) >= 2
        
        # Verify severity breakdown
        assert sum(result.severity_breakdown.values()) >= 2
    
    @pytest.mark.asyncio
    async def test_detect_critical_severity_cycle(self, cycle_detector, graph_builder, clean_database):
        """Test detection of critical severity cycle (large or high complexity)"""
        # Create large cycle with 12 nodes
        entities = [
            CodeEntity(
                name=f"Module_{i}",
                entity_type="module",
                file_path=f"/module_{i}.py",
                complexity=10,
                lines_of_code=100,
                dependencies=[]
            )
            for i in range(12)
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        # Create circular relationships
        relationships = []
        for i in range(12):
            next_i = (i + 1) % 12
            relationships.append((entities[i], entities[next_i], "DEPENDS_ON", {}))
        
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles
        result = await cycle_detector.detect_cycles()
        
        assert result.total_cycles >= 1
        
        cycle = result.cycles[0]
        assert cycle.severity == CycleSeverity.CRITICAL
        assert cycle.depth >= 10
        assert cycle.total_complexity >= 100
    
    @pytest.mark.asyncio
    async def test_detect_cycles_with_severity_filter(self, cycle_detector, graph_builder, clean_database):
        """Test cycle detection with minimum severity filter"""
        # Create cycles with different severities
        # Low severity: 2 nodes
        low_entities = [
            CodeEntity(name="L1", entity_type="module", file_path="/l1.py", complexity=2, lines_of_code=20, dependencies=[]),
            CodeEntity(name="L2", entity_type="module", file_path="/l2.py", complexity=2, lines_of_code=20, dependencies=[])
        ]
        
        # Medium severity: 5 nodes
        medium_entities = [
            CodeEntity(name=f"M{i}", entity_type="module", file_path=f"/m{i}.py", complexity=5, lines_of_code=50, dependencies=[])
            for i in range(5)
        ]
        
        all_entities = low_entities + medium_entities
        await graph_builder.create_or_update_entity_nodes_batch(all_entities)
        
        # Create cycles
        relationships = [
            (low_entities[0], low_entities[1], "DEPENDS_ON", {}),
            (low_entities[1], low_entities[0], "DEPENDS_ON", {})
        ]
        
        for i in range(5):
            next_i = (i + 1) % 5
            relationships.append((medium_entities[i], medium_entities[next_i], "DEPENDS_ON", {}))
        
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles with medium severity filter
        result = await cycle_detector.detect_cycles(min_severity=CycleSeverity.MEDIUM)
        
        # Should only include medium+ severity cycles
        assert result.total_cycles >= 1
        for cycle in result.cycles:
            assert cycle.severity in [CycleSeverity.MEDIUM, CycleSeverity.HIGH, CycleSeverity.CRITICAL]
    
    @pytest.mark.asyncio
    async def test_detect_cycles_for_specific_entity(self, cycle_detector, graph_builder, clean_database):
        """Test detecting cycles involving a specific entity"""
        # Create cycle: A -> B -> C -> A
        entities = [
            CodeEntity(name="A", entity_type="module", file_path="/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="B", entity_type="module", file_path="/b.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="C", entity_type="module", file_path="/c.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        relationships = [
            (entities[0], entities[1], "DEPENDS_ON", {}),
            (entities[1], entities[2], "DEPENDS_ON", {}),
            (entities[2], entities[0], "DEPENDS_ON", {})
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles for entity A
        cycles = await cycle_detector.detect_cycles_for_entity("A", "/a.py")
        
        assert len(cycles) >= 1
        assert all("A" in cycle.nodes for cycle in cycles)
    
    @pytest.mark.asyncio
    async def test_get_cycle_visualization_data(self, cycle_detector, graph_builder, clean_database):
        """Test getting visualization data for a detected cycle"""
        # Create cycle
        entities = [
            CodeEntity(name="X", entity_type="module", file_path="/x.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="Y", entity_type="module", file_path="/y.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="Z", entity_type="module", file_path="/z.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        relationships = [
            (entities[0], entities[1], "DEPENDS_ON", {}),
            (entities[1], entities[2], "DEPENDS_ON", {}),
            (entities[2], entities[0], "DEPENDS_ON", {})
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles
        result = await cycle_detector.detect_cycles()
        assert result.total_cycles >= 1
        
        cycle_id = result.cycles[0].cycle_id
        
        # Get visualization data
        viz_data = await cycle_detector.get_cycle_visualization_data(cycle_id)
        
        assert viz_data is not None
        assert "nodes" in viz_data
        assert "edges" in viz_data
        assert "severity" in viz_data
        assert "metadata" in viz_data
        assert len(viz_data["nodes"]) == 3
        assert len(viz_data["edges"]) >= 3
        assert viz_data["metadata"]["depth"] == 3
    
    @pytest.mark.asyncio
    async def test_cycle_detection_with_project_filter(self, cycle_detector, graph_builder, clean_database):
        """Test cycle detection filtered by project ID"""
        # Create entities with project IDs
        project1_entities = [
            CodeEntity(name="P1_A", entity_type="module", file_path="/p1/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="P1_B", entity_type="module", file_path="/p1/b.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        project2_entities = [
            CodeEntity(name="P2_A", entity_type="module", file_path="/p2/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="P2_B", entity_type="module", file_path="/p2/b.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        # Create entities with project IDs
        await graph_builder.create_or_update_entity_nodes_batch(project1_entities, project_id="project-1")
        await graph_builder.create_or_update_entity_nodes_batch(project2_entities, project_id="project-2")
        
        # Create cycles in both projects
        relationships1 = [
            (project1_entities[0], project1_entities[1], "DEPENDS_ON", {}),
            (project1_entities[1], project1_entities[0], "DEPENDS_ON", {})
        ]
        relationships2 = [
            (project2_entities[0], project2_entities[1], "DEPENDS_ON", {}),
            (project2_entities[1], project2_entities[0], "DEPENDS_ON", {})
        ]
        
        await graph_builder.create_dependency_relationships_batch(relationships1, project_id="project-1")
        await graph_builder.create_dependency_relationships_batch(relationships2, project_id="project-2")
        
        # Detect cycles for project-1 only
        result = await cycle_detector.detect_cycles(project_id="project-1")
        
        # Should only detect cycles from project-1
        assert result.total_cycles >= 1
        for cycle in result.cycles:
            # All nodes should be from project-1
            assert all(node.startswith("P1_") for node in cycle.nodes)
    
    @pytest.mark.asyncio
    async def test_severity_breakdown_statistics(self, cycle_detector, graph_builder, clean_database):
        """Test severity breakdown statistics in detection result"""
        # Create cycles with different severities
        # Low: 2 nodes
        low_entities = [
            CodeEntity(name="L1", entity_type="module", file_path="/l1.py", complexity=2, lines_of_code=20, dependencies=[]),
            CodeEntity(name="L2", entity_type="module", file_path="/l2.py", complexity=2, lines_of_code=20, dependencies=[])
        ]
        
        # Medium: 5 nodes
        medium_entities = [
            CodeEntity(name=f"M{i}", entity_type="module", file_path=f"/m{i}.py", complexity=5, lines_of_code=50, dependencies=[])
            for i in range(5)
        ]
        
        all_entities = low_entities + medium_entities
        await graph_builder.create_or_update_entity_nodes_batch(all_entities)
        
        # Create cycles
        relationships = [
            (low_entities[0], low_entities[1], "DEPENDS_ON", {}),
            (low_entities[1], low_entities[0], "DEPENDS_ON", {})
        ]
        
        for i in range(5):
            next_i = (i + 1) % 5
            relationships.append((medium_entities[i], medium_entities[next_i], "DEPENDS_ON", {}))
        
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles
        result = await cycle_detector.detect_cycles()
        
        assert result.total_cycles >= 2
        assert "low" in result.severity_breakdown
        assert "medium" in result.severity_breakdown
        assert sum(result.severity_breakdown.values()) == result.total_cycles


class TestGraphUpdateOperations:
    """Integration tests for graph update operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_entity_updates(self, graph_builder, clean_database):
        """Test concurrent updates to the same entity"""
        entity = CodeEntity(
            name="concurrent_test",
            entity_type="function",
            file_path="/test.py",
            complexity=5,
            lines_of_code=50,
            dependencies=[]
        )
        
        # Create initial entity
        await graph_builder.create_or_update_entity_node(entity)
        
        # Perform concurrent updates
        update_tasks = []
        for i in range(5):
            updated_entity = CodeEntity(
                name=entity.name,
                entity_type=entity.entity_type,
                file_path=entity.file_path,
                complexity=10 + i,
                lines_of_code=100 + i,
                dependencies=[]
            )
            update_tasks.append(graph_builder.create_or_update_entity_node(updated_entity))
        
        results = await asyncio.gather(*update_tasks)
        
        # All updates should succeed
        for result in results:
            assert len(result.errors) == 0
        
        # Verify final state
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run(
                "MATCH (n:CodeEntity {name: $name}) RETURN n",
                name=entity.name
            )
            record = await query_result.single()
            assert record is not None
    
    @pytest.mark.asyncio
    async def test_large_batch_operations(self, graph_builder, clean_database):
        """Test handling of large batch operations"""
        # Create 2500 entities (more than batch size of 1000)
        large_entity_list = [
            CodeEntity(
                name=f"entity_{i}",
                entity_type="function",
                file_path=f"/file_{i // 100}.py",
                complexity=i % 20,
                lines_of_code=(i % 100) + 10,
                dependencies=[]
            )
            for i in range(2500)
        ]
        
        result = await graph_builder.create_or_update_entity_nodes_batch(large_entity_list)
        
        assert result.nodes_created + result.nodes_updated == len(large_entity_list)
        assert len(result.errors) == 0
        
        # Verify all entities were created
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run("MATCH (n:CodeEntity) RETURN count(n) as count")
            record = await query_result.single()
            assert record["count"] == len(large_entity_list)
    
    @pytest.mark.asyncio
    async def test_relationship_type_mapping(self, graph_builder, clean_database):
        """Test different relationship types are created correctly"""
        entities = [
            CodeEntity(name="Source", entity_type="module", file_path="/source.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="Target", entity_type="module", file_path="/target.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        # Create different relationship types
        relationship_types = ["IMPORTS", "CALLS", "USES", "INHERITS"]
        
        for rel_type in relationship_types:
            result = await graph_builder.create_dependency_relationship(
                entities[0],
                entities[1],
                relationship_type=rel_type
            )
            assert result.relationships_created == 1
        
        # Verify all relationship types exist
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            for rel_type in relationship_types:
                query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
                query_result = await session.run(query)
                record = await query_result.single()
                assert record["count"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
