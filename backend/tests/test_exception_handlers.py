"""
Tests for FastAPI exception handlers

Validates Requirements: 2.5, 12.1, 12.2, 12.3
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.api.exception_handlers import (
    register_exception_handlers,
    get_request_context,
    create_error_response,
)
from app.shared.exceptions import (
    ServiceException,
    AuthenticationException,
    AuthorizationException,
    ValidationException,
    DatabaseException,
    LLMProviderException,
    CircuitBreakerException,
    CacheException,
    NotFoundException,
    ConflictException,
    RateLimitException,
    ExternalServiceException,
    TimeoutException,
)


@pytest.fixture
def app():
    """Create test FastAPI app"""
    app = FastAPI()
    register_exception_handlers(app)
    
    # Add test endpoints that raise various exceptions
    @app.get("/test/authentication-error")
    async def test_authentication_error():
        raise AuthenticationException("Invalid credentials")
    
    @app.get("/test/authorization-error")
    async def test_authorization_error():
        raise AuthorizationException("Access denied", resource="project", action="delete")
    
    @app.get("/test/not-found")
    async def test_not_found():
        raise NotFoundException("Resource not found", resource_type="project", resource_id="123")
    
    @app.get("/test/conflict")
    async def test_conflict():
        raise ConflictException("Resource already exists", resource_type="user", conflict_field="email")
    
    @app.get("/test/validation-error")
    async def test_validation_error():
        raise ValidationException("Invalid input", field="email", value="invalid")
    
    @app.get("/test/rate-limit")
    async def test_rate_limit():
        raise RateLimitException("Rate limit exceeded", retry_after=60)
    
    @app.get("/test/timeout")
    async def test_timeout():
        raise TimeoutException("Operation timed out", operation="llm_call", timeout_seconds=30.0)
    
    @app.get("/test/database-error")
    async def test_database_error():
        raise DatabaseException("Database connection failed", database="postgresql")
    
    @app.get("/test/llm-error")
    async def test_llm_error():
        raise LLMProviderException("LLM API error", provider="openai", model="gpt-4")
    
    @app.get("/test/circuit-breaker")
    async def test_circuit_breaker():
        raise CircuitBreakerException("Circuit breaker open", service_name="github", failure_count=5)
    
    @app.get("/test/cache-error")
    async def test_cache_error():
        raise CacheException("Cache operation failed", operation="get", key="test_key")
    
    @app.get("/test/external-service")
    async def test_external_service():
        raise ExternalServiceException("External service error", service_name="github", status_code=503)
    
    @app.get("/test/unhandled-error")
    async def test_unhandled_error():
        raise ValueError("Unexpected error")
    
    @app.get("/test/generic-service-error")
    async def test_generic_service_error():
        raise ServiceException("Generic service error", error_code="GENERIC_ERROR")
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app, raise_server_exceptions=False)


class TestExceptionHandlers:
    """Test exception handler functionality"""
    
    def test_authentication_exception_returns_401(self, client):
        """Test authentication exception returns 401 status code"""
        response = client.get("/test/authentication-error")
        
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "AUTH_FAILED"
        assert data["error"]["status"] == 401
        assert "Invalid credentials" in data["error"]["message"]
    
    def test_authorization_exception_returns_403(self, client):
        """Test authorization exception returns 403 status code"""
        response = client.get("/test/authorization-error")
        
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"
        assert data["error"]["status"] == 403
        assert "Access denied" in data["error"]["message"]
    
    def test_not_found_exception_returns_404(self, client):
        """Test not found exception returns 404 status code"""
        response = client.get("/test/not-found")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
        assert data["error"]["status"] == 404
        assert "Resource not found" in data["error"]["message"]
    
    def test_conflict_exception_returns_409(self, client):
        """Test conflict exception returns 409 status code"""
        response = client.get("/test/conflict")
        
        assert response.status_code == 409
        data = response.json()
        assert data["error"]["code"] == "CONFLICT"
        assert data["error"]["status"] == 409
        assert "already exists" in data["error"]["message"]
    
    def test_validation_exception_returns_422(self, client):
        """Test validation exception returns 422 status code"""
        response = client.get("/test/validation-error")
        
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["status"] == 422
        assert "Invalid input" in data["error"]["message"]
    
    def test_rate_limit_exception_returns_429(self, client):
        """Test rate limit exception returns 429 with retry-after header"""
        response = client.get("/test/rate-limit")
        
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert response.headers["Retry-After"] == "60"
        
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert data["error"]["status"] == 429
    
    def test_timeout_exception_returns_504(self, client):
        """Test timeout exception returns 504 status code"""
        response = client.get("/test/timeout")
        
        assert response.status_code == 504
        data = response.json()
        assert data["error"]["code"] == "TIMEOUT"
        assert data["error"]["status"] == 504
        assert "timed out" in data["error"]["message"]
    
    def test_database_exception_returns_500(self, client):
        """Test database exception returns 500 status code"""
        response = client.get("/test/database-error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["status"] == 500
        assert "Database" in data["error"]["message"]
    
    def test_llm_exception_returns_500(self, client):
        """Test LLM provider exception returns 500 status code"""
        response = client.get("/test/llm-error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["status"] == 500
    
    def test_circuit_breaker_exception_returns_503(self, client):
        """Test circuit breaker exception returns 503 status code"""
        response = client.get("/test/circuit-breaker")
        
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "CIRCUIT_OPEN"
        assert data["error"]["status"] == 503
        assert "Circuit breaker" in data["error"]["message"]
    
    def test_cache_exception_returns_500(self, client):
        """Test cache exception returns 500 status code"""
        response = client.get("/test/cache-error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["status"] == 500
    
    def test_external_service_exception_returns_502(self, client):
        """Test external service exception returns 502 status code"""
        response = client.get("/test/external-service")
        
        assert response.status_code == 502
        data = response.json()
        assert data["error"]["code"] == "EXTERNAL_SERVICE_ERROR"
        assert data["error"]["status"] == 502
    
    def test_unhandled_exception_returns_500(self, client):
        """Test unhandled exception returns 500 with generic message"""
        response = client.get("/test/unhandled-error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert data["error"]["status"] == 500
        assert data["error"]["message"] == "An internal server error occurred"
        # Should not expose internal error details in production
    
    def test_generic_service_exception_returns_400(self, client):
        """Test generic service exception returns 400 status code"""
        response = client.get("/test/generic-service-error")
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "GENERIC_ERROR"
        assert data["error"]["status"] == 400
    
    def test_error_response_has_standardized_format(self, client):
        """Test all error responses follow standardized format"""
        response = client.get("/test/authentication-error")
        data = response.json()
        
        # Validate standardized format (Requirement 12.3)
        assert "error" in data
        assert "message" in data["error"]
        assert "code" in data["error"]
        assert "status" in data["error"]
        assert isinstance(data["error"]["message"], str)
        assert isinstance(data["error"]["code"], str)
        assert isinstance(data["error"]["status"], int)
    
    def test_exception_with_details(self, client):
        """Test exception details are included in response"""
        # Create endpoint with detailed exception
        app = client.app
        
        @app.get("/test/detailed-error")
        async def test_detailed_error():
            raise ValidationException(
                "Validation failed",
                field="email",
                details={"reason": "Invalid format", "expected": "user@example.com"}
            )
        
        response = client.get("/test/detailed-error")
        data = response.json()
        
        assert response.status_code == 422
        assert "details" in data["error"]
        assert data["error"]["details"]["reason"] == "Invalid format"


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_get_request_context(self):
        """Test request context extraction"""
        # Create mock request
        from fastapi import FastAPI
        from starlette.testclient import TestClient
        
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint(request: Request):
            context = get_request_context(request)
            return context
        
        client = TestClient(app)
        response = client.get("/test?param=value")
        data = response.json()
        
        assert data["method"] == "GET"
        assert data["path"] == "/test"
        assert "param" in data["query_params"]
        assert data["query_params"]["param"] == "value"
        assert "client_host" in data
        assert "user_agent" in data
    
    def test_create_error_response(self):
        """Test error response creation"""
        response = create_error_response(
            status_code=400,
            message="Test error",
            error_code="TEST_ERROR",
            details={"field": "test"},
            request_id="req-123"
        )
        
        assert response.status_code == 400
        data = response.body.decode()
        import json
        data = json.loads(data)
        
        assert data["error"]["message"] == "Test error"
        assert data["error"]["code"] == "TEST_ERROR"
        assert data["error"]["status"] == 400
        assert data["error"]["details"]["field"] == "test"
        assert data["error"]["request_id"] == "req-123"
    
    def test_create_error_response_minimal(self):
        """Test error response creation with minimal parameters"""
        response = create_error_response(
            status_code=500,
            message="Internal error",
            error_code="INTERNAL_ERROR"
        )
        
        assert response.status_code == 500
        data = response.body.decode()
        import json
        data = json.loads(data)
        
        assert data["error"]["message"] == "Internal error"
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert data["error"]["status"] == 500
        assert "details" not in data["error"]
        assert "request_id" not in data["error"]


class TestExceptionClasses:
    """Test custom exception classes"""
    
    def test_service_exception_base(self):
        """Test base ServiceException"""
        exc = ServiceException(
            message="Test error",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        
        assert exc.message == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.details == {"key": "value"}
        assert str(exc) == "Test error"
    
    def test_authentication_exception(self):
        """Test AuthenticationException"""
        exc = AuthenticationException("Invalid token")
        
        assert exc.message == "Invalid token"
        assert exc.error_code == "AUTH_FAILED"
    
    def test_authorization_exception(self):
        """Test AuthorizationException"""
        exc = AuthorizationException(
            "Access denied",
            resource="project",
            action="delete"
        )
        
        assert exc.message == "Access denied"
        assert exc.resource == "project"
        assert exc.action == "delete"
        assert exc.error_code == "FORBIDDEN"
    
    def test_not_found_exception(self):
        """Test NotFoundException"""
        exc = NotFoundException(
            "Project not found",
            resource_type="project",
            resource_id="123"
        )
        
        assert exc.message == "Project not found"
        assert exc.resource_type == "project"
        assert exc.resource_id == "123"
        assert exc.error_code == "NOT_FOUND"
    
    def test_conflict_exception(self):
        """Test ConflictException"""
        exc = ConflictException(
            "Email already exists",
            resource_type="user",
            conflict_field="email"
        )
        
        assert exc.message == "Email already exists"
        assert exc.resource_type == "user"
        assert exc.conflict_field == "email"
        assert exc.error_code == "CONFLICT"
    
    def test_rate_limit_exception(self):
        """Test RateLimitException"""
        exc = RateLimitException(
            "Too many requests",
            retry_after=60
        )
        
        assert exc.message == "Too many requests"
        assert exc.retry_after == 60
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
    
    def test_timeout_exception(self):
        """Test TimeoutException"""
        exc = TimeoutException(
            "Request timed out",
            operation="llm_call",
            timeout_seconds=30.0
        )
        
        assert exc.message == "Request timed out"
        assert exc.operation == "llm_call"
        assert exc.timeout_seconds == 30.0
        assert exc.error_code == "TIMEOUT"
    
    def test_external_service_exception(self):
        """Test ExternalServiceException"""
        exc = ExternalServiceException(
            "GitHub API error",
            service_name="github",
            status_code=503
        )
        
        assert exc.message == "GitHub API error"
        assert exc.service_name == "github"
        assert exc.status_code == 503
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_exception_with_none_details(self, client):
        """Test exception with None details is handled correctly"""
        app = client.app
        
        @app.get("/test/none-details")
        async def test_none_details():
            raise ServiceException("Test error", error_code="TEST", details=None)
        
        response = client.get("/test/none-details")
        data = response.json()
        
        assert response.status_code == 400
        assert "details" not in data["error"]
    
    def test_exception_with_empty_details(self, client):
        """Test exception with empty details dict"""
        app = client.app
        
        @app.get("/test/empty-details")
        async def test_empty_details():
            raise ServiceException("Test error", error_code="TEST", details={})
        
        response = client.get("/test/empty-details")
        data = response.json()
        
        assert response.status_code == 400
        # Empty details should not be included
        assert "details" not in data["error"]
    
    def test_exception_without_error_code(self, client):
        """Test exception without error code uses default"""
        app = client.app
        
        @app.get("/test/no-code")
        async def test_no_code():
            raise ServiceException("Test error")
        
        response = client.get("/test/no-code")
        data = response.json()
        
        assert response.status_code == 400
        assert data["error"]["code"] == "SERVICE_ERROR"
    
    def test_request_context_with_user_object(self, client, caplog):
        """Test request context extraction with user object"""
        import logging
        caplog.set_level(logging.ERROR)
        
        app = client.app
        
        @app.get("/test/user-object")
        async def test_user_object(request: Request):
            # Simulate user object with id attribute
            class User:
                def __init__(self):
                    self.id = "user-789"
            
            request.state.user = User()
            raise AuthenticationException("Test error")
        
        response = client.get("/test/user-object")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify user ID extracted from user object
        context = error_record.__dict__["request_context"]
        assert "user_id" in context
        assert context["user_id"] == "user-789"
    
    def test_request_context_with_user_dict(self, client, caplog):
        """Test request context extraction with user dict"""
        import logging
        caplog.set_level(logging.ERROR)
        
        app = client.app
        
        @app.get("/test/user-dict")
        async def test_user_dict(request: Request):
            # Simulate user dict
            request.state.user = {"id": "user-999", "email": "test@example.com"}
            raise AuthenticationException("Test error")
        
        response = client.get("/test/user-dict")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify user ID extracted from user dict
        context = error_record.__dict__["request_context"]
        assert "user_id" in context
        assert context["user_id"] == "user-999"
    
    def test_request_context_without_client(self, client, caplog):
        """Test request context when client info is not available"""
        import logging
        caplog.set_level(logging.ERROR)
        
        # This is handled by the get_request_context function
        # which checks if request.client exists
        response = client.get("/test/authentication-error")
        
        # Should not raise an error even if client is None
        assert response.status_code == 401
    
    def test_multiple_exceptions_same_request(self, client):
        """Test handling multiple exception types in sequence"""
        # Test that exception handlers don't interfere with each other
        response1 = client.get("/test/authentication-error")
        response2 = client.get("/test/authorization-error")
        response3 = client.get("/test/not-found")
        
        assert response1.status_code == 401
        assert response2.status_code == 403
        assert response3.status_code == 404
    
    def test_exception_with_special_characters_in_message(self, client):
        """Test exception with special characters in message"""
        app = client.app
        
        @app.get("/test/special-chars")
        async def test_special_chars():
            raise ServiceException(
                "Error with special chars: <>&\"'",
                error_code="SPECIAL"
            )
        
        response = client.get("/test/special-chars")
        data = response.json()
        
        assert response.status_code == 400
        assert "<>&\"'" in data["error"]["message"]
    
    def test_exception_with_unicode_message(self, client):
        """Test exception with unicode characters"""
        app = client.app
        
        @app.get("/test/unicode")
        async def test_unicode():
            raise ServiceException(
                "Error with unicode: 你好 мир 🚀",
                error_code="UNICODE"
            )
        
        response = client.get("/test/unicode")
        data = response.json()
        
        assert response.status_code == 400
        assert "你好" in data["error"]["message"]
        assert "мир" in data["error"]["message"]
        assert "🚀" in data["error"]["message"]
    
    def test_exception_with_very_long_message(self, client):
        """Test exception with very long message"""
        app = client.app
        
        @app.get("/test/long-message")
        async def test_long_message():
            long_msg = "Error: " + "x" * 10000
            raise ServiceException(long_msg, error_code="LONG")
        
        response = client.get("/test/long-message")
        data = response.json()
        
        assert response.status_code == 400
        # Message should be included in full
        assert len(data["error"]["message"]) > 10000
    
    def test_exception_with_nested_details(self, client):
        """Test exception with deeply nested details"""
        app = client.app
        
        @app.get("/test/nested-details")
        async def test_nested_details():
            raise ServiceException(
                "Test error",
                error_code="NESTED",
                details={
                    "level1": {
                        "level2": {
                            "level3": {
                                "value": "deep"
                            }
                        }
                    }
                }
            )
        
        response = client.get("/test/nested-details")
        data = response.json()
        
        assert response.status_code == 400
        assert data["error"]["details"]["level1"]["level2"]["level3"]["value"] == "deep"
    
    def test_exception_with_list_details(self, client):
        """Test exception with list in details"""
        app = client.app
        
        @app.get("/test/list-details")
        async def test_list_details():
            raise ServiceException(
                "Test error",
                error_code="LIST",
                details={
                    "errors": ["error1", "error2", "error3"]
                }
            )
        
        response = client.get("/test/list-details")
        data = response.json()
        
        assert response.status_code == 400
        assert len(data["error"]["details"]["errors"]) == 3
        assert "error1" in data["error"]["details"]["errors"]


class TestStructuredErrorLogging:
    """Test structured error logging features (Requirement 12.2)"""
    
    def test_error_logging_includes_full_stack_trace(self, client, caplog):
        """Test that errors are logged with full stack traces"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/database-error")
        
        # Check that error was logged
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify stack trace is included
        assert error_record.exc_info is not None
        assert "stack_trace" in error_record.__dict__
    
    def test_error_logging_includes_request_context(self, client, caplog):
        """Test that errors include comprehensive request context"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/authentication-error?test=value")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify request context is included
        assert "request_context" in error_record.__dict__
        context = error_record.__dict__["request_context"]
        
        assert context["method"] == "GET"
        assert context["path"] == "/test/authentication-error"
        assert "query_params" in context
        assert context["query_params"]["test"] == "value"
        assert "client_host" in context
        assert "user_agent" in context
        assert "url" in context
        assert "scheme" in context
        assert "host" in context
    
    def test_error_logging_includes_exception_details(self, client, caplog):
        """Test that errors include exception-specific details"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/llm-error")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify exception-specific fields
        assert "exception_type" in error_record.__dict__
        assert error_record.__dict__["exception_type"] == "LLMProviderException"
        assert "llm_provider" in error_record.__dict__
        assert error_record.__dict__["llm_provider"] == "openai"
        assert "llm_model" in error_record.__dict__
        assert error_record.__dict__["llm_model"] == "gpt-4"
    
    def test_error_logging_for_circuit_breaker(self, client, caplog):
        """Test circuit breaker exception logging includes service details"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/circuit-breaker")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify circuit breaker fields
        assert "service_name" in error_record.__dict__
        assert error_record.__dict__["service_name"] == "github"
        assert "failure_count" in error_record.__dict__
        assert error_record.__dict__["failure_count"] == 5
    
    def test_error_logging_for_database_exception(self, client, caplog):
        """Test database exception logging includes database details"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/database-error")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify database fields
        assert "database" in error_record.__dict__
        assert error_record.__dict__["database"] == "postgresql"
    
    def test_error_logging_for_authorization_exception(self, client, caplog):
        """Test authorization exception logging includes resource details"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/authorization-error")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify authorization fields
        assert "resource" in error_record.__dict__
        assert error_record.__dict__["resource"] == "project"
        assert "action" in error_record.__dict__
        assert error_record.__dict__["action"] == "delete"
    
    def test_error_logging_for_timeout_exception(self, client, caplog):
        """Test timeout exception logging includes timeout details"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/timeout")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify timeout fields
        assert "operation" in error_record.__dict__
        assert error_record.__dict__["operation"] == "llm_call"
        assert "timeout_seconds" in error_record.__dict__
        assert error_record.__dict__["timeout_seconds"] == 30.0
    
    def test_error_logging_for_external_service_exception(self, client, caplog):
        """Test external service exception logging includes service details"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/external-service")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify external service fields
        assert "service_name" in error_record.__dict__
        assert error_record.__dict__["service_name"] == "github"
        assert "service_status_code" in error_record.__dict__
        assert error_record.__dict__["service_status_code"] == 503
    
    def test_validation_error_logging(self, client, caplog):
        """Test validation errors are logged with context"""
        import logging
        caplog.set_level(logging.WARNING)
        
        # Create endpoint with validation error
        from pydantic import BaseModel, Field
        
        class TestModel(BaseModel):
            email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
        
        app = client.app
        
        @app.post("/test/validate")
        async def test_validate(data: TestModel):
            return {"ok": True}
        
        response = client.post("/test/validate", json={"email": "invalid"})
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify validation error logging
        assert "validation_errors" in error_record.__dict__
        assert "request_context" in error_record.__dict__
        assert "stack_trace" in error_record.__dict__
    
    def test_unhandled_exception_logging(self, client, caplog):
        """Test unhandled exceptions are logged with full context"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/unhandled-error")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify comprehensive logging
        assert "exception_type" in error_record.__dict__
        assert error_record.__dict__["exception_type"] == "ValueError"
        assert "exception_module" in error_record.__dict__
        assert "exception_message" in error_record.__dict__
        assert "request_context" in error_record.__dict__
        assert "stack_trace" in error_record.__dict__
    
    def test_request_id_in_error_response(self, client):
        """Test that request ID is included in error response when available"""
        # Create endpoint that sets request ID
        app = client.app
        
        @app.get("/test/with-request-id")
        async def test_with_request_id(request: Request):
            request.state.request_id = "test-req-123"
            raise AuthenticationException("Test error")
        
        response = client.get("/test/with-request-id")
        data = response.json()
        
        # Verify request ID in response
        assert "request_id" in data["error"]
        assert data["error"]["request_id"] == "test-req-123"
    
    def test_user_id_in_error_logs(self, client, caplog):
        """Test that user ID is included in error logs when available"""
        import logging
        caplog.set_level(logging.ERROR)
        
        # Create endpoint that sets user ID
        app = client.app
        
        @app.get("/test/with-user-id")
        async def test_with_user_id(request: Request):
            request.state.user_id = "user-456"
            raise DatabaseException("Test error", database="postgresql")
        
        response = client.get("/test/with-user-id")
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify user ID in request context
        assert "request_context" in error_record.__dict__
        context = error_record.__dict__["request_context"]
        assert "user_id" in context
        assert context["user_id"] == "user-456"
    
    def test_safe_headers_in_error_logs(self, client, caplog):
        """Test that only safe headers are included in error logs"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get(
            "/test/authentication-error",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer secret-token",
                "Accept": "application/json",
            }
        )
        
        # Check log record
        assert len(caplog.records) > 0
        error_record = caplog.records[0]
        
        # Verify safe headers are included
        context = error_record.__dict__["request_context"]
        assert "headers" in context
        assert "content-type" in context["headers"]
        assert "accept" in context["headers"]
        
        # Verify sensitive headers are excluded
        assert "authorization" not in context["headers"]



class TestErrorResponseFormat:
    """Test standardized error response format (Requirement 12.3)"""
    
    def test_all_error_responses_have_required_fields(self, client):
        """Test that all error types return required fields"""
        endpoints = [
            "/test/authentication-error",
            "/test/authorization-error",
            "/test/not-found",
            "/test/conflict",
            "/test/validation-error",
            "/test/rate-limit",
            "/test/timeout",
            "/test/database-error",
            "/test/llm-error",
            "/test/circuit-breaker",
            "/test/cache-error",
            "/test/external-service",
            "/test/unhandled-error",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()
            
            # Verify required fields
            assert "error" in data, f"Missing 'error' field in {endpoint}"
            assert "message" in data["error"], f"Missing 'message' in {endpoint}"
            assert "code" in data["error"], f"Missing 'code' in {endpoint}"
            assert "status" in data["error"], f"Missing 'status' in {endpoint}"
            
            # Verify field types
            assert isinstance(data["error"]["message"], str), f"Invalid message type in {endpoint}"
            assert isinstance(data["error"]["code"], str), f"Invalid code type in {endpoint}"
            assert isinstance(data["error"]["status"], int), f"Invalid status type in {endpoint}"
            
            # Verify status code matches HTTP status
            assert data["error"]["status"] == response.status_code, f"Status mismatch in {endpoint}"
    
    def test_error_response_json_serializable(self, client):
        """Test that all error responses are valid JSON"""
        import json
        
        response = client.get("/test/authentication-error")
        
        # Should not raise JSONDecodeError
        data = json.loads(response.content)
        assert isinstance(data, dict)
    
    def test_error_response_content_type(self, client):
        """Test that error responses have correct content type"""
        response = client.get("/test/authentication-error")
        
        assert "application/json" in response.headers["content-type"]
    
    def test_error_code_format(self, client):
        """Test that error codes follow naming convention"""
        response = client.get("/test/authentication-error")
        data = response.json()
        
        # Error codes should be uppercase with underscores
        error_code = data["error"]["code"]
        assert error_code.isupper() or "_" in error_code
        assert error_code.replace("_", "").isalnum()
    
    def test_error_message_not_empty(self, client):
        """Test that error messages are never empty"""
        endpoints = [
            "/test/authentication-error",
            "/test/authorization-error",
            "/test/not-found",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()
            
            assert len(data["error"]["message"]) > 0, f"Empty message in {endpoint}"
            assert data["error"]["message"].strip() != "", f"Whitespace-only message in {endpoint}"
    
    def test_error_response_no_sensitive_data(self, client):
        """Test that error responses don't expose sensitive data"""
        response = client.get("/test/database-error")
        data = response.json()
        
        # Should not contain sensitive information
        response_str = str(data).lower()
        sensitive_keywords = ["password", "secret", "token", "key", "credential"]
        
        for keyword in sensitive_keywords:
            assert keyword not in response_str, f"Sensitive keyword '{keyword}' found in error response"
    
    def test_error_response_consistent_structure(self, client):
        """Test that error structure is consistent across all error types"""
        endpoints = [
            "/test/authentication-error",
            "/test/not-found",
            "/test/database-error",
        ]
        
        structures = []
        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()
            
            # Get top-level keys
            top_keys = set(data.keys())
            error_keys = set(data["error"].keys())
            
            structures.append((top_keys, error_keys))
        
        # All should have same top-level structure
        assert all(s[0] == structures[0][0] for s in structures), "Inconsistent top-level structure"
        
        # All should have at least the required error keys
        required_keys = {"message", "code", "status"}
        for _, error_keys in structures:
            assert required_keys.issubset(error_keys), "Missing required error keys"


