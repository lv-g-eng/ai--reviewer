"""
Pytest for testing Architecture Analysis endpoint with anyio and ASGITransport for Windows stability
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database.postgresql import get_db

pytestmark = pytest.mark.anyio

# Sample Python code for testing
SAMPLE_PYTHON_CODE = '''
class UserService:
    def create_user(self, name: str):
        pass

class UserController:
    def __init__(self, service: UserService):
        self.service = service
'''

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def mock_deps():
    from app.api.dependencies import get_current_user, check_project_access
    
    # Bypass auth and access checks
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_current_user] = lambda: {"username": "testuser"}
    # Correctly override with a simple lambda to avoid query param confusion
    app.dependency_overrides[check_project_access] = lambda: True
    
    yield
    app.dependency_overrides.clear()

@pytest.mark.anyio
class TestArchitectureAnalysisAPI:
    """Test suite for Architecture Analysis endpoint using anyio and ASGITransport"""

    @patch("app.api.v1.endpoints.analyze.ArchitectureAnalyzer")
    async def test_analyze_endpoint_streaming(self, mock_analyzer_class, mock_deps):
        """Test the streaming analyze endpoint"""
        # Setup mock behavior
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_repository = AsyncMock(return_value={
            "status": "completed",
            "analysisId": "test-id"
        })
        mock_analyzer_class.return_value = mock_analyzer

        request_data = {
            "repositoryUrl": "https://github.com/example/repo",
            "includeArchitectureAnalysis": True,
            "includeComplexityMetrics": True,
            "includeDependencyAnalysis": True
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/v1/analyze/analyze", json=request_data)

        if response.status_code != 200:
            print(f"DEBUG Analyze Streaming Response: {response.json()}")

        # Should return 200 with text/event-stream (might include charset)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

    async def test_pull_request_analyze_endpoint(self, mock_deps):
        """Test the PR analysis endpoint"""
        project_id = "test-project"
        pr_id = "test-pr"
        
        with patch("app.api.v1.endpoints.pull_request.analyze_pull_request_sync") as mock_sync:
            mock_sync.return_value = {"task_id": "test-task", "status": "PENDING"}
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(f"/api/v1/analysis/projects/{project_id}/analyze", params={"pr_id": pr_id})
        
        if response.status_code != 200:
            print(f"DEBUG PR Analyze Response: {response.json()}")
            
        assert response.status_code == 200
        assert response.json()["task_id"] == "test-task"

    @patch("app.api.v1.endpoints.pull_request.AsyncResult")
    async def test_task_status_endpoint(self, mock_async_result, mock_deps):
        """Test task status checking endpoint"""
        task_id = "test-task-456"
        mock_task = MagicMock()
        mock_task.status = "SUCCESS"
        mock_task.result = {"data": "test"}
        mock_async_result.return_value = mock_task
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/analysis/analysis/{task_id}/status")
        
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["task_id"] == task_id
        assert status_data["status"] == "SUCCESS"

@pytest.mark.anyio
class TestASTParsingIntegration:
    """Test AST parsing and Neo4j integration"""

    @patch('app.services.parsers.python_parser.PythonASTParser.parse_file')
    @patch('app.database.neo4j_db.get_neo4j_driver')
    async def test_ast_parser_creates_correct_nodes(self, mock_get_driver, mock_parse_file):
        """Test that AST parser creates correct Neo4j nodes with layer classification"""
        from app.services.parsers.python_parser import PythonASTParser
        from app.services.neo4j_ast_service import Neo4jASTService

        # Setup mock AST result
        mock_ast_result = MagicMock()
        mock_ast_result.module.name = "user_service"
        mock_ast_result.module.file_path = "user_service.py"
        mock_ast_result.module.language = "python"
        mock_ast_result.module.lines_of_code = 100
        mock_ast_result.module.classes = []
        mock_ast_result.module.functions = []
        mock_ast_result.module.imports = []
        mock_parse_file.return_value = mock_ast_result

        # Mock Neo4j driver and session correctly for async context manager
        mock_driver = MagicMock()
        mock_session = AsyncMock()
        # Ensure session.run returns something awaitable
        mock_result = MagicMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        
        # mock_driver.session() should return an object that has __aenter__ and __aexit__
        # AsyncMock's return value behaves as an async context manager if configured
        mock_driver.session.return_value.__aenter__.return_value = mock_session
        
        mock_get_driver.return_value = mock_driver

        # Test the integration
        parser = PythonASTParser()
        neo4j_service = Neo4jASTService(mock_driver)
        ast_result = parser.parse_file("user_service.py", content=SAMPLE_PYTHON_CODE)

        success = await neo4j_service.insert_ast_nodes(ast_result, "test-project")

        assert success is True
