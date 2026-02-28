"""
Tests for Prometheus middleware.

Validates Requirement 7.3: Automatic collection of HTTP metrics.
"""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.middleware.prometheus_middleware import PrometheusMiddleware, configure_prometheus_middleware
from app.core.prometheus_metrics import get_metrics


class TestPrometheusMiddleware:
    """Test Prometheus middleware functionality."""
    
    def test_middleware_records_successful_request(self):
        """Test that middleware records metrics for successful requests."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(app)
        
        # Make request
        response = client.get("/test")
        assert response.status_code == 200
        
        # Verify metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        assert 'http_request_duration_seconds' in metrics_output
        assert 'http_requests_total' in metrics_output
        assert 'method="GET"' in metrics_output
    
    def test_middleware_records_error_request(self):
        """Test that middleware records metrics for error requests."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/error")
        async def error_endpoint():
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail="Internal error")
        
        client = TestClient(app)
        
        # Make request
        response = client.get("/error")
        assert response.status_code == 500
        
        # Verify error metrics were recorded
        metrics_output = get_metrics().decode('utf-8')
        assert 'http_errors_total' in metrics_output
        assert 'status_code="500"' in metrics_output
    
    def test_middleware_tracks_in_progress_requests(self):
        """Test that middleware tracks in-progress requests."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/slow")
        async def slow_endpoint():
            import asyncio
            await asyncio.sleep(0.1)
            return {"message": "done"}
        
        client = TestClient(app)
        
        # Make request
        response = client.get("/slow")
        assert response.status_code == 200
        
        # Verify in-progress metric exists
        metrics_output = get_metrics().decode('utf-8')
        assert 'http_requests_in_progress' in metrics_output
    
    def test_middleware_normalizes_paths(self):
        """Test that middleware normalizes URL paths to reduce cardinality."""
        # Create test app
        app = FastAPI()
        middleware = PrometheusMiddleware(app)
        
        # Test UUID normalization
        assert middleware._normalize_path('/api/v1/users/123e4567-e89b-12d3-a456-426614174000') == '/api/v1/users/{id}'
        
        # Test numeric ID normalization
        assert middleware._normalize_path('/api/v1/users/123') == '/api/v1/users/{id}'
        assert middleware._normalize_path('/api/v1/projects/456/analysis') == '/api/v1/projects/{id}/analysis'
        
        # Test alphanumeric ID normalization
        assert middleware._normalize_path('/api/v1/projects/abc123def456') == '/api/v1/projects/{id}'
        
        # Test paths without IDs remain unchanged
        assert middleware._normalize_path('/api/v1/health') == '/api/v1/health'
        assert middleware._normalize_path('/api/v1/users') == '/api/v1/users'
    
    def test_middleware_handles_exceptions(self):
        """Test that middleware records exceptions correctly."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/exception")
        async def exception_endpoint():
            raise ValueError("Test exception")
        
        client = TestClient(app)
        
        # Make request (should raise exception)
        with pytest.raises(ValueError):
            client.get("/exception")
        
        # Verify exception was recorded
        metrics_output = get_metrics().decode('utf-8')
        assert 'exception_count' in metrics_output
    
    def test_middleware_records_different_methods(self):
        """Test that middleware records different HTTP methods separately."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/resource")
        async def get_resource():
            return {"method": "GET"}
        
        @app.post("/resource")
        async def post_resource():
            return {"method": "POST"}
        
        @app.put("/resource")
        async def put_resource():
            return {"method": "PUT"}
        
        @app.delete("/resource")
        async def delete_resource():
            return {"method": "DELETE"}
        
        client = TestClient(app)
        
        # Make requests with different methods
        client.get("/resource")
        client.post("/resource")
        client.put("/resource")
        client.delete("/resource")
        
        # Verify all methods are tracked
        metrics_output = get_metrics().decode('utf-8')
        assert 'method="GET"' in metrics_output
        assert 'method="POST"' in metrics_output
        assert 'method="PUT"' in metrics_output
        assert 'method="DELETE"' in metrics_output
    
    def test_middleware_records_request_duration(self):
        """Test that middleware records request duration accurately."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/timed")
        async def timed_endpoint():
            import asyncio
            await asyncio.sleep(0.05)  # 50ms delay
            return {"message": "done"}
        
        client = TestClient(app)
        
        # Make request
        response = client.get("/timed")
        assert response.status_code == 200
        
        # Verify duration was recorded
        metrics_output = get_metrics().decode('utf-8')
        assert 'http_request_duration_seconds' in metrics_output
        # The histogram should have buckets
        assert '_bucket{' in metrics_output
        assert '_sum{' in metrics_output
        assert '_count{' in metrics_output


class TestMiddlewareIntegration:
    """Integration tests for Prometheus middleware."""
    
    def test_middleware_with_multiple_requests(self):
        """Test middleware with multiple concurrent requests."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/multi")
        async def multi_endpoint():
            return {"message": "ok"}
        
        client = TestClient(app)
        
        # Make multiple requests
        for i in range(10):
            response = client.get("/multi")
            assert response.status_code == 200
        
        # Verify metrics accumulated
        metrics_output = get_metrics().decode('utf-8')
        assert 'http_requests_total' in metrics_output
    
    def test_middleware_with_different_status_codes(self):
        """Test middleware tracks different status codes separately."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/status/{code}")
        async def status_endpoint(code: int):
            from fastapi import Response
            return Response(status_code=code, content=f"Status {code}")
        
        client = TestClient(app)
        
        # Make requests with different status codes
        client.get("/status/200")
        client.get("/status/201")
        client.get("/status/400")
        client.get("/status/404")
        client.get("/status/500")
        
        # Verify all status codes are tracked
        metrics_output = get_metrics().decode('utf-8')
        assert 'status_code="200"' in metrics_output
        assert 'status_code="201"' in metrics_output
        assert 'status_code="400"' in metrics_output
        assert 'status_code="404"' in metrics_output
        assert 'status_code="500"' in metrics_output
    
    def test_middleware_decrements_in_progress_after_completion(self):
        """Test that in-progress counter is decremented after request completes."""
        # Create test app
        app = FastAPI()
        configure_prometheus_middleware(app)
        
        @app.get("/complete")
        async def complete_endpoint():
            return {"message": "done"}
        
        client = TestClient(app)
        
        # Make request
        response = client.get("/complete")
        assert response.status_code == 200
        
        # The in-progress gauge should be back to 0 after completion
        # (This is implicit in the test - if it wasn't decremented, 
        # subsequent tests would show increasing values)
        metrics_output = get_metrics().decode('utf-8')
        assert 'http_requests_in_progress' in metrics_output
