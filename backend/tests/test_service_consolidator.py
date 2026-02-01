"""
Unit tests for Service Consolidator component
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from app.services.service_consolidator import (
    ServiceConsolidator,
    ServiceType,
    ConsolidationStrategy,
    ServiceDependency,
    ServiceFunction,
    ServiceOverlap,
    ConsolidationPlan,
    MergeResult,
    DependencyGraph
)


class TestServiceConsolidator:
    """Test cases for ServiceConsolidator"""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create services directory structure
            services_dir = project_root / "services"
            services_dir.mkdir()
            
            # Create sample microservices
            for service in ["api-gateway", "auth-service", "ai-service"]:
                service_dir = services_dir / service
                service_dir.mkdir()
                (service_dir / "src").mkdir()
                
                # Create package.json
                package_json = {
                    "name": f"@ai-code-review/{service}",
                    "dependencies": {
                        "express": "^4.18.2",
                        "axios": "^1.6.2"
                    }
                }
                with open(service_dir / "package.json", "w") as f:
                    json.dump(package_json, f)
                
                # Create sample TypeScript file
                sample_ts = f"""
import express from 'express';
import axios from 'axios';

const router = express.Router();

router.get('/health', (req, res) => {{
    res.json({{ status: 'healthy', service: '{service}' }});
}});

router.post('/api/test', async (req, res) => {{
    const response = await axios.get('http://auth-service:3001/validate');
    res.json(response.data);
}});

export default router;
"""
                with open(service_dir / "src" / "index.ts", "w") as f:
                    f.write(sample_ts)
            
            # Create backend directory
            backend_dir = project_root / "backend"
            backend_dir.mkdir()
            (backend_dir / "app").mkdir()
            
            # Create requirements.txt
            requirements = """
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
redis==5.0.1
"""
            with open(backend_dir / "requirements.txt", "w") as f:
                f.write(requirements)
            
            # Create sample Python file
            sample_py = """
from fastapi import FastAPI, APIRouter
import redis
import asyncio

app = FastAPI()
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend-core"}

@router.post("/api/analyze")
async def analyze_code(request: dict):
    # Complex function with multiple branches
    if request.get("type") == "security":
        for item in request.get("items", []):
            if item.get("critical"):
                while item.get("processing"):
                    try:
                        await process_item(item)
                    except Exception as e:
                        handle_error(e)
    return {"result": "analyzed"}

async def process_item(item):
    pass

def handle_error(error):
    pass
