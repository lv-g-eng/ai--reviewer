"""
Tests for Prometheus metrics collection.

Validates Requirement 7.3: Collect metrics for API response times, error rates, and throughput.
"""
import pytest
import time
from prometheus_client import REGISTRY as DEFAULT_REGISTRY
from fastapi.testclient import TestClient

from app.main import app
from app.core.prometheus_metrics import (
    REGISTRY,
    http_request_duration_seconds,
    http_requests_total,
    http_requests_in_progress,
    http_errors_total,
    exception_count,
    database_query_duration_seconds,
    database_operations_total,
    code_analysis_duration_seconds,
    code_analysis_total,
    llm_requests_total,
    llm_request_duration_seconds,
    llm_tokens_used,
    cache_operations_total,
    celery_tasks_total,
    celery_task_duration_seconds,
    auth_attempts_total,
    github_webhook_events_total,
    github_api_requests_total,
    MetricsTimer,
    record_http_request,
    record_exception,
    record_database_operation,
    record_code_analysis,
    record_llm_request,
    record_cache_operation,
    record_celery_task,
    record_auth_attempt,
    record_github_webhook,
    record_github_api_request,
    get_metrics,
    get_content_type,
)


class TestPrometheusMetrics:
    """Test Prometheus metrics collection."""
    
    def test_http_request_metrics(self):
        """Test HTTP request metrics are recorded correctly."""
        # Record a successful request
        record_http_request(
            method='GET',
            endpoint='/api/v1/users',
            status_code=200,
            duration=0.123
        )
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'http_request_duration_seconds' in metrics_output
        assert 'http_requests_total' in metrics_output
        assert 'method="GET"' in metrics_output
        assert 'endpoint="/api/v1/users"' in metrics_output
        assert 'status_code="200"' in metrics_output
    
    def test_http_error_metrics(self):
        """Test HTTP error metrics are recorded correctly."""
        # Record a client error
        record_http_request(
            method='POST',
            endpoint='/api/v1/auth/login',
            status_code=401,
            duration=0.050
        )
        
        # Record a server error
        record_http_request(
            method='GET',
            endpoint='/api/v1/projects',
            status_code=500,
            duration=0.200
        )
        
        # Verify error metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'http_errors_total' in metrics_output
        assert 'error_type="client_error"' in metrics_output
        assert 'error_type="server_error"' in metrics_output
    
    def test_exception_metrics(self):
        """Test exception metrics are recorded correctly."""
        # Record exceptions
        record_exception('ValueError', '/api/v1/users')
        record_exception('DatabaseError', '/api/v1/projects')
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'exception_count' in metrics_output
        assert 'exception_type="ValueError"' in metrics_output
        assert 'exception_type="DatabaseError"' in metrics_output
    
    def test_database_operation_metrics(self):
        """Test database operation metrics are recorded correctly."""
        # Record database operations
        record_database_operation('postgresql', 'query', 0.015, 'success')
        record_database_operation('neo4j', 'insert', 0.025, 'success')
        record_database_operation('redis', 'get', 0.002, 'success')
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'database_query_duration_seconds' in metrics_output
        assert 'database_operations_total' in metrics_output
        assert 'database="postgresql"' in metrics_output
        assert 'database="neo4j"' in metrics_output
        assert 'database="redis"' in metrics_output
    
    def test_code_analysis_metrics(self):
        """Test code analysis metrics are recorded correctly."""
        # Record code analyses
        record_code_analysis('ast_parsing', 1.5, 'success')
        record_code_analysis('dependency_graph', 3.2, 'success')
        record_code_analysis('llm_review', 15.7, 'success')
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'code_analysis_duration_seconds' in metrics_output
        assert 'code_analysis_total' in metrics_output
        assert 'analysis_type="ast_parsing"' in metrics_output
        assert 'analysis_type="dependency_graph"' in metrics_output
        assert 'analysis_type="llm_review"' in metrics_output
    
    def test_llm_request_metrics(self):
        """Test LLM request metrics are recorded correctly."""
        # Record LLM requests
        record_llm_request(
            provider='openai',
            model='gpt-4',
            duration=2.5,
            status='success',
            prompt_tokens=150,
            completion_tokens=300
        )
        
        record_llm_request(
            provider='anthropic',
            model='claude-3-5-sonnet',
            duration=3.1,
            status='success',
            prompt_tokens=200,
            completion_tokens=400
        )
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'llm_requests_total' in metrics_output
        assert 'llm_request_duration_seconds' in metrics_output
        assert 'llm_tokens_used' in metrics_output
        assert 'provider="openai"' in metrics_output
        assert 'provider="anthropic"' in metrics_output
        assert 'model="gpt-4"' in metrics_output
        assert 'model="claude-3-5-sonnet"' in metrics_output
        assert 'token_type="prompt"' in metrics_output
        assert 'token_type="completion"' in metrics_output
    
    def test_cache_operation_metrics(self):
        """Test cache operation metrics are recorded correctly."""
        # Record cache operations
        record_cache_operation('get', 'hit')
        record_cache_operation('get', 'miss')
        record_cache_operation('set', 'success')
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'cache_operations_total' in metrics_output
        assert 'operation="get"' in metrics_output
        assert 'operation="set"' in metrics_output
        assert 'status="hit"' in metrics_output
        assert 'status="miss"' in metrics_output
    
    def test_celery_task_metrics(self):
        """Test Celery task metrics are recorded correctly."""
        # Record Celery tasks
        record_celery_task('parse_pull_request_files', 5.2, 'success')
        record_celery_task('build_dependency_graph', 8.7, 'success')
        record_celery_task('analyze_with_llm', 25.3, 'failure')
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'celery_tasks_total' in metrics_output
        assert 'celery_task_duration_seconds' in metrics_output
        assert 'task_name="parse_pull_request_files"' in metrics_output
        assert 'task_name="build_dependency_graph"' in metrics_output
        assert 'task_name="analyze_with_llm"' in metrics_output
        assert 'status="success"' in metrics_output
        assert 'status="failure"' in metrics_output
    
    def test_auth_attempt_metrics(self):
        """Test authentication attempt metrics are recorded correctly."""
        # Record auth attempts
        record_auth_attempt('login', 'success')
        record_auth_attempt('login', 'failure')
        record_auth_attempt('register', 'success')
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'auth_attempts_total' in metrics_output
        assert 'method="login"' in metrics_output
        assert 'method="register"' in metrics_output
        assert 'status="success"' in metrics_output
        assert 'status="failure"' in metrics_output
    
    def test_github_webhook_metrics(self):
        """Test GitHub webhook metrics are recorded correctly."""
        # Record webhook events
        record_github_webhook('pull_request', 'success')
        record_github_webhook('push', 'success')
        record_github_webhook('pull_request', 'error')
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'github_webhook_events_total' in metrics_output
        assert 'event_type="pull_request"' in metrics_output
        assert 'event_type="push"' in metrics_output
    
    def test_github_api_request_metrics(self):
        """Test GitHub API request metrics are recorded correctly."""
        # Record API requests
        record_github_api_request('get_pr', 'success')
        record_github_api_request('post_comment', 'success')
        record_github_api_request('get_files', 'rate_limited')
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        
        assert 'github_api_requests_total' in metrics_output
        assert 'operation="get_pr"' in metrics_output
        assert 'operation="post_comment"' in metrics_output
        assert 'status="rate_limited"' in metrics_output
    
    def test_metrics_timer_context_manager(self):
        """Test MetricsTimer context manager works correctly."""
        # Use timer to measure operation
        with MetricsTimer(http_request_duration_seconds, method='GET', endpoint='/test', status_code='200'):
            time.sleep(0.01)  # Simulate work
        
        # Verify metric was recorded
        metrics_output = get_metrics().decode('utf-8')
        assert 'http_request_duration_seconds' in metrics_output
    
    def test_get_content_type(self):
        """Test get_content_type returns correct content type."""
        content_type = get_content_type()
        assert 'text/plain' in content_type
    
    def test_metrics_output_format(self):
        """Test metrics output is in valid Prometheus format."""
        # Record some metrics
        record_http_request('GET', '/api/v1/health', 200, 0.05)
        
        # Get metrics output
        metrics_output = get_metrics().decode('utf-8')
        
        # Verify Prometheus format
        assert '# HELP' in metrics_output
        assert '# TYPE' in metrics_output
        
        # Verify metric types
        assert 'TYPE http_request_duration_seconds histogram' in metrics_output
        assert 'TYPE http_requests_total counter' in metrics_output
        assert 'TYPE http_requests_in_progress gauge' in metrics_output
    
    def test_custom_registry_isolation(self):
        """Test that custom registry is isolated from default registry."""
        # Our custom registry should be separate from the default
        assert REGISTRY != DEFAULT_REGISTRY
        
        # Metrics should be in our custom registry
        metrics_output = get_metrics().decode('utf-8')
        assert len(metrics_output) > 0


