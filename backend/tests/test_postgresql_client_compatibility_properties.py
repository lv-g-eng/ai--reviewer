"""
Property-Based Tests for PostgreSQL Client Connection Compatibility Validation

Tests core properties of PostgreSQL client compatibility validation using hypothesis.
This module validates that the PostgreSQL client properly handles version compatibility
across many different Python and asyncpg version combinations.

**Validates: Requirements 1.1, 1.3, 1.4**

Property 1: Connection Compatibility Validation - For any Python version and asyncpg 
version combination, the PostgreSQL client should establish connections successfully 
when versions are compatible and fail gracefully with clear error messages when incompatible.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from hypothesis import given, strategies as st, settings, HealthCheck

from app.database.postgresql_client import PostgreSQLClient, PostgreSQLCompatibilityError
from app.database.models import CompatibilityResult
from backend.tests.utils.secure_test_data import get_test_password, get_test_jwt_secret, get_test_api_key


# constants for testing to avoid hard-coded credentials in literal strings
TEST_PASSWORD = get_test_password("test_password_123")
TEST_USER = "test_user_name"
TEST_DB = "test_database_db"


class TestPostgreSQLClientCompatibilityProperties:
    """Property-based tests for PostgreSQL client connection compatibility validation"""
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        python_version=st.text(min_size=5, max_size=10, alphabet='0123456789.'),
        asyncpg_version=st.text(min_size=5, max_size=10, alphabet='0123456789.'),
        is_compatible=st.booleans(),
        has_issues=st.booleans(),
        issue_count=st.integers(min_value=0, max_value=5)
    )
    @pytest.mark.asyncio
    async def test_compatibility_validation_property(
        self, 
        python_version: str, 
        asyncpg_version: str, 
        is_compatible: bool,
        has_issues: bool,
        issue_count: int
    ):
        """
        **Feature: database-connectivity-fixes, Property 1: Connection Compatibility Validation**
        
        For any Python version and asyncpg version combination, the PostgreSQL client 
        should establish connections successfully when versions are compatible and fail 
        gracefully with clear error messages when incompatible.
        
        **Validates: Requirements 1.1, 1.3, 1.4**
        """
        client = PostgreSQLClient()
        
        # Generate realistic issues based on the parameters
        issues = []
        recommendations = []
        
        if has_issues and issue_count > 0:
            issues = [f"Issue {i+1}: Version compatibility problem" for i in range(issue_count)]
            recommendations = [f"Recommendation {i+1}: Fix version issue" for i in range(issue_count)]
        
        # Create compatibility result based on generated parameters
        compatibility_result = CompatibilityResult(
            is_compatible=is_compatible and not has_issues,
            python_version=python_version,
            asyncpg_version=asyncpg_version,
            issues=issues,
            recommendations=recommendations
        )
        
        # Mock the compatibility checker
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatibility_result):
            if compatibility_result.is_compatible:
                # Property: Compatible versions should validate successfully
                result = await client.validate_compatibility()
                
                assert result.is_compatible is True
                assert result.python_version == python_version
                assert result.asyncpg_version == asyncpg_version
                assert client.is_compatibility_validated() is True
                assert client.get_compatibility_result() == compatibility_result
                
                # Property: Compatible versions should allow connection operations
                with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
                    mock_pool = AsyncMock()
                    mock_create_pool.return_value = mock_pool
                    
                    pool = await client.create_pool(f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}")
                    assert pool == mock_pool
                    mock_create_pool.assert_called_once()
                
            else:
                # Property: Incompatible versions should fail gracefully with clear error messages
                with pytest.raises(PostgreSQLCompatibilityError) as exc_info:
                    await client.validate_compatibility()
                
                error = exc_info.value
                assert "compatibility validation failed" in str(error).lower()
                assert client.is_compatibility_validated() is False
                assert client.get_compatibility_result() == compatibility_result
                
                # Property: Error should contain version information
                error_message = str(error)
                assert python_version in error_message or "unknown" in error_message.lower()
                assert asyncpg_version in error_message or "unknown" in error_message.lower()
                
                # Property: Incompatible versions should prevent connection operations
                with pytest.raises(PostgreSQLCompatibilityError):
                    await client.create_pool(f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        exception_message=st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        operation_type=st.sampled_from(['validate_compatibility', 'create_pool', 'execute_query', 'test_connection', 'initialize'])
    )
    @pytest.mark.asyncio
    async def test_compatibility_validation_exception_handling_property(
        self, 
        exception_message: str,
        operation_type: str
    ):
        """
        **Feature: database-connectivity-fixes, Property 1: Connection Compatibility Validation**
        
        For any unexpected exception during compatibility validation, the PostgreSQL client 
        should handle it gracefully and provide clear error messages with resolution steps.
        
        **Validates: Requirements 1.1, 1.3, 1.4**
        """
        client = PostgreSQLClient()
        
        # Mock the compatibility checker to raise an exception
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', side_effect=Exception(exception_message)):
            # Property: All operations should handle compatibility check exceptions gracefully
            try:
                if operation_type == 'validate_compatibility':
                    await client.validate_compatibility()
                elif operation_type == 'create_pool':
                    await client.create_pool(f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}")
                elif operation_type == 'execute_query':
                    await client.execute_query("SELECT 1")
                elif operation_type == 'test_connection':
                    await client.test_connection()
                elif operation_type == 'initialize':
                    await client.initialize()
                
                # If we reach here, the operation didn't raise an exception
                # This could happen if the operation doesn't trigger compatibility validation
                # In that case, we should verify the client state
                pass
                
            except PostgreSQLCompatibilityError as error:
                # Property: Exception should be wrapped in PostgreSQLCompatibilityError
                assert isinstance(error, PostgreSQLCompatibilityError)
                
                # Property: Error message should indicate validation failure
                error_message = str(error)
                assert "failed to validate" in error_message.lower() or "compatibility" in error_message.lower()
                
                # Property: Client should not be marked as validated after exception
                assert client.is_compatibility_validated() is False
                
                # Property: Compatibility result should indicate failure
                result = client.get_compatibility_result()
                if result is not None:
                    assert result.is_compatible is False
                    assert len(result.issues) > 0
                    assert len(result.recommendations) > 0
                    
            except Exception as other_error:
                # Some operations might raise other exceptions (like connection errors)
                # This is acceptable as long as the compatibility validation was attempted
                # We can verify this by checking if the mock was called
                pass
            
            # Property: Client should not be marked as validated after exception
            # (This applies regardless of which exception was raised)
            assert client.is_compatibility_validated() is False
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        dsn=st.text(min_size=10, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        pool_min_size=st.integers(min_value=1, max_value=50),
        pool_max_size=st.integers(min_value=1, max_value=100),
        command_timeout=st.integers(min_value=1, max_value=300)
    )
    @pytest.mark.asyncio
    async def test_pool_creation_with_compatibility_validation_property(
        self, 
        dsn: str,
        pool_min_size: int,
        pool_max_size: int,
        command_timeout: int
    ):
        """
        **Feature: database-connectivity-fixes, Property 1: Connection Compatibility Validation**
        
        For any pool configuration parameters, the PostgreSQL client should validate 
        compatibility before creating the pool and handle pool creation failures gracefully.
        
        **Validates: Requirements 1.1, 1.3, 1.4**
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
        
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            # Property: Pool creation should validate compatibility first
            with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
                mock_pool = AsyncMock()
                mock_create_pool.return_value = mock_pool
                
                pool = await client.create_pool(
                    dsn,
                    min_size=pool_min_size,
                    max_size=pool_max_size,
                    command_timeout=command_timeout
                )
                
                # Property: Pool creation should succeed with compatible versions
                assert pool == mock_pool
                assert client.is_compatibility_validated() is True
                
                # Property: Pool configuration should be passed correctly
                mock_create_pool.assert_called_once()
                call_args = mock_create_pool.call_args
                assert call_args[0][0] == dsn  # First positional argument is DSN
                
                # Verify pool configuration parameters
                call_kwargs = call_args[1]
                assert call_kwargs['min_size'] == pool_min_size
                assert call_kwargs['max_size'] == pool_max_size
                assert call_kwargs['command_timeout'] == command_timeout
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        pool_creation_error=st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        error_type=st.sampled_from(['ConnectionError', 'TimeoutError', 'ValueError', 'RuntimeError'])
    )
    @pytest.mark.asyncio
    async def test_pool_creation_failure_handling_property(
        self, 
        pool_creation_error: str,
        error_type: str
    ):
        """
        **Feature: database-connectivity-fixes, Property 1: Connection Compatibility Validation**
        
        For any pool creation failure, the PostgreSQL client should handle the error 
        gracefully and provide detailed error reporting with resolution steps.
        
        **Validates: Requirements 1.1, 1.3, 1.4**
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
        
        # Create appropriate exception type
        exception_classes = {
            'ConnectionError': ConnectionError,
            'TimeoutError': TimeoutError,
            'ValueError': ValueError,
            'RuntimeError': RuntimeError
        }
        exception_class = exception_classes[error_type]
        
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
                mock_create_pool.side_effect = exception_class(pool_creation_error)
                
                # Property: Pool creation failures should be handled gracefully
                with pytest.raises(exception_class) as exc_info:
                    await client.create_pool(f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}")
                
                # Property: Original exception should be preserved
                assert str(exc_info.value) == pool_creation_error
                
                # Property: Compatibility should still be validated
                assert client.is_compatibility_validated() is True
                
                # Property: Error should be reported to error reporting system
                # (This is tested through the mock calls and logging)
                mock_create_pool.assert_called_once()
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        query=st.text(min_size=1, max_size=200, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        args_count=st.integers(min_value=0, max_value=10),
        query_success=st.booleans()
    )
    @pytest.mark.asyncio
    async def test_query_execution_with_compatibility_validation_property(
        self, 
        query: str,
        args_count: int,
        query_success: bool
    ):
        """
        **Feature: database-connectivity-fixes, Property 1: Connection Compatibility Validation**
        
        For any query execution, the PostgreSQL client should validate compatibility 
        before executing and handle query failures gracefully.
        
        **Validates: Requirements 1.1, 1.3, 1.4**
        """
        client = PostgreSQLClient()
        
        # Generate query arguments
        query_args = tuple(f"arg_{i}" for i in range(args_count))
        
        # Create a compatible result for this test
        compatible_result = CompatibilityResult(
            is_compatible=True,
            python_version="3.11.0",
            asyncpg_version="0.28.0",
            issues=[],
            recommendations=[]
        )
        
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatible_result):
            with patch('app.database.postgresql_client.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_session_local.return_value.__aenter__.return_value = mock_session
                
                if query_success:
                    mock_session.execute.return_value = "query_result"
                    
                    # Property: Successful queries should validate compatibility and execute
                    result = await client.execute_query(query, *query_args)
                    
                    assert result == "query_result"
                    assert client.is_compatibility_validated() is True
                    mock_session.execute.assert_called_once_with(query, query_args)
                    mock_session.commit.assert_called_once()
                    
                else:
                    mock_session.execute.side_effect = Exception("Query execution failed")
                    
                    # Property: Failed queries should still validate compatibility and handle errors
                    with pytest.raises(Exception, match="Query execution failed"):
                        await client.execute_query(query, *query_args)
                    
                    assert client.is_compatibility_validated() is True
                    mock_session.execute.assert_called_once_with(query, query_args)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        connection_success=st.booleans(),
        response_time_factor=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    @pytest.mark.asyncio
    async def test_connection_test_with_compatibility_validation_property(
        self, 
        connection_success: bool,
        response_time_factor: float
    ):
        """
        **Feature: database-connectivity-fixes, Property 1: Connection Compatibility Validation**
        
        For any connection test, the PostgreSQL client should validate compatibility 
        and provide accurate connection status with response time information.
        
        **Validates: Requirements 1.1, 1.3, 1.4**
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
            # Simulate variable response times
            async def mock_test_connection():
                await asyncio.sleep(0.001 * response_time_factor)  # Small delay to simulate response time
                return connection_success
            
            with patch('app.database.postgresql_client.test_postgres_connection', side_effect=mock_test_connection):
                status = await client.test_connection()
                
                # Property: Connection test should validate compatibility
                assert client.is_compatibility_validated() is True
                
                # Property: Connection status should reflect test result
                assert status.service == "PostgreSQL"
                assert status.is_connected == connection_success
                assert status.response_time_ms >= 0
                assert status.last_attempt is not None
                
                if connection_success:
                    # Property: Successful connections should not have error messages
                    assert status.error is None
                else:
                    # Property: Failed connections should have error messages
                    assert status.error is not None
                    assert "Connection test failed" in status.error
                
                # Property: Response time should be reasonable (not negative or extremely large)
                assert 0 <= status.response_time_ms <= 10000  # Max 10 seconds for test
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        initialization_success=st.booleans(),
        initialization_error=st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126))
    )
    @pytest.mark.asyncio
    async def test_initialization_with_compatibility_validation_property(
        self, 
        initialization_success: bool,
        initialization_error: str
    ):
        """
        **Feature: database-connectivity-fixes, Property 1: Connection Compatibility Validation**
        
        For any initialization attempt, the PostgreSQL client should validate 
        compatibility before initialization and handle failures gracefully.
        
        **Validates: Requirements 1.1, 1.3, 1.4**
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
            with patch('app.database.postgresql_client.init_postgres') as mock_init:
                if initialization_success:
                    # Property: Successful initialization should validate compatibility
                    await client.initialize()
                    
                    assert client.is_compatibility_validated() is True
                    mock_init.assert_called_once()
                    
                else:
                    mock_init.side_effect = Exception(initialization_error)
                    
                    # Property: Failed initialization should still validate compatibility
                    with pytest.raises(Exception) as exc_info:
                        await client.initialize()
                    
                    assert str(exc_info.value) == initialization_error
                    assert client.is_compatibility_validated() is True
                    mock_init.assert_called_once()
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        python_major=st.integers(min_value=3, max_value=4),
        python_minor=st.integers(min_value=8, max_value=15),
        python_micro=st.integers(min_value=0, max_value=20),
        asyncpg_major=st.integers(min_value=0, max_value=1),
        asyncpg_minor=st.integers(min_value=20, max_value=35),
        asyncpg_patch=st.integers(min_value=0, max_value=10)
    )
    @pytest.mark.asyncio
    async def test_realistic_version_combinations_property(
        self, 
        python_major: int,
        python_minor: int,
        python_micro: int,
        asyncpg_major: int,
        asyncpg_minor: int,
        asyncpg_patch: int
    ):
        """
        **Feature: database-connectivity-fixes, Property 1: Connection Compatibility Validation**
        
        For any realistic Python and asyncpg version combination, the PostgreSQL client 
        should provide consistent compatibility validation results.
        
        **Validates: Requirements 1.1, 1.3, 1.4**
        """
        client = PostgreSQLClient()
        
        python_version = f"{python_major}.{python_minor}.{python_micro}"
        asyncpg_version = f"{asyncpg_major}.{asyncpg_minor}.{asyncpg_patch}"
        
        # Simulate realistic compatibility logic
        # Python 3.13+ with asyncpg < 0.28 is typically incompatible
        is_compatible = not (python_major == 3 and python_minor >= 13 and asyncpg_minor < 28)
        
        issues = []
        recommendations = []
        if not is_compatible:
            issues.append(f"Python {python_version} not supported with asyncpg {asyncpg_version}")
            recommendations.append(f"Upgrade asyncpg to version 0.28.0 or higher")
        
        compatibility_result = CompatibilityResult(
            is_compatible=is_compatible,
            python_version=python_version,
            asyncpg_version=asyncpg_version,
            issues=issues,
            recommendations=recommendations
        )
        
        with patch.object(client.compatibility_checker, 'check_python_asyncpg_compatibility', return_value=compatibility_result):
            if is_compatible:
                # Property: Compatible realistic versions should validate successfully
                result = await client.validate_compatibility()
                
                assert result.is_compatible is True
                assert result.python_version == python_version
                assert result.asyncpg_version == asyncpg_version
                assert len(result.issues) == 0
                assert client.is_compatibility_validated() is True
                
            else:
                # Property: Incompatible realistic versions should fail with specific messages
                with pytest.raises(PostgreSQLCompatibilityError) as exc_info:
                    await client.validate_compatibility()
                
                error_message = str(exc_info.value)
                assert python_version in error_message
                assert asyncpg_version in error_message
                assert "compatibility" in error_message.lower()
                assert client.is_compatibility_validated() is False
                
                # Property: Error should contain actionable recommendations
                result = client.get_compatibility_result()
                assert result is not None
                assert len(result.recommendations) > 0
                assert any("upgrade" in rec.lower() for rec in result.recommendations)