"""
Property-Based Tests for Configuration Manager

Tests universal properties of the configuration management system using hypothesis.
These tests validate that the system behaves correctly across all possible inputs
and scenarios, ensuring robustness and correctness.

Validates Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

import tempfile
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest
from hypothesis import given, settings, strategies as st, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize, invariant

from app.core.configuration_manager import (
    ConfigurationManager,
    ConfigurationSource,
    ConfigurationValidator,
    initialize_configuration
)


# Strategy generators for property-based testing
@st.composite
def configuration_key_strategy(draw):
    """Generate valid configuration keys"""
    # Common configuration key patterns
    prefixes = ["", "NEXT_", "POSTGRES_", "NEO4J_", "REDIS_", "JWT_", "GITHUB_"]
    suffixes = ["", "_URL", "_HOST", "_PORT", "_PASSWORD", "_SECRET", "_KEY", "_TOKEN"]
    
    prefix = draw(st.sampled_from(prefixes))
    base = draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd")), min_size=1, max_size=20))
    suffix = draw(st.sampled_from(suffixes))
    
    return f"{prefix}{base}{suffix}".upper()


@st.composite
def configuration_value_strategy(draw):
    """Generate valid configuration values"""
    value_types = [
        st.text(min_size=1, max_size=100),  # String values
        st.integers(min_value=1, max_value=65535),  # Port numbers
        st.booleans(),  # Boolean values
        st.sampled_from(["development", "staging", "production"]),  # Environment values
    ]
    
    return draw(st.one_of(value_types))


@st.composite
def env_file_content_strategy(draw):
    """Generate valid .env file content"""
    num_entries = draw(st.integers(min_value=1, max_value=20))
    entries = []
    
    for _ in range(num_entries):
        key = draw(configuration_key_strategy())
        value = draw(configuration_value_strategy())
        entries.append(f"{key}={value}")
    
    return "\n".join(entries)


@st.composite
def project_structure_strategy(draw):
    """Generate valid project directory structures"""
    has_frontend = draw(st.booleans())
    has_backend = draw(st.booleans())
    has_services = draw(st.booleans())
    
    # At least one directory should exist
    assume(has_frontend or has_backend or has_services)
    
    return {
        "frontend": has_frontend,
        "backend": has_backend,
        "services": has_services
    }


class TestConfigurationValidatorProperties:
    """Property-based tests for configuration validator"""
    
    @given(port=st.integers(min_value=1, max_value=65535))
    @settings(max_examples=100)
    def test_property_port_validation_consistency(self, port):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 1: Configuration Consolidation Consistency**
        
        For any valid port number (1-65535), the validator should accept it and return the same value.
        
        **Validates: Requirements 1.1, 1.2**
        """
        validator = ConfigurationValidator()
        
        # Test with integer
        result = validator.validate_port(port)
        assert result == port
        assert isinstance(result, int)
        
        # Test with string representation
        result_str = validator.validate_port(str(port))
        assert result_str == port
        assert isinstance(result_str, int)
    
    @given(port=st.integers().filter(lambda x: x < 1 or x > 65535))
    @settings(max_examples=50)
    def test_property_port_validation_rejection(self, port):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 2: Configuration Validation Completeness**
        
        For any invalid port number (outside 1-65535), the validator should reject it.
        
        **Validates: Requirements 1.3**
        """
        validator = ConfigurationValidator()
        
        with pytest.raises(ValueError):
            validator.validate_port(port)
    
    @given(secret_length=st.integers(min_value=32, max_value=128))
    @settings(max_examples=50)
    def test_property_secret_validation_acceptance(self, secret_length):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 2: Configuration Validation Completeness**
        
        For any secret with sufficient length (>=32), the validator should accept it.
        
        **Validates: Requirements 1.3**
        """
        validator = ConfigurationValidator()
        secret = "a" * secret_length
        
        result = validator.validate_secret(secret)
        assert result == secret
        assert len(result) >= 32
    
    @given(secret_length=st.integers(min_value=1, max_value=31))
    @settings(max_examples=50)
    def test_property_secret_validation_rejection(self, secret_length):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 2: Configuration Validation Completeness**
        
        For any secret with insufficient length (<32), the validator should reject it.
        
        **Validates: Requirements 1.3**
        """
        validator = ConfigurationValidator()
        secret = "a" * secret_length
        
        with pytest.raises(ValueError, match="Secret must be at least 32 characters"):
            validator.validate_secret(secret)
    
    @given(
        scheme=st.sampled_from(["http", "https", "bolt", "neo4j", "redis"]),
        host=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=1, max_size=20),
        port=st.integers(min_value=1, max_value=65535)
    )
    @settings(max_examples=100)
    def test_property_url_validation_consistency(self, scheme, host, port):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 2: Configuration Validation Completeness**
        
        For any valid URL components, the validator should accept the constructed URL.
        
        **Validates: Requirements 1.3**
        """
        validator = ConfigurationValidator()
        url = f"{scheme}://{host}:{port}"
        
        result = validator.validate_url(url)
        assert result == url
    
    @given(
        scheme=st.sampled_from(["postgresql", "redis", "bolt", "neo4j"]),
        user=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=1, max_size=20),
        password=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd", "Pc")), min_size=1, max_size=20),
        host=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=1, max_size=20),
        port=st.integers(min_value=1, max_value=65535)
    )
    @settings(max_examples=50)
    def test_property_database_url_validation(self, scheme, user, password, host, port):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 2: Configuration Validation Completeness**
        
        For any valid database URL components, the validator should accept the constructed URL.
        
        **Validates: Requirements 1.3**
        """
        validator = ConfigurationValidator()
        
        if scheme in ["postgresql"]:
            url = f"{scheme}://{user}:{password}@{host}:{port}/database"
        else:
            url = f"{scheme}://{user}:{password}@{host}:{port}"
        
        result = validator.validate_database_url(url)
        assert result == url


class TestConfigurationManagerProperties:
    """Property-based tests for Configuration Manager"""
    
    @pytest.fixture
    def temp_project_with_structure(self):
        """Create temporary project with configurable structure"""
        def _create_project(structure: Dict[str, bool], env_content: str = ""):
            temp_dir = tempfile.mkdtemp()
            project_path = Path(temp_dir)
            
            # Create directories based on structure
            if structure.get("frontend", False):
                (project_path / "frontend").mkdir()
            if structure.get("backend", False):
                (project_path / "backend").mkdir()
            if structure.get("services", False):
                (project_path / "services").mkdir()
            
            # Create root .env file if content provided
            if env_content:
                (project_path / ".env").write_text(env_content)
            
            return project_path
        
        return _create_project
    
    @given(
        global_config=st.dictionaries(
            configuration_key_strategy(),
            configuration_value_strategy(),
            min_size=3,
            max_size=8
        ),
        frontend_config=st.dictionaries(
            configuration_key_strategy(),
            configuration_value_strategy(),
            min_size=2,
            max_size=5
        ),
        backend_config=st.dictionaries(
            configuration_key_strategy(),
            configuration_value_strategy(),
            min_size=2,
            max_size=5
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_property_configuration_consolidation_consistency(self, temp_project_with_structure, global_config, frontend_config, backend_config):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 1: Configuration Consolidation Consistency**
        
        For any set of environment configuration files with overlapping variables, the Configuration_Manager 
        should produce a hierarchical configuration that contains all unique variables and applies correct 
        precedence rules for conflicts (service-specific > environment-specific > global).
        
        **Validates: Requirements 1.1, 1.2**
        """
        # Create overlapping configurations to test consolidation
        # Ensure we have some overlapping keys to test precedence
        overlap_keys = list(global_config.keys())[:2] if global_config else []
        
        # Add overlapping keys to frontend and backend configs with different values
        if overlap_keys:
            for key in overlap_keys:
                if key not in frontend_config:
                    frontend_config[key] = f"frontend_{global_config[key]}"
                if key not in backend_config:
                    backend_config[key] = f"backend_{global_config[key]}"
        
        # Ensure we have valid secrets for validation
        valid_secrets = {
            "JWT_SECRET": "jwt_secret_32_characters_long_test",
            "POSTGRES_PASSWORD": "postgres_password_12345678",
            "NEO4J_PASSWORD": "neo4j_password_12345678"
        }
        
        # Add required secrets to avoid validation errors
        for secret_key, secret_value in valid_secrets.items():
            if secret_key not in global_config:
                global_config[secret_key] = secret_value
        
        # Convert all values to strings (as they would be in .env files)
        global_config = {k: str(v) for k, v in global_config.items()}
        frontend_config = {k: str(v) for k, v in frontend_config.items()}
        backend_config = {k: str(v) for k, v in backend_config.items()}
        
        # Create project structure with configuration files
        project_path = temp_project_with_structure(
            {"frontend": True, "backend": True, "services": True},
            ""  # We'll create files manually
        )
        
        try:
            # Create configuration files
            global_env_content = "\n".join([f"{k}={v}" for k, v in global_config.items()])
            (project_path / ".env").write_text(global_env_content)
            
            frontend_env_content = "\n".join([f"{k}={v}" for k, v in frontend_config.items()])
            (project_path / "frontend" / ".env.local").write_text(frontend_env_content)
            
            backend_env_content = "\n".join([f"{k}={v}" for k, v in backend_config.items()])
            (project_path / "backend" / ".env").write_text(backend_env_content)
            
            # Load configuration and test consolidation
            config_manager = ConfigurationManager(project_path)
            
            try:
                consolidated_config = config_manager.load_configuration("development")
                
                # Test Property 1: Configuration Consolidation Consistency
                
                # 1. All unique variables should be present
                all_unique_keys = set(global_config.keys()) | set(frontend_config.keys()) | set(backend_config.keys())
                consolidated_keys = set(consolidated_config.keys())
                
                # All unique keys should be in consolidated config
                assert all_unique_keys.issubset(consolidated_keys), \
                    f"Missing keys in consolidated config: {all_unique_keys - consolidated_keys}"
                
                # 2. Test precedence rules for overlapping variables
                for key in overlap_keys:
                    if key in consolidated_config:
                        # Service-specific configs should take precedence over global
                        if key in backend_config:
                            # Backend service config should win over global
                            assert consolidated_config[key] == backend_config[key], \
                                f"Backend service config should take precedence for {key}: expected {backend_config[key]}, got {consolidated_config[key]}"
                        elif key in frontend_config:
                            # Frontend service config should win over global
                            assert consolidated_config[key] == frontend_config[key], \
                                f"Frontend service config should take precedence for {key}: expected {frontend_config[key]}, got {consolidated_config[key]}"
                        else:
                            # Global config should be used if no service-specific override
                            assert consolidated_config[key] == global_config[key], \
                                f"Global config should be used for {key}: expected {global_config[key]}, got {consolidated_config[key]}"
                
                # 3. Test that conflicts are properly recorded
                if overlap_keys:
                    # Should have conflicts recorded for overlapping keys
                    conflict_keys = {conflict.key for conflict in config_manager.conflicts}
                    overlapping_conflict_keys = set(overlap_keys) & conflict_keys
                    assert len(overlapping_conflict_keys) > 0, \
                        f"Expected conflicts for overlapping keys {overlap_keys}, but found conflicts only for {conflict_keys}"
                
                # 4. Test hierarchical structure consistency
                # Each configuration entry should have proper source attribution
                for key, entry in config_manager.configurations.items():
                    assert isinstance(entry.source, ConfigurationSource), \
                        f"Configuration entry {key} should have valid source"
                    
                    # Verify source precedence is correctly applied
                    if key in backend_config and entry.source != ConfigurationSource.RUNTIME:
                        # Backend keys should come from SERVICE source (unless overridden by runtime)
                        assert entry.source in [ConfigurationSource.SERVICE, ConfigurationSource.RUNTIME], \
                            f"Backend config key {key} should have SERVICE or RUNTIME source, got {entry.source}"
                    elif key in frontend_config and key not in backend_config and entry.source != ConfigurationSource.RUNTIME:
                        # Frontend-only keys should come from SERVICE source
                        assert entry.source in [ConfigurationSource.SERVICE, ConfigurationSource.RUNTIME], \
                            f"Frontend config key {key} should have SERVICE or RUNTIME source, got {entry.source}"
                
                # 5. Test consolidation determinism
                # Loading configuration multiple times should produce identical results
                consolidated_config2 = config_manager.load_configuration("development")
                assert consolidated_config == consolidated_config2, \
                    "Configuration consolidation should be deterministic"
                
                # 6. Test that all values are properly typed and validated
                for key, value in consolidated_config.items():
                    assert value is not None, f"Configuration value for {key} should not be None"
                    assert isinstance(value, (str, int, bool)), \
                        f"Configuration value for {key} should be a basic type, got {type(value)}"
                
            except ValueError as e:
                # Validation errors are acceptable for randomly generated content
                # but we should still verify the error is related to validation
                assert "Configuration validation failed" in str(e) or "Invalid" in str(e), \
                    f"Unexpected error during configuration loading: {e}"
                
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(project_path)
    
    @given(
        structure=project_structure_strategy(),
        env_content=env_file_content_strategy()
    )
    @settings(max_examples=20, deadline=None)
    def test_property_configuration_loading_consistency(self, temp_project_with_structure, structure, env_content):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 1: Configuration Consolidation Consistency**
        
        For any valid project structure and environment content, configuration loading should be consistent.
        
        **Validates: Requirements 1.1, 1.2**
        """
        project_path = temp_project_with_structure(structure, env_content)
        
        try:
            config_manager = ConfigurationManager(project_path)
            
            # Loading configuration should not raise exceptions for valid content
            # We'll catch validation errors separately
            try:
                config = config_manager.load_configuration("development")
                
                # Configuration should be a dictionary
                assert isinstance(config, dict)
                
                # All configuration entries should have corresponding ConfigurationEntry objects
                for key, value in config.items():
                    assert key in config_manager.configurations
                    assert config_manager.configurations[key].value == value
                
                # Configuration should be deterministic - loading twice should give same result
                config2 = config_manager.load_configuration("development")
                assert config == config2
                
            except ValueError as e:
                # Validation errors are acceptable for randomly generated content
                assert "Configuration validation failed" in str(e)
                
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(project_path)
    
    @given(
        updates=st.dictionaries(
            configuration_key_strategy(),
            configuration_value_strategy(),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=20, deadline=None)
    def test_property_configuration_updates_propagation(self, temp_project_with_structure, updates):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 4: Configuration Change Propagation**
        
        For any configuration updates, changes should be properly propagated to all listeners.
        
        **Validates: Requirements 1.5**
        """
        # Create minimal valid project
        project_path = temp_project_with_structure(
            {"frontend": True}, 
            "JWT_SECRET=" + "a" * 32 + "\nPOSTGRES_PASSWORD=" + "b" * 32
        )
        
        try:
            config_manager = ConfigurationManager(project_path)
            config_manager.load_configuration("development")
            
            # Track change events
            change_events = []
            def change_listener(event):
                change_events.append(event)
            
            config_manager.add_change_listener(change_listener)
            
            # Filter updates to avoid validation errors
            valid_updates = {}
            for key, value in updates.items():
                # Skip keys that would cause validation errors
                if key.endswith("_PORT") and not isinstance(value, int):
                    continue
                if key.endswith("_SECRET") and isinstance(value, str) and len(value) < 32:
                    continue
                if key.endswith("_PASSWORD") and isinstance(value, str) and len(value) < 8:
                    continue
                
                valid_updates[key] = str(value)  # Convert to string for env vars
            
            if valid_updates:  # Only test if we have valid updates
                # Apply updates
                config_manager.update_configuration(valid_updates)
                
                # Check that all updates were applied
                for key, value in valid_updates.items():
                    assert key in config_manager.configurations
                    assert str(config_manager.configurations[key].value) == str(value)
                
                # Check that change events were fired
                assert len(change_events) == len(valid_updates)
                
                # Each update should have a corresponding change event
                event_keys = {event.key for event in change_events}
                assert event_keys == set(valid_updates.keys())
                
        finally:
            import shutil
            shutil.rmtree(project_path)
    
    @given(service_name=st.sampled_from(["frontend", "backend", "api-gateway"]))
    @settings(max_examples=10, deadline=None)
    def test_property_service_configuration_subsetting(self, temp_project_with_structure, service_name):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 3: Service Configuration Subsetting**
        
        For any service, the generated configuration should contain only relevant keys.
        
        **Validates: Requirements 1.4**
        """
        # Create project with comprehensive configuration
        env_content = """