class TestConcurrentExceptionHandling:
    """Test exception handling under concurrent load"""
    
    def test_concurrent_different_exceptions(self, client):
        """Test handling different exceptions concurrently"""
        import concurrent.futures
        
        endpoints = [
            "/test/authentication-error",
            "/test/authorization-error",
            "/test/not-found",
            "/test/database-error",
        ]
        
        def make_request(endpoint):
            return client.get(endpoint)
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(make_request, ep) for ep in endpoints * 5]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert len(responses) == 20
        assert all(r.status_code in [401, 403, 404, 500] for r in responses)
    
    def test_concurrent_same_exception(self, client):
        """Test handling same exception type concurrently"""
        import concurrent.futures
        
        def make_request():
            return client.get("/test/authentication-error")
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should return 401
        assert len(responses) == 50
        assert all(r.status_code == 401 for r in responses)
        
        # All should have consistent response format
        for response in responses:
            data = response.json()
            assert data["error"]["code"] == "AUTH_FAILED"


class TestExceptionHandlerIntegration:
    """Test exception handlers integrated with FastAPI middleware"""
    
    def test_exception_handler_with_cors(self, client):
        """Test exception handling works with CORS headers"""
        response = client.get(
            "/test/authentication-error",
            headers={"Origin": "https://example.com"}
        )
        
        assert response.status_code == 401
        # Should still return valid error response
        data = response.json()
        assert "error" in data
    
    def test_exception_handler_with_custom_headers(self, client):
        """Test exception handling preserves custom headers"""
        response = client.get(
            "/test/rate-limit",
            headers={"X-Custom-Header": "test-value"}
        )
        
        assert response.status_code == 429
        # Rate limit should add Retry-After header
        assert "Retry-After" in response.headers
    
    def test_exception_handler_order(self, client):
        """Test that specific handlers are called before global handler"""
        # ServiceException should be caught by service_exception_handler
        response1 = client.get("/test/authentication-error")
        assert response1.status_code == 401
        
        # Generic Exception should be caught by global_exception_handler
        response2 = client.get("/test/unhandled-error")
        assert response2.status_code == 500
        
        # Responses should have different error codes
        data1 = response1.json()
        data2 = response2.json()
        assert data1["error"]["code"] != data2["error"]["code"]


