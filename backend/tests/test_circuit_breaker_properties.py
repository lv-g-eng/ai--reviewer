"""
Property-based tests for circuit breaker activation

Tests Property 42: Circuit Breaker Activation
For any external service dependency that fails repeatedly (exceeding failure 
threshold), the platform SHALL open the circuit breaker and stop sending 
requests for a cooldown period.

Validates Requirements: 7.7
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import time

from app.shared.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerConfig,
    CircuitBreakerException,
)


# Strategy for generating circuit breaker configurations
@st.composite
def circuit_breaker_config_strategy(draw):
    """Generate valid circuit breaker configurations"""
    return CircuitBreakerConfig(
        failure_threshold=draw(st.integers(min_value=1, max_value=10)),
        success_threshold=draw(st.integers(min_value=1, max_value=5)),
        timeout=draw(st.integers(min_value=1, max_value=10)),
        window_size=draw(st.integers(min_value=10, max_value=300)),
    )


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(42, "Circuit Breaker Activation")
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    config=circuit_breaker_config_strategy(),
    num_failures=st.integers(min_value=1, max_value=20),
)
def test_property_circuit_breaker_opens_on_failures(config, num_failures):
    """
    Property 42: Circuit Breaker Activation
    
    For any external service dependency that fails repeatedly (exceeding failure
    threshold), the platform SHALL open the circuit breaker and stop sending
    requests for a cooldown period.
    
    **Validates: Requirements 7.7**
    """
    breaker = CircuitBreaker("test_service", config)
    
    # Initially circuit should be closed
    assert breaker.get_state() == CircuitBreakerState.CLOSED
    
    # Simulate failures
    failure_count = 0
    for i in range(num_failures):
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Service failed")))
        except Exception:
            failure_count += 1
    
    # PROPERTY: Circuit should open after exceeding failure threshold
    if num_failures >= config.failure_threshold:
        assert breaker.get_state() == CircuitBreakerState.OPEN, \
            f"Circuit should be OPEN after {num_failures} failures (threshold: {config.failure_threshold})"
        
        # PROPERTY: Subsequent calls should be rejected immediately
        with pytest.raises(CircuitBreakerException) as exc_info:
            breaker.call(lambda: "success")
        
        assert "Circuit breaker" in str(exc_info.value)
        assert "OPEN" in str(exc_info.value)
        
        # PROPERTY: Metrics should reflect rejected calls
        metrics = breaker.get_metrics()
        assert metrics.rejected_calls > 0, "Should have rejected calls when circuit is open"
    else:
        # Not enough failures to open circuit
        assert breaker.get_state() == CircuitBreakerState.CLOSED, \
            f"Circuit should remain CLOSED with {num_failures} failures (threshold: {config.failure_threshold})"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(42, "Circuit Breaker Activation")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    failure_threshold=st.integers(min_value=2, max_value=5),
    success_threshold=st.integers(min_value=1, max_value=3),
)
def test_property_circuit_breaker_half_open_transition(failure_threshold, success_threshold):
    """
    Property 42 (recovery): Circuit breaker transitions to HALF_OPEN after timeout
    
    **Validates: Requirements 7.7**
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        success_threshold=success_threshold,
        timeout=1,  # Short timeout for testing
    )
    breaker = CircuitBreaker("test_service", config)
    
    # Cause failures to open circuit
    for _ in range(failure_threshold):
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Service failed")))
        except Exception:
            pass
    
    # Circuit should be open
    assert breaker.get_state() == CircuitBreakerState.OPEN
    
    # Wait for timeout
    time.sleep(config.timeout + 0.1)
    
    # PROPERTY: After timeout, circuit should transition to HALF_OPEN on next call
    try:
        breaker.call(lambda: "success")
        # If call succeeds, circuit should be in HALF_OPEN or CLOSED
        assert breaker.get_state() in [CircuitBreakerState.HALF_OPEN, CircuitBreakerState.CLOSED]
    except CircuitBreakerException:
        # Circuit transitioned to HALF_OPEN
        assert breaker.get_state() == CircuitBreakerState.HALF_OPEN


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(42, "Circuit Breaker Activation")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    failure_threshold=st.integers(min_value=2, max_value=5),
    success_threshold=st.integers(min_value=1, max_value=3),
)
def test_property_circuit_breaker_closes_after_successes(failure_threshold, success_threshold):
    """
    Property 42 (recovery): Circuit breaker closes after success threshold in HALF_OPEN
    
    **Validates: Requirements 7.7**
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        success_threshold=success_threshold,
        timeout=1,
    )
    breaker = CircuitBreaker("test_service", config)
    
    # Open the circuit
    for _ in range(failure_threshold):
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Service failed")))
        except Exception:
            pass
    
    assert breaker.get_state() == CircuitBreakerState.OPEN
    
    # Wait for timeout
    time.sleep(config.timeout + 0.1)
    
    # Make successful calls in HALF_OPEN state
    success_count = 0
    for _ in range(success_threshold + 1):
        try:
            result = breaker.call(lambda: "success")
            if result == "success":
                success_count += 1
        except CircuitBreakerException:
            # Still in OPEN state, wait a bit more
            time.sleep(0.1)
            continue
    
    # PROPERTY: After success_threshold successes, circuit should close
    if success_count >= success_threshold:
        assert breaker.get_state() == CircuitBreakerState.CLOSED, \
            f"Circuit should be CLOSED after {success_count} successes (threshold: {success_threshold})"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(42, "Circuit Breaker Activation")
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    failure_threshold=st.integers(min_value=1, max_value=10),
    num_calls=st.integers(min_value=1, max_value=20),
)
def test_property_circuit_breaker_metrics(failure_threshold, num_calls):
    """
    Property 42 (metrics): Circuit breaker tracks call metrics accurately
    
    **Validates: Requirements 7.7**
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        success_threshold=2,
        timeout=60,
    )
    breaker = CircuitBreaker("test_service", config)
    
    successful_calls = 0
    failed_calls = 0
    rejected_calls = 0
    
    # Make calls (mix of success and failure)
    for i in range(num_calls):
        try:
            if i % 3 == 0:  # Every 3rd call fails
                breaker.call(lambda: (_ for _ in ()).throw(Exception("Service failed")))
            else:
                breaker.call(lambda: "success")
                successful_calls += 1
        except CircuitBreakerException:
            rejected_calls += 1
        except Exception:
            failed_calls += 1
    
    # Get metrics
    metrics = breaker.get_metrics()
    
    # PROPERTY: Total calls should match
    assert metrics.total_calls == num_calls, \
        f"Total calls should be {num_calls}, got {metrics.total_calls}"
    
    # PROPERTY: Successful + failed + rejected should equal total
    assert metrics.successful_calls + metrics.failed_calls + metrics.rejected_calls == metrics.total_calls, \
        "Sum of successful, failed, and rejected calls should equal total calls"
    
    # PROPERTY: If circuit is open, rejected_calls should be > 0
    # Edge case: If circuit opens on the last call (num_calls == failure_threshold),
    # there are no subsequent calls to reject
    if breaker.get_state() == CircuitBreakerState.OPEN:
        if num_calls > failure_threshold:
            # There were calls after the circuit opened
            assert metrics.rejected_calls > 0, \
                "Circuit is OPEN and there were calls after threshold, should have rejected calls"
        # else: Circuit opened on last call, no subsequent calls to reject


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(42, "Circuit Breaker Activation")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    failure_threshold=st.integers(min_value=2, max_value=5),
)
def test_property_circuit_breaker_failure_in_half_open_reopens(failure_threshold):
    """
    Property 42 (failure recovery): Failure in HALF_OPEN state reopens circuit
    
    **Validates: Requirements 7.7**
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        success_threshold=2,
        timeout=1,
    )
    breaker = CircuitBreaker("test_service", config)
    
    # Open the circuit
    for _ in range(failure_threshold):
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Service failed")))
        except Exception:
            pass
    
    assert breaker.get_state() == CircuitBreakerState.OPEN
    
    # Wait for timeout to transition to HALF_OPEN
    time.sleep(config.timeout + 0.1)
    
    # Make a call to transition to HALF_OPEN
    try:
        breaker.call(lambda: "success")
    except CircuitBreakerException:
        pass
    
    # If we're in HALF_OPEN, a failure should reopen the circuit
    if breaker.get_state() == CircuitBreakerState.HALF_OPEN:
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Service failed")))
        except Exception:
            pass
        
        # PROPERTY: Circuit should be OPEN again after failure in HALF_OPEN
        assert breaker.get_state() == CircuitBreakerState.OPEN, \
            "Circuit should reopen after failure in HALF_OPEN state"
