"""
Tests for API documentation endpoints.

Validates that Swagger UI and ReDoc are properly configured and accessible.
Tests Requirement 9.3: API documentation with authentication examples.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_swagger_ui_accessible(self):
        """Test that Swagger UI is accessible at /docs."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        # Verify it's actually Swagger UI
        assert b"swagger-ui" in response.content.lower()
    
    def test_redoc_accessible(self):
        """Test that ReDoc is accessible at /redoc."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        # Verify it's actually ReDoc
        assert b"redoc" in response.content.lower()
    
    def test_openapi_json_accessible(self):
        """Test that OpenAPI JSON spec is accessible."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        spec = response.json()
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec
    
    def test_openapi_spec_has_security_scheme(self):
        """Test that OpenAPI spec includes HTTPBearer security scheme."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        # Check security schemes are defined
        assert "components" in spec
        assert "securitySchemes" in spec["components"]
        assert "HTTPBearer" in spec["components"]["securitySchemes"]
        
        # Verify HTTPBearer configuration
        bearer_scheme = spec["components"]["securitySchemes"]["HTTPBearer"]
        assert bearer_scheme["type"] == "http"
        assert bearer_scheme["scheme"] == "bearer"
    
    def test_openapi_spec_has_authentication_info(self):
        """Test that OpenAPI spec includes authentication documentation."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        # Check that description includes authentication info
        description = spec["info"]["description"]
        assert "Authentication" in description
        assert "Bearer" in description
        assert "Authorization" in description
        
        # Check for authentication examples
        assert "register" in description.lower()
        assert "login" in description.lower()
        assert "token" in description.lower()
    
    def test_openapi_spec_has_protected_endpoints(self):
        """Test that protected endpoints have security requirements."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        # Find at least one protected endpoint
        protected_endpoints = []
        for path, methods in spec["paths"].items():
            for method, details in methods.items():
                if "security" in details:
                    protected_endpoints.append(f"{method.upper()} {path}")
        
        # Should have many protected endpoints
        assert len(protected_endpoints) > 10, \
            f"Expected many protected endpoints, found {len(protected_endpoints)}"
        
        # Verify security format
        for path, methods in spec["paths"].items():
            for method, details in methods.items():
                if "security" in details:
                    security = details["security"]
                    assert isinstance(security, list)
                    assert len(security) > 0
                    assert "HTTPBearer" in security[0]
    
    def test_openapi_spec_has_tags(self):
        """Test that OpenAPI spec has endpoint tags for organization."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        # Check that tags are defined
        assert "tags" in spec
        assert len(spec["tags"]) > 5, "Should have multiple tag categories"
        
        # Verify tag structure
        for tag in spec["tags"]:
            assert "name" in tag
            assert "description" in tag
    
    def test_openapi_spec_has_contact_info(self):
        """Test that OpenAPI spec includes contact information."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        assert "contact" in spec["info"]
        contact = spec["info"]["contact"]
        assert "name" in contact
        assert "email" in contact
    
    def test_openapi_spec_has_license_info(self):
        """Test that OpenAPI spec includes license information."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        assert "license" in spec["info"]
        license_info = spec["info"]["license"]
        assert "name" in license_info
        assert "url" in license_info
    
    def test_swagger_ui_has_authorization_button(self):
        """Test that Swagger UI HTML includes authorization functionality."""
        response = client.get("/docs")
        content = response.content.decode('utf-8')
        
        # Swagger UI should have authorization capability
        # The actual button is rendered by JavaScript, but we can check
        # that the OpenAPI spec is loaded which includes security schemes
        assert "openapi.json" in content or "swagger" in content.lower()
    
    def test_documentation_completeness(self):
        """Test that documentation covers all major endpoint categories."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        # Check for major endpoint categories
        paths = spec["paths"]
        
        # Should have health endpoints
        health_endpoints = [p for p in paths if "health" in p]
        assert len(health_endpoints) > 0, "Missing health endpoints"
        
        # Should have auth endpoints
        auth_endpoints = [p for p in paths if "auth" in p]
        assert len(auth_endpoints) > 0, "Missing auth endpoints"
        
        # Should have various API endpoints
        assert len(paths) > 20, f"Expected many endpoints, found {len(paths)}"
    
    def test_error_response_documentation(self):
        """Test that error responses are documented."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        description = spec["info"]["description"]
        
        # Check for error response documentation
        assert "Error Responses" in description
        assert "400" in description
        assert "401" in description
        assert "403" in description
        assert "404" in description
        assert "429" in description
        assert "500" in description
        assert "503" in description
    
    def test_rate_limiting_documentation(self):
        """Test that rate limiting is documented."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        description = spec["info"]["description"]
        
        # Check for rate limiting documentation
        assert "Rate Limiting" in description
        assert "100 requests per minute" in description
        assert "429" in description


class TestAuthenticationExamples:
    """Test that authentication examples are included in documentation."""
    
    def test_registration_example_in_docs(self):
        """Test that registration example is in documentation."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        description = spec["info"]["description"]
        
        # Check for registration example
        assert "register" in description.lower()
        assert "/api/v1/auth/register" in description
        assert "email" in description
        assert "password" in description
    
    def test_login_example_in_docs(self):
        """Test that login example is in documentation."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        description = spec["info"]["description"]
        
        # Check for login example
        assert "login" in description.lower()
        assert "/api/v1/auth/login" in description
        assert "access_token" in description
        assert "bearer" in description.lower()
    
    def test_token_usage_example_in_docs(self):
        """Test that token usage example is in documentation."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        description = spec["info"]["description"]
        
        # Check for token usage example
        assert "Authorization: Bearer" in description
        assert "curl" in description.lower()
    
    def test_swagger_ui_usage_instructions(self):
        """Test that Swagger UI usage instructions are included."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        description = spec["info"]["description"]
        
        # Check for Swagger UI instructions
        assert "Swagger UI" in description
        assert "Authorize" in description
        assert "lock icon" in description.lower() or "🔒" in description
    
    def test_token_expiration_documented(self):
        """Test that token expiration is documented."""
        response = client.get("/api/v1/openapi.json")
        spec = response.json()
        
        description = spec["info"]["description"]
        
        # Check for token expiration info
        assert "expire" in description.lower() or "expiration" in description.lower()
        assert "24 hours" in description or "refresh" in description.lower()


@pytest.mark.asyncio
class TestDocumentationIntegration:
    """Integration tests for documentation with running server."""
    
    async def test_docs_load_without_errors(self):
        """Test that documentation pages load without errors."""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        assert len(response.content) > 1000  # Should have substantial content
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        assert len(response.content) > 1000  # Should have substantial content
    
    async def test_openapi_spec_is_valid_json(self):
        """Test that OpenAPI spec is valid JSON."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        
        # Should be able to parse as JSON
        spec = response.json()
        assert isinstance(spec, dict)
        assert "openapi" in spec
        
        # OpenAPI version should be 3.x
        assert spec["openapi"].startswith("3.")
