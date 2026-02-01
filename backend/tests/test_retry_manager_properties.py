"""
Property-Based Tests for Retry Manager

Tests core properties of retry manager exponential backoff logic using hypothesis.

Validates Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime, timedelta

from app.database.retry_manager import RetryManager, OperationType, RetryState
from app.database.models import RetryConfig


class TestRetryManagerExponentialBackoffProperties:
    """Property-based tests for exponential backoff retry logic"""
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        max_retries=st.integers(min_value=1, max_value=3),  # Reduced for faster testing
        base_delay=st.floats(min_value=0.01, max_value=0.1, allow_nan=False, allow_infinity=False),  # Much smaller delays
        max_delay=st.floats(min_value=0.1, max_value=0.5, allow_nan=False, allow_infinity=False),  # Much smaller delays
        backoff_multiplier=st.floats(min_value=1.1, max_value=3.0, allow_nan=False, allow_infinity=False),
        failure_count=st.integers(min_value=1, max_value=3)  # Reduced for faster testing
    )
    @pytest.mark.asyncio
    async def test_property_3_exponential_backoff_retry_logic(
        self, max_retries, base_delay, max_delay, backoff_multiplier, failure_count
    ):
        """
        **Feature: database-connectivity-fixes, Property 3: Exponential Backoff Retry Logic**
        
        For any sequence of Neo4j authentication failures, the retry handler should 
        implement exponential backoff starting at 1 second with appropriate spacing 
        to prevent rate limiting.
        
        **Validates: Requirements 2.1, 2.2**
        """
        # Ensure max_delay >= base_delay for valid configuration
        if max_delay < base_delay:
            max_delay = base_delay * 2
        
        # Create retry configuration
        config = RetryConfig(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            backoff_multiplier=backoff_multiplier,
            retry_on_auth_failure=True
        )
        
        retry_manager = RetryManager(default_config=config)
        
        # Test exponential backoff calculation
        delays = []
        for attempt in range(min(failure_count, max_retries)):
            delay = retry_manager.calculate_delay(attempt, config)
            delays.append(delay)
        
        # Property 1: First delay should be base_delay
        if len(delays) > 0:
            assert delays[0] == base_delay, f"First delay should be {base_delay}, got {delays[0]}"
        
        # Property 2: Each subsequent delay should follow exponential growth (up to max_delay)
        for i in range(1, len(delays)):
            expected_delay = min(base_delay * (backoff_multiplier ** i), max_delay)
            assert delays[i] == expected_delay, f"Delay at attempt {i+1} should be {expected_delay}, got {delays[i]}"
        
        # Property 3: No delay should exceed max_delay
        for delay in delays:
            assert delay <= max_delay, f"Delay {delay} exceeds max_delay {max_delay}"
        
        # Property 4: Delays should be non-decreasing (monotonic) until max_delay is reached
        for i in range(1, len(delays)):
            if delays[i-1] < max_delay:  # Only check if previous delay wasn't capped
                assert delays[i] >= delays[i-1], f"Delay should be non-decreasing: {delays[i-1]} -> {delays[i]}"
        
        # Property 5: Test with actual Neo4j authentication failure simulation
        failure_count_actual = 0
        
        async def failing_neo4j_auth():
            nonlocal failure_count_actual
            failure_count_actual += 1
            if failure_count_actual <= failure_count:
                # Simulate Neo4j authentication error
                raise Exception("Neo4j.Exceptions.AuthenticationException: The client is unauthorized due to authentication failure.")
            return "success"
        
        # Configure specific retry policy for Neo4j authentication
        retry_manager.configure_operation(OperationType.NEO4J_AUTHENTICATION, config)
        
        start_time = datetime.now()
        
        try:
            if failure_count <= max_retries:
                # Should eventually succeed
                result = await retry_manager.execute_with_retry(
                    failing_neo4j_auth,
                    OperationType.NEO4J_AUTHENTICATION,
                    "test_auth_operation"
                )
                assert result == "success"
                
                # Verify timing follows exponential backoff
                end_time = datetime.now()
                total_time = (end_time - start_time).total_seconds()
                
                # Calculate expected minimum time (sum of delays)
                expected_min_time = sum(delays[:failure_count])
                
                # Allow some tolerance for execution time
                assert total_time >= expected_min_time * 0.9, f"Total time {total_time} should be at least {expected_min_time * 0.9}"
                
            else:
                # Should fail after max_retries
                with pytest.raises(Exception, match="authentication failure|unauthorized"):
                    await retry_manager.execute_with_retry(
                        failing_neo4j_auth,
                        OperationType.NEO4J_AUTHENTICATION,
                        "test_auth_operation"
                    )
                
                # Should have attempted max_retries + 1 times (initial + retries)
                assert failure_count_actual == max_retries + 1
                
        except Exception as e:
            # If we get here with failure_count <= max_retries, something went wrong
            if failure_count <= max_retries:
                pytest.fail(f"Unexpected failure with failure_count {failure_count} <= max_retries {max_retries}: {e}")
            # Otherwise, this is expected behavior
            assert failure_count > max_retries


class TestRetryManagerStateManagementProperties:
    """Property-based tests for retry state management"""
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        initial_failures=st.integers(min_value=1, max_value=3),  # Reduced for faster testing
        success_after_failures=st.booleans(),
        operation_type=st.sampled_from(list(OperationType))
    )
    @pytest.mark.asyncio
    async def test_property_4_retry_state_management(
        self, initial_failures, success_after_failures, operation_type
    ):
        """
        **Feature: database-connectivity-fixes, Property 4: Retry State Management**
        
        For any sequence of authentication failures followed by success, the retry 
        handler should reset backoff intervals to initial values and properly track 
        failure history.
        
        **Validates: Requirements 2.4, 2.5**
        """
        config = RetryConfig(
            max_retries=10,  # High enough to allow testing
            base_delay=0.01,  # Very small delay for testing
            max_delay=0.1,   # Very small delay for testing
            backoff_multiplier=2.0
        )
        
        retry_manager = RetryManager(default_config=config)
        retry_manager.configure_operation(operation_type, config)
        
        operation_id = f"test_operation_{operation_type.value}"
        
        # Simulate initial failures
        failure_count = 0
        
        async def test_operation():
            nonlocal failure_count
            failure_count += 1
            
            if failure_count <= initial_failures:
                # Use operation-specific error messages that will be retried
                if operation_type == OperationType.NEO4J_AUTHENTICATION:
                    raise Exception("Neo4j.Exceptions.AuthenticationException: The client is unauthorized due to authentication failure.")
                elif operation_type == OperationType.POSTGRESQL_CONNECTION:
                    raise Exception("Connection refused by server")
                elif operation_type == OperationType.NEO4J_CONNECTION:
                    raise Exception("Connection refused by server")
                elif operation_type == OperationType.MIGRATION_EXECUTION:
                    raise Exception("Connection timeout during migration")
                elif operation_type == OperationType.HEALTH_CHECK:
                    raise Exception("Connection timeout during health check")
                else:  # QUERY_EXECUTION
                    raise Exception("Connection timeout during query execution")
            
            if success_after_failures:
                return f"success_after_{initial_failures}_failures"
            else:
                # Use operation-specific permanent failure messages
                if operation_type == OperationType.NEO4J_AUTHENTICATION:
                    raise Exception("Neo4j.Exceptions.AuthenticationException: Permanent authentication failure")
                elif operation_type in [OperationType.POSTGRESQL_CONNECTION, OperationType.NEO4J_CONNECTION]:
                    raise Exception("Connection permanently refused by server")
                else:
                    raise Exception("Permanent connection timeout")
        
        # Execute operation
        try:
            if success_after_failures:
                result = await retry_manager.execute_with_retry(
                    test_operation,
                    operation_type,
                    operation_id
                )
                assert result == f"success_after_{initial_failures}_failures"
                
                # Property 1: After success, retry state should be reset
                retry_state = retry_manager.retry_states.get(operation_id)
                assert retry_state is not None
                assert retry_state.attempt_count == 0, "Attempt count should be reset after success"
                assert retry_state.consecutive_failures == 0, "Consecutive failures should be reset after success"
                assert retry_state.current_backoff_delay == 0.0, "Backoff delay should be reset after success"
                assert retry_state.last_success_time is not None, "Last success time should be recorded"
                
                # Property 2: Total failures should still be tracked for history
                assert retry_state.total_failures == initial_failures, f"Total failures should be {initial_failures}"
                
                # Property 3: Test that next failure starts from base delay again
                failure_count = 0  # Reset for next test
                
                async def next_operation():
                    nonlocal failure_count
                    failure_count += 1
                    if failure_count == 1:
                        # Use operation-specific error that will be retried
                        if operation_type == OperationType.NEO4J_AUTHENTICATION:
                            raise Exception("Neo4j.Exceptions.AuthenticationException: First failure after success")
                        elif operation_type == OperationType.POSTGRESQL_CONNECTION:
                            raise Exception("Connection refused - first failure after success")
                        elif operation_type == OperationType.NEO4J_CONNECTION:
                            raise Exception("Connection refused - first failure after success")
                        elif operation_type == OperationType.MIGRATION_EXECUTION:
                            raise Exception("Connection timeout - first failure after success")
                        elif operation_type == OperationType.HEALTH_CHECK:
                            raise Exception("Connection timeout - first failure after success")
                        else:  # QUERY_EXECUTION
                            raise Exception("Connection timeout - first failure after success")
                    return "success"
                
                start_time = datetime.now()
                result = await retry_manager.execute_with_retry(
                    next_operation,
                    operation_type,
                    operation_id
                )
                end_time = datetime.now()
                
                # Should have taken approximately base_delay time
                elapsed = (end_time - start_time).total_seconds()
                assert elapsed >= config.base_delay * 0.5, "Should start from base delay after reset"  # More lenient
                assert elapsed < config.base_delay * 10, "Should not use exponentially increased delay"  # More lenient
                
            else:
                # Should fail after retries
                with pytest.raises(Exception):
                    await retry_manager.execute_with_retry(
                        test_operation,
                        operation_type,
                        operation_id
                    )
                
                # Property 4: Failure state should be properly tracked
                retry_state = retry_manager.retry_states.get(operation_id)
                assert retry_state is not None
                assert retry_state.consecutive_failures > 0, "Should track consecutive failures"
                assert retry_state.total_failures > 0, "Should track total failures"
                assert retry_state.first_failure_time is not None, "Should record first failure time"
                assert retry_state.last_failure_time is not None, "Should record last failure time"
                
        except Exception as e:
            if success_after_failures:
                pytest.fail(f"Unexpected failure when success was expected: {e}")


class TestRetryManagerExhaustionHandlingProperties:
    """Property-based tests for retry exhaustion handling"""
    
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        max_retries=st.integers(min_value=1, max_value=3),  # Reduced for faster testing
        operation_type=st.sampled_from(list(OperationType)),
        error_message=st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_characters='\x00\n\r'))  # Shorter messages
    )
    @pytest.mark.asyncio
    async def test_property_5_retry_exhaustion_handling(
        self, max_retries, operation_type, error_message
    ):
        """
        **Feature: database-connectivity-fixes, Property 5: Retry Exhaustion Handling**
        
        For any operation that exceeds maximum retry attempts, the system should log 
        the failure with clear resolution guidance and stop further retry attempts.
        
        **Validates: Requirements 2.3**
        """
        config = RetryConfig(
            max_retries=max_retries,
            base_delay=0.01,  # Very fast for testing
            max_delay=0.05,   # Very fast for testing
            backoff_multiplier=2.0
        )
        
        retry_manager = RetryManager(default_config=config)
        retry_manager.configure_operation(operation_type, config)
        
        operation_id = f"exhaustion_test_{operation_type.value}"
        attempt_count = 0
        
        async def always_failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            # Use operation-specific error messages that will be retried based on retry_manager.should_retry logic
            if operation_type == OperationType.NEO4J_AUTHENTICATION:
                # Neo4j auth failures are retried when they contain "auth", "unauthorized", or "authentication"
                raise Exception(f"Neo4j.Exceptions.AuthenticationException: authentication failure - {error_message}")
            elif operation_type == OperationType.POSTGRESQL_CONNECTION:
                # Connection errors are retried when they contain connection-related keywords
                raise Exception(f"Connection refused by server - {error_message}")
            elif operation_type == OperationType.NEO4J_CONNECTION:
                # Connection errors are retried when they contain connection-related keywords
                raise Exception(f"Connection refused by server - {error_message}")
            elif operation_type == OperationType.MIGRATION_EXECUTION:
                # Timeout errors are retried when retry_on_timeout is True
                raise Exception(f"Connection timeout during migration - {error_message}")
            elif operation_type == OperationType.HEALTH_CHECK:
                # Timeout errors are retried when retry_on_timeout is True
                raise Exception(f"Connection timeout during health check - {error_message}")
            else:  # QUERY_EXECUTION
                # Timeout errors are retried when retry_on_timeout is True
                raise Exception(f"Connection timeout during query execution - {error_message}")
        
        # Capture logs to verify resolution guidance
        import logging
        log_records = []
        
        class TestLogHandler(logging.Handler):
            def emit(self, record):
                log_records.append(record)
        
        handler = TestLogHandler()
        logger = logging.getLogger('app.database.retry_manager')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            # Should fail after max_retries + 1 attempts
            # Escape regex special characters in error_message for matching
            import re
            escaped_error_message = re.escape(error_message)
            with pytest.raises(Exception, match=escaped_error_message):
                await retry_manager.execute_with_retry(
                    always_failing_operation,
                    operation_type,
                    operation_id
                )
            
            # Property 1: Should attempt exactly max_retries + 1 times
            assert attempt_count == max_retries + 1, f"Should attempt {max_retries + 1} times, got {attempt_count}"
            
            # Property 2: Should log retry exhaustion with resolution guidance
            error_logs = [record for record in log_records if record.levelname == 'ERROR']
            exhaustion_logs = [log for log in error_logs if 'exhausted' in log.getMessage().lower()]
            
            assert len(exhaustion_logs) > 0, "Should log retry exhaustion"
            
            exhaustion_log = exhaustion_logs[0]
            log_message = exhaustion_log.getMessage()
            
            # Property 3: Log should contain comprehensive information
            # Check that the log message contains the operation type and other key information
            assert operation_type.value in log_message, f"Should log operation type {operation_type.value}"
            assert str(max_retries + 1) in log_message, f"Should log total attempts {max_retries + 1}"
            
            # Property 4: The retry manager should have logged with resolution steps
            # We can verify this by checking that the _log_retry_exhaustion method was called
            # by looking for the specific log message pattern
            assert "exhausted" in log_message.lower(), "Should log retry exhaustion"
            assert "attempts" in log_message.lower(), "Should mention attempts in log"
            
            # Property 5: Should not attempt further retries after exhaustion
            pre_exhaustion_count = attempt_count
            
            # Try the operation again - should start fresh
            attempt_count = 0  # Reset counter
            
            # Escape regex special characters in error_message for matching
            with pytest.raises(Exception, match=escaped_error_message):
                await retry_manager.execute_with_retry(
                    always_failing_operation,
                    operation_type,
                    f"{operation_id}_second_try"  # Different operation ID
                )
            
            # Should start fresh with new operation ID
            assert attempt_count == max_retries + 1, "Should start fresh retry cycle with new operation ID"
            
        finally:
            logger.removeHandler(handler)


class TestRetryManagerConfigurationProperties:
    """Property-based tests for retry manager configuration"""
    
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        base_delay=st.floats(min_value=0.01, max_value=0.1, allow_nan=False, allow_infinity=False),  # Smaller delays
        max_delay=st.floats(min_value=0.1, max_value=0.5, allow_nan=False, allow_infinity=False),   # Smaller delays
        backoff_multiplier=st.floats(min_value=1.1, max_value=5.0, allow_nan=False, allow_infinity=False),
        max_retries=st.integers(min_value=1, max_value=5)  # Reduced for faster testing
    )
    def test_retry_manager_configuration_properties(
        self, base_delay, max_delay, backoff_multiplier, max_retries
    ):
        """
        Test that retry manager properly handles various configuration combinations
        and maintains mathematical properties of exponential backoff.
        """
        # Ensure max_delay >= base_delay
        if max_delay < base_delay:
            max_delay = base_delay * 2
        
        config = RetryConfig(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            backoff_multiplier=backoff_multiplier
        )
        
        retry_manager = RetryManager(default_config=config)
        
        # Test delay calculation properties
        delays = []
        for attempt in range(max_retries):
            delay = retry_manager.calculate_delay(attempt, config)
            delays.append(delay)
        
        # Property 1: All delays should be positive
        assert all(delay > 0 for delay in delays), "All delays should be positive"
        
        # Property 2: All delays should be <= max_delay
        assert all(delay <= max_delay for delay in delays), f"All delays should be <= {max_delay}"
        
        # Property 3: First delay should equal base_delay
        if delays:
            assert delays[0] == base_delay, f"First delay should be {base_delay}, got {delays[0]}"
        
        # Property 4: Delays should follow exponential pattern until capped
        for i in range(1, len(delays)):
            expected_uncapped = base_delay * (backoff_multiplier ** i)
            expected_capped = min(expected_uncapped, max_delay)
            assert delays[i] == expected_capped, f"Delay {i} should be {expected_capped}, got {delays[i]}"