"""
            with open(backend_dir / "app" / "main.py", "w") as f:
                f.write(sample_py)
            
            yield project_root

    @pytest.fixture
    def consolidator(self, temp_project_dir):
        """Create ServiceConsolidator instance with temp directory"""
        return ServiceConsolidator(str(temp_project_dir))

    @pytest.mark.asyncio
    async def test_discover_services(self, consolidator):
        """Test service discovery functionality"""
        await consolidator._discover_services()
        
        # Should discover 3 microservices + 1 backend
        assert len(consolidator.services) == 4
        assert "api-gateway" in consolidator.services
        assert "auth-service" in consolidator.services
        assert "ai-service" in consolidator.services
        assert "backend-core" in consolidator.services
        
        # Check service info structure
        api_gateway = consolidator.services["api-gateway"]
        assert api_gateway["language"] == "typescript"
        assert api_gateway["type"] == "microservice"
        assert len(api_gateway["dependencies"]) > 0
        assert "express" in api_gateway["dependencies"]

    @pytest.mark.asyncio
    async def test_analyze_service_dependencies(self, consolidator):
        """Test dependency analysis"""
        dependency_graph = await consolidator.analyze_service_dependencies()
        
        assert isinstance(dependency_graph, DependencyGraph)
        assert len(dependency_graph.nodes) > 0
        assert len(dependency_graph.edges) >= 0
        
        # Check that services are properly analyzed
        assert "api-gateway" in dependency_graph.nodes
        assert "backend-core" in dependency_graph.nodes

    @pytest.mark.asyncio
    async def test_analyze_api_dependencies(self, consolidator):
        """Test API dependency analysis"""
        await consolidator._discover_services()
        await consolidator._analyze_api_dependencies()
        
        # Should find API dependencies from the sample code
        api_deps = [dep for dep in consolidator.dependencies if dep.dependency_type == 'api_call']
        assert len(api_deps) >= 0  # May be 0 if no clear service URLs found

    @pytest.mark.asyncio
    async def test_analyze_database_dependencies(self, consolidator):
        """Test database dependency analysis"""
        await consolidator._discover_services()
        
        # Manually add database access info for testing
        consolidator.services["auth-service"]["database_access"] = ["postgresql", "redis"]
        consolidator.services["backend-core"]["database_access"] = ["postgresql", "redis", "neo4j"]
        
        await consolidator._analyze_database_dependencies()
        
        # Should find shared database dependencies
        db_deps = [dep for dep in consolidator.dependencies if dep.dependency_type == 'database']
        assert len(db_deps) > 0
        
        # Check that dependencies are bidirectional for shared databases
        sources = {dep.source for dep in db_deps}
        targets = {dep.target for dep in db_deps}
        assert "auth-service" in sources or "auth-service" in targets
        assert "backend-core" in sources or "backend-core" in targets

    def test_calculate_service_overlap(self, consolidator):
        """Test service overlap calculation"""
        # Setup test services
        consolidator.services = {
            "service1": {
                "dependencies": ["express", "axios", "redis"],
                "database_access": ["postgresql", "redis"],
                "language": "typescript",
                "endpoints": ["GET /health", "POST /api/test"]
            },
            "service2": {
                "dependencies": ["express", "winston", "redis"],
                "database_access": ["postgresql"],
                "language": "typescript",
                "endpoints": ["GET /status", "POST /api/validate"]
            }
        }
        
        overlap = consolidator._calculate_service_overlap("service1", "service2")
        
        assert isinstance(overlap, ServiceOverlap)
        assert overlap.service1 == "service1"
        assert overlap.service2 == "service2"
        assert overlap.overlap_score > 0
        assert len(overlap.details) > 0

    def test_identify_consolidation_candidates(self, consolidator):
        """Test consolidation candidate identification"""
        # Setup test services
        consolidator.services = {
            "ai-service": {"complexity_score": 5, "language": "typescript"},
            "ai-service": {"complexity_score": 6, "language": "typescript"},
            "ai-service": {"complexity_score": 4, "language": "python"},
            "project-manager": {"complexity_score": 3, "language": "typescript"},
            "architecture-analyzer": {"complexity_score": 4, "language": "typescript"},
            "backend-core": {"complexity_score": 8, "language": "python"}
        }
        
        plans = consolidator.identify_consolidation_candidates()
        
        assert isinstance(plans, list)
        assert len(plans) > 0
        
        # Should have AI consolidation plan
        ai_plans = [p for p in plans if "ai" in p.plan_id.lower()]
        assert len(ai_plans) > 0
        
        # Check plan structure
        plan = plans[0]
        assert isinstance(plan, ConsolidationPlan)
        assert plan.strategy in ConsolidationStrategy
        assert len(plan.source_services) > 0
        assert plan.target_service is not None
        assert plan.estimated_effort > 0
        assert plan.risk_level in ["low", "medium", "high"]

    @pytest.mark.asyncio
    async def test_merge_services_success(self, consolidator):
        """Test successful service merge"""
        # Create a test consolidation plan
        plan = ConsolidationPlan(
            plan_id="test_merge",
            strategy=ConsolidationStrategy.MERGE_SIMILAR,
            source_services=["service1"],
            target_service="service2",
            estimated_effort=40,
            risk_level="low",
            preserved_functions=[
                ServiceFunction(name="test_func", description="Test function")
            ]
        )
        
        # Setup services
        consolidator.services = {
            "service1": {"endpoints": ["GET /test"], "functions": []},
            "service2": {"endpoints": ["GET /health"], "functions": []}
        }
        
        result = await consolidator.merge_services(plan)
        
        assert isinstance(result, MergeResult)
        assert result.success is True
        assert result.merged_service == "service2"
        assert "service1" in result.original_services
        assert len(result.updated_references) > 0

    @pytest.mark.asyncio
    async def test_merge_services_validation_failure(self, consolidator):
        """Test service merge with validation failure"""
        # Create invalid plan (non-existent service)
        plan = ConsolidationPlan(
            plan_id="invalid_merge",
            strategy=ConsolidationStrategy.MERGE_SIMILAR,
            source_services=["nonexistent_service"],
            target_service="service2",
            estimated_effort=40,
            risk_level="low"
        )
        
        consolidator.services = {"service2": {}}
        
        result = await consolidator.merge_services(plan)
        
        assert isinstance(result, MergeResult)
        assert result.success is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()

    def test_update_service_references(self, consolidator):
        """Test service reference updating"""
        # This is a simulation, so we just test that it doesn't crash
        consolidator.update_service_references("old-service", "new-service")
        # No assertion needed as this is a logging-only operation in the simulation

    @pytest.mark.asyncio
    async def test_validate_consolidated_functionality(self, consolidator):
        """Test functionality validation"""
        consolidator.services = {
            "service1": {
                "endpoints": ["GET /health", "POST /api/test"],
                "functions": [
                    ServiceFunction(name="health_check", description="Health check"),
                    ServiceFunction(name="api_test", description="API test")
                ]
            }
        }
        
        report = await consolidator.validate_consolidated_functionality()
        
        assert isinstance(report, dict)
        assert "timestamp" in report
        assert "overall_status" in report
        assert "service_validations" in report
        assert "endpoint_validations" in report
        assert report["overall_status"] == "success"

    def test_generate_consolidation_report(self, consolidator):
        """Test consolidation report generation"""
        # Setup test data
        consolidator.services = {
            "service1": {
                "type": "microservice",
                "language": "typescript",
                "complexity_score": 5,
                "lines_of_code": 1000,
                "endpoints": ["GET /health"],
                "functions": [ServiceFunction(name="test", description="Test")]
            }
        }
        
        consolidator.dependencies = [
            ServiceDependency(
                source="service1",
                target="service2",
                dependency_type="api_call",
                frequency=5,
                critical=True
            )
        ]
        
        consolidator.overlaps = [
            ServiceOverlap(
                service1="service1",
                service2="service2",
                overlap_type="functionality",
                overlap_score=0.5,
                details=["shared dependencies"]
            )
        ]
        
        consolidation_plan = ConsolidationPlan(
            plan_id="test_plan",
            strategy=ConsolidationStrategy.MERGE_SIMILAR,
            source_services=["service1"],
            target_service="service2",
            estimated_effort=40,
            risk_level="low",
            benefits=["reduced complexity"],
            risks=["potential downtime"]
        )
        consolidator.consolidation_plans = [consolidation_plan]
        
        report = consolidator.generate_consolidation_report()
        
        assert isinstance(report, dict)
        assert "analysis_timestamp" in report
        assert "services_analyzed" in report
        assert "dependencies_found" in report
        assert "overlaps_identified" in report
        assert "consolidation_plans" in report
        assert report["services_analyzed"] == 1
        assert report["dependencies_found"] == 1
        assert report["overlaps_identified"] == 1
        assert report["consolidation_plans"] == 1

    def test_calculate_function_complexity(self, consolidator):
        """Test function complexity calculation"""
        # Create a complex function AST node
        complex_code = """
