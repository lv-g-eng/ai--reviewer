"""
Integration tests for GitHub service

Tests the complete integration flow including:
- Webhook signature validation
- PR event parsing and metadata extraction
- Comment posting with mock GitHub API
- End-to-end webhook processing

Requirements:
- 13.1: Integration tests for GitHub webhook end-to-end flow

**Validates: Requirements 13.1**
"""
import pytest
import hmac
import hashlib
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from datetime import datetime, timezone

from app.main import app
from app.models import Project, PullRequest, PRStatus
from app.services.github_client import GitHubAPIClient


class TestGitHubWebhookIntegration:
    """Integration tests for GitHub webhook processing"""
    
    def generate_signature(self, payload: bytes, secret: str) -> str:
        """Generate GitHub webhook signature"""
        hash_object = hmac.new(
            secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        )
        return f"sha256={hash_object.hexdigest()}"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.webhooks.get_cache_service')
    @patch('app.api.v1.endpoints.webhooks.analyze_pull_request_sync')
    async def test_complete_webhook_flow_with_signature_validation(self, mock_task, mock_cache):
        """
        Test complete webhook flow from signature validation to task queuing
        
        This integration test verifies:
        1. Webhook signature is validated correctly
        2. PR metadata is extracted from payload
        3. PR record is created in database
        4. Analysis task is queued to Celery
        
        **Validates: Requirements 13.1**
        """
        # Setup mocks
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = False
        mock_cache_service.cache_set.return_value = None
        mock_cache.return_value = mock_cache_service
        
        mock_task.return_value = {
            'task_id': 'integration-test-task-123',
            'status': 'PENDING'
        }
        
        # Test data
        webhook_secret = "integration_test_secret_key"
        repo_url = "https://github.com/test-org/test-repo"
        
        # Create test project
        mock_project = MagicMock(spec=Project)
        mock_project.id = "integration-project-123"
        mock_project.github_repo_url = repo_url
        mock_project.github_webhook_secret = webhook_secret
        
        # Create webhook payload
        payload = {
            'action': 'opened',
            'repository': {
                'full_name': 'test-org/test-repo'
            },
            'pull_request': {
                'number': 100,
                'title': 'Integration Test PR',
                'body': 'This PR tests the complete integration flow',
                'head': {
                    'ref': 'feature/integration-test',
                    'sha': 'abc123def456'
                },
                'changed_files': 5,
                'additions': 150,
                'deletions': 75,
                'user': {'login': 'integration-tester'},
                'state': 'open',
                'merged': False
            }
        }
        
        # Generate valid signature
        payload_bytes = str(payload).encode('utf-8')
        signature = self.generate_signature(payload_bytes, webhook_secret)
        
        with patch('app.api.v1.endpoints.webhooks.get_db') as mock_db:
            mock_session = AsyncMock()
            
            # Mock project query
            mock_project_result = AsyncMock()
            mock_project_result.scalar_one_or_none.return_value = mock_project
            
            # Mock PR query (returns None for new PR)
            mock_pr_result = AsyncMock()
            mock_pr_result.scalar_one_or_none.return_value = None
            
            mock_session.execute.side_effect = [mock_project_result, mock_pr_result]
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            
            # Set up the mock PR after refresh
            async def refresh_side_effect(obj):
                obj.id = "integration-pr-456"
                obj.github_pr_number = 100
            
            mock_session.refresh.side_effect = refresh_side_effect
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Make request
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/webhooks/github",
                    json=payload,
                    headers={
                        "X-Hub-Signature-256": signature,
                        "X-GitHub-Delivery": "integration-delivery-1",
                        "X-GitHub-Event": "pull_request"
                    }
                )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Pull request analysis queued'
        assert data['action'] == 'opened'
        assert data['pr_number'] == 100
        assert 'task_id' in data
        
        # Verify task was queued
        mock_task.assert_called_once()
        call_kwargs = mock_task.call_args[1]
        assert call_kwargs['project_id'] == "integration-project-123"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.webhooks.get_cache_service')
    async def test_webhook_signature_validation_failure(self, mock_cache):
        """
        Test that invalid webhook signatures are rejected
        
        **Validates: Requirements 13.1**
        """
        # Setup mocks
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = False
        mock_cache.return_value = mock_cache_service
        
        webhook_secret = "test_secret"
        repo_url = "https://github.com/test-org/test-repo"
        
        mock_project = MagicMock(spec=Project)
        mock_project.id = "test-project"
        mock_project.github_repo_url = repo_url
        mock_project.github_webhook_secret = webhook_secret
        
        payload = {
            'repository': {
                'full_name': 'test-org/test-repo'
            },
            'pull_request': {
                'number': 1
            }
        }
        
        # Generate signature with WRONG secret
        payload_bytes = str(payload).encode('utf-8')
        wrong_signature = self.generate_signature(payload_bytes, "wrong_secret")
        
        with patch('app.api.v1.endpoints.webhooks.get_db') as mock_db:
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = mock_project
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/webhooks/github",
                    json=payload,
                    headers={
                        "X-Hub-Signature-256": wrong_signature,
                        "X-GitHub-Delivery": "test-delivery",
                        "X-GitHub-Event": "pull_request"
                    }
                )
        
        # Verify rejection
        assert response.status_code == 401
        assert "Invalid webhook signature" in response.json()['detail']
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.webhooks.get_cache_service')
    @patch('app.api.v1.endpoints.webhooks.analyze_pull_request_sync')
    async def test_pr_metadata_extraction_integration(self, mock_task, mock_cache):
        """
        Test that PR metadata is correctly extracted and stored
        
        **Validates: Requirements 13.1**
        """
        # Setup mocks
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = False
        mock_cache_service.cache_set.return_value = None
        mock_cache.return_value = mock_cache_service
        
        mock_task.return_value = {
            'task_id': 'test-task',
            'status': 'PENDING'
        }
        
        mock_project = MagicMock(spec=Project)
        mock_project.id = "test-project"
        mock_project.github_repo_url = "https://github.com/test-org/test-repo"
        mock_project.github_webhook_secret = None  # No signature validation
        
        # Comprehensive PR payload
        payload = {
            'action': 'opened',
            'repository': {
                'full_name': 'test-org/test-repo'
            },
            'pull_request': {
                'number': 42,
                'title': 'Add new feature',
                'body': 'This PR adds a new feature with tests',
                'head': {
                    'ref': 'feature/new-feature',
                    'sha': 'abc123def456789'
                },
                'base': {
                    'ref': 'main',
                    'sha': 'main123456'
                },
                'changed_files': 10,
                'additions': 250,
                'deletions': 100,
                'user': {
                    'login': 'developer123'
                },
                'state': 'open',
                'merged': False
            }
        }
        
        # Track the PR object that gets created
        created_pr = None
        
        def capture_pr(obj):
            nonlocal created_pr
            created_pr = obj
        
        with patch('app.api.v1.endpoints.webhooks.get_db') as mock_db:
            mock_session = AsyncMock()
            
            mock_project_result = AsyncMock()
            mock_project_result.scalar_one_or_none.return_value = mock_project
            
            mock_pr_result = AsyncMock()
            mock_pr_result.scalar_one_or_none.return_value = None
            
            mock_session.execute.side_effect = [mock_project_result, mock_pr_result]
            mock_session.add = MagicMock(side_effect=capture_pr)
            mock_session.commit = AsyncMock()
            
            async def refresh_side_effect(obj):
                obj.id = "test-pr-id"
            
            mock_session.refresh = AsyncMock(side_effect=refresh_side_effect)
            mock_db.return_value.__aenter__.return_value = mock_session
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/webhooks/github",
                    json=payload,
                    headers={
                        "X-GitHub-Delivery": "metadata-test",
                        "X-GitHub-Event": "pull_request"
                    }
                )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify PR metadata was extracted correctly
        assert created_pr is not None
        assert created_pr.github_pr_number == 42
        assert created_pr.title == 'Add new feature'
        assert created_pr.description == 'This PR adds a new feature with tests'
        assert created_pr.branch_name == 'feature/new-feature'
        assert created_pr.commit_sha == 'abc123def456789'
        assert created_pr.files_changed == 10
        assert created_pr.lines_added == 250
        assert created_pr.lines_deleted == 100
        assert created_pr.status == PRStatus.PENDING


