"""
Tests for security headers middleware.

Validates Requirement 8.5
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.security_headers import configure_security_headers


@pytest.fixture
def app_with_security_headers():
    """Create FastAPI app with security headers middleware"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    configure_security_headers(
        app,
        enable_hsts=True,
        hsts_max_age=31536000,
        enable_csp=True,
        environment="production",
    )
    
    return app


@pytest.fixture
def app_dev_environment():
    """Create FastAPI app with development environment (no HSTS)"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    configure_security_headers(
        app,
        enable_hsts=True,
        hsts_max_age=31536000,
        enable_csp=True,
        environment="development",
    )
    
    return app


@pytest.fixture
def client(app_with_security_headers):
    """Create test client"""
    return TestClient(app_with_security_headers)


@pytest.fixture
def dev_client(app_dev_environment):
    """Create test client for development environment"""
    return TestClient(app_dev_environment)


class TestSecurityHeaders:
    """Test security headers middleware"""
    
    def test_x_content_type_options_header(self, client):
        """Test X-Content-Type-Options header is set"""
        response = client.get("/test")
        assert response.status_code == 200
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"
    
    def test_x_frame_options_header(self, client):
        """Test X-Frame-Options header is set"""
        response = client.get("/test")
        assert response.status_code == 200
        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"
    
    def test_x_xss_protection_header(self, client):
        """Test X-XSS-Protection header is set"""
        response = client.get("/test")
        assert response.status_code == 200
        assert "x-xss-protection" in response.headers
        assert response.headers["x-xss-protection"] == "1; mode=block"
    
    def test_strict_transport_security_header_production(self, client):
        """Test Strict-Transport-Security header is set in production"""
        response = client.get("/test")
        assert response.status_code == 200
        assert "strict-transport-security" in response.headers
        hsts_header = response.headers["strict-transport-security"]
        assert "max-age=31536000" in hsts_header
        assert "includeSubDomains" in hsts_header
        assert "preload" in hsts_header
    
    def test_strict_transport_security_header_development(self, dev_client):
        """Test Strict-Transport-Security header is NOT set in development"""
        response = dev_client.get("/test")
        assert response.status_code == 200
        # HSTS should not be set in development environment
        assert "strict-transport-security" not in response.headers
    
    def test_content_security_policy_header(self, client):
        """Test Content-Security-Policy header is set"""
        response = client.get("/test")
        assert response.status_code == 200
        assert "content-security-policy" in response.headers
        csp_header = response.headers["content-security-policy"]
        
        # Check key CSP directives
        assert "default-src 'self'" in csp_header
        assert "script-src 'self'" in csp_header
        assert "style-src 'self'" in csp_header
        assert "img-src 'self' data: https:" in csp_header
        assert "frame-ancestors 'none'" in csp_header
    
    def test_referrer_policy_header(self, client):
        """Test Referrer-Policy header is set"""
        response = client.get("/test")
        assert response.status_code == 200
        assert "referrer-policy" in response.headers
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    
    def test_permissions_policy_header(self, client):
        """Test Permissions-Policy header is set"""
        response = client.get("/test")
        assert response.status_code == 200
        assert "permissions-policy" in response.headers
        permissions_header = response.headers["permissions-policy"]
        
        # Check that dangerous features are disabled
        assert "geolocation=()" in permissions_header
        assert "microphone=()" in permissions_header
        assert "camera=()" in permissions_header
        assert "payment=()" in permissions_header
    
    def test_all_security_headers_present(self, client):
        """Test that all required security headers are present"""
        response = client.get("/test")
        assert response.status_code == 200
        
        required_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "strict-transport-security",  # Only in production
            "content-security-policy",
            "referrer-policy",
            "permissions-policy",
        ]
        
        for header in required_headers:
            assert header in response.headers, f"Missing security header: {header}"


class TestSecurityHeadersConfiguration:
    """Test security headers configuration options"""
    
    def test_disable_hsts(self):
        """Test disabling HSTS"""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        configure_security_headers(
            app,
            enable_hsts=False,
            enable_csp=True,
            environment="production",
        )
        
        client = TestClient(app)
        response = client.get("/test")
        
        # HSTS should not be present when disabled
        assert "strict-transport-security" not in response.headers
    
    def test_disable_csp(self):
        """Test disabling CSP"""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        configure_security_headers(
            app,
            enable_hsts=True,
            enable_csp=False,
            environment="production",
        )
        
        client = TestClient(app)
        response = client.get("/test")
        
        # CSP should not be present when disabled
        assert "content-security-policy" not in response.headers
    
    def test_custom_hsts_max_age(self):
        """Test custom HSTS max-age"""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        custom_max_age = 7776000  # 90 days
        configure_security_headers(
            app,
            enable_hsts=True,
            hsts_max_age=custom_max_age,
            enable_csp=True,
            environment="production",
        )
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert "strict-transport-security" in response.headers
        assert f"max-age={custom_max_age}" in response.headers["strict-transport-security"]


class TestSecurityHeadersRequirement:
    """Test Requirement 8.5: Security headers implementation"""
    
    def test_requirement_8_5_x_content_type_options(self, client):
        """
        Test Requirement 8.5: X-Content-Type-Options header prevents MIME sniffing
        """
        response = client.get("/test")
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"
    
    def test_requirement_8_5_x_frame_options(self, client):
        """
        Test Requirement 8.5: X-Frame-Options header prevents clickjacking
        """
        response = client.get("/test")
        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"
    
    def test_requirement_8_5_x_xss_protection(self, client):
        """
        Test Requirement 8.5: X-XSS-Protection header enables browser XSS filter
        """
        response = client.get("/test")
        assert "x-xss-protection" in response.headers
        assert response.headers["x-xss-protection"] == "1; mode=block"
    
    def test_requirement_8_5_hsts_production(self, client):
        """
        Test Requirement 8.5: HSTS header enforces HTTPS in production
        """
        response = client.get("/test")
        assert "strict-transport-security" in response.headers
        hsts = response.headers["strict-transport-security"]
        assert "max-age=" in hsts
        assert "includeSubDomains" in hsts
    
    def test_requirement_8_5_csp(self, client):
        """
        Test Requirement 8.5: CSP header controls resource loading
        """
        response = client.get("/test")
        assert "content-security-policy" in response.headers
        csp = response.headers["content-security-policy"]
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