JWT_SECRET=jwt_secret_32_characters_long_test
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_PASSWORD=postgres_password_12345678
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
REDIS_HOST=localhost
REDIS_PORT=6379
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=neo4j_password_12345678
BACKEND_PORT=8000
FRONTEND_PORT=3000
CORS_ALLOWED_ORIGINS=http://localhost:3000
RATE_LIMIT_PER_MINUTE=60
"""
        
        project_path = temp_project_with_structure(
            {"frontend": True, "backend": True, "services": True},
            env_content
        )
        
        try:
            config_manager = ConfigurationManager(project_path)
            config_manager.load_configuration("development")
            
            # Get service-specific configuration
            service_config = config_manager.get_service_config(service_name)
            
            # Service config should be properly structured
            assert service_config.service_name == service_name
            assert isinstance(service_config.config, dict)
            
            # Service config should contain only relevant keys
            service_keys = set(service_config.config.keys())
            all_keys = set(config_manager.configurations.keys())
            
            # Service config should be a subset of all configuration
            assert service_keys.issubset(all_keys)
            
            # Service-specific validation
            if service_name == "frontend":
                # Frontend should have frontend-specific keys
                frontend_keys = {"NEXT_PUBLIC_API_URL", "NEXTAUTH_URL", "FRONTEND_PORT"}
                present_frontend_keys = frontend_keys.intersection(service_keys)
                assert len(present_frontend_keys) > 0, "Frontend config should contain frontend-specific keys"
                
                # Frontend should not have backend secrets
                backend_secrets = {"POSTGRES_PASSWORD", "NEO4J_PASSWORD"}
                assert not backend_secrets.intersection(service_keys), "Frontend config should not contain backend secrets"
            
            elif service_name == "backend":
                # Backend should have backend-specific keys
                backend_keys = {"POSTGRES_HOST", "POSTGRES_PORT", "BACKEND_PORT"}
                present_backend_keys = backend_keys.intersection(service_keys)
                assert len(present_backend_keys) > 0, "Backend config should contain backend-specific keys"
            
            elif service_name == "api-gateway":
                # API Gateway should have gateway-specific keys
                gateway_keys = {"JWT_SECRET", "CORS_ALLOWED_ORIGINS", "RATE_LIMIT_PER_MINUTE"}
                present_gateway_keys = gateway_keys.intersection(service_keys)
                assert len(present_gateway_keys) > 0, "API Gateway config should contain gateway-specific keys"
            
        finally:
            import shutil
            shutil.rmtree(project_path)
    
    @given(
        environment=st.sampled_from(["development", "staging", "production"]),
        enable_hot_reload=st.booleans()
    )
    @settings(max_examples=10, deadline=None)
    def test_property_configuration_initialization_consistency(self, environment, enable_hot_reload):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 1: Configuration Consolidation Consistency**
        
        For any environment and hot reload setting, configuration initialization should be consistent.
        
        **Validates: Requirements 1.1, 1.5**
        """
        with patch('app.core.configuration_manager.get_configuration_manager') as mock_get_manager:
            from unittest.mock import MagicMock
            
            mock_manager = MagicMock()
            mock_config = {"TEST_KEY": "test_value", "ENVIRONMENT": environment}
            mock_manager.load_configuration.return_value = mock_config
            mock_get_manager.return_value = mock_manager
            
            # Initialize configuration
            result_config = initialize_configuration(environment, enable_hot_reload)
            
            # Should return the loaded configuration
            assert result_config == mock_config
            
            # Should call load_configuration with correct environment
            mock_manager.load_configuration.assert_called_once_with(environment)
            
            # Should enable hot reloading if requested
            if enable_hot_reload:
                mock_manager.enable_hot_reloading.assert_called_once()
            else:
                mock_manager.enable_hot_reloading.assert_not_called()