class TestMetricsIntegration:
    """Integration tests for metrics collection."""
    
    def test_multiple_requests_accumulate(self):
        """Test that multiple requests accumulate correctly."""
        # Record multiple requests
        for i in range(5):
            record_http_request('GET', '/api/v1/users', 200, 0.1)
        
        # Verify count increased
        metrics_output = get_metrics().decode('utf-8')
        assert 'http_requests_total' in metrics_output
    
    def test_different_endpoints_tracked_separately(self):
        """Test that different endpoints are tracked separately."""
        # Record requests to different endpoints
        record_http_request('GET', '/api/v1/users', 200, 0.1)
        record_http_request('GET', '/api/v1/projects', 200, 0.2)
        record_http_request('POST', '/api/v1/auth/login', 200, 0.15)
        
        # Verify all endpoints are tracked
        metrics_output = get_metrics().decode('utf-8')
        assert 'endpoint="/api/v1/users"' in metrics_output
        assert 'endpoint="/api/v1/projects"' in metrics_output
        assert 'endpoint="/api/v1/auth/login"' in metrics_output
    
    def test_error_rate_calculation(self):
        """Test that error rates can be calculated from metrics."""
        # Record mix of successful and failed requests
        for i in range(7):
            record_http_request('GET', '/api/v1/data', 200, 0.1)
        
        for i in range(3):
            record_http_request('GET', '/api/v1/data', 500, 0.2)
        
        # Verify both success and error metrics exist
        metrics_output = get_metrics().decode('utf-8')
        assert 'status_code="200"' in metrics_output
        assert 'status_code="500"' in metrics_output
        assert 'http_errors_total' in metrics_output


class TestMetricsEndpoint:
    """Test the /metrics endpoint."""
    
    def test_metrics_endpoint_returns_prometheus_format(self):
        """Test that /metrics endpoint returns valid Prometheus format."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/api/v1/metrics")
        
        assert response.status_code == 200
        assert 'text/plain' in response.headers['content-type']
        
        content = response.text
        assert '# HELP' in content
        assert '# TYPE' in content
    
    def test_metrics_endpoint_includes_http_metrics(self):
        """Test that /metrics endpoint includes HTTP metrics."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Make a request to generate metrics
        client.get("/health")
        
        # Get metrics
        response = client.get("/api/v1/metrics")
        content = response.text
        
        assert 'http_request_duration_seconds' in content
        assert 'http_requests_total' in content
    
    def test_metrics_endpoint_not_in_openapi_schema(self):
        """Test that /metrics endpoint is not included in OpenAPI schema."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        openapi_spec = response.json()
        
        # Metrics endpoint should not be in the schema
        paths = openapi_spec.get('paths', {})
        assert '/api/v1/metrics' not in paths