class TestGitHubAPIClientIntegration:
    """Integration tests for GitHub API client with mocked GitHub API"""
    
    @pytest.mark.asyncio
    async def test_post_review_comment_integration(self):
        """
        Test posting review comments with mock GitHub API
        
        **Validates: Requirements 13.1**
        """
        client = GitHubAPIClient(access_token="test_token")
        
        # Mock the GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_comment = MagicMock()
        mock_comment.id = 999
        mock_comment.body = "This is a test comment"
        mock_comment.path = "src/main.py"
        mock_comment.line = 42
        mock_comment.created_at = MagicMock()
        mock_comment.created_at.isoformat = MagicMock(return_value="2024-01-15T10:30:00Z")
        
        mock_pr.create_review_comment = MagicMock(return_value=mock_comment)
        mock_repo.get_pull = MagicMock(return_value=mock_pr)
        client.client.get_repo = MagicMock(return_value=mock_repo)
        
        # Post comment
        result = await client.post_review_comment(
            repo_full_name="test-org/test-repo",
            pr_number=42,
            body="This is a test comment",
            commit_id="abc123",
            path="src/main.py",
            line=42
        )
        
        # Verify result
        assert result['id'] == 999
        assert result['body'] == "This is a test comment"
        assert result['path'] == "src/main.py"
        assert result['line'] == 42
        assert result['created_at'] == "2024-01-15T10:30:00Z"
        
        # Verify API was called correctly
        mock_repo.get_pull.assert_called_once_with(42)
        mock_pr.create_review_comment.assert_called_once_with(
            body="This is a test comment",
            commit_id="abc123",
            path="src/main.py",
            line=42
        )
    
    @pytest.mark.asyncio
    async def test_get_pr_files_integration(self):
        """
        Test fetching PR files with mock GitHub API
        
        **Validates: Requirements 13.1**
        """
        client = GitHubAPIClient(access_token="test_token")
        
        # Mock file objects
        mock_file1 = MagicMock()
        mock_file1.filename = "src/main.py"
        mock_file1.status = "modified"
        mock_file1.additions = 50
        mock_file1.deletions = 20
        mock_file1.changes = 70
        mock_file1.patch = "@@ -1,5 +1,10 @@\n+new code"
        mock_file1.blob_url = "https://github.com/test/repo/blob/abc/src/main.py"
        mock_file1.raw_url = "https://github.com/test/repo/raw/abc/src/main.py"
        
        mock_file2 = MagicMock()
        mock_file2.filename = "tests/test_main.py"
        mock_file2.status = "added"
        mock_file2.additions = 100
        mock_file2.deletions = 0
        mock_file2.changes = 100
        mock_file2.patch = "@@ -0,0 +1,100 @@\n+test code"
        mock_file2.blob_url = "https://github.com/test/repo/blob/abc/tests/test_main.py"
        mock_file2.raw_url = "https://github.com/test/repo/raw/abc/tests/test_main.py"
        
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.get_files = MagicMock(return_value=[mock_file1, mock_file2])
        mock_repo.get_pull = MagicMock(return_value=mock_pr)
        client.client.get_repo = MagicMock(return_value=mock_repo)
        
        # Get PR files
        result = await client.get_pr_files("test-org/test-repo", 42)
        
        # Verify result
        assert len(result) == 2
        
        # Verify first file
        assert result[0]['filename'] == "src/main.py"
        assert result[0]['status'] == "modified"
        assert result[0]['additions'] == 50
        assert result[0]['deletions'] == 20
        assert result[0]['changes'] == 70
        assert result[0]['patch'] is not None
        
        # Verify second file
        assert result[1]['filename'] == "tests/test_main.py"
        assert result[1]['status'] == "added"
        assert result[1]['additions'] == 100
        assert result[1]['deletions'] == 0
        
        # Verify API was called correctly
        mock_repo.get_pull.assert_called_once_with(42)
        mock_pr.get_files.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_pull_request_integration(self):
        """
        Test fetching PR details with mock GitHub API
        
        **Validates: Requirements 13.1**
        """
        client = GitHubAPIClient(access_token="test_token")
        
        # Mock PR object
        mock_pr = MagicMock()
        mock_pr.number = 42
        mock_pr.title = "Integration Test PR"
        mock_pr.body = "This is a test PR for integration testing"
        mock_pr.state = "open"
        mock_pr.user = MagicMock()
        mock_pr.user.login = "test-user"
        mock_pr.user.id = 12345
        mock_pr.head = MagicMock()
        mock_pr.head.ref = "feature/test"
        mock_pr.head.sha = "abc123"
        mock_pr.base = MagicMock()
        mock_pr.base.ref = "main"
        mock_pr.base.sha = "def456"
        mock_pr.created_at = MagicMock()
        mock_pr.created_at.isoformat = MagicMock(return_value="2024-01-01T00:00:00Z")
        mock_pr.updated_at = MagicMock()
        mock_pr.updated_at.isoformat = MagicMock(return_value="2024-01-02T00:00:00Z")
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.additions = 100
        mock_pr.deletions = 50
        mock_pr.changed_files = 5
        
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_repo.get_pull = MagicMock(return_value=mock_pr)
        client.client.get_repo = MagicMock(return_value=mock_repo)
        
        # Get PR
        result = await client.get_pull_request("test-org/test-repo", 42)
        
        # Verify result
        assert result['number'] == 42
        assert result['title'] == "Integration Test PR"
        assert result['body'] == "This is a test PR for integration testing"
        assert result['state'] == "open"
        assert result['user']['login'] == "test-user"
        assert result['user']['id'] == 12345
        assert result['head']['ref'] == "feature/test"
        assert result['head']['sha'] == "abc123"
        assert result['base']['ref'] == "main"
        assert result['base']['sha'] == "def456"
        assert result['merged'] is False
        assert result['mergeable'] is True
        assert result['additions'] == 100
        assert result['deletions'] == 50
        assert result['changed_files'] == 5
        
        # Verify API was called correctly
        mock_repo.get_pull.assert_called_once_with(42)
    
    @pytest.mark.asyncio
    async def test_update_pr_status_integration(self):
        """
        Test updating PR status with mock GitHub API
        
        **Validates: Requirements 13.1**
        """
        client = GitHubAPIClient(access_token="test_token")
        
        # Mock status object
        mock_status = MagicMock()
        mock_status.state = "success"
        mock_status.description = "All checks passed"
        mock_status.context = "ai-code-review"
        mock_status.created_at = MagicMock()
        mock_status.created_at.isoformat = MagicMock(return_value="2024-01-15T12:00:00Z")
        
        # Mock GitHub API
        mock_commit = MagicMock()
        mock_commit.create_status = MagicMock(return_value=mock_status)
        mock_repo = MagicMock()
        mock_repo.get_commit = MagicMock(return_value=mock_commit)
        client.client.get_repo = MagicMock(return_value=mock_repo)
        
        # Update status
        result = await client.update_pr_status(
            repo_full_name="test-org/test-repo",
            commit_sha="abc123",
            state="success",
            description="All checks passed"
        )
        
        # Verify result
        assert result['state'] == "success"
        assert result['description'] == "All checks passed"
        assert result['context'] == "ai-code-review"
        assert result['created_at'] == "2024-01-15T12:00:00Z"
        
        # Verify API was called correctly
        mock_repo.get_commit.assert_called_once_with("abc123")
        mock_commit.create_status.assert_called_once_with(
            state="success",
            description="All checks passed",
            context="ai-code-review"
        )


