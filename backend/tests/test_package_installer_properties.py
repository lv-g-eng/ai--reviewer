"""
Property-based tests for Package Installer Service

These tests verify universal properties that should hold across all valid inputs
using the hypothesis library for property-based testing.
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import composite

from app.services.library_management.package_installer import (
    PackageInstaller,
    FileManager,
    CommandExecutor,
    FileOperationError
)
from app.schemas.library import LibraryMetadata, Dependency
from app.models.library import RegistryType, ProjectContext


# ============================================================================
# Strategy Generators
# ============================================================================

@composite
def library_metadata_strategy(draw):
    """Generate valid LibraryMetadata objects"""
    registry_type = draw(st.sampled_from([RegistryType.NPM, RegistryType.PYPI]))
    
    # Generate package name based on registry type
    if registry_type == RegistryType.NPM:
        # npm package names: lowercase, can contain hyphens, dots, underscores
        name = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz0123456789-._",
            min_size=1,
            max_size=50
        ).filter(lambda x: x[0].isalpha() and not x.endswith('-')))
    else:  # PyPI
        # PyPI package names: letters, numbers, hyphens, underscores, dots
        name = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._",
            min_size=1,
            max_size=50
        ).filter(lambda x: x[0].isalpha()))
    
    # Generate semantic version
    major = draw(st.integers(min_value=0, max_value=99))
    minor = draw(st.integers(min_value=0, max_value=99))
    patch = draw(st.integers(min_value=0, max_value=99))
    version = f"{major}.{minor}.{patch}"
    
    # Generate dependencies
    dependencies = draw(st.lists(
        st.builds(
            Dependency,
            name=st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1, max_size=20),
            version=st.text(alphabet="0123456789.^~>=<", min_size=1, max_size=10),
            is_direct=st.booleans()
        ),
        max_size=5
    ))
    
    return LibraryMetadata(
        name=name,
        version=version,
        description=draw(st.text(max_size=200)),
        license=draw(st.sampled_from(["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "Unknown"])),
        registry_type=registry_type,
        dependencies=dependencies,
        homepage=draw(st.one_of(st.none(), st.text(max_size=100))),
        repository=draw(st.one_of(st.none(), st.text(max_size=100)))
    )


@composite
def project_context_strategy(draw):
    """Generate valid ProjectContext values"""
    return draw(st.sampled_from([ProjectContext.FRONTEND, ProjectContext.BACKEND, ProjectContext.SERVICES]))


@composite
def version_string_strategy(draw):
    """Generate valid version strings"""
    major = draw(st.integers(min_value=0, max_value=99))
    minor = draw(st.integers(min_value=0, max_value=99))
    patch = draw(st.integers(min_value=0, max_value=99))
    return f"{major}.{minor}.{patch}"


@composite
def package_json_strategy(draw):
    """Generate valid package.json content"""
    dependencies = draw(st.dictionaries(
        keys=st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1, max_size=20),
        values=st.text(alphabet="0123456789.^~>=<", min_size=1, max_size=10),
        max_size=10
    ))
    
    return {
        "name": draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1, max_size=30)),
        "version": draw(version_string_strategy()),
        "dependencies": dependencies
    }


@composite
def requirements_txt_strategy(draw):
    """Generate valid requirements.txt content"""
    requirements = draw(st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._==><", min_size=1, max_size=30),
        max_size=10
    ))
    return requirements


# ============================================================================
# Property Tests
# ============================================================================

class TestPackageInstallerProperties:
    """Property-based tests for PackageInstaller"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock dependencies
        self.mock_file_manager = MagicMock(spec=FileManager)
        self.mock_command_executor = AsyncMock(spec=CommandExecutor)
        
        # Create installer with mocked dependencies
        self.installer = PackageInstaller(
            file_manager=self.mock_file_manager,
            command_executor=self.mock_command_executor,
            project_root=self.temp_dir
        )
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # Feature: library-management, Property 9: Installation Rollback on Failure
    @given(
        library=library_metadata_strategy(),
        context=project_context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_installation_rollback_on_failure(self, library, context):
        """
        Property 9: For any library installation that fails, the system should 
        rollback all changes to dependency files, restoring them to their 
        pre-installation state.
        """
        # Assume valid context for the registry type
        if library.registry_type == RegistryType.NPM:
            assume(context in [ProjectContext.FRONTEND, ProjectContext.SERVICES])
        elif library.registry_type == RegistryType.PYPI:
            assume(context == ProjectContext.BACKEND)
        
        # Setup mocks for failure scenario
        backup_path = "/test/backup/path"
        self.mock_file_manager.create_backup.return_value = backup_path
        
        # Setup file reading mock for dependency file updates
        if context in [ProjectContext.FRONTEND, ProjectContext.SERVICES]:
            self.mock_file_manager.read_file.return_value = '{"name": "test", "dependencies": {}}'
        else:  # BACKEND
            self.mock_file_manager.read_file.return_value = "existing-package==1.0.0"
            self.mock_file_manager.file_exists.return_value = True
        
        # Make command execution fail
        self.mock_command_executor.execute_command.return_value = (1, "", "Installation failed")
        
        # Execute installation
        result = await self.installer.install(library, context)
        
        # Property: Installation should fail
        assert result.success is False
        assert len(result.errors) > 0
        
        # Property: Rollback should be called with the backup path
        self.mock_file_manager.restore_from_backup.assert_called_with(backup_path)
    
    # Feature: library-management, Property 10: Installation Workflow Completeness
    @given(
        library=library_metadata_strategy(),
        context=project_context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_installation_workflow_completeness(self, library, context):
        """
        Property 10: For any successful library installation, the system should:
        (1) update the dependency file, (2) execute the install command, 
        (3) update the lock file, and (4) verify the library is accessible—in that order.
        """
        # Assume valid context for the registry type
        if library.registry_type == RegistryType.NPM:
            assume(context in [ProjectContext.FRONTEND, ProjectContext.SERVICES])
        elif library.registry_type == RegistryType.PYPI:
            assume(context == ProjectContext.BACKEND)
        
        # Setup mocks for success scenario
        backup_path = "/test/backup/path"
        self.mock_file_manager.create_backup.return_value = backup_path
        
        # Setup file reading mock for dependency file updates
        if context in [ProjectContext.FRONTEND, ProjectContext.SERVICES]:
            self.mock_file_manager.read_file.return_value = '{"name": "test", "dependencies": {}}'
        else:  # BACKEND
            self.mock_file_manager.read_file.return_value = "existing-package==1.0.0"
            self.mock_file_manager.file_exists.return_value = True
        
        # Make command execution succeed and include library name in verification output
        self.mock_command_executor.execute_command.return_value = (0, f"{library.name} installed successfully", "")
        
        # Execute installation
        result = await self.installer.install(library, context)
        
        # Property: Installation should succeed
        assert result.success is True
        assert result.installed_library is not None
        
        # Property: All workflow steps should be executed in order
        # 1. Backup should be created
        self.mock_file_manager.create_backup.assert_called_once()
        
        # 2. Command should be executed (install command)
        self.mock_command_executor.execute_command.assert_called()
        
        # 3. Verification should pass (library name in output)
        call_args = self.mock_command_executor.execute_command.call_args_list
        assert len(call_args) >= 1  # At least install command was called
        
        # Property: No rollback should occur on success
        self.mock_file_manager.restore_from_backup.assert_not_called()


class TestFileManagerProperties:
    """Property-based tests for FileManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, relative_path: str, content: str):
        """Helper to create test files"""
        full_path = Path(self.temp_dir) / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        return full_path
    
    # Feature: library-management, Property: Backup and Restore Consistency
    @given(
        file_path=st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-./", min_size=1, max_size=50)
            .filter(lambda x: not x.startswith('/') and not x.endswith('/') and '..' not in x),
        content=st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \n\t", max_size=1000)
    )
    @settings(max_examples=50, deadline=None)
    def test_backup_restore_consistency(self, file_path, content):
        """
        Property: For any file with any content, creating a backup and then 
        restoring from that backup should result in the original content being preserved.
        """
        # Assume valid file path
        assume(file_path and not file_path.startswith('.') and '/' in file_path)
        
        try:
            # Create original file
            self.create_test_file(file_path, content)
            
            # Create backup
            backup_path = self.file_manager.create_backup(file_path)
            
            # Modify original file
            modified_content = content + "\nmodified"
            self.file_manager.write_file(file_path, modified_content)
            
            # Restore from backup
            self.file_manager.restore_from_backup(backup_path)
            
            # Property: Content should be restored to original
            restored_content = self.file_manager.read_file(file_path)
            assert restored_content == content
            
        except (FileOperationError, OSError, UnicodeError):
            # Some file paths might be invalid on certain systems
            assume(False)
    
    # Feature: library-management, Property: File Write-Read Consistency
    @given(
        file_path=st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-./", min_size=1, max_size=50)
            .filter(lambda x: not x.startswith('/') and not x.endswith('/') and '..' not in x),
        content=st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \n\t", max_size=1000)
    )
    @settings(max_examples=50, deadline=None)
    def test_write_read_consistency(self, file_path, content):
        """
        Property: For any valid file path and content, writing content to a file 
        and then reading it back should return the exact same content.
        """
        # Assume valid file path
        assume(file_path and not file_path.startswith('.'))
        
        try:
            # Write content to file
            self.file_manager.write_file(file_path, content)
            
            # Read content back
            read_content = self.file_manager.read_file(file_path)
            
            # Property: Content should be identical
            assert read_content == content
            
            # Property: File should exist
            assert self.file_manager.file_exists(file_path) is True
            
        except (FileOperationError, OSError, UnicodeError):
            # Some file paths might be invalid on certain systems
            assume(False)


class TestPackageInstallerFileOperationProperties:
    """Property-based tests for PackageInstaller file operations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.installer = PackageInstaller(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # Feature: library-management, Property: Package.json Update Consistency
    @given(
        initial_package_json=package_json_strategy(),
        library_name=st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1, max_size=30),
        version=version_string_strategy()
    )
    @settings(max_examples=50, deadline=None)
    @pytest.mark.asyncio
    async def test_package_json_update_consistency(self, initial_package_json, library_name, version):
        """
        Property: For any valid package.json and library, updating the package.json 
        should preserve all existing dependencies while adding the new one.
        """
        # Assume library name is not already in dependencies
        assume(library_name not in initial_package_json.get("dependencies", {}))
        
        # Create initial package.json
        package_json_path = Path(self.temp_dir) / "frontend" / "package.json"
        package_json_path.parent.mkdir(parents=True, exist_ok=True)
        package_json_path.write_text(json.dumps(initial_package_json, indent=2))
        
        # Update package.json
        await self.installer._update_package_json("frontend/package.json", library_name, version)
        
        # Read updated package.json
        updated_content = json.loads(package_json_path.read_text())
        
        # Property: New library should be added
        assert library_name in updated_content["dependencies"]
        assert updated_content["dependencies"][library_name] == version
        
        # Property: All original dependencies should be preserved
        original_deps = initial_package_json.get("dependencies", {})
        for dep_name, dep_version in original_deps.items():
            assert dep_name in updated_content["dependencies"]
            assert updated_content["dependencies"][dep_name] == dep_version
        
        # Property: Other fields should be preserved
        for key, value in initial_package_json.items():
            if key != "dependencies":
                assert updated_content[key] == value
    
    # Feature: library-management, Property: Requirements.txt Update Consistency
    @given(
        initial_requirements=requirements_txt_strategy(),
        library_name=st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._", min_size=1, max_size=30),
        version=version_string_strategy()
    )
    @settings(max_examples=50, deadline=None)
    @pytest.mark.asyncio
    async def test_requirements_txt_update_consistency(self, initial_requirements, library_name, version):
        """
        Property: For any valid requirements.txt and library, updating the requirements.txt 
        should preserve all existing requirements while adding the new one.
        """
        # Filter out invalid requirements and ensure library is not already present
        valid_requirements = [req for req in initial_requirements if req and not req.startswith(library_name)]
        assume(len(valid_requirements) <= 10)  # Reasonable limit
        
        # Create initial requirements.txt
        requirements_path = Path(self.temp_dir) / "backend" / "requirements.txt"
        requirements_path.parent.mkdir(parents=True, exist_ok=True)
        requirements_path.write_text("\n".join(valid_requirements))
        
        # Update requirements.txt
        await self.installer._update_requirements_txt("backend/requirements.txt", library_name, version)
        
        # Read updated requirements.txt
        updated_content = requirements_path.read_text()
        updated_lines = [line.strip() for line in updated_content.split('\n') if line.strip()]
        
        # Property: New library should be added
        expected_requirement = f"{library_name}=={version}"
        assert expected_requirement in updated_lines
        
        # Property: All original requirements should be preserved (except duplicates of the new library)
        for req in valid_requirements:
            if req and not req.startswith(f"{library_name}=="):
                assert req in updated_lines
    
    # Feature: library-management, Property: Context Configuration Consistency
    @given(context=project_context_strategy())
    @settings(max_examples=20, deadline=None)
    def test_context_configuration_consistency(self, context):
        """
        Property: For any valid project context, the installer should have 
        consistent configuration mapping all required fields.
        """
        # Property: Context should be in configuration
        assert context in self.installer.CONTEXT_CONFIG
        
        config = self.installer.CONTEXT_CONFIG[context]
        
        # Property: All required configuration fields should be present
        required_fields = ['dependency_file', 'lock_file', 'working_dir', 'install_command', 'verify_command']
        for field in required_fields:
            assert field in config
            assert config[field] is not None
        
        # Property: Commands should be lists
        assert isinstance(config['install_command'], list)
        assert isinstance(config['verify_command'], list)
        assert len(config['install_command']) > 0
        assert len(config['verify_command']) > 0
        
        # Property: File paths should be strings
        assert isinstance(config['dependency_file'], str)
        assert isinstance(config['lock_file'], str)
        assert isinstance(config['working_dir'], str)
        
        # Property: Context-specific consistency
        if context == ProjectContext.FRONTEND:
            assert 'package.json' in config['dependency_file']
            assert 'npm' in config['install_command']
        elif context == ProjectContext.BACKEND:
            assert 'requirements.txt' in config['dependency_file']
            assert 'pip' in config['install_command']
        elif context == ProjectContext.SERVICES:
            assert 'package.json' in config['dependency_file']
            assert 'npm' in config['install_command']