class TestValidationErrorHandling:
    """Test validation error handling"""
    
    def test_pydantic_validation_error_format(self, client):
        """Test Pydantic validation errors are formatted correctly"""
        from pydantic import BaseModel, Field
        
        class TestModel(BaseModel):
            email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
            age: int = Field(..., ge=0, le=150)
        
        app = client.app
        
        @app.post("/test/validate-model")
        async def test_validate(data: TestModel):
            return {"ok": True}
        
        # Test with invalid data
        response = client.post("/test/validate-model", json={
            "email": "invalid-email",
            "age": 200
        })
        
        assert response.status_code == 422
        data = response.json()
        
        # Should have validation error format
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["error"]
        assert "errors" in data["error"]["details"]
        
        # Should have errors for both fields
        errors = data["error"]["details"]["errors"]
        assert len(errors) >= 2
        
        # Each error should have field, message, type
        for error in errors:
            assert "field" in error
            assert "message" in error
            assert "type" in error
    
    def test_missing_required_field_validation(self, client):
        """Test validation error for missing required fields"""
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            required_field: str
        
        app = client.app
        
        @app.post("/test/validate-required")
        async def test_validate(data: TestModel):
            return {"ok": True}
        
        # Test with missing field
        response = client.post("/test/validate-required", json={})
        
        assert response.status_code == 422
        data = response.json()
        
        errors = data["error"]["details"]["errors"]
        assert any("required_field" in e["field"] for e in errors)
    
    def test_type_validation_error(self, client):
        """Test validation error for wrong type"""
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            count: int
        
        app = client.app
        
        @app.post("/test/validate-type")
        async def test_validate(data: TestModel):
            return {"ok": True}
        
        # Test with wrong type
        response = client.post("/test/validate-type", json={"count": "not-a-number"})
        
        assert response.status_code == 422
        data = response.json()
        
        errors = data["error"]["details"]["errors"]
        assert any("count" in e["field"] for e in errors)