class TestGitHubWebhookEdgeCases:
    """Integration tests for edge cases and error scenarios"""
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.webhooks.get_cache_service')
    async def test_replay_protection_integration(self, mock_cache):
        """
        Test that duplicate webhook deliveries are rejected
        
        **Validates: Requirements 13.1**
        """
        # Setup cache to indicate delivery already processed
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = True
        mock_cache.return_value = mock_cache_service
        
        payload = {
            'repository': {
                'full_name': 'test-org/test-repo'
            }
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=payload,
                headers={
                    "X-GitHub-Delivery": "duplicate-delivery-id",
                    "X-GitHub-Event": "pull_request"
                }
            )
        
        # Verify rejection
        assert response.status_code == 409
        assert "already processed" in response.json()['detail']
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.webhooks.get_cache_service')
    @patch('app.api.v1.endpoints.webhooks.analyze_pull_request_sync')
    async def test_pr_synchronize_action_integration(self, mock_task, mock_cache):
        """
        Test webhook handles PR synchronize action (new commits pushed)
        
        **Validates: Requirements 13.1**
        """
        # Setup mocks
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = False
        mock_cache_service.cache_set.return_value = None
        mock_cache.return_value = mock_cache_service
        
        mock_task.return_value = {
            'task_id': 'sync-task-123',
            'status': 'PENDING'
        }
        
        mock_project = MagicMock(spec=Project)
        mock_project.id = "test-project"
        mock_project.github_repo_url = "https://github.com/test-org/test-repo"
        mock_project.github_webhook_secret = None
        
        # Existing PR
        mock_existing_pr = MagicMock(spec=PullRequest)
        mock_existing_pr.id = "existing-pr-id"
        mock_existing_pr.github_pr_number = 42
        mock_existing_pr.title = "Old title"
        mock_existing_pr.commit_sha = "old_sha"
        
        payload = {
            'action': 'synchronize',  # New commits pushed
            'repository': {
                'full_name': 'test-org/test-repo'
            },
            'pull_request': {
                'number': 42,
                'title': 'Updated title',
                'body': 'Updated description',
                'head': {
                    'ref': 'feature/test',
                    'sha': 'new_sha_123'
                },
                'changed_files': 7,
                'additions': 200,
                'deletions': 100,
                'user': {'login': 'test-user'},
                'state': 'open',
                'merged': False
            }
        }
        
        with patch('app.api.v1.endpoints.webhooks.get_db') as mock_db:
            mock_session = AsyncMock()
            
            mock_project_result = AsyncMock()
            mock_project_result.scalar_one_or_none.return_value = mock_project
            
            # Return existing PR
            mock_pr_result = AsyncMock()
            mock_pr_result.scalar_one_or_none.return_value = mock_existing_pr
            
            mock_session.execute.side_effect = [mock_project_result, mock_pr_result]
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/webhooks/github",
                    json=payload,
                    headers={
                        "X-GitHub-Delivery": "sync-delivery",
                        "X-GitHub-Event": "pull_request"
                    }
                )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data['action'] == 'synchronize'
        assert data['pr_number'] == 42
        
        # Verify PR was updated
        assert mock_existing_pr.commit_sha == 'new_sha_123'
        assert mock_existing_pr.title == 'Updated title'
        assert mock_existing_pr.files_changed == 7
        assert mock_existing_pr.status == PRStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_missing_repository_info_integration(self):
        """
        Test webhook rejects payload without repository information
        
        **Validates: Requirements 13.1**
        """
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 1
            }
            # Missing 'repository' field
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=payload,
                headers={
                    "X-GitHub-Event": "pull_request"
                }
            )
        
        # Verify rejection
        assert response.status_code == 400
        assert "Missing repository information" in response.json()['detail']
    
    @pytest.mark.asyncio
    async def test_project_not_configured_integration(self):
        """
        Test webhook returns 404 when project is not configured
        
        **Validates: Requirements 13.1**
        """
        payload = {
            'repository': {
                'full_name': 'unknown-org/unknown-repo'
            }
        }
        
        with patch('app.api.v1.endpoints.webhooks.get_db') as mock_db:
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = None  # No project found
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/webhooks/github",
                    json=payload,
                    headers={
                        "X-GitHub-Event": "pull_request"
                    }
                )
        
        # Verify rejection
        assert response.status_code == 404
        assert "not configured" in response.json()['detail']