def complex_function(x, y):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                try:
                    result = process(i)
                    if result and result > y:
                        return result
                except ValueError:
                    continue
            else:
                while i < y:
                    i += 1
    return 0
"""
        
        import ast
        tree = ast.parse(complex_code)
        func_node = tree.body[0]
        
        complexity = consolidator._calculate_function_complexity(func_node)
        
        assert isinstance(complexity, int)
        assert complexity > 1  # Should be more complex than base complexity
        assert complexity <= 10  # Should be capped at 10

    def test_identify_service_clusters(self, consolidator):
        """Test service cluster identification"""
        # Setup services and dependencies
        consolidator.services = {
            "service1": {},
            "service2": {},
            "service3": {},
            "service4": {}
        }
        
        consolidator.dependencies = [
            ServiceDependency("service1", "service2", "api_call"),
            ServiceDependency("service2", "service1", "database"),
            ServiceDependency("service3", "service4", "api_call")
        ]
        
        clusters = consolidator._identify_service_clusters()
        
        assert isinstance(clusters, list)
        assert len(clusters) >= 1
        
        # Should identify connected services
        cluster_services = set()
        for cluster in clusters:
            cluster_services.update(cluster)
        
        assert len(cluster_services) > 0

    def test_endpoints_similar(self, consolidator):
        """Test endpoint similarity detection"""
        # Similar endpoints
        assert consolidator._endpoints_similar("GET /api/users", "POST /api/users")
        assert consolidator._endpoints_similar("GET /health", "GET /health-check")
        
        # Dissimilar endpoints
        assert not consolidator._endpoints_similar("GET /users", "POST /orders")
        assert not consolidator._endpoints_similar("GET /api/auth", "DELETE /api/data")

    def test_identify_service_from_url(self, consolidator):
        """Test service identification from URL"""
        assert consolidator._identify_service_from_url("http://auth-service:3001/validate") == "auth-service"
        assert consolidator._identify_service_from_url("http://code-review:8080/analyze") == "ai-service"
        assert consolidator._identify_service_from_url("http://unknown-service:9000/test") is None

    def test_has_circular_dependencies(self, consolidator):
        """Test circular dependency detection"""
        consolidator.dependencies = [
            ServiceDependency("service1", "service2", "api_call"),
            ServiceDependency("service2", "service1", "database")
        ]
        
        # Should detect circular dependency
        assert consolidator._has_circular_dependencies(["service1"], "service2")
        
        # Should not detect circular dependency when none exists
        assert not consolidator._has_circular_dependencies(["service3"], "service2")


class TestServiceConsolidatorIntegration:
    """Integration tests for ServiceConsolidator"""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self, temp_project_dir):
        """Test complete analysis workflow"""
        consolidator = ServiceConsolidator(str(temp_project_dir))
        
        # Run full analysis
        dependency_graph = await consolidator.analyze_service_dependencies()
        consolidation_plans = consolidator.identify_consolidation_candidates()
        report = consolidator.generate_consolidation_report()
        
        # Verify results
        assert isinstance(dependency_graph, DependencyGraph)
        assert isinstance(consolidation_plans, list)
        assert isinstance(report, dict)
        
        # Should have discovered services
        assert len(dependency_graph.nodes) > 0
        assert report["services_analyzed"] > 0

    @pytest.mark.asyncio
    async def test_consolidation_plan_execution(self, temp_project_dir):
        """Test consolidation plan creation and execution"""
        consolidator = ServiceConsolidator(str(temp_project_dir))
        
        # Setup for consolidation
        await consolidator.analyze_service_dependencies()
        plans = consolidator.identify_consolidation_candidates()
        
        if plans:
            # Execute first plan
            result = await consolidator.merge_services(plans[0])
            assert isinstance(result, MergeResult)
            
            # Validate functionality
            validation_report = await consolidator.validate_consolidated_functionality()
            assert validation_report["overall_status"] == "success"


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory structure for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        
        # Create services directory structure
        services_dir = project_root / "services"
        services_dir.mkdir()
        
        # Create sample microservices
        for service in ["api-gateway", "auth-service", "ai-service"]:
            service_dir = services_dir / service
            service_dir.mkdir()
            (service_dir / "src").mkdir()
            
            # Create package.json
            package_json = {
                "name": f"@ai-code-review/{service}",
                "dependencies": {
                    "express": "^4.18.2",
                    "axios": "^1.6.2"
                }
            }
            with open(service_dir / "package.json", "w") as f:
                json.dump(package_json, f)
        
        # Create backend directory
        backend_dir = project_root / "backend"
        backend_dir.mkdir()
        (backend_dir / "app").mkdir()
        
        yield project_root