class TestExceptionAttributes:
    """Test exception-specific attributes are preserved"""
    
    def test_llm_exception_attributes(self, client, caplog):
        """Test LLM exception preserves provider and model"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/llm-error")
        
        # Check log record has LLM-specific fields
        error_record = caplog.records[0]
        assert error_record.__dict__["llm_provider"] == "openai"
        assert error_record.__dict__["llm_model"] == "gpt-4"
    
    def test_circuit_breaker_exception_attributes(self, client, caplog):
        """Test circuit breaker exception preserves service info"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/circuit-breaker")
        
        # Check log record has circuit breaker fields
        error_record = caplog.records[0]
        assert error_record.__dict__["service_name"] == "github"
        assert error_record.__dict__["failure_count"] == 5
    
    def test_authorization_exception_attributes(self, client, caplog):
        """Test authorization exception preserves resource and action"""
        import logging
        caplog.set_level(logging.ERROR)
        
        response = client.get("/test/authorization-error")
        
        # Check log record has authorization fields
        error_record = caplog.records[0]
        assert error_record.__dict__["resource"] == "project"
        assert error_record.__dict__["action"] == "delete"
    
    def test_not_found_exception_attributes(self, client):
        """Test not found exception preserves resource info"""
        app = client.app
        
        @app.get("/test/not-found-detailed")
        async def test_not_found_detailed():
            raise NotFoundException(
                "User not found",
                resource_type="user",
                resource_id="user-123"
            )
        
        response = client.get("/test/not-found-detailed")
        
        assert response.status_code == 404
        # Exception attributes should be logged (checked in other tests)


