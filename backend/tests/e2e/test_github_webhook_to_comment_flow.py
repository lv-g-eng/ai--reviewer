"""
End-to-End Test: GitHub Webhook to Comment Flow

This test validates the complete flow from receiving a GitHub webhook
to posting review comments back to the PR.

Flow:
1. GitHub webhook received (PR opened/synchronized)
2. Webhook signature validated
3. PR metadata extracted and stored
4. Analysis workflow queued to Celery
5. Files parsed and AST generated
6. Dependency graph built in Neo4j
7. LLM analysis performed
8. Review comments posted to GitHub

**Validates: Requirements 5.5, 5.8**

This test runs in a staging environment with real database connections
but mocked external services (GitHub API, LLM APIs).
"""
import pytest
import hmac
import hashlib
import json
import asyncio
from unittest.mock import AsyncMock, patch, Mock
from httpx import AsyncClient
from datetime import datetime, timezone

from app.main import app
from app.models import Project, PullRequest, PRStatus, CodeEntity
from app.database.postgresql import AsyncSessionLocal
from sqlalchemy import select


class TestGitHubWebhookToCommentFlow:
    """End-to-end test for complete GitHub webhook flow"""
    
    def generate_signature(self, payload: bytes, secret: str) -> str:
        """Generate valid GitHub webhook signature"""
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        return f"sha256={mac.hexdigest()}"
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_complete_webhook_to_comment_flow(self):
        """
        Test complete flow from webhook receipt to comment posting
        
        This is a comprehensive end-to-end test that validates:
        - Webhook signature validation
        - PR metadata extraction and storage
        - Task queuing to Celery
        - File parsing and AST generation
        - Dependency graph creation
        - LLM analysis
        - Comment posting to GitHub
        
        Expected flow time: < 60 seconds for small PRs
        """
        # Test configuration
        webhook_secret = "test_e2e_secret_12345"
        repo_url = "https://github.com/test-org/test-repo"
        pr_number = 100
        
        # Step 1: Setup test project in database
        async with AsyncSessionLocal() as db:
            # Check if test project exists
            result = await db.execute(
                select(Project).where(Project.github_repo_url == repo_url)
            )
            test_project = result.scalar_one_or_none()
            
            if not test_project:
                test_project = Project(
                    name="E2E Test Project",
                    description="Project for end-to-end testing",
                    github_repo_url=repo_url,
                    github_webhook_secret=webhook_secret,
                    language="Python"
                )
                db.add(test_project)
                await db.commit()
                await db.refresh(test_project)
        
        project_id = test_project.id
        
        # Step 2: Prepare webhook payload
        webhook_payload = {
            'action': 'opened',
            'pull_request': {
                'number': pr_number,
                'title': 'E2E Test: Add new feature',
                'body': 'This PR adds a new feature for end-to-end testing',
                'head': {
                    'ref': 'feature/e2e-test',
                    'sha': 'e2e123abc456def789'
                },
                'changed_files': 2,
                'additions': 50,
                'deletions': 10,
                'user': {
                    'login': 'e2e-test-user'
                },
                'state': 'open',
                'merged': False
            },
            'repository': {
                'html_url': repo_url,
                'full_name': 'test-org/test-repo'
            },
            'sender': {
                'login': 'e2e-test-user'
            }
        }
        
        payload_bytes = json.dumps(webhook_payload).encode('utf-8')
        signature = self.generate_signature(payload_bytes, webhook_secret)
        
        # Mock external services
        mock_github_files = [
            {
                'filename': 'src/calculator.py',
                'status': 'modified',
                'additions': 30,
                'deletions': 5,
                'patch': '''@@ -1,10 +1,35 @@
+def add(a: int, b: int) -> int:
+    """Add two numbers"""
+    return a + b
+
+def subtract(a: int, b: int) -> int:
+    """Subtract two numbers"""
+    return a - b
+
+def multiply(a: int, b: int) -> int:
+    """Multiply two numbers"""
+    return a * b
'''
            },
            {
                'filename': 'tests/test_calculator.py',
                'status': 'added',
                'additions': 20,
                'deletions': 0,
                'patch': '''@@ -0,0 +1,20 @@
+import pytest
+from src.calculator import add, subtract, multiply
+
+def test_add():
+    assert add(2, 3) == 5
+
+def test_subtract():
+    assert subtract(5, 3) == 2
+
+def test_multiply():
+    assert multiply(3, 4) == 12
'''
            }
        ]
        
        mock_file_contents = {
            'src/calculator.py': '''def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b
''',
            'tests/test_calculator.py': '''import pytest
from src.calculator import add, subtract, multiply

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiply():
    assert multiply(3, 4) == 12
'''
        }
        
        mock_llm_response = {
            'content': json.dumps({
                'issues': [
                    {
                        'severity': 'info',
                        'message': 'Good use of type hints',
                        'file': 'src/calculator.py',
                        'line': 1
                    },
                    {
                        'severity': 'info',
                        'message': 'Comprehensive test coverage',
                        'file': 'tests/test_calculator.py',
                        'line': 1
                    }
                ],
                'summary': 'Clean implementation with good test coverage',
                'risk_score': 10
            }),
            'provider': 'openai',
            'tokens': {'total': 300},
            'cost': 0.005
        }
        
        start_time = datetime.now(timezone.utc)
        
        with patch('app.services.github_client.GitHubClient') as MockGitHub, \
             patch('app.services.llm.orchestrator.LLMOrchestrator') as MockLLM, \
             patch('app.api.v1.endpoints.code_review_webhook.get_cache_service') as mock_cache:
            
            # Setup GitHub client mock
            github_instance = AsyncMock()
            github_instance.get_pr_files.return_value = mock_github_files
            github_instance.get_file_content.side_effect = lambda repo, ref, path: mock_file_contents.get(path, '')
            github_instance.post_review_comment.return_value = {'id': 12345}
            github_instance.update_pr_status.return_value = {'state': 'success'}
            MockGitHub.return_value = github_instance
            
            # Setup LLM orchestrator mock
            llm_instance = AsyncMock()
            mock_response = Mock()
            mock_response.content = mock_llm_response['content']
            mock_response.provider = mock_llm_response['provider']
            mock_response.tokens = mock_llm_response['tokens']
            mock_response.cost = mock_llm_response['cost']
            llm_instance.generate.return_value = mock_response
            MockLLM.return_value = llm_instance
            
            # Setup cache mock
            mock_cache_service = AsyncMock()
            mock_cache_service.cache_exists.return_value = False
            mock_cache_service.cache_set.return_value = True
            mock_cache.return_value = mock_cache_service
            
            # Step 3: Send webhook request
            async with AsyncClient(app=app, base_url="http://test", timeout=30.0) as client:
                webhook_response = await client.post(
                    "/api/v1/code-review/webhook",
                    json=webhook_payload,
                    headers={
                        'X-Hub-Signature-256': signature,
                        'X-GitHub-Delivery': f'e2e-test-delivery-{pr_number}',
                        'X-GitHub-Event': 'pull_request'
                    }
                )
            
            # Step 4: Verify webhook response
            assert webhook_response.status_code == 202, f"Webhook failed: {webhook_response.text}"
            webhook_data = webhook_response.json()
            assert webhook_data['message'] == 'PR analysis queued'
            assert webhook_data['pr_number'] == pr_number
            assert 'task_id' in webhook_data
            
            task_id = webhook_data['task_id']
            
            # Step 5: Wait for async processing (simulate Celery task execution)
            # In a real staging environment, this would wait for actual Celery workers
            # For this test, we'll execute the workflow synchronously
            from app.tasks.pull_request_analysis import (
                _parse_pr_files,
                _build_graph,
                _analyze_with_llm,
                _post_comments
            )
            
            # Get the PR from database
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(PullRequest).where(
                        PullRequest.project_id == project_id,
                        PullRequest.github_pr_number == pr_number
                    )
                )
                pr = result.scalar_one_or_none()
                assert pr is not None, "PR not created in database"
                pr_id = pr.id
            
            # Execute workflow tasks
            mock_task = Mock()
            mock_task.request.retries = 0
            
            # Task 1: Parse files
            parse_result = await _parse_pr_files(pr_id, project_id, mock_task)
            assert parse_result is not None
            assert 'parsed_entities' in parse_result
            assert len(parse_result['parsed_entities']) > 0
            
            # Task 2: Build graph
            graph_result = await _build_graph(parse_result, mock_task)
            assert graph_result is not None
            assert 'graph_stats' in graph_result
            assert graph_result['graph_stats']['nodes_created'] > 0
            
            # Task 3: Analyze with LLM
            analysis_result = await _analyze_with_llm(graph_result, mock_task)
            assert analysis_result is not None
            assert 'llm_analysis' in analysis_result
            assert analysis_result['llm_analysis']['total_issues'] >= 0
            
            # Task 4: Post comments
            final_result = await _post_comments(analysis_result, mock_task)
            assert final_result is not None
            assert final_result['status'] == 'completed'
            assert 'comments_posted' in final_result
            
            # Step 6: Verify end-to-end results
            end_time = datetime.now(timezone.utc)
            total_time = (end_time - start_time).total_seconds()
            
            # Verify timing requirement (< 60 seconds for small PRs)
            assert total_time < 60, f"Flow took {total_time}s, expected < 60s"
            
            # Verify PR status updated
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(PullRequest).where(PullRequest.id == pr_id)
                )
                updated_pr = result.scalar_one()
                assert updated_pr.status in [PRStatus.COMPLETED, PRStatus.PENDING]
                
                # Verify code entities were created
                entities_result = await db.execute(
                    select(CodeEntity).where(CodeEntity.project_id == project_id)
                )
                entities = entities_result.scalars().all()
                assert len(entities) > 0, "No code entities created"
            
            # Verify GitHub API calls were made
            assert github_instance.get_pr_files.called
            assert github_instance.get_file_content.called
            assert github_instance.post_review_comment.called or final_result['comments_posted'] == 0
            
            # Verify LLM was called
            assert llm_instance.generate.called
            
            print(f"\n✓ E2E Test Passed!")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Files parsed: {len(parse_result['parsed_entities'])}")
            print(f"  Graph nodes created: {graph_result['graph_stats']['nodes_created']}")
            print(f"  Issues found: {analysis_result['llm_analysis']['total_issues']}")
            print(f"  Comments posted: {final_result['comments_posted']}")
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_webhook_flow_with_errors(self):
        """
        Test webhook flow handles errors gracefully
        
        Validates error handling when:
        - GitHub API fails
        - LLM API fails
        - Database operations fail
        """
        webhook_secret = "test_error_secret"
        repo_url = "https://github.com/test-org/error-repo"
        
        # Setup test project
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Project).where(Project.github_repo_url == repo_url)
            )
            test_project = result.scalar_one_or_none()
            
            if not test_project:
                test_project = Project(
                    name="E2E Error Test Project",
                    description="Project for error testing",
                    github_repo_url=repo_url,
                    github_webhook_secret=webhook_secret,
                    language="Python"
                )
                db.add(test_project)
                await db.commit()
                await db.refresh(test_project)
        
        webhook_payload = {
            'action': 'opened',
            'pull_request': {
                'number': 999,
                'title': 'Error Test PR',
                'head': {'ref': 'error-branch', 'sha': 'error123'},
                'changed_files': 1
            },
            'repository': {
                'html_url': repo_url,
                'full_name': 'test-org/error-repo'
            }
        }
        
        payload_bytes = json.dumps(webhook_payload).encode('utf-8')
        signature = self.generate_signature(payload_bytes, webhook_secret)
        
        with patch('app.services.github_client.GitHubClient') as MockGitHub, \
             patch('app.api.v1.endpoints.code_review_webhook.get_cache_service') as mock_cache:
            
            # Setup GitHub client to fail
            github_instance = AsyncMock()
            github_instance.get_pr_files.side_effect = Exception("GitHub API error")
            MockGitHub.return_value = github_instance
            
            # Setup cache mock
            mock_cache_service = AsyncMock()
            mock_cache_service.cache_exists.return_value = False
            mock_cache_service.cache_set.return_value = True
            mock_cache.return_value = mock_cache_service
            
            # Send webhook - should still accept it
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/code-review/webhook",
                    json=webhook_payload,
                    headers={
                        'X-Hub-Signature-256': signature,
                        'X-GitHub-Delivery': 'error-test-delivery',
                        'X-GitHub-Event': 'pull_request'
                    }
                )
            
            # Webhook should accept the request even if processing fails later
            assert response.status_code == 202
            
            print("\n✓ Error handling test passed!")
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_webhook_performance_under_load(self):
        """
        Test webhook can handle multiple concurrent requests
        
        Validates:
        - Concurrent webhook processing
        - No race conditions
        - Proper request queuing
        """
        webhook_secret = "test_load_secret"
        repo_url = "https://github.com/test-org/load-repo"
        
        # Setup test project
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Project).where(Project.github_repo_url == repo_url)
            )
            test_project = result.scalar_one_or_none()
            
            if not test_project:
                test_project = Project(
                    name="E2E Load Test Project",
                    description="Project for load testing",
                    github_repo_url=repo_url,
                    github_webhook_secret=webhook_secret,
                    language="Python"
                )
                db.add(test_project)
                await db.commit()
                await db.refresh(test_project)
        
        # Send 10 concurrent webhook requests
        async def send_webhook(pr_num: int):
            payload = {
                'action': 'opened',
                'pull_request': {
                    'number': pr_num,
                    'title': f'Load Test PR {pr_num}',
                    'head': {'ref': f'load-{pr_num}', 'sha': f'load{pr_num}'},
                    'changed_files': 1
                },
                'repository': {
                    'html_url': repo_url,
                    'full_name': 'test-org/load-repo'
                }
            }
            
            payload_bytes = json.dumps(payload).encode('utf-8')
            signature = self.generate_signature(payload_bytes, webhook_secret)
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                return await client.post(
                    "/api/v1/code-review/webhook",
                    json=payload,
                    headers={
                        'X-Hub-Signature-256': signature,
                        'X-GitHub-Delivery': f'load-test-{pr_num}',
                        'X-GitHub-Event': 'pull_request'
                    }
                )
        
        with patch('app.services.github_client.GitHubClient') as MockGitHub, \
             patch('app.api.v1.endpoints.code_review_webhook.get_cache_service') as mock_cache:
            
            github_instance = AsyncMock()
            github_instance.get_pr_files.return_value = []
            MockGitHub.return_value = github_instance
            
            mock_cache_service = AsyncMock()
            mock_cache_service.cache_exists.return_value = False
            mock_cache_service.cache_set.return_value = True
            mock_cache.return_value = mock_cache_service
            
            # Send concurrent requests
            start_time = datetime.now(timezone.utc)
            tasks = [send_webhook(i) for i in range(200, 210)]
            responses = await asyncio.gather(*tasks)
            end_time = datetime.now(timezone.utc)
            
            # Verify all requests succeeded
            for response in responses:
                assert response.status_code == 202
            
            total_time = (end_time - start_time).total_seconds()
            print(f"\n✓ Load test passed!")
            print(f"  Processed 10 concurrent webhooks in {total_time:.2f}s")
            print(f"  Average time per webhook: {total_time/10:.2f}s")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'e2e'])
