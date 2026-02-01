"""
Unit tests for Package Installer Service
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.library_management.package_installer import (
    PackageInstaller,
    FileManager,
    CommandExecutor,
    PackageInstallerError,
    FileOperationError,
    CommandExecutionError,
    InstallationVerificationError
)
from app.schemas.library import LibraryMetadata, Dependency, InstallationResult
from app.models.library import RegistryType, ProjectContext


class TestFileManager:
    """Test cases for FileManager utility class"""
    
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
    
    def test_create_backup_success(self):
        """Test successful backup creation"""
        # Create test file
        test_content = "test content"
        self.create_test_file("test.txt", test_content)
        
        # Create backup
        backup_path = self.file_manager.create_backup("test.txt")
        
        # Verify backup exists and has correct content
        assert Path(backup_path).exists()
        assert Path(backup_path).read_text() == test_content
        assert "backup_" in backup_path
    
    def test_create_backup_nonexistent_file(self):
        """Test backup creation for nonexistent file"""
        with pytest.raises(FileOperationError, match="Source file does not exist"):
            self.file_manager.create_backup("nonexistent.txt")
    
    def test_restore_from_backup_success(self):
        """Test successful restore from backup"""
        # Create original file
        original_content = "original content"
        self.create_test_file("test.txt", original_content)
        
        # Create backup
        backup_path = self.file_manager.create_backup("test.txt")
        
        # Modify original file
        modified_content = "modified content"
        self.file_manager.write_file("test.txt", modified_content)
        
        # Restore from backup
        self.file_manager.restore_from_backup(backup_path)
        
        # Verify restoration
        restored_content = self.file_manager.read_file("test.txt")
        assert restored_content == original_content
    
    def test_restore_from_backup_nonexistent_backup(self):
        """Test restore from nonexistent backup"""
        with pytest.raises(FileOperationError, match="Backup file does not exist"):
            self.file_manager.restore_from_backup("nonexistent_backup.txt")
    
    def test_read_file_success(self):
        """Test successful file reading"""
        content = "test file content"
        self.create_test_file("test.txt", content)
        
        result = self.file_manager.read_file("test.txt")
        assert result == content
    
    def test_read_file_nonexistent(self):
        """Test reading nonexistent file"""
        with pytest.raises(FileOperationError, match="File does not exist"):
            self.file_manager.read_file("nonexistent.txt")
    
    def test_write_file_success(self):
        """Test successful file writing"""
        content = "new file content"
        self.file_manager.write_file("new_file.txt", content)
        
        # Verify file was created with correct content
        full_path = Path(self.temp_dir) / "new_file.txt"
        assert full_path.exists()
        assert full_path.read_text() == content
    
    def test_write_file_creates_directories(self):
        """Test that write_file creates parent directories"""
        content = "nested file content"
        self.file_manager.write_file("nested/dir/file.txt", content)
        
        # Verify file was created in nested directory
        full_path = Path(self.temp_dir) / "nested/dir/file.txt"
        assert full_path.exists()
        assert full_path.read_text() == content
    
    def test_file_exists_true(self):
        """Test file_exists returns True for existing file"""
        self.create_test_file("existing.txt", "content")
        assert self.file_manager.file_exists("existing.txt") is True
    
    def test_file_exists_false(self):
        """Test file_exists returns False for nonexistent file"""
        assert self.file_manager.file_exists("nonexistent.txt") is False


class TestCommandExecutor:
    """Test cases for CommandExecutor utility class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.command_executor = CommandExecutor(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Test successful command execution"""
        # Create working directory
        working_dir = Path(self.temp_dir) / "work"
        working_dir.mkdir()
        
        # Use platform-appropriate command
        import sys
        if sys.platform == "win32":
            command = ["cmd", "/c", "echo hello world"]
        else:
            command = ["echo", "hello world"]
        
        # Execute simple command
        return_code, stdout, stderr = await self.command_executor.execute_command(
            command,
            "work"
        )
        
        assert return_code == 0
        assert "hello world" in stdout
    
    @pytest.mark.asyncio
    async def test_execute_command_failure(self):
        """Test command execution failure"""
        # Create working directory
        working_dir = Path(self.temp_dir) / "work"
        working_dir.mkdir()
        
        # Use platform-appropriate command that fails
        import sys
        if sys.platform == "win32":
            command = ["cmd", "/c", "exit 1"]
        else:
            command = ["false"]
        
        # Execute command that should fail
        return_code, stdout, stderr = await self.command_executor.execute_command(
            command,
            "work"
        )
        
        assert return_code == 1
    
    @pytest.mark.asyncio
    async def test_execute_command_nonexistent_directory(self):
        """Test command execution with nonexistent working directory"""
        with pytest.raises(CommandExecutionError, match="Working directory does not exist"):
            await self.command_executor.execute_command(
                ["echo", "test"],
                "nonexistent_dir"
            )
    
    @pytest.mark.asyncio
    async def test_execute_command_timeout(self):
        """Test command execution timeout"""
        # Create working directory
        working_dir = Path(self.temp_dir) / "work"
        working_dir.mkdir()
        
        # Use platform-appropriate command that sleeps
        import sys
        if sys.platform == "win32":
            # Use ping command with a long delay as a workaround for Windows
            command = ["ping", "127.0.0.1", "-n", "20"]
        else:
            command = ["sleep", "10"]
        
        # Execute command that should timeout
        with pytest.raises(CommandExecutionError, match="Command timed out"):
            await self.command_executor.execute_command(
                command,
                "work",
                timeout=0.1  # Very short timeout
            )


class TestPackageInstaller:
    """Test cases for PackageInstaller service"""
    
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
        
        # Ensure CONTEXT_CONFIG is properly set (in case it gets modified)
        self.installer.CONTEXT_CONFIG = {
            ProjectContext.FRONTEND: {
                'dependency_file': 'frontend/package.json',
                'lock_file': 'frontend/package-lock.json',
                'working_dir': 'frontend',
                'install_command': ['npm', 'install'],
                'verify_command': ['npm', 'list', '--depth=0']
            },
            ProjectContext.BACKEND: {
                'dependency_file': 'backend/requirements.txt',
                'lock_file': 'backend/poetry.lock',
                'working_dir': 'backend',
                'install_command': ['pip', 'install', '-r', 'requirements.txt'],
                'verify_command': ['pip', 'list']
            },
            ProjectContext.SERVICES: {
                'dependency_file': 'services/package.json',
                'lock_file': 'services/package-lock.json',
                'working_dir': 'services',
                'install_command': ['npm', 'install'],
                'verify_command': ['npm', 'list', '--depth=0']
            }
        }
        
        # Create test library metadata
        self.test_library = LibraryMetadata(
            name="test-library",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="dep1", version="^2.0.0"),
                Dependency(name="dep2", version="~1.5.0")
            ],
            homepage="https://example.com",
            repository="https://github.com/example/test-library"
        )
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_install_npm_package_success(self):
        """Test successful npm package installation"""
        # Setup mocks
        self.mock_file_manager.create_backup.return_value = "/path/to/backup"
        self.mock_file_manager.read_file.return_value = '{"name": "test", "dependencies": {}}'
        self.mock_command_executor.execute_command.return_value = (0, "test-library@1.0.0 success output", "")
        
        # Execute installation
        result = await self.installer.install(
            self.test_library,
            ProjectContext.FRONTEND
        )
        
        # Verify result
        assert result.success is True
        assert result.installed_library is not None
        assert result.installed_library.name == "test-library"
        assert result.installed_library.version == "1.0.0"
        assert result.installed_library.project_context == ProjectContext.FRONTEND
        assert result.errors == []
        
        # Verify method calls
        self.mock_file_manager.create_backup.assert_called_once_with("frontend/package.json")
        # Should be called twice: once for install, once for verification
        assert self.mock_command_executor.execute_command.call_count == 2
    
    @pytest.mark.asyncio
    async def test_install_pypi_package_success(self):
        """Test successful PyPI package installation"""
        # Create PyPI library
        pypi_library = LibraryMetadata(
            name="django",
            version="4.2.0",
            description="Django web framework",
            license="BSD",
            registry_type=RegistryType.PYPI,
            dependencies=[]
        )
        
        # Setup mocks
        self.mock_file_manager.create_backup.return_value = "/path/to/backup"
        self.mock_file_manager.file_exists.return_value = True
        self.mock_file_manager.read_file.return_value = "existing-package==1.0.0"
        self.mock_command_executor.execute_command.return_value = (0, "django 4.2.0", "")
        
        # Execute installation
        result = await self.installer.install(
            pypi_library,
            ProjectContext.BACKEND
        )
        
        # Verify result
        assert result.success is True
        assert result.installed_library.name == "django"
        assert result.installed_library.project_context == ProjectContext.BACKEND
        
        # Verify method calls
        self.mock_file_manager.create_backup.assert_called_once_with("backend/requirements.txt")
        # Should be called twice: once for install, once for verification
        assert self.mock_command_executor.execute_command.call_count == 2
    
    @pytest.mark.asyncio
    async def test_install_with_version_override(self):
        """Test installation with version override"""
        # Setup mocks
        self.mock_file_manager.create_backup.return_value = "/path/to/backup"
        self.mock_file_manager.read_file.return_value = '{"name": "test", "dependencies": {}}'
        self.mock_command_executor.execute_command.return_value = (0, "test-library@2.0.0 success", "")
        
        # Execute installation with version override
        result = await self.installer.install(
            self.test_library,
            ProjectContext.FRONTEND,
            version="2.0.0"
        )
        
        # Verify version override was used
        assert result.success is True
        assert result.installed_library.version == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_install_unsupported_context(self):
        """Test installation with unsupported project context"""
        # Mock an unsupported context by temporarily removing it
        original_config = self.installer.CONTEXT_CONFIG.copy()
        del self.installer.CONTEXT_CONFIG[ProjectContext.FRONTEND]
        
        try:
            result = await self.installer.install(
                self.test_library,
                ProjectContext.FRONTEND
            )
            
            # Verify failure
            assert result.success is False
            assert "Unsupported project context" in result.errors[0]
        finally:
            # Restore original config
            self.installer.CONTEXT_CONFIG = original_config
    
    @pytest.mark.asyncio
    async def test_install_backup_failure(self):
        """Test installation failure during backup creation"""
        # Setup mock to fail on backup
        self.mock_file_manager.create_backup.side_effect = FileOperationError("Backup failed")
        
        # Execute installation
        result = await self.installer.install(
            self.test_library,
            ProjectContext.FRONTEND
        )
        
        # Verify failure
        assert result.success is False
        assert "Backup failed" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_install_command_failure_with_rollback(self):
        """Test installation failure during command execution with rollback"""
        # Setup mocks
        backup_path = "/path/to/backup"
        self.mock_file_manager.create_backup.return_value = backup_path
        self.mock_file_manager.read_file.return_value = '{"name": "test", "dependencies": {}}'
        self.mock_command_executor.execute_command.return_value = (1, "", "Install failed")
        
        # Execute installation
        result = await self.installer.install(
            self.test_library,
            ProjectContext.FRONTEND
        )
        
        # Verify failure and rollback
        assert result.success is False
        assert "Package manager install failed" in result.errors[0]
        
        # Verify rollback was called
        self.mock_file_manager.restore_from_backup.assert_called_once_with(backup_path)
    
    @pytest.mark.asyncio
    async def test_install_verification_failure(self):
        """Test installation failure during verification"""
        # Setup mocks
        backup_path = "/path/to/backup"
        self.mock_file_manager.create_backup.return_value = backup_path
        self.mock_file_manager.read_file.return_value = '{"name": "test", "dependencies": {}}'
        # Install command succeeds but verification fails
        self.mock_command_executor.execute_command.side_effect = [
            (0, "install success", ""),  # Install command
            (0, "other packages listed", "")  # Verification command (library not in output)
        ]
        
        # Execute installation
        result = await self.installer.install(
            self.test_library,
            ProjectContext.FRONTEND
        )
        
        # Verify failure and rollback
        assert result.success is False
        assert "not found in installed packages" in result.errors[0]
        
        # Verify rollback was called
        self.mock_file_manager.restore_from_backup.assert_called_once_with(backup_path)
    
    @pytest.mark.asyncio
    async def test_rollback_success(self):
        """Test successful rollback operation"""
        backup_path = "/path/to/backup"
        
        # Execute rollback
        await self.installer.rollback(backup_path)
        
        # Verify rollback was called
        self.mock_file_manager.restore_from_backup.assert_called_once_with(backup_path)
    
    @pytest.mark.asyncio
    async def test_rollback_failure(self):
        """Test rollback failure"""
        # Setup mock to fail on restore
        self.mock_file_manager.restore_from_backup.side_effect = FileOperationError("Restore failed")
        
        # Execute rollback and expect exception
        with pytest.raises(FileOperationError, match="Rollback failed"):
            await self.installer.rollback("/path/to/backup")


class TestPackageInstallerIntegration:
    """Integration tests for PackageInstaller with real file operations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.installer = PackageInstaller(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_package_json(self, path: str = "frontend/package.json", dependencies: dict = None):
        """Helper to create package.json files"""
        full_path = Path(self.temp_dir) / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        package_data = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": dependencies or {}
        }
        
        full_path.write_text(json.dumps(package_data, indent=2))
    
    def create_requirements_txt(self, path: str = "backend/requirements.txt", requirements: list = None):
        """Helper to create requirements.txt files"""
        full_path = Path(self.temp_dir) / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = "\n".join(requirements or [])
        full_path.write_text(content)
    
    @pytest.mark.asyncio
    async def test_update_package_json_integration(self):
        """Test package.json update with real file operations"""
        # Create initial package.json
        initial_deps = {"existing-package": "^1.0.0"}
        self.create_package_json(dependencies=initial_deps)
        
        # Mock command executor to avoid actual npm install
        with patch.object(self.installer.command_executor, 'execute_command') as mock_exec:
            mock_exec.return_value = (0, "test-library@2.0.0", "")
            
            # Create test library
            library = LibraryMetadata(
                name="test-library",
                version="2.0.0",
                description="Test library",
                license="MIT",
                registry_type=RegistryType.NPM,
                dependencies=[]
            )
            
            # Execute installation
            result = await self.installer.install(library, ProjectContext.FRONTEND)
            
            # Verify success
            assert result.success is True
            
            # Verify package.json was updated
            package_json_path = Path(self.temp_dir) / "frontend/package.json"
            updated_content = json.loads(package_json_path.read_text())
            
            assert "test-library" in updated_content["dependencies"]
            assert updated_content["dependencies"]["test-library"] == "2.0.0"
            assert updated_content["dependencies"]["existing-package"] == "^1.0.0"
    
    @pytest.mark.asyncio
    async def test_update_requirements_txt_integration(self):
        """Test requirements.txt update with real file operations"""
        # Create initial requirements.txt
        initial_reqs = ["existing-package==1.0.0", "another-package>=2.0.0"]
        self.create_requirements_txt(requirements=initial_reqs)
        
        # Mock command executor to avoid actual pip install
        with patch.object(self.installer.command_executor, 'execute_command') as mock_exec:
            mock_exec.return_value = (0, "django 4.2.0", "")
            
            # Create test library
            library = LibraryMetadata(
                name="django",
                version="4.2.0",
                description="Django web framework",
                license="BSD",
                registry_type=RegistryType.PYPI,
                dependencies=[]
            )
            
            # Execute installation
            result = await self.installer.install(library, ProjectContext.BACKEND)
            
            # Verify success
            assert result.success is True
            
            # Verify requirements.txt was updated
            requirements_path = Path(self.temp_dir) / "backend/requirements.txt"
            updated_content = requirements_path.read_text()
            
            assert "django==4.2.0" in updated_content
            assert "existing-package==1.0.0" in updated_content
            assert "another-package>=2.0.0" in updated_content
    
    @pytest.mark.asyncio
    async def test_backup_and_rollback_integration(self):
        """Test backup creation and rollback with real file operations"""
        # Create initial package.json
        initial_deps = {"existing-package": "^1.0.0"}
        self.create_package_json(dependencies=initial_deps)
        
        # Mock command executor to fail after backup
        with patch.object(self.installer.command_executor, 'execute_command') as mock_exec:
            mock_exec.return_value = (1, "", "Install failed")
            
            # Create test library
            library = LibraryMetadata(
                name="test-library",
                version="2.0.0",
                description="Test library",
                license="MIT",
                registry_type=RegistryType.NPM,
                dependencies=[]
            )
            
            # Execute installation (should fail and rollback)
            result = await self.installer.install(library, ProjectContext.FRONTEND)
            
            # Verify failure
            assert result.success is False
            
            # Verify package.json was restored to original state
            package_json_path = Path(self.temp_dir) / "frontend/package.json"
            restored_content = json.loads(package_json_path.read_text())
            
            # Should only have original dependency, not the new one
            assert "test-library" not in restored_content["dependencies"]
            assert restored_content["dependencies"]["existing-package"] == "^1.0.0"