"""
Unit tests for GitHub API client retry logic

Tests that the GitHub API client implements retry logic with exponential backoff
as required by task 6.2 and requirement 2.2.

Requirements:
- 2.2: Implement exponential backoff with maximum of 3 retry attempts
"""

import pytest
from unittest.mock import MagicMock
from github import GithubException
import httpx

from app.services.github_client import GitHubAPIClient


@pytest.mark.asyncio
async def test_get_pr_files_retries_on_github_exception():
    """
    Test that get_pr_files retries on GithubException
    
    Requirements:
    - 2.2: Retry with exponential backoff (max 3 attempts)
    """
    # Create client
    client = GitHubAPIClient(access_token="test_token")
    
    # Mock the Github client to raise exception twice, then succeed
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_file = MagicMock()
    mock_file.filename = "test.py"
    mock_file.status = "modified"
    mock_file.additions = 10
    mock_file.deletions = 5
    mock_file.changes = 15
    mock_file.patch = "diff content"
    mock_file.blob_url = "https://github.com/test/repo/blob/abc123/test.py"
    mock_file.raw_url = "https://github.com/test/repo/raw/abc123/test.py"
    
    call_count = 0
    
    def get_files_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            # Fail first 2 attempts
            raise GithubException(500, {"message": "Internal Server Error"}, None)
        # Succeed on 3rd attempt
        return [mock_file]
    
    mock_pr.get_files = MagicMock(side_effect=get_files_side_effect)
    mock_repo.get_pull = MagicMock(return_value=mock_pr)
    client.client.get_repo = MagicMock(return_value=mock_repo)
    
    # Call the method
    result = await client.get_pr_files("test/repo", 123)
    
    # Verify it retried and eventually succeeded
    assert call_count == 3, f"Should have retried 3 times, got {call_count}"
    assert len(result) == 1
    assert result[0]["filename"] == "test.py"


@pytest.mark.asyncio
async def test_get_pr_files_fails_after_max_retries():
    """
    Test that get_pr_files fails after max retries
    
    Requirements:
    - 2.2: Maximum of 3 retry attempts
    """
    # Create client
    client = GitHubAPIClient(access_token="test_token")
    
    # Mock the Github client to always raise exception
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    
    call_count = 0
    
    def get_files_side_effect():
        nonlocal call_count
        call_count += 1
        raise GithubException(500, {"message": "Internal Server Error"}, None)
    
    mock_pr.get_files = MagicMock(side_effect=get_files_side_effect)
    mock_repo.get_pull = MagicMock(return_value=mock_pr)
    client.client.get_repo = MagicMock(return_value=mock_repo)
    
    # Call the method and expect it to fail
    with pytest.raises(Exception):  # Will raise HTTPException
        await client.get_pr_files("test/repo", 123)
    
    # Verify it tried 3 times
    assert call_count == 3, f"Should have tried 3 times, got {call_count}"


@pytest.mark.asyncio
async def test_post_review_comment_retries_on_timeout():
    """
    Test that post_review_comment retries on timeout
    
    Requirements:
    - 2.2: Retry with exponential backoff on transient failures
    """
    # Create client
    client = GitHubAPIClient(access_token="test_token")
    
    # Mock the Github client to timeout twice, then succeed
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_comment = MagicMock()
    mock_comment.id = 12345
    mock_comment.body = "Test comment"
    mock_comment.path = "test.py"
    mock_comment.line = 42
    mock_comment.created_at = MagicMock()
    mock_comment.created_at.isoformat = MagicMock(return_value="2024-01-01T00:00:00Z")
    
    call_count = 0
    
    def create_comment_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            # Fail first 2 attempts with timeout
            raise httpx.TimeoutException("Request timeout")
        # Succeed on 3rd attempt
        return mock_comment
    
    mock_pr.create_review_comment = MagicMock(side_effect=create_comment_side_effect)
    mock_repo.get_pull = MagicMock(return_value=mock_pr)
    client.client.get_repo = MagicMock(return_value=mock_repo)
    
    # Call the method
    result = await client.post_review_comment(
        repo_full_name="test/repo",
        pr_number=123,
        body="Test comment",
        commit_id="abc123",
        path="test.py",
        line=42
    )
    
    # Verify it retried and eventually succeeded
    assert call_count == 3, f"Should have retried 3 times, got {call_count}"
    assert result["id"] == 12345
    assert result["body"] == "Test comment"


