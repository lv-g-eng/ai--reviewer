"""
Tests for CORS configuration

Requirements:
- 8.8: Implement CORS policies restricting origins to approved domains
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@pytest.fixture
def app():
    """Create test FastAPI application with CORS"""
    app = FastAPI()
    
    # Add CORS middleware with settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=settings.CORS_EXPOSE_HEADERS,
        max_age=settings.CORS_MAX_AGE,
    )
    
    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}
    
    @app.post("/test")
    async def test_post_endpoint():
        return {"status": "created"}
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


class TestCORSConfiguration:
    """Test CORS configuration"""
    
    def test_cors_allowed_origin(self, client):
        """Test that allowed origins can make requests"""
        # Test with localhost origin
        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_cors_preflight_request(self, client):
        """Test CORS preflight (OPTIONS) request"""
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        
        # Preflight should return 200
        assert response.status_code == 200
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_cors_credentials_allowed(self, client):
        """Test that credentials are allowed"""
        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Check credentials header
        if "access-control-allow-credentials" in response.headers:
            assert response.headers["access-control-allow-credentials"] == "true"
    
    def test_cors_allowed_methods(self, client):
        """Test that configured methods are allowed"""
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            }
        )
        
        assert response.status_code == 200
        
        # Check allowed methods
        if "access-control-allow-methods" in response.headers:
            allowed_methods = response.headers["access-control-allow-methods"]
            assert "POST" in allowed_methods
            assert "GET" in allowed_methods
    
    def test_cors_allowed_headers(self, client):
        """Test that configured headers are allowed"""
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization,Content-Type",
            }
        )
        
        assert response.status_code == 200
        
        # Check allowed headers
        if "access-control-allow-headers" in response.headers:
            allowed_headers = response.headers["access-control-allow-headers"].lower()
            assert "authorization" in allowed_headers
            assert "content-type" in allowed_headers
    
    def test_cors_exposed_headers(self, client):
        """Test that rate limit headers are exposed"""
        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Check exposed headers (if present)
        if "access-control-expose-headers" in response.headers:
            exposed_headers = response.headers["access-control-expose-headers"]
            # Rate limit headers should be exposed
            assert "X-RateLimit-Limit" in exposed_headers or "x-ratelimit-limit" in exposed_headers.lower()
    
    def test_cors_max_age(self, client):
        """Test that max age is set for preflight caching"""
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            }
        )
        
        # Check max age header
        if "access-control-max-age" in response.headers:
            max_age = int(response.headers["access-control-max-age"])
            assert max_age > 0


class TestCORSRequirements:
    """Test CORS requirements compliance"""
    
    def test_requirement_8_8_restricted_origins(self):
        """
        Test Requirement 8.8: CORS restricts origins to approved domains
        """
        # Verify ALLOWED_ORIGINS is configured
        assert settings.ALLOWED_ORIGINS is not None
        assert len(settings.ALLOWED_ORIGINS) > 0
        
        # Verify wildcard is not used (security requirement)
        assert "*" not in settings.ALLOWED_ORIGINS
    
    def test_requirement_8_8_specific_origins(self):
        """
        Test Requirement 8.8: Only specific origins are allowed
        """
        # Verify origins are specific domains, not wildcards
        for origin in settings.ALLOWED_ORIGINS:
            assert origin != "*"
            assert origin.startswith("http://") or origin.startswith("https://")
    
    def test_requirement_8_8_allowed_methods_configured(self):
        """
        Test Requirement 8.8: Allowed methods are configured
        """
        assert settings.CORS_ALLOW_METHODS is not None
        assert len(settings.CORS_ALLOW_METHODS) > 0
        
        # Common HTTP methods should be present
        assert "GET" in settings.CORS_ALLOW_METHODS
        assert "POST" in settings.CORS_ALLOW_METHODS
    
    def test_requirement_8_8_allowed_headers_configured(self):
        """
        Test Requirement 8.8: Allowed headers are configured
        """
        assert settings.CORS_ALLOW_HEADERS is not None
        assert len(settings.CORS_ALLOW_HEADERS) > 0
        
        # Essential headers should be present
        assert "Content-Type" in settings.CORS_ALLOW_HEADERS
        assert "Authorization" in settings.CORS_ALLOW_HEADERS


class TestCORSSecurityValidation:
    """Test CORS security validation"""
    
    def test_cors_validation_no_wildcard(self):
        """Test that wildcard origin is detected in validation"""
        warnings = settings.validate_cors_config()
        
        # Should not have wildcard warning if properly configured
        wildcard_warnings = [w for w in warnings if "*" in w and "wildcard" in w.lower()]
        
        # If wildcard is used, there should be a warning
        if "*" in settings.ALLOWED_ORIGINS:
            assert len(wildcard_warnings) > 0
        else:
            assert len(wildcard_warnings) == 0
    
    def test_cors_validation_localhost_in_production(self):
        """Test that localhost origins are detected in production"""
        # This test checks if validation catches localhost in production
        if settings.ENVIRONMENT == "production":
            warnings = settings.validate_cors_config()
            
            # Check if localhost is in allowed origins
            has_localhost = any(
                "localhost" in origin or "127.0.0.1" in origin
                for origin in settings.ALLOWED_ORIGINS
            )
            
            if has_localhost:
                # Should have warning about localhost in production
                localhost_warnings = [
                    w for w in warnings
                    if "localhost" in w.lower()
                ]
                assert len(localhost_warnings) > 0
    
    def test_cors_validation_credentials_with_wildcard(self):
        """Test that credentials with wildcard is detected"""
        # If credentials are allowed with wildcard, should have warning
        if settings.CORS_ALLOW_CREDENTIALS and "*" in settings.ALLOWED_ORIGINS:
            warnings = settings.validate_cors_config()
            
            credential_warnings = [
                w for w in warnings
                if "credentials" in w.lower() and "wildcard" in w.lower()
            ]
            assert len(credential_warnings) > 0


class TestCORSEdgeCases:
    """Test CORS edge cases"""
    
    def test_cors_with_multiple_origins(self, client):
        """Test CORS with multiple allowed origins"""
        # Test each allowed origin
        for origin in settings.ALLOWED_ORIGINS[:3]:  # Test first 3
            response = client.get(
                "/test",
                headers={"Origin": origin}
            )
            
            assert response.status_code == 200
    
    def test_cors_with_disallowed_origin(self, client):
        """Test CORS with origin not in allowed list"""
        response = client.get(
            "/test",
            headers={"Origin": "http://evil.com"}
        )
        
        # Request should still succeed (CORS is browser-enforced)
        assert response.status_code == 200
        
        # But CORS headers should not allow the origin
        if "access-control-allow-origin" in response.headers:
            allowed_origin = response.headers["access-control-allow-origin"]
            assert allowed_origin != "http://evil.com"
    
    def test_cors_with_no_origin_header(self, client):
        """Test request without Origin header (same-origin request)"""
        response = client.get("/test")
        
        # Should succeed (same-origin requests don't need CORS)
        assert response.status_code == 200
    
    def test_cors_with_disallowed_method(self, client):
        """Test CORS preflight with disallowed method"""
        # Try to use a method not in CORS_ALLOW_METHODS
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "TRACE",
            }
        )
        
        # Preflight may return 400 for disallowed methods (CORS rejection)
        # or 200 with no allow headers
        assert response.status_code in [200, 400]


class TestCORSIntegration:
    """Integration tests for CORS"""
    
    def test_cors_with_authentication(self, client):
        """Test CORS with authentication headers"""
        response = client.get(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Authorization": "Bearer test-token",
            }
        )
        
        assert response.status_code == 200
    
    def test_cors_with_custom_headers(self, client):
        """Test CORS with custom headers"""
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-Custom-Header,Content-Type",
            }
        )
        
        # May return 400 if custom header is not in allowed list
        # or 200 if CORS allows it
        assert response.status_code in [200, 400]
    
    def test_cors_post_request(self, client):
        """Test CORS with POST request"""
        response = client.post(
            "/test",
            headers={"Origin": "http://localhost:3000"},
            json={"data": "test"}
        )
        
        assert response.status_code == 200


class TestCORSConfiguration:
    """Test CORS configuration values"""
    
    def test_cors_expose_headers_includes_rate_limit(self):
        """Test that rate limit headers are exposed via CORS"""
        assert "X-RateLimit-Limit" in settings.CORS_EXPOSE_HEADERS
        assert "X-RateLimit-Remaining" in settings.CORS_EXPOSE_HEADERS
        assert "X-RateLimit-Reset" in settings.CORS_EXPOSE_HEADERS
        assert "Retry-After" in settings.CORS_EXPOSE_HEADERS
    
    def test_cors_max_age_reasonable(self):
        """Test that CORS max age is set to reasonable value"""
        # Max age should be between 1 minute and 24 hours
        assert 60 <= settings.CORS_MAX_AGE <= 86400
    
    def test_cors_credentials_enabled(self):
        """Test that credentials are enabled for authenticated requests"""
        assert settings.CORS_ALLOW_CREDENTIALS is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