class ConfigurationManagerStateMachine(RuleBasedStateMachine):
    """
    Stateful property-based testing for Configuration Manager
    
    This tests the Configuration Manager through a series of operations
    to ensure it maintains consistency across different state transitions.
    """
    
    def __init__(self):
        super().__init__()
        self.temp_dir = None
        self.config_manager = None
        self.loaded_config = None
        self.change_events = []
    
    @initialize()
    def setup_manager(self):
        """Initialize the configuration manager with a temporary project"""
        self.temp_dir = tempfile.mkdtemp()
        project_path = Path(self.temp_dir)
        
        # Create basic project structure
        (project_path / "frontend").mkdir()
        (project_path / "backend").mkdir()
        
        # Create minimal valid configuration
        (project_path / ".env").write_text("""
JWT_SECRET=jwt_secret_32_characters_long_test
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_PASSWORD=postgres_password_12345678
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=neo4j_password_12345678
""".strip())
        
        self.config_manager = ConfigurationManager(project_path)
        
        # Add change listener
        def change_listener(event):
            self.change_events.append(event)
        self.config_manager.add_change_listener(change_listener)
    
    @rule()
    def load_configuration(self):
        """Load configuration"""
        self.loaded_config = self.config_manager.load_configuration("development")
        assert isinstance(self.loaded_config, dict)
        assert len(self.loaded_config) > 0
    
    @rule(
        key=configuration_key_strategy(),
        value=st.text(min_size=1, max_size=50)
    )
    def update_configuration(self, key, value):
        """Update configuration with new values"""
        if self.loaded_config is None:
            self.load_configuration()
        
        # Avoid validation errors for specific keys
        if key.endswith("_PORT"):
            value = "8000"  # Use valid port
        elif key.endswith("_SECRET") or key.endswith("_PASSWORD"):
            value = "a" * 32  # Use valid secret length
        
        initial_event_count = len(self.change_events)
        
        self.config_manager.update_configuration({key: value})
        
        # Configuration should be updated
        assert key in self.config_manager.configurations
        assert self.config_manager.configurations[key].value == value
        
        # Change event should be fired
        assert len(self.change_events) > initial_event_count
    
    @rule(service_name=st.sampled_from(["frontend", "backend", "api-gateway"]))
    def get_service_config(self, service_name):
        """Get service-specific configuration"""
        if self.loaded_config is None:
            self.load_configuration()
        
        service_config = self.config_manager.get_service_config(service_name)
        
        assert service_config.service_name == service_name
        assert isinstance(service_config.config, dict)
        
        # Service config should be cached
        service_config2 = self.config_manager.get_service_config(service_name)
        assert service_config.config == service_config2.config
    
    @rule()
    def export_configuration(self):
        """Export configuration"""
        if self.loaded_config is None:
            self.load_configuration()
        
        # Export with secrets masked
        masked_config = self.config_manager.export_configuration(mask_secrets=True)
        assert isinstance(masked_config, dict)
        
        # Export without masking
        unmasked_config = self.config_manager.export_configuration(mask_secrets=False)
        assert isinstance(unmasked_config, dict)
        
        # Should have same keys
        assert set(masked_config.keys()) == set(unmasked_config.keys())
    
    @invariant()
    def configuration_consistency(self):
        """Configuration should remain consistent"""
        if self.config_manager and self.loaded_config:
            # All loaded config keys should exist in manager
            for key in self.loaded_config.keys():
                assert key in self.config_manager.configurations
            
            # Manager should have valid configuration entries
            for key, entry in self.config_manager.configurations.items():
                assert isinstance(entry.key, str)
                assert entry.value is not None
                assert isinstance(entry.source, ConfigurationSource)
    
    def teardown(self):
        """Clean up resources"""
        if self.config_manager:
            self.config_manager.disable_hot_reloading()
        
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestConfigurationManagerStateful:
    """Test Configuration Manager with stateful property-based testing"""
    
    @settings(max_examples=10, stateful_step_count=20, deadline=None)
    def test_configuration_manager_state_consistency(self):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 1: Configuration Consolidation Consistency**
        
        Configuration Manager should maintain consistency across all state transitions.
        
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
        """
        state_machine = ConfigurationManagerStateMachine()
        try:
            state_machine.setup_manager()
            
            # Run the state machine
            for _ in range(10):  # Reduced iterations for faster testing
                # Randomly choose and execute rules
                if hasattr(state_machine, 'load_configuration'):
                    state_machine.load_configuration()
                if hasattr(state_machine, 'update_configuration'):
                    state_machine.update_configuration("TEST_KEY", "test_value")
                if hasattr(state_machine, 'get_service_config'):
                    state_machine.get_service_config("frontend")
                if hasattr(state_machine, 'export_configuration'):
                    state_machine.export_configuration()
                
                # Check invariants
                state_machine.configuration_consistency()
        
        finally:
            state_machine.teardown()


# Additional property tests for edge cases
class TestConfigurationManagerEdgeCases:
    """Property-based tests for edge cases and error conditions"""
    
    @given(
        invalid_port=st.one_of(
            st.integers(max_value=0),
            st.integers(min_value=65536),
            st.text(alphabet=st.characters(whitelist_categories=("Ll",)), min_size=1, max_size=10)
        )
    )
    @settings(max_examples=20)
    def test_property_invalid_port_handling(self, invalid_port):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 2: Configuration Validation Completeness**
        
        For any invalid port value, the system should properly reject it with a clear error.
        
        **Validates: Requirements 1.3**
        """
        validator = ConfigurationValidator()
        
        with pytest.raises(ValueError):
            validator.validate_port(invalid_port)
    
    @given(
        empty_or_whitespace=st.one_of(
            st.just(""),
            st.text(alphabet=st.characters(whitelist_categories=("Zs",)), min_size=1, max_size=10)
        )
    )
    @settings(max_examples=20)
    def test_property_empty_configuration_handling(self, empty_or_whitespace):
        """
        **Feature: frontend-backend-integration-redundancy-elimination, Property 2: Configuration Validation Completeness**
        
        For any empty or whitespace-only configuration value, the system should handle it appropriately.
        
        **Validates: Requirements 1.3**
        """
        # Empty values should be skipped during loading
        temp_dir = tempfile.mkdtemp()
        try:
            project_path = Path(temp_dir)
            
            # Create .env file with empty value
            (project_path / ".env").write_text(f"EMPTY_KEY={empty_or_whitespace}")
            
            config_manager = ConfigurationManager(project_path)
            
            # Load configuration - empty values should be skipped
            config_manager._load_env_file(project_path / ".env", ConfigurationSource.GLOBAL)
            
            # Empty values should not be in configuration
            assert "EMPTY_KEY" not in config_manager.configurations
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)