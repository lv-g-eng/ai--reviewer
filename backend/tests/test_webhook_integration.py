"""
Integration test for webhook handler

Tests the complete webhook flow including signature validation,
payload processing, and task queuing.

Validates Requirements: 1.1
"""
import pytest
import hmac
import hashlib
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from httpx import AsyncClient
from datetime import datetime

from app.main import app


class TestWebhookIntegration:
    """Integration tests for webhook endpoint"""
    
    def generate_signature(self, payload: bytes, secret: str) -> str:
        """Generate valid GitHub webhook signature"""
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        return f"sha256={mac.hexdigest()}"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.code_review_webhook.get_cache_service')
    @patch('app.tasks.pull_request_analysis.analyze_pull_request')
    async def test_webhook_complete_flow(self, mock_task, mock_cache):
        """Test complete webhook flow from receipt to task queuing"""
        # Setup cache mock
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = False
        mock_cache_service.cache_set.return_value = True
        mock_cache.return_value = mock_cache_service
        
        # Setup database mock
        mock_session = AsyncMock()
        mock_project = Mock()
        mock_project.id = "project-123"
        mock_project.github_repo_url = "https://github.com/owner/repo"
        mock_project.github_webhook_secret = "test_secret"
        
        # Setup query results
        mock_project_result = Mock()
        mock_project_result.scalar_one_or_none.return_value = mock_project
        
        mock_pr_result = Mock()
        mock_pr_result.scalar_one_or_none.return_value = None  # New PR
        
        # Track execute calls
        execute_call_count = [0]
        
        async def mock_execute(stmt):
            execute_call_count[0] += 1
            if execute_call_count[0] == 1:
                return mock_project_result
            else:
                return mock_pr_result
        
        mock_session.execute = mock_execute
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Mock the PR object that gets created
        def mock_refresh_side_effect(obj):
            obj.id = "pr-456"
        
        mock_session.refresh.side_effect = mock_refresh_side_effect
        
        # Create async generator for database session
        async def mock_get_db():
            yield mock_session
        
        # Override the dependency
        from app.api.v1.endpoints.code_review_webhook import router
        from app.database.postgresql import get_db
        app.dependency_overrides[get_db] = mock_get_db
        
        # Mock Celery task
        mock_task_result = Mock()
        mock_task_result.id = "task-789"
        mock_task.apply_async.return_value = mock_task_result
        
        # Prepare webhook payload
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR',
                'body': 'Test description',
                'head': {
                    'ref': 'feature-branch',
                    'sha': 'abc123def456'
                },
                'changed_files': 5,
                'additions': 100,
                'deletions': 50
            },
            'repository': {
                'html_url': 'https://github.com/owner/repo',
                'full_name': 'owner/repo'
            },
            'sender': {
                'login': 'test_webhook_user'
            }
        }
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = self.generate_signature(payload_bytes, "test_secret")
        
        try:
            # Make request using AsyncClient
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/code-review/webhook",
                    json=payload,
                    headers={
                        'X-Hub-Signature-256': signature,
                        'X-GitHub-Delivery': 'delivery-123',
                        'X-GitHub-Event': 'pull_request'
                    }
                )
            
            # Verify response
            assert response.status_code == 202
            data = response.json()
            assert data['message'] == 'PR analysis queued'
            assert data['pr_number'] == 123
            assert 'task_id' in data
            assert 'processing_time_seconds' in data
            
            # Verify processing time is reasonable (< 5 seconds as per requirement)
            assert data['processing_time_seconds'] < 5.0
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_webhook_ping_event(self):
        """Test webhook responds to ping events"""
        payload = {'zen': 'Design for failure.'}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/code-review/webhook",
                json=payload,
                headers={
                    'X-GitHub-Event': 'ping'
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'pong'
    
    @pytest.mark.asyncio
    async def test_webhook_unsupported_event(self):
        """Test webhook handles unsupported events gracefully"""
        payload = {'action': 'created'}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/code-review/webhook",
                json=payload,
                headers={
                    'X-GitHub-Event': 'issues'
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert 'not supported' in data['message']
    
    @pytest.mark.asyncio
    async def test_webhook_invalid_json(self):
        """Test webhook rejects invalid JSON"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/code-review/webhook",
                content="invalid json",
                headers={
                    'X-GitHub-Event': 'pull_request',
                    'Content-Type': 'application/json'
                }
            )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.code_review_webhook.get_cache_service')
    async def test_webhook_duplicate_delivery(self, mock_cache):
        """Test webhook rejects duplicate deliveries"""
        # Setup mock cache to indicate delivery already processed
        mock_cache_service = AsyncMock()
        mock_cache_service.cache_exists.return_value = True
        mock_cache.return_value = mock_cache_service
        
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR',
                'head': {
                    'ref': 'feature',
                    'sha': 'abc123'
                }
            },
            'repository': {
                'html_url': 'https://github.com/owner/repo',
                'full_name': 'owner/repo'
            }
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/code-review/webhook",
                json=payload,
                headers={
                    'X-GitHub-Delivery': 'delivery-123',
                    'X-GitHub-Event': 'pull_request'
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert 'already processed' in data['message']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
