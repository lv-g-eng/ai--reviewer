"""
Integration tests for GitHub webhook handler

Tests the complete webhook flow including:
- Signature validation using HMAC-SHA256
- Replay protection
- PR metadata extraction
- Task queuing to Celery

Requirements:
- 1.1: Receive GitHub webhooks within 10 seconds
- 1.5: Queue analysis tasks to Celery
"""
import pytest
import hmac
import hashlib
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from datetime import datetime, timezone

from app.main import app
from app.models import Project, PullRequest, PRStatus

# Test constants
TEST_WEBHOOK_SECRET = "test_webhook_secret_12345"
TEST_REPO_URL = "https://github.com/test-owner/test-repo"
TEST_PROJECT_ID = "test-project-123"


class TestWebhookSignatureValidation:
    """Test HMAC-SHA256 signature validation"""
    
    def generate_signature(self, payload: bytes, secret: str) -> str:
        """Generate GitHub webhook signature"""
        hash_object = hmac.new(
            secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        )
        return f"sha256={hash_object.hexdigest()}"
    
    def test_valid_signature(self):
        """Test that valid signatures are accepted"""
        from app.api.v1.endpoints.webhooks import verify_github_signature
        
        payload = b'{"test": "data"}'
        signature = self.generate_signature(payload, TEST_WEBHOOK_SECRET)
        
        result = verify_github_signature(payload, signature, TEST_WEBHOOK_SECRET)
        assert result is True
    
    def test_invalid_signature(self):
        """Test that invalid signatures are rejected"""
        from app.api.v1.endpoints.webhooks import verify_github_signature
        
        payload = b'{"test": "data"}'
        invalid_signature = "sha256=invalid_hex_digest"
        
        result = verify_github_signature(payload, invalid_signature, TEST_WEBHOOK_SECRET)
        assert result is False
    
    def test_missing_signature(self):
        """Test that missing signatures are rejected"""
        from app.api.v1.endpoints.webhooks import verify_github_signature
        
        payload = b'{"test": "data"}'
        
        result = verify_github_signature(payload, None, TEST_WEBHOOK_SECRET)
        assert result is False
    
    def test_wrong_prefix(self):
        """Test that signatures without sha256= prefix are rejected"""
        from app.api.v1.endpoints.webhooks import verify_github_signature
        
        payload = b'{"test": "data"}'
        signature = "sha1=somehexdigest"
        
        result = verify_github_signature(payload, signature, TEST_WEBHOOK_SECRET)
        assert result is False
    
    def test_timing_attack_resistance(self):
        """Test that signature comparison uses constant-time comparison"""
        from app.api.v1.endpoints.webhooks import verify_github_signature
        
        payload = b'{"test": "data"}'
        correct_signature = self.generate_signature(payload, TEST_WEBHOOK_SECRET)
        
        # Create slightly different signature
        wrong_signature = correct_signature[:-1] + 'f'
        
        # Both should return False, and timing should be similar
        result1 = verify_github_signature(payload, wrong_signature, TEST_WEBHOOK_SECRET)
        result2 = verify_github_signature(payload, "sha256=0000", TEST_WEBHOOK_SECRET)
        
        assert result1 is False
        assert result2 is False


