"""
Property-based tests for Context Detector Service

These tests verify universal properties that should hold across all valid inputs
using the hypothesis library for property-based testing.
"""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, assume, settings
import pytest

from app.services.library_management.context_detector import ContextDetector
from app.models.library import RegistryType, ProjectContext


class TestContextDetectorProperties:
    """Property-based tests for ContextDetector"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        # Ensure we use an isolated temporary directory
        self.detector = ContextDetector(project_root=self.temp_dir)
        
        # Verify the detector is using our temp directory
        assert str(self.detector.project_root) == str(Path(self.temp_dir))
    
    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def clean_temp_directory(self):
        """Clean the temporary directory between test iterations"""
        # Remove all files and subdirectories
        for item in Path(self.temp_dir).iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
    
    def create_config_file(self, relative_path: str, content: str = "{}"):
        """Helper method to create configuration files"""
        full_path = Path(self.temp_dir) / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        # Use UTF-8 encoding to handle unicode characters
        full_path.write_text(content, encoding='utf-8')
        return full_path
    
    # ========================================================================
    # Property 5: Context Detection Consistency
    # ========================================================================
    
    # Feature: library-management, Property 5: Context Detection Consistency
    @given(st.sampled_from(list(RegistryType)))
    @settings(max_examples=100)
    def test_context_detection_consistency(self, registry_type: RegistryType):
        """
        Property 5: For any library URI, the context detector should consistently 
        map npm packages to frontend context and PyPI packages to backend context.
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Test the property multiple times to ensure consistency
        results = []
        for _ in range(5):  # Test consistency across multiple calls
            context = self.detector.detect_context(registry_type)
            results.append(context)
        
        # All results should be identical (consistency)
        assert all(result == results[0] for result in results), \
            f"Context detection inconsistent for {registry_type}: {results}"
        
        # Verify specific mappings
        if registry_type == RegistryType.NPM:
            assert results[0] == ProjectContext.FRONTEND, \
                f"npm should map to FRONTEND, got {results[0]}"
        elif registry_type == RegistryType.PYPI:
            assert results[0] == ProjectContext.BACKEND, \
                f"pypi should map to BACKEND, got {results[0]}"
        elif registry_type == RegistryType.MAVEN:
            assert results[0] == ProjectContext.BACKEND, \
                f"maven should map to BACKEND, got {results[0]}"
    
    # ========================================================================
    # Property 6: Configuration File Validation
    # ========================================================================
    
    # Feature: library-management, Property 6: Configuration File Validation
    @given(
        context=st.sampled_from(list(ProjectContext)),
        file_exists=st.booleans(),
        file_content=st.text(min_size=0, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126))
    )
    @settings(max_examples=100)
    def test_configuration_file_validation(
        self, 
        context: ProjectContext, 
        file_exists: bool, 
        file_content: str
    ):
        """
        Property 6: For any project context, the validator should verify that 
        the appropriate package manager configuration file exists (package.json 
        for frontend, requirements.txt for backend) before allowing installation.
        
        **Validates: Requirements 3.4**
        """
        # Clean temp directory at start of each iteration
        self.clean_temp_directory()
        
        # Get the expected config file path for this context
        try:
            config_file_path = self.detector.get_config_file_path(context)
        except ValueError:
            # Skip unsupported contexts
            assume(False)
        
        if file_exists:
            # Create the configuration file
            self.create_config_file(config_file_path, file_content)
        
        # Validate the context
        is_valid, error_message = self.detector.validate_context(context)
        
        # Debug information
        config_file_path = self.detector.get_config_file_path(context)
        abs_path = self.detector.get_absolute_config_path(context)
        file_actually_exists = abs_path.exists()
        
        # Property: Validation result should match file existence
        if file_exists:
            assert is_valid is True, \
                f"Context {context} should be valid when config file exists. " \
                f"Config path: {config_file_path}, Abs path: {abs_path}, " \
                f"File exists: {file_actually_exists}, Error: {error_message}"
            assert error_message is None, \
                f"No error expected when config file exists, got: {error_message}"
        else:
            assert is_valid is False, \
                f"Context {context} should be invalid when config file missing. " \
                f"Config path: {config_file_path}, Abs path: {abs_path}, " \
                f"File exists: {file_actually_exists}, Error: {error_message}"
            assert error_message is not None, \
                f"Error message expected when config file missing"
            assert "Configuration file not found" in error_message, \
                f"Error should mention missing file, got: {error_message}"
    
    # ========================================================================
    # Property: Context-Registry Mapping Completeness
    # ========================================================================
    
    # Feature: library-management, Property: Context-Registry Mapping Completeness
    @given(st.sampled_from(list(RegistryType)))
    @settings(max_examples=100)
    def test_registry_mapping_completeness(self, registry_type: RegistryType):
        """
        Property: Every supported registry type should have a corresponding 
        project context mapping, and the mapping should be deterministic.
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Should not raise an exception for any supported registry type
        try:
            context = self.detector.detect_context(registry_type)
        except ValueError as e:
            pytest.fail(f"Registry type {registry_type} should be supported, got error: {e}")
        
        # Result should be a valid ProjectContext
        assert isinstance(context, ProjectContext), \
            f"Expected ProjectContext, got {type(context)}"
        
        # Mapping should be deterministic (same input -> same output)
        context2 = self.detector.detect_context(registry_type)
        assert context == context2, \
            f"Registry mapping should be deterministic: {context} != {context2}"
    
    # ========================================================================
    # Property: Configuration Path Consistency
    # ========================================================================
    
    # Feature: library-management, Property: Configuration Path Consistency
    @given(st.sampled_from(list(ProjectContext)))
    @settings(max_examples=100)
    def test_configuration_path_consistency(self, context: ProjectContext):
        """
        Property: For any project context, the configuration file path should 
        be consistent and follow expected patterns.
        
        **Validates: Requirements 3.4**
        """
        try:
            # Get relative path
            relative_path = self.detector.get_config_file_path(context)
            
            # Get absolute path
            absolute_path = self.detector.get_absolute_config_path(context)
            
            # Paths should be consistent
            expected_absolute = Path(self.detector.project_root) / relative_path
            assert absolute_path == expected_absolute, \
                f"Absolute path inconsistent: {absolute_path} != {expected_absolute}"
            
            # Path should follow expected patterns
            if context == ProjectContext.FRONTEND:
                assert relative_path == "frontend/package.json", \
                    f"Frontend should use package.json, got: {relative_path}"
            elif context == ProjectContext.BACKEND:
                assert relative_path == "backend/requirements.txt", \
                    f"Backend should use requirements.txt, got: {relative_path}"
            elif context == ProjectContext.SERVICES:
                assert relative_path == "services/package.json", \
                    f"Services should use package.json, got: {relative_path}"
            
            # Path should be non-empty string
            assert isinstance(relative_path, str), \
                f"Config path should be string, got {type(relative_path)}"
            assert len(relative_path) > 0, \
                f"Config path should not be empty"
            
        except ValueError:
            # Some contexts might not be supported - that's okay
            pass
    
    # ========================================================================
    # Property: Validation Error Message Quality
    # ========================================================================
    
    # Feature: library-management, Property: Validation Error Message Quality
    @given(
        context=st.sampled_from(list(ProjectContext)),
        create_directory=st.booleans()
    )
    @settings(max_examples=100)
    def test_validation_error_message_quality(
        self, 
        context: ProjectContext, 
        create_directory: bool
    ):
        """
        Property: When validation fails, error messages should be descriptive 
        and contain relevant information about what's missing.
        
        **Validates: Requirements 3.5**
        """
        try:
            config_file_path = self.detector.get_config_file_path(context)
        except ValueError:
            # Skip unsupported contexts
            assume(False)
        
        if create_directory:
            # Create the parent directory but not the file
            full_path = Path(self.temp_dir) / config_file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate context (should fail since file doesn't exist)
        is_valid, error_message = self.detector.validate_context(context)
        
        # Should be invalid
        assert is_valid is False, \
            f"Context should be invalid when config file missing"
        
        # Error message should be informative
        assert error_message is not None, \
            f"Error message should not be None when validation fails"
        assert isinstance(error_message, str), \
            f"Error message should be string, got {type(error_message)}"
        assert len(error_message) > 0, \
            f"Error message should not be empty"
        
        # Error message should contain the config file path
        assert config_file_path in error_message, \
            f"Error message should mention config file path: {error_message}"
        
        # Error message should be descriptive
        assert any(keyword in error_message.lower() for keyword in 
                  ["not found", "missing", "does not exist"]), \
            f"Error message should describe the problem: {error_message}"
    
    # ========================================================================
    # Property: Alternative Context Suggestions
    # ========================================================================
    
    # Feature: library-management, Property: Alternative Context Suggestions
    @given(
        registry_type=st.sampled_from(list(RegistryType)),
        available_contexts=st.sets(
            st.sampled_from(list(ProjectContext)), 
            min_size=0, 
            max_size=len(ProjectContext)
        )
    )
    @settings(max_examples=100)
    def test_alternative_context_suggestions(
        self, 
        registry_type: RegistryType, 
        available_contexts: set
    ):
        """
        Property: Alternative context suggestions should only include contexts 
        that are actually valid (have config files) and should exclude the 
        primary context for the registry type.
        
        **Validates: Requirements 3.3**
        """
        # Create config files for the specified available contexts
        for context in available_contexts:
            try:
                config_file_path = self.detector.get_config_file_path(context)
                self.create_config_file(config_file_path, "{}")
            except ValueError:
                # Skip unsupported contexts
                continue
        
        # Get primary context for this registry type
        primary_context = self.detector.detect_context(registry_type)
        
        # Get alternative suggestions
        alternatives = self.detector.suggest_alternative_contexts(registry_type)
        
        # Property 1: Alternatives should not include primary context
        assert primary_context not in alternatives, \
            f"Primary context {primary_context} should not be in alternatives: {alternatives}"
        
        # Property 2: All alternatives should be valid contexts
        for alt_context in alternatives:
            is_valid, _ = self.detector.validate_context(alt_context)
            assert is_valid is True, \
                f"Alternative context {alt_context} should be valid"
        
        # Property 3: All valid non-primary contexts should be in alternatives
        for context in ProjectContext:
            if context != primary_context:
                is_valid, _ = self.detector.validate_context(context)
                if is_valid:
                    assert context in alternatives, \
                        f"Valid context {context} should be in alternatives: {alternatives}"
        
        # Property 4: Alternatives should be a list of ProjectContext
        assert isinstance(alternatives, list), \
            f"Alternatives should be list, got {type(alternatives)}"
        for alt in alternatives:
            assert isinstance(alt, ProjectContext), \
                f"Each alternative should be ProjectContext, got {type(alt)}"
    
    # ========================================================================
    # Property: Combined Operation Consistency
    # ========================================================================
    
    # Feature: library-management, Property: Combined Operation Consistency
    @given(
        registry_type=st.sampled_from(list(RegistryType)),
        config_exists=st.booleans()
    )
    @settings(max_examples=100)
    def test_combined_operation_consistency(
        self, 
        registry_type: RegistryType, 
        config_exists: bool
    ):
        """
        Property: The combined detect_and_validate_context operation should 
        produce results consistent with calling detect_context and 
        validate_context separately.
        
        **Validates: Requirements 3.1, 3.2, 3.4**
        """
        # Setup: create config file if needed
        primary_context = self.detector.detect_context(registry_type)
        
        if config_exists:
            try:
                config_file_path = self.detector.get_config_file_path(primary_context)
                self.create_config_file(config_file_path, "{}")
            except ValueError:
                assume(False)  # Skip if context not supported
        
        # Call methods separately
        detected_context = self.detector.detect_context(registry_type)
        is_valid_separate, error_separate = self.detector.validate_context(detected_context)
        
        # Call combined method
        combined_context, is_valid_combined, error_combined = \
            self.detector.detect_and_validate_context(registry_type)
        
        # Results should be consistent
        assert detected_context == combined_context, \
            f"Context detection inconsistent: {detected_context} != {combined_context}"
        assert is_valid_separate == is_valid_combined, \
            f"Validation result inconsistent: {is_valid_separate} != {is_valid_combined}"
        assert error_separate == error_combined, \
            f"Error message inconsistent: {error_separate} != {error_combined}"
    
    # ========================================================================
    # Property: Context List Completeness
    # ========================================================================
    
    # Feature: library-management, Property: Context List Completeness
    @given(
        contexts_to_create=st.sets(
            st.sampled_from(list(ProjectContext)), 
            min_size=0, 
            max_size=len(ProjectContext)
        )
    )
    @settings(max_examples=100)
    def test_context_list_completeness(self, contexts_to_create: set):
        """
        Property: The list_available_contexts method should return information 
        for all project contexts, with accurate validity status.
        
        **Validates: Requirements 3.4**
        """
        # Create config files for specified contexts
        for context in contexts_to_create:
            try:
                config_file_path = self.detector.get_config_file_path(context)
                self.create_config_file(config_file_path, "{}")
            except ValueError:
                # Skip unsupported contexts
                continue
        
        # Get context list
        context_list = self.detector.list_available_contexts()
        
        # Property 1: Should include all project contexts
        expected_contexts = {ctx.value for ctx in ProjectContext}
        actual_contexts = set(context_list.keys())
        assert expected_contexts == actual_contexts, \
            f"Missing contexts: {expected_contexts - actual_contexts}"
        
        # Property 2: Validity should match actual file existence
        for context in ProjectContext:
            context_name = context.value
            context_info = context_list[context_name]
            
            # Check if validation matches actual file existence
            is_valid_reported = context_info['valid']
            is_valid_actual, _ = self.detector.validate_context(context)
            
            assert is_valid_reported == is_valid_actual, \
                f"Context {context_name} validity mismatch: " \
                f"reported={is_valid_reported}, actual={is_valid_actual}"
            
            # Property 3: Config file path should be present
            assert 'config_file' in context_info, \
                f"Context {context_name} should have config_file field"
            
            # Property 4: Error field should be present iff context is invalid
            has_error = 'error' in context_info
            if is_valid_reported:
                assert not has_error, \
                    f"Valid context {context_name} should not have error field"
            else:
                assert has_error, \
                    f"Invalid context {context_name} should have error field"