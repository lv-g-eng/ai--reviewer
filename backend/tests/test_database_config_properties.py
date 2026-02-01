"""
Property-Based Tests for Database Configuration Validation

Tests core properties of database configuration validation using hypothesis.

Validates Requirements: 7.1, 7.2, 7.4
"""

import pytest
import os
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import patch, MagicMock
from app.database.config_validator import ConfigurationValidator
from app.database.models import DatabaseConfig, RetryConfig, get_python_version
from app.core.config import Settings
from pydantic import ValidationError


class TestConfigurationValidationProperties:
    """Property-based tests for configuration validation completeness"""
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        missing_var_index=st.integers(min_value=0, max_value=7)
    )
    def test_property_16_configuration_validation_completeness(self, missing_var_index):
        """
        **Feature: database-connectivity-fixes, Property 16: Configuration Validation Completeness**
        
        For any system startup, the configuration validator should verify all required 
        database parameters are present, validate version compatibility, and check that 
        timeout and retry values are within acceptable ranges.
        
        Validates: Requirements 7.1, 7.2, 7.4
        """
        validator = ConfigurationValidator()
        
        # List of required environment variables
        required_vars = [
            'POSTGRES_HOST',
            'POSTGRES_DB', 
            'POSTGRES_USER',
            'POSTGRES_PASSWORD',
            'NEO4J_URI',
            'NEO4J_USER',
            'NEO4J_PASSWORD',
            'REDIS_HOST'
        ]
        
        # Create valid environment with one missing variable
        valid_env = {
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'testdb',
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass',
            'NEO4J_URI': 'bolt://localhost:7687',
            'NEO4J_USER': 'neo4j',
            'NEO4J_PASSWORD': 'neo4jpass',
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': '6379'
        }
        
        # Remove one required variable
        var_to_remove = required_vars[missing_var_index % len(required_vars)]
        test_env = valid_env.copy()
        del test_env[var_to_remove]
        
        with patch.dict(os.environ, test_env, clear=True):
            errors = validator.validate_environment_variables()
            
            # Should detect missing required variable
            assert len(errors) > 0
            
            # Should specifically mention the missing variable
            assert any(var_to_remove in error for error in errors)
            
            # Error message should be descriptive
            missing_var_errors = [e for e in errors if var_to_remove in e]
            assert len(missing_var_errors) > 0
            for error in missing_var_errors:
                assert 'required' in error.lower() or 'missing' in error.lower()
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        connection_timeout=st.integers(min_value=-10, max_value=1000),
        pool_min_size=st.integers(min_value=-5, max_value=100),
        pool_max_size=st.integers(min_value=-5, max_value=100),
        max_retries=st.integers(min_value=-5, max_value=50),
        base_delay=st.floats(min_value=-1.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        max_delay=st.floats(min_value=-1.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        backoff_multiplier=st.floats(min_value=-1.0, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_property_16_timeout_and_retry_validation(
        self, connection_timeout, pool_min_size, pool_max_size, 
        max_retries, base_delay, max_delay, backoff_multiplier
    ):
        """
        **Feature: database-connectivity-fixes, Property 16: Configuration Validation Completeness**
        
        For any configuration parameters, the validator should check that timeout 
        and retry values are within acceptable ranges and report validation errors 
        for invalid values.
        
        Validates: Requirements 7.1, 7.2, 7.4
        """
        # Test RetryConfig validation
        try:
            retry_config = RetryConfig(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_multiplier=backoff_multiplier
            )
            
            # If creation succeeded, values should be valid
            assert retry_config.max_retries >= 0
            assert retry_config.base_delay > 0
            assert retry_config.max_delay > 0
            assert retry_config.backoff_multiplier > 1
            assert retry_config.max_delay >= retry_config.base_delay
            
        except ValueError as e:
            # If creation failed, should be due to invalid values
            error_msg = str(e).lower()
            
            if max_retries < 0:
                assert 'max_retries' in error_msg and 'non-negative' in error_msg
            elif base_delay <= 0:
                assert 'base_delay' in error_msg and 'positive' in error_msg
            elif max_delay <= 0:
                assert 'max_delay' in error_msg and 'positive' in error_msg
            elif backoff_multiplier <= 1:
                assert 'backoff_multiplier' in error_msg and 'greater than 1' in error_msg
            elif max_delay < base_delay:
                assert 'max_delay' in error_msg and 'base_delay' in error_msg
        
        # Test DatabaseConfig validation
        try:
            db_config = DatabaseConfig(
                postgresql_dsn="postgresql://user:pass@localhost:5432/db",
                neo4j_uri="bolt://localhost:7687",
                neo4j_auth=("neo4j", "password"),
                connection_timeout=connection_timeout,
                pool_min_size=pool_min_size,
                pool_max_size=pool_max_size
            )
            
            # If creation succeeded, values should be valid
            assert db_config.connection_timeout > 0
            assert db_config.pool_min_size >= 0
            assert db_config.pool_max_size > 0
            assert db_config.pool_max_size >= db_config.pool_min_size
            
        except ValueError as e:
            # If creation failed, should be due to invalid values
            error_msg = str(e).lower()
            
            if connection_timeout <= 0:
                assert 'connection_timeout' in error_msg and 'positive' in error_msg
            elif pool_min_size < 0:
                assert 'pool_min_size' in error_msg and 'non-negative' in error_msg
            elif pool_max_size <= 0:
                assert 'pool_max_size' in error_msg and 'positive' in error_msg
            elif pool_max_size < pool_min_size:
                assert 'pool_max_size' in error_msg and 'pool_min_size' in error_msg
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        python_version=st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_characters='\x00')),
        asyncpg_version=st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_characters='\x00'))
    )
    def test_property_16_version_compatibility_validation(self, python_version, asyncpg_version):
        """
        **Feature: database-connectivity-fixes, Property 16: Configuration Validation Completeness**
        
        For any Python and asyncpg version combination, the validator should check 
        compatibility and provide clear recommendations when versions are incompatible.
        
        Validates: Requirements 7.1, 7.2, 7.4
        """
        validator = ConfigurationValidator()
        
        # Mock version detection
        with patch('app.database.config_validator.get_python_version', return_value=python_version):
            with patch('asyncpg.__version__', asyncpg_version, create=True):
                try:
                    result = validator.check_python_asyncpg_compatibility()
                    
                    # Result should have required fields
                    assert hasattr(result, 'is_compatible')
                    assert hasattr(result, 'python_version')
                    assert hasattr(result, 'asyncpg_version')
                    assert hasattr(result, 'issues')
                    assert hasattr(result, 'recommendations')
                    
                    # Versions should match what we provided
                    assert result.python_version == python_version
                    assert result.asyncpg_version == asyncpg_version
                    
                    # If incompatible, should have issues and recommendations
                    if not result.is_compatible:
                        assert len(result.issues) > 0
                        assert len(result.recommendations) > 0
                        
                        # Issues should be descriptive
                        for issue in result.issues:
                            assert len(issue) > 0
                            assert isinstance(issue, str)
                        
                        # Recommendations should be actionable
                        for rec in result.recommendations:
                            assert len(rec) > 0
                            assert isinstance(rec, str)
                    
                except Exception as e:
                    # If validation fails, should be due to invalid version format
                    # This is acceptable for property testing with arbitrary strings
                    assert isinstance(e, (ValueError, AttributeError, ImportError))
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        port_values=st.lists(
            st.integers(min_value=-1000, max_value=100000),
            min_size=3,
            max_size=3
        )
    )
    def test_property_16_port_validation(self, port_values):
        """
        **Feature: database-connectivity-fixes, Property 16: Configuration Validation Completeness**
        
        For any port configuration values, the validator should ensure ports are 
        within valid ranges (1-65535) and report errors for invalid ports.
        
        Validates: Requirements 7.1, 7.2, 7.4
        """
        postgres_port, neo4j_port, redis_port = port_values
        
        # Test with Settings validation
        test_env = {
            'JWT_SECRET': 'a' * 32,
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': str(postgres_port),
            'POSTGRES_DB': 'testdb',
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass',
            'NEO4J_URI': f'bolt://localhost:{neo4j_port}',
            'NEO4J_USER': 'neo4j',
            'NEO4J_PASSWORD': 'neo4jpass',
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': str(redis_port)
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            try:
                settings = Settings()
                
                # If creation succeeded, ports should be valid
                assert 1 <= settings.POSTGRES_PORT <= 65535
                assert 1 <= settings.REDIS_PORT <= 65535
                
                # Neo4j port is embedded in URI, harder to validate directly
                # but URI should be parseable
                assert settings.NEO4J_URI.startswith('bolt://')
                
            except (ValidationError, ValueError) as e:
                # If validation failed, should be due to invalid port values
                error_msg = str(e).lower()
                
                if not (1 <= postgres_port <= 65535):
                    # Should have error about postgres port
                    assert 'postgres_port' in error_msg or 'port' in error_msg
                
                if not (1 <= redis_port <= 65535):
                    # Should have error about redis port  
                    assert 'redis_port' in error_msg or 'port' in error_msg


class TestConfigurationConflictPreventionProperties:
    """Property-based tests for configuration conflict prevention"""
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow])
    @given(
        environment=st.sampled_from(['development', 'staging', 'production']),
        jwt_secret_length=st.integers(min_value=0, max_value=100),
        postgres_password=st.text(min_size=0, max_size=50, alphabet=st.characters(blacklist_characters='\x00')),
        neo4j_password=st.text(min_size=0, max_size=50, alphabet=st.characters(blacklist_characters='\x00')),
        pool_min_size=st.integers(min_value=0, max_value=50),
        pool_max_size=st.integers(min_value=0, max_value=100),
        base_delay=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
        max_delay=st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    def test_property_17_configuration_conflict_prevention(
        self, environment, jwt_secret_length, postgres_password, neo4j_password,
        pool_min_size, pool_max_size, base_delay, max_delay
    ):
        """
        **Feature: database-connectivity-fixes, Property 17: Configuration Conflict Prevention**
        
        For any configuration with conflicts, the system should prevent startup and 
        provide clear resolution instructions with appropriate configuration templates.
        
        Validates: Requirements 7.3, 7.5
        """
        validator = ConfigurationValidator()
        
        # Create test environment with potential conflicts
        jwt_secret = 'a' * jwt_secret_length
        test_env = {
            'ENVIRONMENT': environment,
            'JWT_SECRET': jwt_secret,
            'POSTGRES_PASSWORD': postgres_password,
            'NEO4J_PASSWORD': neo4j_password,
            'DB_POOL_MIN_SIZE': str(pool_min_size),
            'DB_POOL_MAX_SIZE': str(pool_max_size),
            'DB_RETRY_BASE_DELAY': str(base_delay),
            'DB_RETRY_MAX_DELAY': str(max_delay)
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            conflicts = validator.validate_configuration_conflicts()
            
            # Check for expected conflicts based on input
            expected_conflicts = []
            
            # Production security conflicts
            if environment == 'production':
                if jwt_secret_length < 32:
                    expected_conflicts.append('JWT_SECRET')
                
                if postgres_password == 'password':
                    expected_conflicts.append('POSTGRES_PASSWORD')
                
                if neo4j_password == 'password':
                    expected_conflicts.append('NEO4J_PASSWORD')
            
            # Pool size conflicts
            if pool_max_size < pool_min_size:
                expected_conflicts.append('POOL_SIZE')
            
            # Retry delay conflicts
            if max_delay < base_delay:
                expected_conflicts.append('RETRY_DELAY')
            
            # Validate conflicts were detected
            if expected_conflicts:
                assert len(conflicts) > 0, f"Expected conflicts for {expected_conflicts} but got none"
                
                # Check that conflict messages are descriptive
                for conflict in conflicts:
                    assert len(conflict) > 0
                    assert isinstance(conflict, str)
                    assert 'conflict' in conflict.lower() or 'security' in conflict.lower()
                    
                    # Check for specific conflict types
                    if 'JWT_SECRET' in expected_conflicts and 'JWT_SECRET' in conflict:
                        assert 'production' in conflict.lower()
                        assert '32' in conflict
                    
                    if 'POSTGRES_PASSWORD' in expected_conflicts and 'password' in conflict.lower():
                        assert 'production' in conflict.lower()
                    
                    if 'NEO4J_PASSWORD' in expected_conflicts and 'neo4j' in conflict.lower():
                        assert 'production' in conflict.lower()
                    
                    if 'POOL_SIZE' in expected_conflicts and 'pool' in conflict.lower():
                        assert 'DB_POOL_MAX_SIZE' in conflict
                        assert 'DB_POOL_MIN_SIZE' in conflict
                    
                    if 'RETRY_DELAY' in expected_conflicts and 'retry' in conflict.lower():
                        assert 'DB_RETRY_MAX_DELAY' in conflict
                        assert 'DB_RETRY_BASE_DELAY' in conflict
            else:
                # No conflicts expected - should return empty list or no critical conflicts
                critical_conflicts = [c for c in conflicts if 'security' in c.lower() or 'conflict' in c.lower()]
                assert len(critical_conflicts) == 0, f"Unexpected conflicts: {critical_conflicts}"
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        environment=st.sampled_from(['development', 'staging', 'production'])
    )
    def test_property_17_configuration_template_provision(self, environment):
        """
        **Feature: database-connectivity-fixes, Property 17: Configuration Conflict Prevention**
        
        For any environment type, the system should provide appropriate configuration 
        templates with recommended values for that environment.
        
        Validates: Requirements 7.5
        """
        validator = ConfigurationValidator()
        
        # Test that we can get configuration templates (if method exists)
        if hasattr(validator, 'get_configuration_template'):
            template = validator.get_configuration_template(environment)
            
            # Template should be a dictionary
            assert isinstance(template, dict)
            
            # Should have required database configuration keys
            required_keys = [
                'POSTGRES_HOST', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD',
                'NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD',
                'REDIS_HOST'
            ]
            
            for key in required_keys:
                assert key in template, f"Template missing required key: {key}"
                assert template[key] is not None
                assert len(str(template[key])) > 0
            
            # Environment-specific validations
            if environment == 'production':
                # Production should use secure URIs and placeholder passwords
                assert template['NEO4J_URI'].startswith(('bolt+s://', 'neo4j+s://'))
                assert '${' in template['POSTGRES_PASSWORD']  # Should be placeholder
                assert '${' in template['NEO4J_PASSWORD']  # Should be placeholder
            
            elif environment == 'development':
                # Development can use localhost and simple passwords
                assert 'localhost' in template['POSTGRES_HOST']
                assert 'localhost' in template['NEO4J_URI']


class TestConfigurationValidatorMethods:
    """Test specific ConfigurationValidator methods"""
    
    def test_validate_environment_variables_all_present(self):
        """Test that validate_environment_variables returns no errors when all vars present"""
        validator = ConfigurationValidator()
        
        valid_env = {
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'testdb',
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass',
            'NEO4J_URI': 'bolt://localhost:7687',
            'NEO4J_USER': 'neo4j',
            'NEO4J_PASSWORD': 'neo4jpass',
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': '6379'
        }
        
        with patch.dict(os.environ, valid_env, clear=True):
            errors = validator.validate_environment_variables()
            assert len(errors) == 0
    
    def test_check_python_asyncpg_compatibility_valid_versions(self):
        """Test compatibility check with known good versions"""
        validator = ConfigurationValidator()
        
        with patch('app.database.config_validator.get_python_version', return_value='3.11.0'):
            with patch('asyncpg.__version__', '0.28.0', create=True):
                result = validator.check_python_asyncpg_compatibility()
                
                assert result.python_version == '3.11.0'
                assert result.asyncpg_version == '0.28.0'
                assert isinstance(result.is_compatible, bool)
                assert isinstance(result.issues, list)
                assert isinstance(result.recommendations, list)
    
    def test_validate_database_config_valid_config(self):
        """Test database config validation with valid configuration"""
        validator = ConfigurationValidator()
        
        config = DatabaseConfig(
            postgresql_dsn="postgresql://user:pass@localhost:5432/db",
            neo4j_uri="bolt://localhost:7687",
            neo4j_auth=("neo4j", "password"),
            connection_timeout=30,
            pool_min_size=5,
            pool_max_size=20
        )
        
        errors = validator.validate_database_config(config)
        assert len(errors) == 0
    
    def test_validate_database_config_invalid_dsn(self):
        """Test database config validation with invalid DSN"""
        validator = ConfigurationValidator()
        
        config = DatabaseConfig(
            postgresql_dsn="",  # Invalid empty DSN
            neo4j_uri="bolt://localhost:7687",
            neo4j_auth=("neo4j", "password")
        )
        
        errors = validator.validate_database_config(config)
        assert len(errors) > 0
        assert any('postgresql_dsn' in error.lower() for error in errors)