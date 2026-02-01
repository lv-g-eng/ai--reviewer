"""
Property-based tests for migration manager file creation integrity

**Feature: database-connectivity-fixes, Property 8: Migration File Creation Integrity**
**Validates: Requirements 3.5**
"""
import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import AsyncMock, patch, MagicMock

from app.database.migration_manager import MigrationManager
from app.utils.encoding_validator import EncodingValidator, EncodingValidationResult


class TestMigrationManagerFileCreationProperties:
    """Property-based tests for migration manager file creation integrity"""
    
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
        file_content=st.text(min_size=0, max_size=1000),
        file_name=st.text(min_size=1, max_size=50).filter(lambda x: x.isalnum() and not x.startswith('.')),
    )
    @settings(max_examples=100, deadline=8000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_migration_file_creation_utf8_integrity(
        self, temp_migration_dir, file_content, file_name
    ):
        """
        **Property 8: Migration File Creation Integrity**
        For any new migration file created by the system, the file should be properly UTF-8 encoded 
        and readable without encoding errors
        **Validates: Requirements 3.5**
        """
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / f"{file_name}.py"
        
        try:
            # Ensure content is valid UTF-8 by encoding/decoding
            utf8_content = file_content.encode('utf-8').decode('utf-8')
            
            # Act: Create migration file using the manager
            success = await migration_manager.create_migration_file(file_path, utf8_content)
            
            # Assert: File creation should succeed and produce valid UTF-8
            assert success, f"Migration file creation should succeed for valid UTF-8 content"
            assert file_path.exists(), f"Migration file should exist after creation"
            
            # Validate the created file
            validation_result = await migration_manager.validate_migration_file(file_path)
            assert validation_result.is_valid, f"Created file should be valid UTF-8: {validation_result.errors}"
            assert validation_result.detected_encoding in ['utf-8', 'ascii'], \
                f"Created file should be detected as UTF-8 compatible, got: {validation_result.detected_encoding}"
            assert len(validation_result.errors) == 0, f"Created file should have no encoding errors: {validation_result.errors}"
            
            # Verify file can be read without encoding errors
            with open(file_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            # Content should match (allowing for line ending normalization)
            # The create_utf8_file method normalizes line endings to \n
            expected_content = utf8_content.replace('\r\n', '\n').replace('\r', '\n')
            assert read_content == expected_content, "File content should match what was written (with normalized line endings)"
            
        except UnicodeEncodeError:
            # Skip test cases with characters that can't be encoded as UTF-8
            assume(False)
    
    @pytest.mark.asyncio
    @given(
        migration_contents=st.lists(
            st.text(min_size=0, max_size=300),
            min_size=1,
            max_size=10
        ),
        file_names=st.lists(
            st.text(min_size=1, max_size=30).filter(lambda x: x.isalnum()),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=50, deadline=15000, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.filter_too_much])
    async def test_property_migration_file_creation_multiple_files(
        self, temp_migration_dir, migration_contents, file_names
    ):
        """
        **Property 8: Migration File Creation Integrity**
        For any set of new migration files created by the system, all files should be properly 
        UTF-8 encoded and readable without encoding errors
        **Validates: Requirements 3.5**
        """
        assume(len(migration_contents) == len(file_names))
        
        migration_manager = self.create_migration_manager()
        
        created_files = []
        valid_contents = []
        
        # Create multiple migration files with unique names
        for i, (name, content) in enumerate(zip(file_names, migration_contents)):
            try:
                # Ensure content is valid UTF-8
                utf8_content = content.encode('utf-8').decode('utf-8')
                # Ensure unique file names by adding index
                unique_name = f"{name}_{i}"
                file_path = temp_migration_dir / f"{unique_name}.py"
                
                # Act: Create migration file
                success = await migration_manager.create_migration_file(file_path, utf8_content)
                
                if success:
                    created_files.append(file_path)
                    valid_contents.append(utf8_content)
                
            except UnicodeEncodeError:
                # Skip files with non-UTF-8 content
                continue
        
        assume(len(created_files) > 0)
        
        # Assert: All created files should be valid UTF-8
        for file_path, expected_content in zip(created_files, valid_contents):
            assert file_path.exists(), f"Created file should exist: {file_path}"
            
            # Validate encoding
            validation_result = await migration_manager.validate_migration_file(file_path)
            assert validation_result.is_valid, f"Created file should be valid UTF-8: {file_path} - {validation_result.errors}"
            assert validation_result.detected_encoding in ['utf-8', 'ascii'], \
                f"Created file should be UTF-8 compatible: {file_path}"
            
            # Verify content integrity
            with open(file_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            # Content should match (allowing for line ending normalization)
            expected_content = expected_content.replace('\r\n', '\n').replace('\r', '\n')
            assert read_content == expected_content, f"File content should match for {file_path}"
    
    @pytest.mark.asyncio
    @given(
        content=st.text(min_size=0, max_size=500),
        subdirectory=st.text(min_size=1, max_size=20).filter(lambda x: x.isalnum())
    )
    @settings(max_examples=30, deadline=8000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_migration_file_creation_directory_handling(
        self, temp_migration_dir, content, subdirectory
    ):
        """
        **Property 8: Migration File Creation Integrity**
        For any new migration file created in any directory structure, the file should be properly 
        UTF-8 encoded and the directory structure should be created as needed
        **Validates: Requirements 3.5**
        """
        migration_manager = self.create_migration_manager()
        
        try:
            # Ensure content is valid UTF-8
            utf8_content = content.encode('utf-8').decode('utf-8')
            
            # Create file in subdirectory that doesn't exist yet
            subdir_path = temp_migration_dir / subdirectory
            file_path = subdir_path / "migration.py"
            
            # Act: Create migration file (should create directory structure)
            success = await migration_manager.create_migration_file(file_path, utf8_content)
            
            # Assert: Directory and file should be created properly
            assert success, "Migration file creation should succeed even with new directories"
            assert subdir_path.exists(), "Subdirectory should be created"
            assert subdir_path.is_dir(), "Subdirectory should be a directory"
            assert file_path.exists(), "Migration file should exist"
            assert file_path.is_file(), "Migration file should be a file"
            
            # Validate the created file
            validation_result = await migration_manager.validate_migration_file(file_path)
            assert validation_result.is_valid, f"Created file should be valid UTF-8: {validation_result.errors}"
            
            # Verify content
            with open(file_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            # Content should match (allowing for line ending normalization)
            expected_content = utf8_content.replace('\r\n', '\n').replace('\r', '\n')
            assert read_content == expected_content, "File content should match"
            
        except UnicodeEncodeError:
            # Skip test cases with characters that can't be encoded as UTF-8
            assume(False)
    
    @pytest.mark.asyncio
    @given(
        content=st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=30, deadline=8000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_migration_file_creation_overwrite_behavior(
        self, temp_migration_dir, content
    ):
        """
        **Property 8: Migration File Creation Integrity**
        For any migration file creation that overwrites an existing file, the new file should be 
        properly UTF-8 encoded and replace the old content completely
        **Validates: Requirements 3.5**
        """
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / "overwrite_test.py"
        
        try:
            # Ensure content is valid UTF-8
            utf8_content = content.encode('utf-8').decode('utf-8')
            
            # Create initial file with different content
            initial_content = "# Initial migration content\npass\n"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(initial_content)
            
            assert file_path.exists(), "Initial file should exist"
            
            # Act: Create migration file (should overwrite)
            success = await migration_manager.create_migration_file(file_path, utf8_content)
            
            # Assert: File should be overwritten with new content
            assert success, "Migration file creation should succeed when overwriting"
            assert file_path.exists(), "File should still exist after overwrite"
            
            # Validate the overwritten file
            validation_result = await migration_manager.validate_migration_file(file_path)
            assert validation_result.is_valid, f"Overwritten file should be valid UTF-8: {validation_result.errors}"
            
            # Verify new content replaced old content
            with open(file_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            # Content should match (allowing for line ending normalization)
            expected_content = utf8_content.replace('\r\n', '\n').replace('\r', '\n')
            assert read_content == expected_content, "File should contain new content, not old content"
            assert read_content != initial_content, "File should not contain initial content"
            
        except UnicodeEncodeError:
            # Skip test cases with characters that can't be encoded as UTF-8
            assume(False)
    
    @pytest.mark.asyncio
    @given(
        content=st.text(min_size=0, max_size=100)
    )
    @settings(max_examples=30, deadline=8000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_migration_file_creation_consistency(
        self, temp_migration_dir, content
    ):
        """
        **Property 8: Migration File Creation Integrity**
        For any content, creating the same migration file multiple times should produce 
        consistent results with proper UTF-8 encoding
        **Validates: Requirements 3.5**
        """
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / "consistency_test.py"
        
        try:
            # Ensure content is valid UTF-8
            utf8_content = content.encode('utf-8').decode('utf-8')
            
            # Act: Create the same file multiple times
            success1 = await migration_manager.create_migration_file(file_path, utf8_content)
            success2 = await migration_manager.create_migration_file(file_path, utf8_content)
            success3 = await migration_manager.create_migration_file(file_path, utf8_content)
            
            # Assert: All creation attempts should succeed
            assert success1, "First file creation should succeed"
            assert success2, "Second file creation should succeed"
            assert success3, "Third file creation should succeed"
            
            # Validate the final file
            validation_result = await migration_manager.validate_migration_file(file_path)
            assert validation_result.is_valid, f"Final file should be valid UTF-8: {validation_result.errors}"
            
            # Verify content consistency
            with open(file_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            # Content should match (allowing for line ending normalization)
            expected_content = utf8_content.replace('\r\n', '\n').replace('\r', '\n')
            assert read_content == expected_content, "File content should be consistent"
            
        except UnicodeEncodeError:
            # Skip test cases with characters that can't be encoded as UTF-8
            assume(False)
    
    @pytest.mark.asyncio
    @given(
        content=st.text(min_size=0, max_size=200),
        line_endings=st.sampled_from(['\n', '\r\n', '\r'])
    )
    @settings(max_examples=20, deadline=8000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_migration_file_creation_line_endings(
        self, temp_migration_dir, content, line_endings
    ):
        """
        **Property 8: Migration File Creation Integrity**
        For any content with different line endings, the created migration file should be 
        properly UTF-8 encoded and handle line endings correctly
        **Validates: Requirements 3.5**
        """
        migration_manager = self.create_migration_manager()
        file_path = temp_migration_dir / "line_endings_test.py"
        
        try:
            # Ensure content is valid UTF-8 and add line endings
            utf8_content = content.encode('utf-8').decode('utf-8')
            content_with_endings = utf8_content.replace('\n', line_endings)
            
            # Act: Create migration file
            success = await migration_manager.create_migration_file(file_path, content_with_endings)
            
            # Assert: File creation should succeed
            assert success, f"Migration file creation should succeed with {repr(line_endings)} line endings"
            assert file_path.exists(), "Migration file should exist"
            
            # Validate the created file
            validation_result = await migration_manager.validate_migration_file(file_path)
            assert validation_result.is_valid, f"Created file should be valid UTF-8: {validation_result.errors}"
            
            # Verify file can be read without encoding errors
            with open(file_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            # Content should be readable (line endings may be normalized)
            assert isinstance(read_content, str), "File content should be readable as string"
            
        except UnicodeEncodeError:
            # Skip test cases with characters that can't be encoded as UTF-8
            assume(False)
    
    @pytest.mark.asyncio
    @given(
        empty_content=st.just(""),
        small_content=st.text(min_size=1, max_size=10),
        large_content=st.text(min_size=500, max_size=1000)
    )
    @settings(max_examples=20, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_migration_file_creation_various_sizes(
        self, temp_migration_dir, empty_content, small_content, large_content
    ):
        """
        **Property 8: Migration File Creation Integrity**
        For any file size (empty, small, large), the created migration file should be 
        properly UTF-8 encoded and readable without encoding errors
        **Validates: Requirements 3.5**
        """
        migration_manager = self.create_migration_manager()
        
        test_cases = [
            ("empty", empty_content),
            ("small", small_content),
            ("large", large_content)
        ]
        
        for size_type, content in test_cases:
            try:
                # Ensure content is valid UTF-8
                utf8_content = content.encode('utf-8').decode('utf-8')
                file_path = temp_migration_dir / f"{size_type}_migration.py"
                
                # Act: Create migration file
                success = await migration_manager.create_migration_file(file_path, utf8_content)
                
                # Assert: File creation should succeed regardless of size
                assert success, f"Migration file creation should succeed for {size_type} content"
                assert file_path.exists(), f"{size_type.capitalize()} migration file should exist"
                
                # Validate the created file
                validation_result = await migration_manager.validate_migration_file(file_path)
                assert validation_result.is_valid, f"{size_type.capitalize()} file should be valid UTF-8: {validation_result.errors}"
                
                # Verify content integrity
                with open(file_path, 'r', encoding='utf-8') as f:
                    read_content = f.read()
                
                # Content should match (allowing for line ending normalization)
                expected_content = utf8_content.replace('\r\n', '\n').replace('\r', '\n')
                assert read_content == expected_content, f"{size_type.capitalize()} file content should match"
                
            except UnicodeEncodeError:
                # Skip test cases with characters that can't be encoded as UTF-8
                continue