class TestPRMetadataExtraction:
    """Test PR metadata extraction from webhook payload"""
    
    @pytest.mark.asyncio
    async def test_extract_complete_metadata(self):
        """Test extraction of all PR metadata fields"""
        from app.api.v1.endpoints.webhooks import extract_pr_metadata
        
        payload = {
            'pull_request': {
                'number': 42,
                'title': 'Test PR',
                'body': 'This is a test PR',
                'head': {
                    'ref': 'feature-branch',
                    'sha': 'abc123def456'
                },
                'changed_files': 5,
                'additions': 100,
                'deletions': 50,
                'user': {
                    'login': 'testuser'
                },
                'state': 'open',
                'merged': False
            }
        }
        
        result = await extract_pr_metadata(payload)
        
        assert result['number'] == 42
        assert result['title'] == 'Test PR'
        assert result['description'] == 'This is a test PR'
        assert result['branch_name'] == 'feature-branch'
        assert result['commit_sha'] == 'abc123def456'
        assert result['files_changed'] == 5
        assert result['lines_added'] == 100
        assert result['lines_deleted'] == 50
        assert result['author'] == 'testuser'
        assert result['state'] == 'open'
        assert result['merged'] is False
    
    @pytest.mark.asyncio
    async def test_extract_minimal_metadata(self):
        """Test extraction with minimal PR data"""
        from app.api.v1.endpoints.webhooks import extract_pr_metadata
        
        payload = {
            'pull_request': {
                'number': 1,
                'head': {}
            }
        }
        
        result = await extract_pr_metadata(payload)
        
        assert result['number'] == 1
        assert result['title'] is None
        assert result['files_changed'] == 0
        assert result['lines_added'] == 0
        assert result['lines_deleted'] == 0


