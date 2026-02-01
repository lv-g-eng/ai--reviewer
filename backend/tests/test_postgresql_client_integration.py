"""
Integration tests for PostgreSQLClient with existing database functionality.

This module tests the integration between the new PostgreSQLClient class
and the existing PostgreSQL database functionality.
"""

import pytest
from unittest.mock import patch, AsyncMock

from app.database.postgresql_client import PostgreSQLClient
from app.database.models import CompatibilityResult


class TestPostgreSQLClientIntegration:
    """Integration test cases for PostgreSQLClient."""
    
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
    
    @pytest.mark.asyncio
    async def test_client_wraps_existing_functionality(self, client, compatible_result):
        """Test that PostgreSQLClient properly wraps existing postgresql.py functionality."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            # Test that it uses existing init_postgres
            with patch('app.database.postgresql_client.init_postgres') as mock_init:
                await client.initialize()
                mock_init.assert_called_once()
            
            # Test that it uses existing test_postgres_connection
            with patch('app.database.postgresql_client.test_postgres_connection', return_value=True) as mock_test:
                status = await client.test_connection()
                mock_test.assert_called_once()
                assert status.is_connected is True
            
            # Test that it uses existing close_postgres
            with patch('app.database.postgresql_client.close_postgres') as mock_close:
                await client.close()
                mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_client_adds_compatibility_validation(self, client, compatible_result):
        """Test that PostgreSQLClient adds compatibility validation to existing functionality."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result) as mock_check:
            # Any operation should trigger compatibility validation
            with patch('app.database.postgresql_client.init_postgres'):
                await client.initialize()
            
            # Verify compatibility was checked
            mock_check.assert_called_once()
            assert client.is_compatibility_validated() is True
    
    @pytest.mark.asyncio
    async def test_client_uses_existing_session_local(self, client, compatible_result):
        """Test that PostgreSQLClient uses existing AsyncSessionLocal."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_session_local.return_value.__aenter__.return_value = mock_session
                mock_session.execute.return_value = "test_result"
                
                result = await client.execute_query("SELECT 1")
                
                # Verify it uses the existing AsyncSessionLocal
                mock_session_local.assert_called_once()
                mock_session.execute.assert_called_once_with("SELECT 1", ())
                mock_session.commit.assert_called_once()
                assert result == "test_result"
    
    @pytest.mark.asyncio
    async def test_client_session_context_manager(self, client, compatible_result):
        """Test that PostgreSQLClient session context manager works with existing functionality."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_session_local.return_value.__aenter__.return_value = mock_session
                mock_session_local.return_value.__aexit__.return_value = None
                
                async with client.get_session() as session:
                    assert session == mock_session
                
                # Verify proper session lifecycle management
                mock_session.commit.assert_called_once()
                mock_session.close.assert_called_once()
    
    def test_client_provides_enhanced_error_handling(self, client):
        """Test that PostgreSQLClient provides enhanced error handling."""
        # Test resolution steps for different error types
        from app.database.models import ErrorType
        
        compatibility_steps = client._get_resolution_steps(ErrorType.COMPATIBILITY_ERROR)
        assert len(compatibility_steps) > 0
        assert any("asyncpg" in step.lower() for step in compatibility_steps)
        
        connection_steps = client._get_resolution_steps(ErrorType.CONNECTION_TIMEOUT)
        assert len(connection_steps) > 0
        assert any("postgresql" in step.lower() for step in connection_steps)
    
    def test_client_maintains_backward_compatibility(self, client):
        """Test that PostgreSQLClient maintains backward compatibility."""
        # The client should not break existing interfaces
        assert hasattr(client, 'initialize')
        assert hasattr(client, 'close')
        assert hasattr(client, 'test_connection')
        assert hasattr(client, 'execute_query')
        assert hasattr(client, 'get_session')
        
        # New functionality should be available
        assert hasattr(client, 'validate_compatibility')
        assert hasattr(client, 'create_pool')
        assert hasattr(client, 'get_compatibility_result')
        assert hasattr(client, 'is_compatibility_validated')
    
    @pytest.mark.asyncio
    async def test_client_error_reporting_integration(self, client, compatible_result):
        """Test that PostgreSQLClient integrates with the error reporting system."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch.object(client.error_reporter, 'format_connection_error', return_value="Formatted error") as mock_format:
                with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                    mock_session = AsyncMock()
                    mock_session_local.return_value.__aenter__.return_value = mock_session
                    mock_session.execute.side_effect = Exception("Test error")
                    
                    with pytest.raises(Exception, match="Test error"):
                        await client.execute_query("SELECT 1")
                    
                    # Verify error reporting was used
                    mock_format.assert_called_once()
                    call_kwargs = mock_format.call_args.kwargs
                    assert call_kwargs['service'] == "PostgreSQL"
    
    @pytest.mark.asyncio
    async def test_client_connection_status_reporting(self, client, compatible_result):
        """Test that PostgreSQLClient provides detailed connection status."""
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.test_postgres_connection', return_value=True):
                status = await client.test_connection()
                
                # Verify status contains required information
                assert status.service == "PostgreSQL"
                assert status.is_connected is True
                assert status.response_time_ms >= 0
                assert status.last_attempt is not None
                
                # Test string representation
                status_str = str(status)
                assert "PostgreSQL" in status_str
                assert "✅" in status_str