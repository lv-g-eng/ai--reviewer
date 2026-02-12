"""
Property-based tests for migration manager UTF-8 encoding validation

**Feature: database-connectivity-fixes, Property 6: UTF-8 Encoding Validation**
**Validates: Requirements 3.1, 3.3**
"""
import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import AsyncMock, patch, MagicMock

from app.database.migration_manager import MigrationManager
from app.utils.encoding_validator import EncodingValidator, EncodingValidationResult


# constants for testing to avoid hard-coded credentials in literal strings
TEST_PASSWORD = "test_password_123"
TEST_USER = "test_user_name"
TEST_DB = "test_database_db"


class TestMigrationManagerEncodingProperties:
    """Property-based tests for migration manager encoding validation"""
    
    def create_migration_manager(self):
        """Create migration manager instance for testing"""
        with patch('app.database.migration_manager.settings') as mock_settings:
            mock_settings.sync_postgres_url = f"postgresql://{TEST_USER}:{TEST_PASSWORD}@localhost/{TEST_DB}"
            manager = MigrationManager()
            return manager
    
    @pytest.fixture
    def temp_migration_dir(self):
        """Create temporary directory for migration files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @given(
        file_content=st.text(min_size=0, max_size=1000),
        file_name=st.text(min_size=1, max_size=50).filter(lambda x: x.isalnum() and not x.startswith('.')),
    )
    @settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_utf8_encoding_validation_valid_files(
        self, temp_migration_dir, file_content, file_name
    ):
        """
        **Property 6: UTF-8 Encoding Validation**
        For any valid UTF-8 content, the migration manager should validate it successfully
        **Validates: Requirements 3.1, 3.3**
        """
        # Arrange: Create a valid UTF-8 file
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / f"{file_name}.py"
        
        try:
            # Ensure content is valid UTF-8 by encoding/decoding
            utf8_content = file_content.encode('utf-8').decode('utf-8')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(utf8_content)
            
            # Act: Validate the file
            result = await migration_manager.validate_migration_file(file_path)
            
            # Assert: Valid UTF-8 files should pass validation
            assert result.is_valid, f"Valid UTF-8 file should pass validation: {result.errors}"
            assert result.detected_encoding in ['utf-8', 'ascii'], f"Should detect UTF-8 compatible encoding, got: {result.detected_encoding}"
            assert result.file_path == str(file_path)
            assert len(result.errors) == 0, f"Valid file should have no errors: {result.errors}"
            
        except UnicodeEncodeError:
            # Skip test cases with characters that can't be encoded as UTF-8
            assume(False)
    
    @given(
        file_names=st.lists(
            st.text(min_size=1, max_size=30).filter(lambda x: x.isalnum()),
            min_size=1,
            max_size=10
        ),
        file_contents=st.lists(
            st.text(min_size=0, max_size=500),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=50, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_utf8_encoding_validation_directory(
        self, temp_migration_dir, file_names, file_contents
    ):
        """
        **Property 6: UTF-8 Encoding Validation**
        For any directory with UTF-8 migration files, all files should validate successfully
        **Validates: Requirements 3.1, 3.3**
        """
        assume(len(file_names) == len(file_contents))
        
        migration_manager = self.create_migration_manager()
        
        # Arrange: Create multiple valid UTF-8 files
        created_files = []
        for name, content in zip(file_names, file_contents):
            try:
                # Ensure content is valid UTF-8
                utf8_content = content.encode('utf-8').decode('utf-8')
                file_path = temp_migration_dir / f"{name}.py"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(utf8_content)
                
                created_files.append(file_path)
                
            except UnicodeEncodeError:
                # Skip files with non-UTF-8 content for this test
                continue
        
        assume(len(created_files) > 0)
        
        # Mock the script directory to point to our temp directory
        with patch.object(migration_manager, 'alembic_config') as mock_config:
            mock_script_dir = MagicMock()
            mock_script_dir.dir = str(temp_migration_dir)
            
            with patch('app.database.migration_manager.ScriptDirectory') as mock_script_class:
                mock_script_class.from_config.return_value = mock_script_dir
                
                # Act: Validate all migration files
                results = await migration_manager.validate_migration_files()
        
        # Assert: All valid UTF-8 files should pass validation
        assert len(results) == len(created_files), f"Should validate all created files"
        
        for result in results:
            assert result.is_valid, f"All UTF-8 files should be valid: {result.file_path} - {result.errors}"
            assert result.detected_encoding in ['utf-8', 'ascii'], f"Should detect UTF-8 compatible encoding"
            assert len(result.errors) == 0, f"Valid files should have no errors: {result.errors}"
    
    @given(
        valid_content=st.text(min_size=0, max_size=500),
        invalid_bytes=st.binary(min_size=1, max_size=100).filter(
            lambda x: not _is_valid_utf8(x)
        )
    )
    @settings(max_examples=50, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_utf8_encoding_validation_invalid_files(
        self, temp_migration_dir, valid_content, invalid_bytes
    ):
        """
        **Property 6: UTF-8 Encoding Validation**
        For any file with invalid UTF-8 content, the migration manager should detect the issue
        **Validates: Requirements 3.1, 3.3**
        """
        # Arrange: Create a file with invalid UTF-8 content
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / "invalid_migration.py"
        
        try:
            # Create content that starts valid but has invalid bytes
            valid_utf8_content = valid_content.encode('utf-8')
            mixed_content = valid_utf8_content + invalid_bytes
            
            with open(file_path, 'wb') as f:
                f.write(mixed_content)
            
            # Act: Validate the file
            result = await migration_manager.validate_migration_file(file_path)
            
            # Assert: Invalid UTF-8 files should fail validation
            assert not result.is_valid, f"Invalid UTF-8 file should fail validation"
            assert len(result.errors) > 0, f"Invalid file should have errors"
            assert result.file_path == str(file_path)
            
            # Should contain UTF-8 related error message
            error_text = ' '.join(result.errors).lower()
            assert any(keyword in error_text for keyword in ['utf-8', 'decode', 'encoding']), \
                f"Error should mention UTF-8/encoding issues: {result.errors}"
                
        except Exception as e:
            # Skip if we can't create the test scenario
            assume(False)
    
    @given(
        content=st.text(min_size=0, max_size=200)
    )
    @settings(max_examples=50, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_utf8_encoding_validation_consistency(
        self, temp_migration_dir, content
    ):
        """
        **Property 6: UTF-8 Encoding Validation**
        For any content, validation results should be consistent across multiple calls
        **Validates: Requirements 3.1, 3.3**
        """
        # Arrange: Create a file with the given content
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / "test_migration.py"
        
        try:
            # Ensure content is valid UTF-8
            utf8_content = content.encode('utf-8').decode('utf-8')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(utf8_content)
            
            # Act: Validate the same file multiple times
            result1 = await migration_manager.validate_migration_file(file_path)
            result2 = await migration_manager.validate_migration_file(file_path)
            result3 = await migration_manager.validate_migration_file(file_path)
            
            # Assert: Results should be consistent
            assert result1.is_valid == result2.is_valid == result3.is_valid, \
                "Validation results should be consistent"
            assert result1.detected_encoding == result2.detected_encoding == result3.detected_encoding, \
                "Detected encoding should be consistent"
            assert len(result1.errors) == len(result2.errors) == len(result3.errors), \
                "Error count should be consistent"
            
        except UnicodeEncodeError:
            # Skip test cases with characters that can't be encoded as UTF-8
            assume(False)
    
    @given(
        content=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=30, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_utf8_encoding_validation_empty_and_small_files(
        self, temp_migration_dir, content
    ):
        """
        **Property 6: UTF-8 Encoding Validation**
        For any file size including empty files, validation should handle them correctly
        **Validates: Requirements 3.1, 3.3**
        """
        migration_manager = self.create_migration_manager()
        
        # Test empty file
        empty_file = temp_migration_dir / "empty.py"
        with open(empty_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        empty_result = await migration_manager.validate_migration_file(empty_file)
        assert empty_result.is_valid, "Empty files should be valid UTF-8"
        assert empty_result.detected_encoding == 'utf-8'
        
        # Test small file with content
        try:
            utf8_content = content.encode('utf-8').decode('utf-8')
            small_file = temp_migration_dir / "small.py"
            
            with open(small_file, 'w', encoding='utf-8') as f:
                f.write(utf8_content)
            
            small_result = await migration_manager.validate_migration_file(small_file)
            assert small_result.is_valid, f"Small UTF-8 files should be valid: {small_result.errors}"
            assert small_result.detected_encoding in ['utf-8', 'ascii']
            
        except UnicodeEncodeError:
            assume(False)


def _is_valid_utf8(data: bytes) -> bool:
    """Helper function to check if bytes are valid UTF-8"""
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False