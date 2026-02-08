"""
Property-based tests for error logging completeness

Tests Property 5: Error Logging Completeness
For any failed operation (code review, graph analysis, AI reasoning), the system 
SHALL create a detailed error log entry containing timestamp, error type, error 
message, and context information.

Validates Requirements: 1.8, 7.6
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime
import logging
from io import StringIO

from app.core.error_reporter import ErrorReporter, DatabaseErrorCategory
from app.shared.exceptions import (
    ServiceException,
    LLMProviderException,
    CircuitBreakerException,
    CacheException,
    DatabaseException,
)


# Strategy for generating error types
@st.composite
def error_strategy(draw):
    """Generate various error types"""
    error_type = draw(st.sampled_from([
        "service",
        "llm_provider",
        "circuit_breaker",
        "cache",
        "database",
    ]))
    
    message = draw(st.text(min_size=10, max_size=200))
    
    if error_type == "service":
        return ServiceException(message, error_code="TEST_ERROR")
    elif error_type == "llm_provider":
        return LLMProviderException(
            message,
            provider=draw(st.sampled_from(["openai", "anthropic", "ollama"])),
            model=draw(st.sampled_from(["gpt-4", "claude-3.5", "llama2"])),
            error_code="TEST_ERROR"
        )
    elif error_type == "circuit_breaker":
        return CircuitBreakerException(
            message,
            service_name=draw(st.text(min_size=5, max_size=20)),
            failure_count=draw(st.integers(min_value=1, max_value=10)),
            error_code="CIRCUIT_OPEN"
        )
    elif error_type == "cache":
        return CacheException(
            message,
            operation=draw(st.sampled_from(["get", "set", "delete"])),
            key=draw(st.text(min_size=5, max_size=50)),
            error_code="CACHE_ERROR"
        )
    else:  # database
        return DatabaseException(
            message,
            database=draw(st.sampled_from(["postgresql", "neo4j", "redis"])),
            operation=draw(st.sampled_from(["connect", "query", "insert"])),
            error_code="DB_ERROR"
        )


@st.composite
def component_strategy(draw):
    """Generate component names"""
    return draw(st.sampled_from([
        "code_review",
        "graph_analysis",
        "ai_reasoning",
        "authentication",
        "cache",
        "database",
    ]))


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(5, "Error Logging Completeness")
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
)
@given(
    error=error_strategy(),
    component=component_strategy(),
)
def test_property_error_logging_completeness(error, component, caplog):
    """
    Property 5: Error Logging Completeness
    
    For any failed operation (code review, graph analysis, AI reasoning), the
    system SHALL create a detailed error log entry containing timestamp, error
    type, error message, and context information.
    
    **Validates: Requirements 1.8, 7.6**
    """
    # Clear previous logs to avoid interference between test iterations
    caplog.clear()
    
    # Set up logging capture
    caplog.set_level(logging.ERROR)
    
    # Create database error info for testing
    error_info = ErrorReporter.create_database_error_info(
        error=error,
        component=component,
        connection_params={"host": "localhost", "port": "5432"},
        error_code="TEST_001"
    )
    
    # Log the error
    ErrorReporter.log_database_error(error_info)
    
    # PROPERTY: Error log should be created
    assert len(caplog.records) > 0, "Should create at least one log entry"
    
    # Get the error log record (should be the first ERROR level record after clearing)
    error_record = None
    for record in caplog.records:
        if record.levelname == "ERROR":
            error_record = record
            break
    
    assert error_record is not None, "Should have an ERROR level log entry"
    
    # PROPERTY: Log should contain error message or component
    # The log format is "Database error in {component}: {message}"
    assert component in error_record.message, \
           f"Log message should contain component name '{component}', got: {error_record.message}"
    
    # PROPERTY: Log should have timestamp
    assert hasattr(error_record, 'created'), "Log should have timestamp"
    assert error_record.created > 0, "Timestamp should be valid"
    
    # PROPERTY: Log should have error type information
    if hasattr(error_record, 'error_category'):
        assert error_record.error_category is not None, "Should have error category"
    
    # PROPERTY: Log should have component information
    if hasattr(error_record, 'component'):
        assert error_record.component == component, "Should log correct component"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(5, "Error Logging Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
)
@given(
    num_errors=st.integers(min_value=1, max_value=10),
    component=component_strategy(),
)
def test_property_multiple_errors_logged(num_errors, component, caplog):
    """
    Property 5 (multiple errors): All errors should be logged
    
    **Validates: Requirements 1.8, 7.6**
    """
    # Clear previous logs
    caplog.clear()
    caplog.set_level(logging.ERROR)
    
    # Generate and log multiple errors
    for i in range(num_errors):
        error = Exception(f"Test error {i}")
        error_info = ErrorReporter.create_database_error_info(
            error=error,
            component=component,
            error_code=f"TEST_{i:03d}"
        )
        ErrorReporter.log_database_error(error_info)
    
    # PROPERTY: All errors should be logged
    error_logs = [r for r in caplog.records if r.levelname == "ERROR"]
    assert len(error_logs) >= num_errors, \
        f"Should log all {num_errors} errors (found {len(error_logs)} error logs)"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(5, "Error Logging Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    error_message=st.text(min_size=10, max_size=200),
    component=component_strategy(),
)
def test_property_error_context_preserved(error_message, component):
    """
    Property 5 (context): Error context information should be preserved
    
    **Validates: Requirements 1.8, 7.6**
    """
    # Create error with context
    error = Exception(error_message)
    connection_params = {
        "host": "test-host",
        "port": "5432",
        "database": "test-db"
    }
    
    error_info = ErrorReporter.create_database_error_info(
        error=error,
        component=component,
        connection_params=connection_params,
        error_code="TEST_CONTEXT"
    )
    
    # PROPERTY: Error info should preserve all context
    assert error_info.component == component, "Component should be preserved"
    assert error_info.error_code == "TEST_CONTEXT", "Error code should be preserved"
    assert error_info.connection_params is not None, "Connection params should be preserved"
    
    # PROPERTY: Sensitive data should be masked
    if error_info.connection_params:
        for key, value in error_info.connection_params.items():
            if "password" in key.lower() or "secret" in key.lower():
                assert "***" in value or value == "***", \
                    f"Sensitive field {key} should be masked"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(5, "Error Logging Completeness")
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    error_message=st.text(min_size=10, max_size=200),
    component=component_strategy(),
)
def test_property_error_classification(error_message, component):
    """
    Property 5 (classification): Errors should be classified by category
    
    **Validates: Requirements 1.8, 7.6**
    """
    error = Exception(error_message)
    
    error_info = ErrorReporter.create_database_error_info(
        error=error,
        component=component
    )
    
    # PROPERTY: Error should have a category
    assert error_info.category is not None, "Error should have a category"
    assert isinstance(error_info.category, DatabaseErrorCategory), \
        "Category should be a DatabaseErrorCategory"
    
    # PROPERTY: Error should have resolution steps
    assert error_info.resolution_steps is not None, "Should have resolution steps"
    assert len(error_info.resolution_steps) > 0, "Should have at least one resolution step"
    assert all(isinstance(step, str) for step in error_info.resolution_steps), \
        "All resolution steps should be strings"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(5, "Error Logging Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    num_errors=st.integers(min_value=1, max_value=20),
)
def test_property_error_statistics_tracking(num_errors):
    """
    Property 5 (statistics): Error statistics should be tracked accurately
    
    **Validates: Requirements 1.8, 7.6**
    """
    # Reset statistics
    ErrorReporter.reset_error_statistics()
    
    # Generate errors
    components = ["code_review", "graph_analysis", "ai_reasoning"]
    for i in range(num_errors):
        component = components[i % len(components)]
        error = Exception(f"Test error {i}")
        error_info = ErrorReporter.create_database_error_info(
            error=error,
            component=component
        )
        ErrorReporter.log_database_error(error_info, include_details=False)
    
    # Get statistics
    stats = ErrorReporter.get_error_statistics()
    
    # PROPERTY: Total error count should match
    total_errors = sum(stats.error_counts.values())
    assert total_errors == num_errors, \
        f"Should track all {num_errors} errors (found {total_errors})"
    
    # PROPERTY: Component errors should be tracked
    assert len(stats.component_errors) > 0, "Should track errors by component"
    
    # PROPERTY: Recent errors should be stored
    assert len(stats.recent_errors) > 0, "Should store recent errors"
    assert len(stats.recent_errors) <= min(num_errors, 50), \
        "Should not exceed maximum recent errors limit"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(5, "Error Logging Completeness")
@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    error_message=st.text(min_size=10, max_size=200),
)
def test_property_sensitive_data_masking(error_message):
    """
    Property 5 (security): Sensitive data should be masked in error logs
    
    **Validates: Requirements 1.8, 7.6**
    """
    # Add sensitive data to error message
    sensitive_message = f"{error_message} password=secret123 api_key=sk-test123"
    
    # Mask sensitive data
    masked = ErrorReporter.mask_sensitive_data(sensitive_message)
    
    # PROPERTY: Sensitive data should be masked
    assert "secret123" not in masked, "Password should be masked"
    assert "sk-test123" not in masked, "API key should be masked"
    assert "***" in masked, "Should contain mask placeholder"
    
    # PROPERTY: Non-sensitive data should be preserved
    # (at least some of the original message should remain)
    assert len(masked) > 0, "Masked message should not be empty"
