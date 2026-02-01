"""
Tests for PostgreSQLClient class with compatibility validation.

This module tests the PostgreSQLClient class functionality including
compatibility validation, error handling, and integration with existing
PostgreSQL functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.database.postgresql_client import PostgreSQLClient, PostgreSQLCompatibilityError
from app.database.models import CompatibilityResult, ConnectionStatus, ErrorType


class TestPostgreSQLClient:
    """Test cases for PostgreSQLClient class."""
    
    @pytest.fixture
    def client(self):
        """Create PostgreSQLClient instance for testing."""
        return PostgreSQLClient()
    
    @pytest.fixture
    def compatible_result(self):
        """Create a compatible CompatibilityResult for testing."""
        return CompatibilityResult(
            is_compatible=True,
            python_version="3.11.0",
            asyncpg_version="0.28.0",
            issues=[],
            recommendations=[]
        )
    
    @pytest.fixture
    def incompatible_result(self):
        """Create an incompatible CompatibilityResult for testing."""
        return CompatibilityResult(
            is_compatible=False,
            python_version="3.13.0",
            asyncpg_version="0.27.0",
            issues=["Python 3.13 not supported with asyncpg 0.27.0"],
            recommendations=["Upgrade asyncpg to version 0.28.0 or higher"]
        )
    
    @pytest.mark.asyncio
    async def test_validate_compatibility_success(self, client, compatible_result):
        """Test successful compatibility validation."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            result = await client.validate_compatibility()
            
            assert result.is_compatible is True
            assert result.python_version == "3.11.0"
            assert result.asyncpg_version == "0.28.0"
            assert client.is_compatibility_validated() is True
            assert client.get_compatibility_result() == compatible_result
    
    @pytest.mark.asyncio
    async def test_validate_compatibility_failure(self, client, incompatible_result):
        """Test compatibility validation failure."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=incompatible_result):
            with pytest.raises(PostgreSQLCompatibilityError) as exc_info:
                await client.validate_compatibility()
            
            assert "compatibility validation failed" in str(exc_info.value).lower()
            assert client.is_compatibility_validated() is False
            assert client.get_compatibility_result() == incompatible_result
    
    @pytest.mark.asyncio
    async def test_validate_compatibility_exception_handling(self, client):
        """Test compatibility validation with unexpected exceptions."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', side_effect=Exception("Unexpected error")):
            with pytest.raises(PostgreSQLCompatibilityError) as exc_info:
                await client.validate_compatibility()
            
            assert "Failed to validate PostgreSQL compatibility" in str(exc_info.value)
            assert client.is_compatibility_validated() is False
    
    @pytest.mark.asyncio
    async def test_create_pool_with_validation(self, client, compatible_result):
        """Test connection pool creation with compatibility validation."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
                mock_pool = AsyncMock()
                mock_create_pool.return_value = mock_pool
                
                pool = await client.create_pool("postgresql://user:pass@localhost/db")
                
                assert pool == mock_pool
                assert client.is_compatibility_validated() is True
                mock_create_pool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_pool_without_prior_validation(self, client, compatible_result):
        """Test that create_pool validates compatibility automatically."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
                mock_pool = AsyncMock()
                mock_create_pool.return_value = mock_pool
                
                # Should automatically validate compatibility
                pool = await client.create_pool("postgresql://user:pass@localhost/db")
                
                assert pool == mock_pool
                assert client.is_compatibility_validated() is True
    
    @pytest.mark.asyncio
    async def test_create_pool_compatibility_failure(self, client, incompatible_result):
        """Test connection pool creation with compatibility failure."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=incompatible_result):
            with pytest.raises(PostgreSQLCompatibilityError):
                await client.create_pool("postgresql://user:pass@localhost/db")
    
    @pytest.mark.asyncio
    async def test_execute_query_with_validation(self, client, compatible_result):
        """Test query execution with compatibility validation."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_session_local.return_value.__aenter__.return_value = mock_session
                mock_session.execute.return_value = "query_result"
                
                result = await client.execute_query("SELECT 1")
                
                assert result == "query_result"
                assert client.is_compatibility_validated() is True
                mock_session.execute.assert_called_once_with("SELECT 1", ())
                mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_session_context_manager(self, client, compatible_result):
        """Test session context manager with compatibility validation."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_session_local.return_value.__aenter__.return_value = mock_session
                mock_session_local.return_value.__aexit__.return_value = None
                
                async with client.get_session() as session:
                    assert session == mock_session
                
                assert client.is_compatibility_validated() is True
                mock_session.commit.assert_called_once()
                mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_session_with_exception(self, client, compatible_result):
        """Test session context manager with exception handling."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_session_local.return_value.__aenter__.return_value = mock_session
                mock_session_local.return_value.__aexit__.return_value = None
                
                with pytest.raises(Exception, match="Test exception"):
                    async with client.get_session() as session:
                        raise Exception("Test exception")
                
                mock_session.rollback.assert_called_once()
                mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, client, compatible_result):
        """Test successful connection test."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.test_postgres_connection', return_value=True):
                status = await client.test_connection()
                
                assert status.service == "PostgreSQL"
                assert status.is_connected is True
                assert status.response_time_ms > 0
                assert status.last_attempt is not None
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, client, compatible_result):
        """Test connection test failure."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.test_postgres_connection', return_value=False):
                status = await client.test_connection()
                
                assert status.service == "PostgreSQL"
                assert status.is_connected is False
                assert status.error == "Connection test failed"
                assert status.response_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_test_connection_compatibility_error(self, client, incompatible_result):
        """Test connection test with compatibility error."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=incompatible_result):
            status = await client.test_connection()
            
            assert status.service == "PostgreSQL"
            assert status.is_connected is False
            assert "Compatibility error" in status.error
            assert status.response_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_initialize_with_validation(self, client, compatible_result):
        """Test PostgreSQL initialization with compatibility validation."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.init_postgres') as mock_init:
                await client.initialize()
                
                assert client.is_compatibility_validated() is True
                mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_compatibility_failure(self, client, incompatible_result):
        """Test PostgreSQL initialization with compatibility failure."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=incompatible_result):
            with pytest.raises(PostgreSQLCompatibilityError):
                await client.initialize()
    
    @pytest.mark.asyncio
    async def test_close_connections(self, client):
        """Test closing PostgreSQL connections."""
        with patch('app.database.postgresql_client.close_postgres') as mock_close:
            await client.close()
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_reporting_integration(self, client, compatible_result):
        """Test integration with error reporting system."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch.object(client.error_reporter, 'format_connection_error') as mock_format:
                mock_format.return_value = "Formatted error message"
                with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                    mock_session = AsyncMock()
                    mock_session_local.return_value.__aenter__.return_value = mock_session
                    mock_session.execute.side_effect = Exception("Database error")
                    
                    with pytest.raises(Exception, match="Database error"):
                        await client.execute_query("SELECT 1")
                    
                    # Verify error was formatted and reported
                    mock_format.assert_called_once()
                    # Check that the method was called with keyword arguments
                    call_kwargs = mock_format.call_args.kwargs
                    assert call_kwargs['service'] == "PostgreSQL"
                    assert "Database error" in str(call_kwargs['error'])
    
    def test_get_resolution_steps(self, client):
        """Test resolution steps for different error types."""
        compatibility_steps = client._get_resolution_steps(ErrorType.COMPATIBILITY_ERROR)
        assert any("asyncpg" in step.lower() for step in compatibility_steps)
        assert any("python" in step.lower() for step in compatibility_steps)
        
        connection_steps = client._get_resolution_steps(ErrorType.CONNECTION_TIMEOUT)
        assert any("postgresql" in step.lower() for step in connection_steps)
        assert any("connection" in step.lower() for step in connection_steps)
    
    def test_client_state_management(self, client):
        """Test client state management."""
        # Initially not validated
        assert client.is_compatibility_validated() is False
        assert client.get_compatibility_result() is None
        
        # After setting result
        result = CompatibilityResult(
            is_compatible=True,
            python_version="3.11.0",
            asyncpg_version="0.28.0",
            issues=[],
            recommendations=[]
        )
        client._compatibility_result = result
        client._compatibility_validated = True
        
        assert client.is_compatibility_validated() is True
        assert client.get_compatibility_result() == result