@pytest.mark.asyncio
async def test_get_pull_request_succeeds_on_first_try():
    """
    Test that get_pull_request succeeds without retry when API works
    
    Requirements:
    - 1.5: Fetch PR data for analysis
    """
    # Create client
    client = GitHubAPIClient(access_token="test_token")
    
    # Mock the Github client to succeed immediately
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_pr.number = 123
    mock_pr.title = "Test PR"
    mock_pr.body = "Test description"
    mock_pr.state = "open"
    mock_pr.user = MagicMock()
    mock_pr.user.login = "testuser"
    mock_pr.user.id = 456
    mock_pr.head = MagicMock()
    mock_pr.head.ref = "feature-branch"
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
    
    call_count = 0
    
    def get_pull_side_effect(pr_number):
        nonlocal call_count
        call_count += 1
        return mock_pr
    
    mock_repo.get_pull = MagicMock(side_effect=get_pull_side_effect)
    client.client.get_repo = MagicMock(return_value=mock_repo)
    
    # Call the method
    result = await client.get_pull_request("test/repo", 123)
    
    # Verify it succeeded on first try
    assert call_count == 1, f"Should have succeeded on first try, got {call_count} calls"
    assert result["number"] == 123
    assert result["title"] == "Test PR"
    assert result["state"] == "open"


@pytest.mark.asyncio
async def test_get_repository_retries_with_exponential_backoff():
    """
    Test that get_repository uses exponential backoff
    
    Requirements:
    - 2.2: Exponential backoff with multiplier=1, min=2, max=10
    """
    # Create client
    client = GitHubAPIClient(access_token="test_token")
    
    # Mock the Github client to fail twice, then succeed
    mock_repo = MagicMock()
    mock_repo.id = 123
    mock_repo.name = "test-repo"
    mock_repo.full_name = "test/test-repo"
    mock_repo.description = "Test repository"
    mock_repo.language = "Python"
    mock_repo.default_branch = "main"
    mock_repo.private = False
    
    call_count = 0
    
    def get_repo_side_effect(repo_name):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            # Fail first 2 attempts
            raise GithubException(503, {"message": "Service Unavailable"}, None)
        # Succeed on 3rd attempt
        return mock_repo
    
    client.client.get_repo = MagicMock(side_effect=get_repo_side_effect)
    
    # Call the method
    result = await client.get_repository("https://github.com/test/test-repo")
    
    # Verify it retried and eventually succeeded
    assert call_count == 3, f"Should have retried 3 times, got {call_count}"
    assert result["name"] == "test-repo"
    assert result["full_name"] == "test/test-repo"


@pytest.mark.asyncio
async def test_update_pr_status_retries_on_http_error():
    """
    Test that update_pr_status retries on HTTP errors
    
    Requirements:
    - 2.2: Retry on httpx.HTTPError
    """
    # Create client
    client = GitHubAPIClient(access_token="test_token")
    
    # Mock the Github client to fail once with HTTP error, then succeed
    mock_repo = MagicMock()
    mock_commit = MagicMock()
    mock_status = MagicMock()
    mock_status.state = "success"
    mock_status.description = "All checks passed"
    mock_status.context = "ai-code-review"
    mock_status.created_at = MagicMock()
    mock_status.created_at.isoformat = MagicMock(return_value="2024-01-01T00:00:00Z")
    
    call_count = 0
    
    def create_status_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            # Fail first attempt with HTTP error
            raise httpx.HTTPError("Connection error")
        # Succeed on 2nd attempt
        return mock_status
    
    mock_commit.create_status = MagicMock(side_effect=create_status_side_effect)
    mock_repo.get_commit = MagicMock(return_value=mock_commit)
    client.client.get_repo = MagicMock(return_value=mock_repo)
    
    # Call the method
    result = await client.update_pr_status(
        repo_full_name="test/repo",
        commit_sha="abc123",
        state="success",
        description="All checks passed"
    )
    
    # Verify it retried and eventually succeeded
    assert call_count == 2, f"Should have retried 2 times, got {call_count}"
    assert result["state"] == "success"
    assert result["description"] == "All checks passed"
