"""
Tests for PR Analysis Workflow Tasks

Tests the complete workflow:
1. parse_pull_request_files
2. build_dependency_graph
3. analyze_with_llm
4. post_review_comments

Validates Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.tasks.pull_request_analysis import (
    analyze_pull_request_workflow
)


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def mock_pr():
    """Mock PullRequest model"""
    pr = Mock()
    pr.id = "pr-123"
    pr.title = "Add new feature"
    pr.description = "This PR adds a new feature"
    pr.commit_sha = "abc123"
    pr.files_changed = 3
    pr.github_pr_number = 42
    pr.status = "pending"
    return pr


@pytest.fixture
def mock_project():
    """Mock Project model"""
    project = Mock()
    project.id = "project-456"
    project.github_repo_url = "https://github.com/owner/repo"
    project.language = "Python"
    return project


@pytest.fixture
def mock_github_files():
    """Mock GitHub PR files"""
    return [
        {
            'filename': 'src/main.py',
            'status': 'modified',
            'additions': 10,
            'deletions': 5,
            'patch': '@@ -1,5 +1,10 @@\n+def new_function():\n+    pass'
        },
        {
            'filename': 'src/utils.py',
            'status': 'added',
            'additions': 20,
            'deletions': 0,
            'patch': '@@ -0,0 +1,20 @@\n+class Utils:\n+    pass'
        }
    ]


@pytest.fixture
def mock_parsed_entities():
    """Mock parsed code entities"""
    return [
        {
            'name': 'new_function',
            'entity_type': 'function',
            'file_path': 'src/main.py',
            'complexity': 2,
            'lines_of_code': 5,
            'dependencies': []
        },
        {
            'name': 'Utils',
            'entity_type': 'class',
            'file_path': 'src/utils.py',
            'complexity': 1,
            'lines_of_code': 10,
            'dependencies': []
        }
    ]


@pytest.fixture
def mock_parse_result(mock_parsed_entities):
    """Mock result from parse_pull_request_files"""
    return {
        'pr_id': 'pr-123',
        'project_id': 'project-456',
        'parsed_entities': mock_parsed_entities,
        'file_contents': {
            'src/main.py': 'def new_function():\n    pass',
            'src/utils.py': 'class Utils:\n    pass'
        },
        'full_diff': 'diff --git a/src/main.py b/src/main.py\n@@ -1,5 +1,10 @@',
        'pr_data': {
            'title': 'Add new feature',
            'description': 'This PR adds a new feature',
            'commit_sha': 'abc123',
            'files_changed': 2,
            'github_pr_number': 42
        },
        'project_data': {
            'repo_full_name': 'owner/repo',
            'language': 'Python'
        }
    }


@pytest.fixture
def mock_graph_result(mock_parse_result):
    """Mock result from build_dependency_graph"""
    return {
        **mock_parse_result,
        'graph_stats': {
            'nodes_created': 2,
            'nodes_updated': 0,
            'relationships_created': 0,
            'relationships_updated': 0,
            'errors': []
        }
    }


@pytest.fixture
def mock_llm_analysis():
    """Mock LLM analysis result"""
    return {
        'issues': [
            {
                'severity': 'warning',
                'message': 'Function lacks documentation',
                'file': 'src/main.py',
                'line': 1
            }
        ],
        'summary': 'Overall code quality is good',
        'risk_score': 30,
        'total_issues': 1,
        'critical_issues': 0,
        'provider_used': 'openai',
        'tokens_used': 500,
        'cost': 0.01
    }


# ========================================
# TEST TASK 1: parse_pull_request_files
# ========================================

@pytest.mark.asyncio
async def test_parse_pull_request_files_success(
    mock_pr,
    mock_project,
    mock_github_files
):
    """Test successful PR file parsing"""
    with patch('app.tasks.pull_request_analysis.AsyncSessionLocal') as mock_session, \
         patch('app.tasks.pull_request_analysis.get_github_client') as mock_github, \
         patch('app.tasks.pull_request_analysis.OptimizedParser') as mock_parser, \
         patch('app.tasks.pull_request_analysis.CodeEntityExtractor') as mock_extractor:
        
        # Setup mocks
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db
        
        # Mock database queries
        mock_pr_result = Mock()
        mock_pr_result.scalar_one_or_none.return_value = mock_pr
        mock_project_result = Mock()
        mock_project_result.scalar_one_or_none.return_value = mock_project
        
        mock_db.execute.side_effect = [mock_pr_result, mock_project_result]
        
        # Mock GitHub client
        github_client = AsyncMock()
        github_client.get_pr_files.return_value = mock_github_files
        github_client.get_file_content.return_value = "def new_function():\n    pass"
        mock_github.return_value = github_client
        
        # Mock parser
        parser_instance = Mock()
        mock_parsed_file = Mock()
        parser_instance.parse_file.return_value = (mock_parsed_file, 0.5)
        mock_parser.return_value = parser_instance
        
        # Mock extractor
        extractor_instance = Mock()
        mock_entity = Mock()
        mock_entity.name = 'new_function'
        mock_entity.entity_type = 'function'
        mock_entity.file_path = 'src/main.py'
        mock_entity.complexity = 2
        mock_entity.lines_of_code = 5
        mock_entity.dependencies = []
        extractor_instance.extract_from_parsed_file.return_value = [mock_entity]
        mock_extractor.return_value = extractor_instance
        
        # Execute task
        mock_task = Mock()
        from app.tasks.pull_request_analysis import _parse_pr_files
        result = await _parse_pr_files('pr-123', 'project-456', mock_task)
        
        # Assertions
        assert result['pr_id'] == 'pr-123'
        assert result['project_id'] == 'project-456'
        assert len(result['parsed_entities']) > 0
        assert 'full_diff' in result
        assert 'pr_data' in result
        assert 'project_data' in result


# ========================================
# TEST TASK 2: build_dependency_graph
# ========================================

@pytest.mark.asyncio
async def test_build_dependency_graph_success(mock_parse_result):
    """Test successful dependency graph building"""
    with patch('app.tasks.pull_request_analysis.GraphBuilderService') as mock_service:
        
        # Setup mocks
        service_instance = AsyncMock()
        
        # Mock graph builder results
        nodes_result = Mock()
        nodes_result.nodes_created = 2
        nodes_result.nodes_updated = 0
        nodes_result.errors = []
        
        rels_result = Mock()
        rels_result.relationships_created = 1
        rels_result.relationships_updated = 0
        rels_result.errors = []
        
        service_instance.create_or_update_entity_nodes_batch.return_value = nodes_result
        service_instance.create_dependency_relationships_batch.return_value = rels_result
        
        mock_service.return_value = service_instance
        
        # Execute task
        mock_task = Mock()
        from app.tasks.pull_request_analysis import _build_graph
        result = await _build_graph(mock_parse_result, mock_task)
        
        # Assertions
        assert 'graph_stats' in result
        assert result['graph_stats']['nodes_created'] == 2
        assert result['graph_stats']['relationships_created'] == 1
        assert result['pr_id'] == mock_parse_result['pr_id']


# ========================================
# TEST TASK 3: analyze_with_llm
# ========================================

@pytest.mark.asyncio
async def test_analyze_with_llm_success(mock_graph_result, mock_llm_analysis):
    """Test successful LLM analysis"""
    with patch('app.tasks.pull_request_analysis.LLMOrchestrator') as mock_orchestrator, \
         patch('app.tasks.pull_request_analysis.PromptManager') as mock_prompt_mgr, \
         patch('app.services.llm.response_parser.ResponseParser') as mock_parser:
        
        # Setup mocks
        orchestrator_instance = AsyncMock()
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Analysis result"
        mock_response.provider = "openai"
        mock_response.tokens = {'total': 500}
        mock_response.cost = 0.01
        
        orchestrator_instance.generate.return_value = mock_response
        mock_orchestrator.return_value = orchestrator_instance
        
        # Mock prompt manager
        prompt_mgr_instance = Mock()
        prompt_mgr_instance.get_prompt.return_value = "Analyze this PR"
        mock_prompt_mgr.return_value = prompt_mgr_instance
        
        # Mock response parser
        parser_instance = Mock()
        parser_instance.parse_code_review_response.return_value = {
            'issues': mock_llm_analysis['issues'],
            'summary': mock_llm_analysis['summary'],
            'risk_score': mock_llm_analysis['risk_score']
        }
        mock_parser.return_value = parser_instance
        
        # Execute task
        mock_task = Mock()
        mock_task.request.retries = 0
        from app.tasks.pull_request_analysis import _analyze_with_llm
        result = await _analyze_with_llm(mock_graph_result, mock_task)
        
        # Assertions
        assert 'llm_analysis' in result
        assert result['llm_analysis']['total_issues'] == 1
        assert result['llm_analysis']['risk_score'] == 30
        assert result['llm_analysis']['provider_used'] == 'openai'


# ========================================
# TEST TASK 4: post_review_comments
# ========================================

@pytest.mark.asyncio
async def test_post_review_comments_success(mock_graph_result, mock_llm_analysis, mock_pr):
    """Test successful posting of review comments"""
    analysis_result = {
        **mock_graph_result,
        'llm_analysis': mock_llm_analysis
    }
    
    with patch('app.tasks.pull_request_analysis.AsyncSessionLocal') as mock_session, \
         patch('app.tasks.pull_request_analysis.get_github_client') as mock_github:
        
        # Setup mocks
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db
        
        # Mock database query
        mock_pr_result = Mock()
        mock_pr_result.scalar_one_or_none.return_value = mock_pr
        mock_db.execute.return_value = mock_pr_result
        
        # Mock GitHub client
        github_client = AsyncMock()
        github_client.post_review_comment.return_value = {'id': 1}
        github_client.update_pr_status.return_value = {'state': 'success'}
        mock_github.return_value = github_client
        
        # Execute task
        mock_task = Mock()
        from app.tasks.pull_request_analysis import _post_comments
        result = await _post_comments(analysis_result, mock_task)
        
        # Assertions
        assert result['status'] == 'completed'
        assert result['comments_posted'] >= 0
        assert result['issues_found'] == 1
        assert result['risk_score'] == 30


# ========================================
# TEST WORKFLOW ORCHESTRATION
# ========================================

def test_analyze_pull_request_workflow():
    """Test workflow orchestration"""
    with patch('app.tasks.pull_request_analysis.chain') as mock_chain:
        
        # Setup mock
        mock_workflow = Mock()
        mock_result = Mock()
        mock_result.id = 'task-789'
        mock_workflow.apply_async.return_value = mock_result
        mock_chain.return_value = mock_workflow
        
        # Execute workflow
        result = analyze_pull_request_workflow('pr-123', 'project-456')
        
        # Assertions
        assert result['task_id'] == 'task-789'
        assert result['status'] == 'PENDING'
        assert result['pr_id'] == 'pr-123'
        assert result['project_id'] == 'project-456'
        assert len(result['workflow_tasks']) == 4
        assert 'parse_pull_request_files' in result['workflow_tasks']
        assert 'build_dependency_graph' in result['workflow_tasks']
        assert 'analyze_with_llm' in result['workflow_tasks']
        assert 'post_review_comments' in result['workflow_tasks']


# ========================================
# TEST ERROR HANDLING
# ========================================

@pytest.mark.asyncio
async def test_parse_pr_files_pr_not_found():
    """Test error handling when PR is not found"""
    with patch('app.tasks.pull_request_analysis.AsyncSessionLocal') as mock_session:
        
        # Setup mocks
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db
        
        # Mock database query returning None
        mock_pr_result = Mock()
        mock_pr_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_pr_result
        
        # Execute task and expect error
        mock_task = Mock()
        mock_task.request.retries = 0
        mock_task.retry.side_effect = Exception("Retry triggered")
        
        from app.tasks.pull_request_analysis import _parse_pr_files
        
        with pytest.raises(Exception):
            await _parse_pr_files('pr-123', 'project-456', mock_task)


@pytest.mark.asyncio
async def test_build_graph_with_errors(mock_parse_result):
    """Test graph building with errors"""
    with patch('app.tasks.pull_request_analysis.GraphBuilderService') as mock_service:
        
        # Setup mocks with errors
        service_instance = AsyncMock()
        
        nodes_result = Mock()
        nodes_result.nodes_created = 1
        nodes_result.nodes_updated = 0
        nodes_result.errors = ['Error creating node']
        
        rels_result = Mock()
        rels_result.relationships_created = 0
        rels_result.relationships_updated = 0
        rels_result.errors = []
        
        service_instance.create_or_update_entity_nodes_batch.return_value = nodes_result
        service_instance.create_dependency_relationships_batch.return_value = rels_result
        
        mock_service.return_value = service_instance
        
        # Execute task
        mock_task = Mock()
        from app.tasks.pull_request_analysis import _build_graph
        result = await _build_graph(mock_parse_result, mock_task)
        
        # Assertions - should complete despite errors
        assert 'graph_stats' in result
        assert len(result['graph_stats']['errors']) > 0


# ========================================
# INTEGRATION TEST
# ========================================

def test_workflow_task_chaining():
    """Test that workflow tasks are properly chained"""
    with patch('app.tasks.pull_request_analysis.chain') as mock_chain:
        
        # Setup mock
        mock_workflow = Mock()
        mock_result = Mock()
        mock_result.id = 'task-integration'
        mock_workflow.apply_async.return_value = mock_result
        mock_chain.return_value = mock_workflow
        
        # Execute workflow
        result = analyze_pull_request_workflow('pr-test', 'project-test')
        
        # Verify chain was called with correct tasks
        mock_chain.assert_called_once()
        
        # Verify apply_async was called with correct parameters
        mock_workflow.apply_async.assert_called_once()
        call_kwargs = mock_workflow.apply_async.call_args[1]
        assert call_kwargs['queue'] == 'high_priority'
        assert call_kwargs['expires'] == 3600
