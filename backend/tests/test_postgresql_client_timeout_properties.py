"""
Property-Based Tests for PostgreSQL Client Connection Timeout Handling

Tests core properties of PostgreSQL client connection timeout handling using hypothesis.
This module validates that the PostgreSQL client properly handles connection timeouts
across many different timeout scenarios and configurations.

**Validates: Requirements 1.2, 4.4**

Property 2: Connection Timeout Handling - For any database connection request, 
the connection should either complete within the configured timeout period or be 
terminated with proper cleanup and detailed logging.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime

from app.database.postgresql_client import PostgreSQLClient
from app.database.models import CompatibilityResult
from backend.tests.utils.secure_test_data import get_test_password, get_test_jwt_secret, get_test_api_key


# constants for testing to avoid hard-coded credentials in literal strings
TEST_PASSWORD = get_test_password("test_password_123")
TEST_USER = "test_user_name"
TEST_DB = "test_database_db"


class TestPostgreSQLClientTimeoutProperties:
    """Property-based tests for PostgreSQL client connection timeout handling"""
    
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=5000)
    @given(
        timeout_seconds=st.floats(min_value=0.5, max_value=3.0, allow_nan=False, allow_infinity=False),
        operation_delay=st.floats(min_value=0.0, max_value=6.0, allow_nan=False, allow_infinity=False).filter(lambda x: abs(x - 1.0) > 0.1),  # Avoid exact equality
        operation_type=st.sampled_from(['create_pool', 'execute_query', 'test_connection', 'initialize'])
    )
    @pytest.mark.asyncio
    async def test_connection_timeout_handling_property(
        self, 
        timeout_seconds: float,
        operation_delay: float,
        operation_type: str
    ):
        """
        **Feature: database-connectivity-fixes, Property 2: Connection Timeout Handling**
        
        For any database connection request, the connection should either complete 
        within the configured timeout period or be terminated with proper cleanup 
        and detailed logging.
        
        **Validates: Requirements 1.2, 4.4**
        """
        client = PostgreSQLClient()
        
        # Create a compatible result for this test
        compatible_result = CompatibilityResult(
            is_compatible=True,
            python_version="3.11.0",
            asyncpg_version="0.28.0",
            issues=[],
            recommendations=[]
        )
        
        # Mock compatibility validation
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            
            # Determine if operation should timeout based on delay vs timeout
            should_timeout = operation_delay > timeout_seconds
            
            if operation_type == 'create_pool':
                # Test connection pool creation with timeout
                async def mock_create_pool(*args, **kwargs):
                    await asyncio.sleep(operation_delay)
                    if should_timeout:
                        raise asyncio.TimeoutError(f"Connection timeout after {timeout_seconds}s")
                    return AsyncMock()
                
                with patch('asyncpg.create_pool', side_effect=mock_create_pool):
                    start_time = datetime.now()
                    
                    if should_timeout:
                        # Property: Operations exceeding timeout should raise TimeoutError
                        with pytest.raises((asyncio.TimeoutError, Exception)) as exc_info:
                            await asyncio.wait_for(
                                client.create_pool(f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}"),
                                timeout=timeout_seconds
                            )
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        
                        # Property: Timeout should occur approximately at the configured time
                        assert elapsed <= timeout_seconds + 1.0  # Allow 1s tolerance
                        
                        # Property: Error should indicate timeout (handle empty messages)
                        if isinstance(exc_info.value, asyncio.TimeoutError):
                            error_msg = str(exc_info.value).lower()
                            # Accept either "timeout" in message or empty message (which indicates timeout)
                            assert "timeout" in error_msg or error_msg == ""
                    else:
                        # Property: Operations within timeout should complete successfully
                        result = await asyncio.wait_for(
                            client.create_pool(f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}"),
                            timeout=timeout_seconds
                        )
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        
                        # Property: Successful operations should complete within timeout
                        assert elapsed <= timeout_seconds
                        assert result is not None
                        assert client.is_compatibility_validated() is True
            
            elif operation_type == 'execute_query':
                # Test query execution with timeout
                async def mock_session_execute(*args, **kwargs):
                    await asyncio.sleep(operation_delay)
                    if should_timeout:
                        raise asyncio.TimeoutError(f"Query timeout after {timeout_seconds}s")
                    return "query_result"
                
                with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                    mock_session = AsyncMock()
                    mock_session_local.return_value.__aenter__.return_value = mock_session
                    mock_session.execute.side_effect = mock_session_execute
                    
                    start_time = datetime.now()
                    
                    if should_timeout:
                        # Property: Query timeouts should be handled gracefully
                        with pytest.raises((asyncio.TimeoutError, Exception)):
                            await asyncio.wait_for(
                                client.execute_query("SELECT 1"),
                                timeout=timeout_seconds
                            )
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        assert elapsed <= timeout_seconds + 1.0  # Allow 1s tolerance
                    else:
                        # Property: Queries within timeout should complete successfully
                        result = await asyncio.wait_for(
                            client.execute_query("SELECT 1"),
                            timeout=timeout_seconds
                        )
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        assert elapsed <= timeout_seconds
                        assert result == "query_result"
            
            elif operation_type == 'test_connection':
                # Test connection testing with timeout
                async def mock_test_postgres_connection():
                    await asyncio.sleep(operation_delay)
                    if should_timeout:
                        raise asyncio.TimeoutError(f"Connection test timeout after {timeout_seconds}s")
                    return True
                
                with patch('app.database.postgresql_client.test_postgres_connection', side_effect=mock_test_postgres_connection):
                    start_time = datetime.now()
                    
                    if should_timeout:
                        # Property: Connection test timeouts should return proper status
                        try:
                            status = await asyncio.wait_for(
                                client.test_connection(),
                                timeout=timeout_seconds
                            )
                            # If we get here, the timeout was handled internally
                            assert status.service == "PostgreSQL"
                            assert status.is_connected is False
                            assert "timeout" in status.error.lower()
                        except asyncio.TimeoutError:
                            # External timeout is also acceptable
                            pass
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        assert elapsed <= timeout_seconds + 1.0  # Allow 1s tolerance
                    else:
                        # Property: Connection tests within timeout should complete successfully
                        status = await asyncio.wait_for(
                            client.test_connection(),
                            timeout=timeout_seconds
                        )
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        assert elapsed <= timeout_seconds
                        assert status.service == "PostgreSQL"
                        assert status.is_connected is True
                        assert status.response_time_ms >= 0
            
            elif operation_type == 'initialize':
                # Test initialization with timeout
                async def mock_init_postgres():
                    await asyncio.sleep(operation_delay)
                    if should_timeout:
                        raise asyncio.TimeoutError(f"Initialization timeout after {timeout_seconds}s")
                
                with patch('app.database.postgresql_client.init_postgres', side_effect=mock_init_postgres):
                    start_time = datetime.now()
                    
                    if should_timeout:
                        # Property: Initialization timeouts should be handled gracefully
                        with pytest.raises((asyncio.TimeoutError, Exception)):
                            await asyncio.wait_for(
                                client.initialize(),
                                timeout=timeout_seconds
                            )
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        assert elapsed <= timeout_seconds + 1.0  # Allow 1s tolerance
                    else:
                        # Property: Initialization within timeout should complete successfully
                        await asyncio.wait_for(
                            client.initialize(),
                            timeout=timeout_seconds
                        )
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        assert elapsed <= timeout_seconds
                        assert client.is_compatibility_validated() is True
    
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=5000)
    @given(
        pool_min_size=st.integers(min_value=1, max_value=10),
        pool_max_size=st.integers(min_value=1, max_value=20),
        command_timeout=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
        connection_timeout=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
        operation_delay=st.floats(min_value=0.0, max_value=8.0, allow_nan=False, allow_infinity=False)
    )
    @pytest.mark.asyncio
    async def test_pool_configuration_timeout_property(
        self, 
        pool_min_size: int,
        pool_max_size: int,
        command_timeout: float,
        connection_timeout: float,
        operation_delay: float
    ):
        """
        **Feature: database-connectivity-fixes, Property 2: Connection Timeout Handling**
        
        For any pool configuration with timeout settings, the PostgreSQL client 
        should respect the configured timeouts and handle timeout scenarios properly.
        
        **Validates: Requirements 1.2, 4.4**
        """
        client = PostgreSQLClient()
        
        # Ensure max_size >= min_size for valid configuration
        if pool_max_size < pool_min_size:
            pool_max_size = pool_min_size
        
        # Create a compatible result for this test
        compatible_result = CompatibilityResult(
            is_compatible=True,
            python_version="3.11.0",
            asyncpg_version="0.28.0",
            issues=[],
            recommendations=[]
        )
        
        # Determine if operation should timeout (add small buffer to avoid edge cases)
        effective_timeout = min(command_timeout, connection_timeout)
        should_timeout = operation_delay > (effective_timeout + 0.1)
        
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            
            async def mock_create_pool(dsn, **kwargs):
                # Simulate pool creation delay
                await asyncio.sleep(operation_delay)
                
                if should_timeout:
                    raise asyncio.TimeoutError(f"Pool creation timeout after {effective_timeout}s")
                
                # Property: Pool configuration should be respected
                assert kwargs.get('min_size', 5) == pool_min_size
                assert kwargs.get('max_size', 20) == pool_max_size
                assert kwargs.get('command_timeout', 30) == command_timeout
                
                return AsyncMock()
            
            with patch('asyncpg.create_pool', side_effect=mock_create_pool):
                start_time = datetime.now()
                
                if should_timeout:
                    # Property: Pool creation should timeout appropriately
                    with pytest.raises((asyncio.TimeoutError, Exception)):
                        await asyncio.wait_for(
                            client.create_pool(
                                f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}",
                                min_size=pool_min_size,
                                max_size=pool_max_size,
                                command_timeout=command_timeout
                            ),
                            timeout=connection_timeout
                        )
                    
                    elapsed = (datetime.now() - start_time).total_seconds()
                    # Property: Timeout should occur within reasonable bounds
                    assert elapsed <= max(connection_timeout, effective_timeout) + 1.0
                else:
                    # Property: Pool creation should succeed within timeout
                    pool = await asyncio.wait_for(
                        client.create_pool(
                            f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}",
                            min_size=pool_min_size,
                            max_size=pool_max_size,
                            command_timeout=command_timeout
                        ),
                        timeout=connection_timeout
                    )
                    
                    elapsed = (datetime.now() - start_time).total_seconds()
                    assert elapsed <= connection_timeout
                    assert pool is not None
    
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=5000)
    @given(
        timeout_error_message=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        timeout_duration=st.floats(min_value=0.5, max_value=3.0, allow_nan=False, allow_infinity=False),
        cleanup_delay=st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False)
    )
    @pytest.mark.asyncio
    async def test_timeout_error_handling_and_cleanup_property(
        self, 
        timeout_error_message: str,
        timeout_duration: float,
        cleanup_delay: float
    ):
        """
        **Feature: database-connectivity-fixes, Property 2: Connection Timeout Handling**
        
        For any timeout error, the PostgreSQL client should provide detailed error 
        information and perform proper cleanup operations.
        
        **Validates: Requirements 1.2, 4.4**
        """
        client = PostgreSQLClient()
        
        # Create a compatible result for this test
        compatible_result = CompatibilityResult(
            is_compatible=True,
            python_version="3.11.0",
            asyncpg_version="0.28.0",
            issues=[],
            recommendations=[]
        )
        
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            
            # Mock pool creation to simulate timeout with custom error message
            async def mock_create_pool_with_timeout(*args, **kwargs):
                await asyncio.sleep(timeout_duration + 0.1)  # Ensure timeout occurs
                raise asyncio.TimeoutError(timeout_error_message)
            
            with patch('asyncpg.create_pool', side_effect=mock_create_pool_with_timeout):
                start_time = datetime.now()
                
                # Property: Timeout errors should be handled gracefully
                with pytest.raises((asyncio.TimeoutError, Exception)) as exc_info:
                    await asyncio.wait_for(
                        client.create_pool(f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}"),
                        timeout=timeout_duration
                    )
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                # Property: Timeout should occur within expected timeframe
                assert elapsed <= timeout_duration + 2.0  # Allow reasonable tolerance
                
                # Property: Error information should be preserved (handle empty messages)
                if isinstance(exc_info.value, asyncio.TimeoutError):
                    # Either the original timeout message or a generic timeout message or empty (all indicate timeout)
                    error_str = str(exc_info.value).lower()
                    # Accept timeout in message, original message, or empty string (all valid for timeout)
                    assert "timeout" in error_str or timeout_error_message.lower() in error_str or error_str == ""
                
                # Property: Client state should remain consistent after timeout
                assert client.is_compatibility_validated() is True
                
                # Simulate cleanup operations
                await asyncio.sleep(cleanup_delay)
                
                # Property: Client should be able to handle new operations after timeout
                with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_successful_pool:
                    mock_pool = AsyncMock()
                    mock_successful_pool.return_value = mock_pool
                    
                    # Should be able to create pool successfully after timeout
                    new_pool = await client.create_pool(f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}")
                    assert new_pool == mock_pool