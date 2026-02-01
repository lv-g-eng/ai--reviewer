"""
Property-Based Tests for Startup Validator

Tests core properties of startup validation using hypothesis.

Validates Requirements: 2.2, 2.6, 9.2, 9.3, 9.4, 9.5
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import patch, AsyncMock, MagicMock
from app.core.startup_validator import (
    StartupValidator,
    ValidationError,
    ValidationErrorType,
    ConnectionStatus,
)
from app.core.config import settings as app_settings


class TestStartupValidationProperties:
    """Property-based tests for startup validation"""
    
    @pytest.mark.asyncio
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        missing_var_index=st.integers(min_value=0, max_value=8)
    )
    async def test_property_5_missing_environment_variables(self, missing_var_index):
        """
        **Property 5: Startup validation detects missing environment variables**
        
        For any missing required environment variable, startup validation should 
        report it as a critical error.
        
        Validates: Requirements 2.2, 9.3
        """
        validator = StartupValidator()
        
        # List of required variables
        required_vars = [
            'JWT_SECRET',
            'POSTGRES_HOST',
            'POSTGRES_DB',
            'POSTGRES_USER',
            'POSTGRES_PASSWORD',
            'NEO4J_URI',
            'NEO4J_USER',
            'NEO4J_PASSWORD',
            'REDIS_HOST',
        ]
        
        # Mock settings to simulate missing one variable
        mock_settings = MagicMock()
        
        # Set all required variables to valid values
        for var in required_vars:
            setattr(mock_settings, var, 'valid_value')
        
        # Set one variable to empty to simulate missing
        var_to_miss = required_vars[missing_var_index % len(required_vars)]
        setattr(mock_settings, var_to_miss, '')
        
        with patch('app.core.startup_validator.settings', mock_settings):
            errors = await validator.validate_environment()
            
            # Should have at least one error for missing variable
            assert len(validator.result.errors) > 0
            
            # All errors should be critical
            for error in validator.result.errors:
                assert error.is_critical is True
                assert error.error_type == ValidationErrorType.MISSING_VARIABLE
            
            # Should have error for the missing variable
            assert any(var_to_miss in str(e) for e in validator.result.errors)
    
    @pytest.mark.asyncio
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        bcrypt_rounds=st.integers(min_value=1, max_value=11)
    )
    async def test_property_6_weak_security_settings(self, bcrypt_rounds):
        """
        **Property 6: Startup validation detects weak security settings**
        
        For any security setting below minimum threshold, startup validation 
        should report it as a warning or error.
        
        Validates: Requirements 2.2, 9.4
        """
        validator = StartupValidator()
        
        # Mock settings with weak BCRYPT_ROUNDS
        mock_settings = MagicMock()
        mock_settings.JWT_SECRET = 'a' * 32
        mock_settings.BCRYPT_ROUNDS = bcrypt_rounds
        
        with patch('app.core.startup_validator.settings', mock_settings):
            errors = await validator.validate_security()
            
            # Should have error for weak BCRYPT_ROUNDS (< 12)
            assert len(validator.result.errors) > 0
            
            # Error should be about BCRYPT_ROUNDS
            assert any('BCRYPT_ROUNDS' in str(e) for e in validator.result.errors)
            
            # Error should be critical
            assert any(e.is_critical for e in validator.result.errors)
    
    @pytest.mark.asyncio
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        error_message=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00'))
    )
    async def test_property_7_database_connection_failures_reported(self, error_message):
        """
        **Property 7: Database connection failures are reported**
        
        For any database that fails to connect, the startup validator should 
        report the specific error message.
        
        Validates: Requirements 2.2, 2.6, 9.2
        """
        validator = StartupValidator()
        
        # Mock connection manager with failure
        with patch('app.database.connection_manager.ConnectionManager') as mock_cm:
            mock_instance = AsyncMock()
            mock_cm.return_value = mock_instance
            
            postgres_status = ConnectionStatus(
                service="PostgreSQL",
                is_connected=False,
                error=error_message,
                is_critical=True
            )
            
            mock_instance.verify_all.return_value = {
                "PostgreSQL": postgres_status,
                "Neo4j": ConnectionStatus(
                    service="Neo4j",
                    is_connected=False,
                    error="Connection refused",
                    is_critical=False
                ),
                "Redis": ConnectionStatus(
                    service="Redis",
                    is_connected=False,
                    error="Connection refused",
                    is_critical=False
                ),
            }
            
            status = await validator.validate_databases()
            
            # Should have PostgreSQL disconnected
            assert status["PostgreSQL"].is_connected is False
            
            # Should have error with the specific error message
            assert len(validator.result.errors) > 0
            assert any(error_message in str(e) for e in validator.result.errors)
            
            # Error should be critical
            assert any(e.is_critical for e in validator.result.errors)
    
    @pytest.mark.asyncio
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        service_names=st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_characters='\x00')),
            min_size=1,
            max_size=5,
            unique=True
        )
    )
    async def test_property_8_startup_logs_include_services(self, service_names):
        """
        **Property 8: Startup logs include all initialized services**
        
        For any successful startup, the startup logs should include status 
        of all initialized services.
        
        Validates: Requirements 2.3, 2.5, 9.5
        """
        validator = StartupValidator()
        
        # Create connection statuses for each service
        database_status = {}
        for service_name in service_names:
            database_status[service_name] = ConnectionStatus(
                service=service_name,
                is_connected=True,
                response_time_ms=50.0,
                is_critical=True
            )
        
        validator.result.database_status = database_status
        validator.result.celery_enabled = True
        validator.result.migration_status = "All migrations applied"
        validator.result.is_valid = True
        
        # Generate summary
        validator._generate_summary()
        
        # Summary should be generated
        assert validator.result.summary is not None
        assert len(validator.result.summary) > 0
        
        # Summary should indicate success
        assert "✅" in validator.result.summary
        
        # Summary should include database status
        assert "Databases:" in validator.result.summary or len(database_status) == 0
        
        # Summary should include migration status
        assert "Migrations:" in validator.result.summary
        
        # Summary should include Celery status
        assert "Celery:" in validator.result.summary


class TestStartupValidationErrorReporting:
    """Property-based tests for error reporting"""
    
    @pytest.mark.asyncio
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        error_count=st.integers(min_value=1, max_value=10),
        warning_count=st.integers(min_value=0, max_value=10)
    )
    async def test_error_reporting_includes_all_errors(self, error_count, warning_count):
        """
        Test that error reporting includes all errors and warnings
        
        Validates: Requirements 9.2, 9.3
        """
        validator = StartupValidator()
        
        # Add errors
        for i in range(error_count):
            error = ValidationError(
                error_type=ValidationErrorType.MISSING_VARIABLE,
                message=f"Error {i}",
                is_critical=True,
                remediation=f"Fix error {i}"
            )
            validator.result.errors.append(error)
        
        # Add warnings
        for i in range(warning_count):
            validator.result.warnings.append(f"Warning {i}")
        
        # Format error report
        report = validator.format_error_report()
        
        # Report should contain all errors
        for i in range(error_count):
            assert f"Error {i}" in report
        
        # Report should contain all warnings
        for i in range(warning_count):
            assert f"Warning {i}" in report
        
        # Report should include remediation suggestions
        if error_count > 0:
            assert "How to fix" in report or "remediation" in report.lower()
    
    @pytest.mark.asyncio
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        response_times=st.lists(
            st.floats(min_value=0.1, max_value=1000.0),
            min_size=1,
            max_size=5,
            unique=True
        )
    )
    async def test_connection_status_includes_response_time(self, response_times):
        """
        Test that connection status includes response time information
        
        Validates: Requirements 2.6, 9.5
        """
        for response_time in response_times:
            status = ConnectionStatus(
                service="TestService",
                is_connected=True,
                response_time_ms=response_time,
                is_critical=True
            )
            
            # Status string should include response time
            status_str = str(status)
            assert "✅" in status_str
            assert "TestService" in status_str
            # Response time should be in the string (rounded)
            assert str(int(response_time)) in status_str or str(round(response_time)) in status_str


class TestStartupValidationEdgeCases:
    """Property-based tests for edge cases"""
    
    @pytest.mark.asyncio
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        jwt_secret_length=st.integers(min_value=1, max_value=100)
    )
    async def test_jwt_secret_validation_edge_cases(self, jwt_secret_length):
        """
        Test JWT secret validation with various lengths
        
        Validates: Requirements 2.2, 9.4
        """
        validator = StartupValidator()
        
        # Create JWT secret of specified length
        jwt_secret = 'a' * jwt_secret_length
        
        mock_settings = MagicMock()
        mock_settings.JWT_SECRET = jwt_secret
        mock_settings.BCRYPT_ROUNDS = 12
        
        with patch('app.core.startup_validator.settings', mock_settings):
            errors = await validator.validate_security()
            
            # If JWT_SECRET is less than 32 characters, should have warning
            if jwt_secret_length < 32:
                assert any('JWT_SECRET' in w for w in validator.result.warnings)
            
            # Should not have critical errors for JWT_SECRET length
            jwt_errors = [e for e in validator.result.errors if 'JWT_SECRET' in str(e)]
            assert len(jwt_errors) == 0
    
    @pytest.mark.asyncio
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        bcrypt_rounds=st.integers(min_value=12, max_value=30)
    )
    async def test_bcrypt_rounds_validation_edge_cases(self, bcrypt_rounds):
        """
        Test BCRYPT_ROUNDS validation with various values
        
        Validates: Requirements 2.2, 9.4
        """
        validator = StartupValidator()
        
        mock_settings = MagicMock()
        mock_settings.JWT_SECRET = 'a' * 32
        mock_settings.BCRYPT_ROUNDS = bcrypt_rounds
        
        with patch('app.core.startup_validator.settings', mock_settings):
            errors = await validator.validate_security()
            
            # If BCRYPT_ROUNDS is >= 12 and <= 20, should be valid
            if 12 <= bcrypt_rounds <= 20:
                bcrypt_errors = [e for e in validator.result.errors if 'BCRYPT_ROUNDS' in str(e)]
                assert len(bcrypt_errors) == 0
            
            # If BCRYPT_ROUNDS is > 20, should have warning
            if bcrypt_rounds > 20:
                assert any('BCRYPT_ROUNDS' in w for w in validator.result.warnings)
