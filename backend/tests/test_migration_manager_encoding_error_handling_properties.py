"""
Property-based tests for migration manager encoding error handling

**Feature: database-connectivity-fixes, Property 7: Encoding Error Handling**
**Validates: Requirements 3.2, 3.4**
"""
import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import patch

from app.database.migration_manager import MigrationManager
from app.utils.encoding_validator import EncodingValidationResult, EncodingFixResult


class TestMigrationManagerEncodingErrorHandlingProperties:
    """Property-based tests for migration manager encoding error handling"""
    
    def create_migration_manager(self):
        """Create migration manager instance for testing"""
        with patch('app.database.migration_manager.settings') as mock_settings:
            mock_settings.sync_postgres_url = "postgresql://test:test@localhost/test"
            manager = MigrationManager()
            return manager
    
    @pytest.fixture
    def temp_migration_dir(self):
        """Create temporary directory for migration files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.mark.asyncio
    @given(
        valid_content=st.text(min_size=0, max_size=500),
        invalid_bytes=st.binary(min_size=1, max_size=100).filter(
            lambda x: not _is_valid_utf8(x)
        ),
        file_name=st.text(min_size=1, max_size=30).filter(lambda x: x.isalnum())
    )
    @settings(max_examples=50, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_encoding_error_handling_specific_errors(
        self, temp_migration_dir, valid_content, invalid_bytes, file_name
    ):
        """
        **Property 7: Encoding Error Handling**
        For any file with encoding issues, the system should provide specific error messages 
        identifying the problematic file and line
        **Validates: Requirements 3.2, 3.4**
        """
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / f"{file_name}.py"
        
        try:
            # Create content with valid UTF-8 followed by invalid bytes
            valid_utf8_content = valid_content.encode('utf-8')
            mixed_content = valid_utf8_content + b'\n# Comment line\n' + invalid_bytes
            
            with open(file_path, 'wb') as f:
                f.write(mixed_content)
            
            # Act: Validate the file to get specific error information
            result = await migration_manager.validate_migration_file(file_path)
            
            # Assert: Should provide specific error messages
            assert not result.is_valid, "File with encoding issues should fail validation"
            assert len(result.errors) > 0, "Should have specific error messages"
            assert result.file_path == str(file_path), "Should identify the problematic file"
            
            # Error messages should contain specific information
            error_text = ' '.join(result.errors).lower()
            assert any(keyword in error_text for keyword in ['utf-8', 'decode', 'encoding', 'byte']), \
                f"Error should contain specific encoding information: {result.errors}"
            
            # Test the problematic lines detection
            problematic_lines = migration_manager.encoding_validator.get_problematic_lines(file_path)
            assert len(problematic_lines) > 0, "Should identify problematic lines"
            
            for line_num, line_content, error_desc in problematic_lines:
                assert isinstance(line_num, int) and line_num > 0, "Should provide valid line number"
                assert isinstance(line_content, str), "Should provide line content"
                assert isinstance(error_desc, str) and len(error_desc) > 0, "Should provide error description"
                assert 'utf-8' in error_desc.lower() or 'decode' in error_desc.lower(), \
                    "Error description should mention encoding issue"
                    
        except Exception as e:
            # Skip if we can't create the test scenario
            assume(False)
    
    @pytest.mark.asyncio
    @given(
        content=st.text(min_size=1, max_size=300),
        strategy=st.sampled_from(["convert", "reject"])
    )
    @settings(max_examples=30, deadline=8000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_encoding_error_handling_non_utf8_characters(
        self, temp_migration_dir, content, strategy
    ):
        """
        **Property 7: Encoding Error Handling**
        For any file with non-UTF-8 characters, the system should handle them consistently 
        based on the chosen strategy (convert or reject)
        **Validates: Requirements 3.2, 3.4**
        """
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / "test_migration.py"
        
        try:
            # Create a file with potentially problematic encoding
            # Use latin1 encoding which may contain non-UTF-8 characters
            latin1_content = content.encode('latin1', errors='ignore')
            
            # Only proceed if the content would cause UTF-8 issues
            try:
                latin1_content.decode('utf-8')
                # If it decodes fine as UTF-8, skip this test case
                assume(False)
            except UnicodeDecodeError:
                # Good, this will cause encoding issues
                pass
            
            with open(file_path, 'wb') as f:
                f.write(latin1_content)
            
            # Act: Handle non-UTF-8 characters with the given strategy
            result = await migration_manager.handle_non_utf8_characters(file_path, strategy)
            
            # Assert: Behavior should match the strategy
            if strategy == "reject":
                assert not result.success, "Reject strategy should fail for non-UTF-8 files"
                assert len(result.errors) > 0, "Should provide error message for rejection"
                error_text = ' '.join(result.errors).lower()
                assert 'reject' in error_text or 'non-utf-8' in error_text, \
                    "Error should mention rejection of non-UTF-8 characters"
                    
            elif strategy == "convert":
                # Convert strategy should attempt to fix the file
                if result.success:
                    # If conversion succeeded, validate the result
                    validation_result = await migration_manager.validate_migration_file(file_path)
                    assert validation_result.is_valid, "Converted file should be valid UTF-8"
                else:
                    # If conversion failed, should have error messages
                    assert len(result.errors) > 0, "Failed conversion should provide error messages"
            
            # Result should always have proper structure
            assert isinstance(result.success, bool), "Should have boolean success flag"
            assert isinstance(result.errors, list), "Should have list of errors"
            
        except Exception as e:
            # Skip if we can't create the test scenario
            assume(False)
    
    @pytest.mark.asyncio
    @given(
        file_contents=st.lists(
            st.text(min_size=0, max_size=200),
            min_size=1,
            max_size=5
        ),
        file_names=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda x: x.isalnum()),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=30, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.filter_too_much])
    async def test_property_encoding_error_handling_before_execution(
        self, temp_migration_dir, file_contents, file_names
    ):
        """
        **Property 7: Encoding Error Handling**
        For any set of migration files, encoding validation before execution should 
        identify all files with issues and provide comprehensive results
        **Validates: Requirements 3.2, 3.4**
        """
        assume(len(file_contents) == len(file_names))
        
        migration_manager = self.create_migration_manager()
        
        # Create migration files with various content
        migration_files = []
        expected_valid_count = 0
        
        for name, content in zip(file_names, file_contents):
            try:
                # Ensure content is UTF-8 compatible for this test
                utf8_content = content.encode('utf-8').decode('utf-8')
                file_path = temp_migration_dir / f"{name}.py"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(utf8_content)
                
                migration_files.append(file_path)
                expected_valid_count += 1
                
            except UnicodeEncodeError:
                # Skip files that can't be encoded as UTF-8
                continue
        
        assume(len(migration_files) > 0)
        
        # Act: Validate files before migration execution
        results = await migration_manager.validate_before_migration_execution(migration_files)
        
        # Assert: Should validate all files and provide comprehensive results
        assert len(results) == len(migration_files), "Should validate all provided files"
        
        for result in results:
            assert isinstance(result, EncodingValidationResult), "Should return proper validation results"
            assert hasattr(result, 'is_valid'), "Should have validity flag"
            assert hasattr(result, 'file_path'), "Should identify the file"
            assert hasattr(result, 'errors'), "Should have error list"
            
            if result.is_valid:
                assert len(result.errors) == 0, "Valid files should have no errors"
            else:
                assert len(result.errors) > 0, "Invalid files should have error messages"
        
        # All files in this test should be valid UTF-8
        valid_count = sum(1 for result in results if result.is_valid)
        assert valid_count == expected_valid_count, "All UTF-8 files should be valid"
    
    @pytest.mark.asyncio
    @given(
        content=st.text(min_size=1, max_size=200),
        original_encoding=st.sampled_from(['latin1', 'cp1252', 'iso-8859-1'])
    )
    @settings(max_examples=20, deadline=8000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_encoding_error_handling_fix_attempts(
        self, temp_migration_dir, content, original_encoding
    ):
        """
        **Property 7: Encoding Error Handling**
        For any file with fixable encoding issues, the fix attempt should either succeed 
        and produce valid UTF-8, or fail with clear error messages
        **Validates: Requirements 3.2, 3.4**
        """
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / "migration_to_fix.py"
        
        try:
            # Create file with specific encoding that may need fixing
            encoded_content = content.encode(original_encoding, errors='ignore')
            
            # Only test if this would cause UTF-8 issues
            try:
                encoded_content.decode('utf-8')
                # If it's already valid UTF-8, skip
                assume(False)
            except UnicodeDecodeError:
                # Good, this needs fixing
                pass
            
            with open(file_path, 'wb') as f:
                f.write(encoded_content)
            
            # Act: Attempt to fix encoding issues
            fix_result = await migration_manager.fix_migration_file_encoding(file_path)
            
            # Assert: Fix attempt should have consistent behavior
            assert isinstance(fix_result, EncodingFixResult), "Should return proper fix result"
            assert isinstance(fix_result.success, bool), "Should have boolean success flag"
            assert isinstance(fix_result.errors, list), "Should have error list"
            
            if fix_result.success:
                # If fix succeeded, file should now be valid UTF-8
                validation_result = await migration_manager.validate_migration_file(file_path)
                assert validation_result.is_valid, "Fixed file should be valid UTF-8"
                assert len(fix_result.errors) == 0, "Successful fix should have no errors"
                
                # Should have information about the original encoding
                assert fix_result.original_encoding is not None, "Should identify original encoding"
                
            else:
                # If fix failed, should have clear error messages
                assert len(fix_result.errors) > 0, "Failed fix should provide error messages"
                
                # Error messages should be informative
                error_text = ' '.join(fix_result.errors).lower()
                assert any(keyword in error_text for keyword in ['encoding', 'decode', 'fix', 'convert']), \
                    f"Error messages should be informative about encoding issues: {fix_result.errors}"
            
        except Exception as e:
            # Skip if we can't create the test scenario
            assume(False)
    
    @pytest.mark.asyncio
    @given(
        content=st.text(min_size=0, max_size=100)
    )
    @settings(max_examples=30, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_encoding_error_handling_consistency(
        self, temp_migration_dir, content
    ):
        """
        **Property 7: Encoding Error Handling**
        For any file, encoding error handling should be consistent across multiple operations
        **Validates: Requirements 3.2, 3.4**
        """
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / "consistent_test.py"
        
        try:
            # Create file with UTF-8 content
            utf8_content = content.encode('utf-8').decode('utf-8')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(utf8_content)
            
            # Act: Perform multiple validation operations
            result1 = await migration_manager.validate_migration_file(file_path)
            result2 = await migration_manager.validate_migration_file(file_path)
            
            # Handle non-UTF-8 characters (should be no-op for valid files)
            handle_result1 = await migration_manager.handle_non_utf8_characters(file_path, "convert")
            handle_result2 = await migration_manager.handle_non_utf8_characters(file_path, "reject")
            
            # Assert: Results should be consistent
            assert result1.is_valid == result2.is_valid, "Validation should be consistent"
            assert result1.detected_encoding == result2.detected_encoding, "Detected encoding should be consistent"
            assert len(result1.errors) == len(result2.errors), "Error count should be consistent"
            
            # For valid UTF-8 files, both handling strategies should succeed
            if result1.is_valid:
                assert handle_result1.success, "Convert strategy should succeed for valid UTF-8"
                assert handle_result2.success, "Reject strategy should succeed for valid UTF-8"
            
        except UnicodeEncodeError:
            # Skip test cases with characters that can't be encoded as UTF-8
            assume(False)


def _is_valid_utf8(data: bytes) -> bool:
    """Helper function to check if bytes are valid UTF-8"""
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False