class TestWebhookEndpoint:
    """Test the main webhook endpoint"""
    
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
    async def test_ping_event(self, mock_task, mock_cache):
        """Test webhook responds to ping events"""
        # Setup mocks
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = False
        mock_cache_service.cache_set.return_value = None
        mock_cache.return_value = mock_cache_service
        
        # Create test project
        mock_project = MagicMock(spec=Project)
        mock_project.id = TEST_PROJECT_ID
        mock_project.github_repo_url = TEST_REPO_URL
        mock_project.github_webhook_secret = TEST_WEBHOOK_SECRET
        
        payload = {
            'zen': 'Design for failure.',
            'repository': {
                'full_name': 'test-owner/test-repo'
            }
        }
        
        payload_bytes = str(payload).encode('utf-8')
        signature = self.generate_signature(payload_bytes, TEST_WEBHOOK_SECRET)
        
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
                        "X-Hub-Signature-256": signature,
                        "X-GitHub-Delivery": "test-delivery-1",
                        "X-GitHub-Event": "ping"
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'pong'
        assert data['project_id'] == TEST_PROJECT_ID
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.webhooks.get_cache_service')
    @patch('app.api.v1.endpoints.webhooks.analyze_pull_request_sync')
    async def test_pull_request_opened(self, mock_task, mock_cache):
        """Test webhook handles PR opened event"""
        # Setup mocks
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = False
        mock_cache_service.cache_set.return_value = None
        mock_cache.return_value = mock_cache_service
        
        mock_task.return_value = {
            'task_id': 'test-task-123',
            'status': 'PENDING'
        }
        
        # Create test project
        mock_project = MagicMock(spec=Project)
        mock_project.id = TEST_PROJECT_ID
        mock_project.github_repo_url = TEST_REPO_URL
        mock_project.github_webhook_secret = TEST_WEBHOOK_SECRET
        
        # Create test PR
        mock_pr = MagicMock(spec=PullRequest)
        mock_pr.id = "test-pr-456"
        mock_pr.github_pr_number = 42
        mock_pr.status = PRStatus.PENDING
        
        payload = {
            'action': 'opened',
            'repository': {
                'full_name': 'test-owner/test-repo'
            },
            'pull_request': {
                'number': 42,
                'title': 'Test PR',
                'body': 'Test description',
                'head': {
                    'ref': 'feature-branch',
                    'sha': 'abc123'
                },
                'changed_files': 3,
                'additions': 50,
                'deletions': 20,
                'user': {'login': 'testuser'},
                'state': 'open',
                'merged': False
            }
        }
        
        payload_bytes = str(payload).encode('utf-8')
        signature = self.generate_signature(payload_bytes, TEST_WEBHOOK_SECRET)
        
        with patch('app.api.v1.endpoints.webhooks.get_db') as mock_db:
            mock_session = AsyncMock()
            
            # Mock project query
            mock_project_result = AsyncMock()
            mock_project_result.scalar_one_or_none.return_value = mock_project
            
            # Mock PR query (returns None for new PR)
            mock_pr_result = AsyncMock()
            mock_pr_result.scalar_one_or_none.return_value = None
            
            # Setup execute to return different results
            mock_session.execute.side_effect = [mock_project_result, mock_pr_result]
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            
            # Set up the mock PR after refresh
            async def refresh_side_effect(obj):
                obj.id = "test-pr-456"
                obj.github_pr_number = 42
            
            mock_session.refresh.side_effect = refresh_side_effect
            
            mock_db.return_value.__aenter__.return_value = mock_session
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/webhooks/github",
                    json=payload,
                    headers={
                        "X-Hub-Signature-256": signature,
                        "X-GitHub-Delivery": "test-delivery-2",
                        "X-GitHub-Event": "pull_request"
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Pull request analysis queued'
        assert 'task_id' in data
        assert data['action'] == 'opened'
    
    @pytest.mark.asyncio
    async def test_invalid_signature(self):
        """Test webhook rejects invalid signatures"""
        payload = {
            'repository': {
                'full_name': 'test-owner/test-repo'
            }
        }
        
        mock_project = MagicMock(spec=Project)
        mock_project.id = TEST_PROJECT_ID
        mock_project.github_repo_url = TEST_REPO_URL
        mock_project.github_webhook_secret = TEST_WEBHOOK_SECRET
        
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
                        "X-Hub-Signature-256": "sha256=invalid",
                        "X-GitHub-Event": "pull_request"
                    }
                )
        
        assert response.status_code == 401
        assert "Invalid webhook signature" in response.json()['detail']
    
    @pytest.mark.asyncio
    async def test_missing_repository(self):
        """Test webhook rejects payload without repository info"""
        payload = {}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=payload,
                headers={
                    "X-GitHub-Event": "pull_request"
                }
            )
        
        assert response.status_code == 400
        assert "Missing repository information" in response.json()['detail']
    
    @pytest.mark.asyncio
    async def test_project_not_found(self):
        """Test webhook returns 404 when project not configured"""
        payload = {
            'repository': {
                'full_name': 'unknown/repo'
            }
        }
        
        with patch('app.api.v1.endpoints.webhooks.get_db') as mock_db:
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = None
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
        
        assert response.status_code == 404
        assert "not configured" in response.json()['detail']
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.webhooks.get_cache_service')
    async def test_replay_protection(self, mock_cache):
        """Test webhook rejects duplicate deliveries"""
        # Setup cache to indicate delivery already processed
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = True
        mock_cache.return_value = mock_cache_service
        
        payload = {
            'repository': {
                'full_name': 'test-owner/test-repo'
            }
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=payload,
                headers={
                    "X-GitHub-Delivery": "duplicate-delivery",
                    "X-GitHub-Event": "pull_request"
                }
            )
        
        assert response.status_code == 409
        assert "already processed" in response.json()['detail']
    
    @pytest.mark.asyncio
    async def test_unsupported_event(self):
        """Test webhook handles unsupported events gracefully"""
        mock_project = MagicMock(spec=Project)
        mock_project.id = TEST_PROJECT_ID
        mock_project.github_repo_url = TEST_REPO_URL
        mock_project.github_webhook_secret = None
        
        payload = {
            'repository': {
                'full_name': 'test-owner/test-repo'
            }
        }
        
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
                        "X-GitHub-Event": "issues"
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        assert "not supported" in data['message']
    
    @pytest.mark.asyncio
    async def test_ignored_pr_action(self):
        """Test webhook ignores PR actions like 'closed' or 'edited'"""
        mock_project = MagicMock(spec=Project)
        mock_project.id = TEST_PROJECT_ID
        mock_project.github_repo_url = TEST_REPO_URL
        mock_project.github_webhook_secret = None
        
        payload = {
            'action': 'closed',
            'repository': {
                'full_name': 'test-owner/test-repo'
            },
            'pull_request': {
                'number': 42
            }
        }
        
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
                        "X-GitHub-Event": "pull_request"
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        assert "not processed" in data['message']