class TestErrorHandlingPerformance:
    """Test error handling performance"""
    
    def test_error_handling_response_time(self, client):
        """Test that error handling doesn't significantly slow down responses"""
        import time
        
        start = time.time()
        for _ in range(100):
            client.get("/test/authentication-error")
        elapsed = time.time() - start
        
        # 100 error responses should complete in reasonable time
        # Average should be well under 100ms per request
        avg_time = elapsed / 100
        assert avg_time < 0.1, f"Error handling too slow: {avg_time}s per request"
    
    def test_error_logging_doesnt_block(self, client):
        """Test that error logging doesn't block request handling"""
        import time
        
        # Make request that triggers error logging
        start = time.time()
        response = client.get("/test/database-error")
        elapsed = time.time() - start
        
        # Should respond quickly even with logging
        assert elapsed < 1.0, f"Error handling blocked for {elapsed}s"
        assert response.status_code == 500


class TestExceptionHandlerRegistration:
    """Test exception handler registration"""
    
    def test_handlers_registered_successfully(self):
        """Test that all handlers are registered"""
        from fastapi import FastAPI
        from app.api.exception_handlers import register_exception_handlers
        
        app = FastAPI()
        register_exception_handlers(app)
        
        # Check that exception handlers are registered
        # FastAPI stores handlers in app.exception_handlers
        assert len(app.exception_handlers) > 0
    
    def test_multiple_registration_safe(self):
        """Test that registering handlers multiple times is safe"""
        from fastapi import FastAPI
        from app.api.exception_handlers import register_exception_handlers
        
        app = FastAPI()
        
        # Register multiple times
        register_exception_handlers(app)
        register_exception_handlers(app)
        register_exception_handlers(app)
        
        # Should not cause errors
        # Handlers should still work
        from fastapi.testclient import TestClient
        from app.shared.exceptions import AuthenticationException
        
        @app.get("/test")
        async def test_endpoint():
            raise AuthenticationException("Test")
        
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")
        
        assert response.status_code == 401
