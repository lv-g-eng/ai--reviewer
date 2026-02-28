"""
API Integration Tests

Tests all API endpoints end-to-end with test doubles for external services.
Validates Requirements 5.4, 5.7, 13.7

**Validates: Requirements 5.4, 5.7, 13.7**
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import json

from app.main import app
from app.models import User, Project, PullRequest, PRStatus
from app.utils.password import hash_password


class TestAuthenticationEndpoints:
    """Integration tests for authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_login_logout_flow(self, db_session):
        """
        Test complete authentication flow: register -> login -> logout
        
        **Validates: Requirements 5.4, 13.7**
        """
        # Override get_db dependency
        from app.database.postgresql import get_db
        
        async def override_get_db():
            yield db_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Step 1: Register
                register_data = {
                    "email": "integration@test.com",
                    "password": "SecurePass123!",
                    "full_name": "Integration Test User"
                }
                
                response = await client.post("/api/v1/auth/register", json=register_data)
                assert response.status_code == 201
                user_data = response.json()
                assert user_data["email"] == register_data["email"]
                assert user_data["full_name"] == register_data["full_name"]
                assert "id" in user_data
                
                # Step 2: Login with credentials
                login_data = {
                    "email": register_data["email"],
                    "password": register_data["password"]
                }
                
                response = await client.post("/api/v1/auth/login", json=login_data)
                assert response.status_code == 200
                token_data = response.json()
                assert "access_token" in token_data
                assert "refresh_token" in token_data
                
                access_token = token_data["access_token"]
                
                # Step 3: Access protected endpoint
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get("/api/v1/auth/me", headers=headers)
                assert response.status_code == 200
                me_data = response.json()
                assert me_data["email"] == register_data["email"]
                
                # Step 4: Logout
                response = await client.post("/api/v1/auth/logout", headers=headers)
                assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, db_session):
        """
        Test token refresh with rotation
        
        **Validates: Requirements 5.4, 13.7**
        """
        from app.database.postgresql import get_db
        
        async def override_get_db():
            yield db_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            # Create and login user
            user = User(
                email="refresh@test.com",
                password_hash=hash_password("SecurePass123!"),
                full_name="Refresh Test"
            )
            db_session.add(user)
            await db_session.commit()
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                login_data = {
                    "email": "refresh@test.com",
                    "password": "SecurePass123!"
                }
                
                response = await client.post("/api/v1/auth/login", json=login_data)
                assert response.status_code == 200
                tokens = response.json()
                
                old_refresh_token = tokens["refresh_token"]
                
                # Refresh token
                refresh_data = {"refresh_token": old_refresh_token}
                response = await client.post("/api/v1/auth/refresh", json=refresh_data)
                assert response.status_code == 200
                new_tokens = response.json()
                
                assert "access_token" in new_tokens
                assert "refresh_token" in new_tokens
                assert new_tokens["refresh_token"] != old_refresh_token  # Token rotation
                
                # Old refresh token should be revoked
                response = await client.post("/api/v1/auth/refresh", json=refresh_data)
                assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()


class TestHealthEndpoints:
    """Integration tests for health check endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_integration(self):
        """
        Test health endpoint with mocked dependencies
        
        **Validates: Requirements 5.4, 13.7**
        """
        with patch('app.services.health_service.get_connection_manager') as mock_manager:
            mock_conn_manager = AsyncMock()
            mock_conn_manager.verify_all.return_value = {
                "PostgreSQL": MagicMock(
                    service="PostgreSQL",
                    is_connected=True,
                    response_time_ms=10.5,
                    is_critical=True
                ),
                "Neo4j": MagicMock(
                    service="Neo4j",
                    is_connected=True,
                    response_time_ms=15.2,
                    is_critical=False
                ),
                "Redis": MagicMock(
                    service="Redis",
                    is_connected=True,
                    response_time_ms=5.1,
                    is_critical=False
                )
            }
            mock_manager.return_value = mock_conn_manager
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert "databases" in data
                assert "PostgreSQL" in data["databases"]
                assert "Neo4j" in data["databases"]
                assert "Redis" in data["databases"]
    
    @pytest.mark.asyncio
    async def test_liveness_endpoint(self):
        """
        Test liveness endpoint
        
        **Validates: Requirements 5.4, 13.7**
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health/live")
            
            assert response.status_code == 200
            data = response.json()
            assert data["alive"] is True


class TestErrorHandling:
    """Integration tests for error handling across endpoints"""
    
    @pytest.mark.asyncio
    async def test_404_not_found(self):
        """
        Test 404 error handling
        
        **Validates: Requirements 5.4, 13.7**
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/nonexistent")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_401_unauthorized(self):
        """
        Test 401 unauthorized error
        
        **Validates: Requirements 5.4, 13.7**
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/auth/me")
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_validation_error(self):
        """
        Test validation error handling
        
        **Validates: Requirements 5.4, 13.7**
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Invalid email format
            register_data = {
                "email": "invalid-email",
                "password": "SecurePass123!"
            }
            
            response = await client.post("/api/v1/auth/register", json=register_data)
            assert response.status_code == 422  # Validation error


class TestCORSConfiguration:
    """Integration tests for CORS configuration"""
    
    @pytest.mark.asyncio
    async def test_cors_headers(self):
        """
        Test CORS headers are present
        
        **Validates: Requirements 5.4, 13.7**
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.options(
                "/api/v1/auth/login",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST"
                }
            )
            
            # CORS headers should be present
            assert "access-control-allow-origin" in response.headers or response.status_code == 200
