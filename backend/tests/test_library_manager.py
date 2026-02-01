"""
Unit tests for Library Manager Orchestrator Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.library_management.library_manager import (
    LibraryManager,
    LibraryManagerError,
    ValidationError,
    InstallationError,
    SearchError
)
from app.services.library_management.uri_parser import URIParser
from app.services.library_management.metadata_fetcher import (
    MetadataFetcher,
    NetworkError,
    PackageNotFoundError
)
from app.services.library_management.context_detector import ContextDetector
from app.services.library_management.dependency_resolver import DependencyResolver
from app.services.library_management.package_installer import PackageInstaller
from app.services.library_management.library_repository import LibraryRepository
from app.services.library_management.search_service import SearchService

from app.schemas.library import (
    ParsedURI,
    LibraryMetadata,
    Dependency,
    ValidationResult,
    InstallationResult,
    InstalledLibrary,
    ConflictAnalysis,
    LibrarySearchResult
)
from app.models.library import RegistryType, ProjectContext


class TestLibraryManager:
    """Test cases for LibraryManager orchestrator service"""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing"""
        return {
            'uri_parser': MagicMock(spec=URIParser),
            'metadata_fetcher': AsyncMock(spec=MetadataFetcher),
            'context_detector': MagicMock(spec=ContextDetector),
            'dependency_resolver': AsyncMock(spec=DependencyResolver),
            'package_installer': AsyncMock(spec=PackageInstaller),
            'library_repository': AsyncMock(spec=LibraryRepository),
            'search_service': AsyncMock(spec=SearchService)
        }
    
    @pytest.fixture
    def library_manager(self, mock_services):
        """Create LibraryManager instance with mocked services"""
        return LibraryManager(**mock_services)
    
    @pytest.fixture
    def sample_parsed_uri(self):
        """Sample parsed URI for testing"""
        return ParsedURI(
            registry_type=RegistryType.NPM,
            package_name="react",
            version="18.0.0",
            raw_uri="npm:react@18.0.0"
        )
    
    @pytest.fixture
    def sample_library_metadata(self):
        """Sample library metadata for testing"""
        return LibraryMetadata(
            name="react",
            version="18.0.0",
            description="A JavaScript library for building user interfaces",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="loose-envify", version="^1.1.0", is_direct=True)
            ],
            homepage="https://reactjs.org/",
            repository="https://github.com/facebook/react"
        )
    
    @pytest.fixture
    def sample_installed_library(self):
        """Sample installed library for testing"""
        return InstalledLibrary(
            id=1,
            project_id="test-project",
            name="react",
            version="18.0.0",
            registry_type=RegistryType.NPM,
            project_context=ProjectContext.FRONTEND,
            description="A JavaScript library for building user interfaces",
            license="MIT",
            installed_at=datetime.now(),
            installed_by="test-user",
            uri="npm:react@18.0.0",
            metadata={"dependencies": []}
        )


class TestValidateLibrary(TestLibraryManager):
    """Test cases for validate_library method"""
    
    @pytest.mark.asyncio
    async def test_validate_library_success(
        self,
        library_manager,
        mock_services,
        sample_parsed_uri,
        sample_library_metadata
    ):
        """Test successful library validation"""
        # Setup mocks
        mock_services['uri_parser'].parse.return_value = sample_parsed_uri
        mock_services['metadata_fetcher'].fetch_metadata.return_value = sample_library_metadata
        mock_services['context_detector'].detect_and_validate_context.return_value = (
            ProjectContext.FRONTEND, True, None
        )
        
        # Execute
        result = await library_manager.validate_library("npm:react@18.0.0")
        
        # Verify
        assert result.valid is True
        assert result.library is not None
        assert result.library.name == "react"
        assert result.library.version == "18.0.0"
        assert result.suggested_context == ProjectContext.FRONTEND
        assert len(result.errors) == 0
        
        # Verify service calls
        mock_services['uri_parser'].parse.assert_called_once_with("npm:react@18.0.0")
        mock_services['metadata_fetcher'].fetch_metadata.assert_called_once_with(
            registry_type=RegistryType.NPM,
            package_name="react",
            version="18.0.0"
        )
        mock_services['context_detector'].detect_and_validate_context.assert_called_once_with(
            RegistryType.NPM
        )
    
    @pytest.mark.asyncio
    async def test_validate_library_invalid_uri(self, library_manager, mock_services):
        """Test validation with invalid URI"""
        # Setup mocks
        mock_services['uri_parser'].parse.side_effect = ValueError("Invalid URI format")
        
        # Execute
        result = await library_manager.validate_library("invalid:uri")
        
        # Verify
        assert result.valid is False
        assert result.library is None
        assert len(result.errors) == 1
        assert "Invalid URI format" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_validate_library_package_not_found(
        self,
        library_manager,
        mock_services,
        sample_parsed_uri
    ):
        """Test validation when package is not found"""
        # Setup mocks
        mock_services['uri_parser'].parse.return_value = sample_parsed_uri
        mock_services['metadata_fetcher'].fetch_metadata.side_effect = PackageNotFoundError(
            "Package 'nonexistent' not found"
        )
        
        # Execute
        result = await library_manager.validate_library("npm:nonexistent@1.0.0")
        
        # Verify
        assert result.valid is False
        assert result.library is None
        assert len(result.errors) == 1
        assert "Package not found" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_validate_library_network_error(
        self,
        library_manager,
        mock_services,
        sample_parsed_uri
    ):
        """Test validation with network error"""
        # Setup mocks
        mock_services['uri_parser'].parse.return_value = sample_parsed_uri
        mock_services['metadata_fetcher'].fetch_metadata.side_effect = NetworkError(
            "Connection timeout"
        )
        
        # Execute
        result = await library_manager.validate_library("npm:react@18.0.0")
        
        # Verify
        assert result.valid is False
        assert result.library is None
        assert len(result.errors) == 1
        assert "Network error" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_validate_library_context_invalid(
        self,
        library_manager,
        mock_services,
        sample_parsed_uri,
        sample_library_metadata
    ):
        """Test validation when context is invalid"""
        # Setup mocks
        mock_services['uri_parser'].parse.return_value = sample_parsed_uri
        mock_services['metadata_fetcher'].fetch_metadata.return_value = sample_library_metadata
        mock_services['context_detector'].detect_and_validate_context.return_value = (
            ProjectContext.FRONTEND, False, "Configuration file not found: frontend/package.json"
        )
        mock_services['context_detector'].suggest_alternative_contexts.return_value = [
            ProjectContext.BACKEND
        ]
        
        # Execute
        result = await library_manager.validate_library("npm:react@18.0.0")
        
        # Verify
        assert result.valid is False
        assert result.library is not None
        assert result.suggested_context == ProjectContext.BACKEND  # Alternative context
        assert len(result.errors) > 0
        assert "Configuration file not found" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_validate_library_with_provided_context(
        self,
        library_manager,
        mock_services,
        sample_parsed_uri,
        sample_library_metadata
    ):
        """Test validation with user-provided context"""
        # Setup mocks
        mock_services['uri_parser'].parse.return_value = sample_parsed_uri
        mock_services['metadata_fetcher'].fetch_metadata.return_value = sample_library_metadata
        mock_services['context_detector'].validate_context.return_value = (True, None)
        
        # Execute
        result = await library_manager.validate_library(
            "npm:react@18.0.0",
            context=ProjectContext.FRONTEND
        )
        
        # Verify
        assert result.valid is True
        assert result.suggested_context == ProjectContext.FRONTEND
        mock_services['context_detector'].validate_context.assert_called_once_with(
            ProjectContext.FRONTEND
        )


class TestInstallLibrary(TestLibraryManager):
    """Test cases for install_library method"""
    
    @pytest.mark.asyncio
    async def test_install_library_success(
        self,
        library_manager,
        mock_services,
        sample_library_metadata,
        sample_installed_library
    ):
        """Test successful library installation"""
        # Setup mocks
        validation_result = ValidationResult(
            valid=True,
            library=sample_library_metadata,
            suggested_context=ProjectContext.FRONTEND,
            errors=[]
        )
        
        conflict_analysis = ConflictAnalysis(
            has_conflicts=False,
            conflicts=[],
            suggestions=[],
            circular_dependencies=None
        )
        
        installation_result = InstallationResult(
            success=True,
            installed_library=sample_installed_library,
            errors=[]
        )
        
        # Mock the validate_library method
        library_manager.validate_library = AsyncMock(return_value=validation_result)
        mock_services['dependency_resolver'].check_conflicts.return_value = conflict_analysis
        mock_services['package_installer'].install.return_value = installation_result
        mock_services['library_repository'].save_library.return_value = 1
        mock_services['library_repository'].save_dependencies.return_value = None
        
        # Execute
        result = await library_manager.install_library(
            uri="npm:react@18.0.0",
            context=ProjectContext.FRONTEND,
            user_id="test-user",
            project_id="test-project"
        )
        
        # Verify
        assert result.success is True
        assert result.installed_library is not None
        assert result.installed_library.name == "react"
        assert len(result.errors) == 0
        
        # Verify service calls
        library_manager.validate_library.assert_called_once()
        mock_services['dependency_resolver'].check_conflicts.assert_called_once()
        mock_services['package_installer'].install.assert_called_once()
        mock_services['library_repository'].save_library.assert_called_once()
        mock_services['library_repository'].save_dependencies.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_install_library_validation_failed(
        self,
        library_manager,
        mock_services
    ):
        """Test installation when validation fails"""
        # Setup mocks
        validation_result = ValidationResult(
            valid=False,
            library=None,
            suggested_context=None,
            errors=["Invalid URI format"]
        )
        
        library_manager.validate_library = AsyncMock(return_value=validation_result)
        
        # Execute
        result = await library_manager.install_library(
            uri="invalid:uri",
            context=ProjectContext.FRONTEND
        )
        
        # Verify
        assert result.success is False
        assert result.installed_library is None
        assert len(result.errors) == 1
        assert "Invalid URI format" in result.errors[0]
        
        # Verify no installation was attempted
        mock_services['package_installer'].install.assert_not_called()
        mock_services['library_repository'].save_library.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_install_library_with_conflicts(
        self,
        library_manager,
        mock_services,
        sample_library_metadata,
        sample_installed_library
    ):
        """Test installation with dependency conflicts"""
        # Setup mocks
        validation_result = ValidationResult(
            valid=True,
            library=sample_library_metadata,
            suggested_context=ProjectContext.FRONTEND,
            errors=[]
        )
        
        conflict_analysis = ConflictAnalysis(
            has_conflicts=True,
            conflicts=[],  # We'll test with conflicts but still proceed
            suggestions=["Upgrade existing package"],
            circular_dependencies=None
        )
        
        installation_result = InstallationResult(
            success=True,
            installed_library=sample_installed_library,
            errors=[]
        )
        
        library_manager.validate_library = AsyncMock(return_value=validation_result)
        mock_services['dependency_resolver'].check_conflicts.return_value = conflict_analysis
        mock_services['package_installer'].install.return_value = installation_result
        mock_services['library_repository'].save_library.return_value = 1
        mock_services['library_repository'].save_dependencies.return_value = None
        
        # Execute
        result = await library_manager.install_library(
            uri="npm:react@18.0.0",
            context=ProjectContext.FRONTEND
        )
        
        # Verify installation still proceeds despite conflicts
        assert result.success is True
        mock_services['package_installer'].install.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_install_library_package_installation_failed(
        self,
        library_manager,
        mock_services,
        sample_library_metadata
    ):
        """Test installation when package installation fails"""
        # Setup mocks
        validation_result = ValidationResult(
            valid=True,
            library=sample_library_metadata,
            suggested_context=ProjectContext.FRONTEND,
            errors=[]
        )
        
        conflict_analysis = ConflictAnalysis(
            has_conflicts=False,
            conflicts=[],
            suggestions=[],
            circular_dependencies=None
        )
        
        installation_result = InstallationResult(
            success=False,
            installed_library=None,
            errors=["npm install failed"]
        )
        
        library_manager.validate_library = AsyncMock(return_value=validation_result)
        mock_services['dependency_resolver'].check_conflicts.return_value = conflict_analysis
        mock_services['package_installer'].install.return_value = installation_result
        
        # Execute
        result = await library_manager.install_library(
            uri="npm:react@18.0.0",
            context=ProjectContext.FRONTEND
        )
        
        # Verify
        assert result.success is False
        assert result.installed_library is None
        assert "npm install failed" in result.errors
        
        # Verify database operations were not attempted
        mock_services['library_repository'].save_library.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_install_library_database_save_failed(
        self,
        library_manager,
        mock_services,
        sample_library_metadata,
        sample_installed_library
    ):
        """Test installation when database save fails"""
        # Setup mocks
        validation_result = ValidationResult(
            valid=True,
            library=sample_library_metadata,
            suggested_context=ProjectContext.FRONTEND,
            errors=[]
        )
        
        conflict_analysis = ConflictAnalysis(
            has_conflicts=False,
            conflicts=[],
            suggestions=[],
            circular_dependencies=None
        )
        
        installation_result = InstallationResult(
            success=True,
            installed_library=sample_installed_library,
            errors=[]
        )
        
        library_manager.validate_library = AsyncMock(return_value=validation_result)
        mock_services['dependency_resolver'].check_conflicts.return_value = conflict_analysis
        mock_services['package_installer'].install.return_value = installation_result
        mock_services['library_repository'].save_library.side_effect = Exception("Database error")
        
        # Execute
        result = await library_manager.install_library(
            uri="npm:react@18.0.0",
            context=ProjectContext.FRONTEND
        )
        
        # Verify
        assert result.success is False
        assert result.installed_library is not None  # Package was installed
        assert len(result.errors) == 2
        assert "failed to save metadata to database" in result.errors[0]
        assert "Database error" in result.errors[1]


class TestSearchLibraries(TestLibraryManager):
    """Test cases for search_libraries method"""
    
    @pytest.mark.asyncio
    async def test_search_libraries_success(self, library_manager, mock_services, sample_library_metadata):
        """Test successful library search"""
        # Setup mocks - create sample search results
        mock_search_results = [
            LibrarySearchResult(
                name="react",
                description="A JavaScript library for building user interfaces",
                version="18.0.0",
                downloads=1000000,
                uri="npm:react@18.0.0",
                registry_type=RegistryType.NPM
            ),
            LibrarySearchResult(
                name="react",
                description="Server-side rendering of React components",
                version="4.3.0",
                downloads=50000,
                uri="pypi:react==4.3.0",
                registry_type=RegistryType.PYPI
            ),
            LibrarySearchResult(
                name="react-core",
                description="React core library for Maven",
                version="1.0.0",
                downloads=10000,
                uri="maven:com.example:react-core:1.0.0",
                registry_type=RegistryType.MAVEN
            )
        ]
        mock_services['search_service'].search.return_value = mock_search_results
        
        # Execute
        results = await library_manager.search_libraries("react")
        
        # Verify
        assert len(results) == 3  # One for each registry type
        assert all(isinstance(result, LibrarySearchResult) for result in results)
        
        # Verify search service was called correctly
        mock_services['search_service'].search.assert_called_once_with(
            query="react",
            registry_type=None,
            limit=20
        )
    
    @pytest.mark.asyncio
    async def test_search_libraries_with_registry_filter(
        self,
        library_manager,
        mock_services,
        sample_library_metadata
    ):
        """Test library search with registry filter"""
        # Setup mocks - create npm-only search results
        mock_search_results = [
            LibrarySearchResult(
                name="react",
                description="A JavaScript library for building user interfaces",
                version="18.0.0",
                downloads=1000000,
                uri="npm:react@18.0.0",
                registry_type=RegistryType.NPM
            )
        ]
        mock_services['search_service'].search.return_value = mock_search_results
        
        # Execute
        results = await library_manager.search_libraries("react", registry_type=RegistryType.NPM)
        
        # Verify
        assert len(results) == 1
        assert results[0].registry_type == RegistryType.NPM
        
        # Verify search service was called with registry filter
        mock_services['search_service'].search.assert_called_once_with(
            query="react",
            registry_type=RegistryType.NPM,
            limit=20
        )
    
    @pytest.mark.asyncio
    async def test_search_libraries_empty_query(self, library_manager, mock_services):
        """Test search with empty query"""
        # Setup mocks - SearchService should return empty results for empty query
        mock_services['search_service'].search.return_value = []
        
        # Execute
        results = await library_manager.search_libraries("")
        
        # Verify
        assert len(results) == 0
        
        # Verify search service was called (it handles empty query validation internally)
        mock_services['search_service'].search.assert_called_once_with(
            query="",
            registry_type=None,
            limit=20
        )
    
    @pytest.mark.asyncio
    async def test_search_libraries_package_not_found(self, library_manager, mock_services):
        """Test search when package is not found in any registry"""
        # Setup mocks - SearchService returns empty results when nothing found
        mock_services['search_service'].search.return_value = []
        
        # Execute
        results = await library_manager.search_libraries("nonexistent")
        
        # Verify
        assert len(results) == 0
        
        # Verify search service was called
        mock_services['search_service'].search.assert_called_once_with(
            query="nonexistent",
            registry_type=None,
            limit=20
        )
    
    @pytest.mark.asyncio
    async def test_search_libraries_network_error(self, library_manager, mock_services):
        """Test search with network error"""
        # Setup mocks - SearchService raises SearchError for network issues
        from app.services.library_management.search_service import SearchError as SearchServiceError
        mock_services['search_service'].search.side_effect = SearchServiceError("Network error")
        
        # Execute and verify LibraryManager's SearchError is raised
        with pytest.raises(SearchError):  # This is LibraryManager's SearchError
            await library_manager.search_libraries("react")
        
        # Verify search service was called
        mock_services['search_service'].search.assert_called_once_with(
            query="react",
            registry_type=None,
            limit=20
        )
    
    @pytest.mark.asyncio
    async def test_search_libraries_limit_parameter(self, library_manager, mock_services):
        """Test search with custom limit parameter"""
        # Setup mocks
        mock_search_results = [
            LibrarySearchResult(
                name=f"package-{i}",
                description=f"Test package {i}",
                version="1.0.0",
                downloads=1000,
                uri=f"npm:package-{i}@1.0.0",
                registry_type=RegistryType.NPM
            )
            for i in range(10)
        ]
        mock_services['search_service'].search.return_value = mock_search_results
        
        # Execute with custom limit
        results = await library_manager.search_libraries("package", limit=10)
        
        # Verify
        assert len(results) == 10
        
        # Verify search service was called with custom limit
        mock_services['search_service'].search.assert_called_once_with(
            query="package",
            registry_type=None,
            limit=10
        )


class TestGetInstalledLibraries(TestLibraryManager):
    """Test cases for get_installed_libraries method"""
    
    @pytest.mark.asyncio
    async def test_get_installed_libraries_success(
        self,
        library_manager,
        mock_services,
        sample_installed_library
    ):
        """Test successful retrieval of installed libraries"""
        # Setup mocks
        mock_services['library_repository'].get_libraries_by_project.return_value = [
            sample_installed_library
        ]
        
        # Execute
        libraries = await library_manager.get_installed_libraries("test-project")
        
        # Verify
        assert len(libraries) == 1
        assert libraries[0].name == "react"
        
        mock_services['library_repository'].get_libraries_by_project.assert_called_once_with(
            project_id="test-project",
            context=None
        )
    
    @pytest.mark.asyncio
    async def test_get_installed_libraries_with_context_filter(
        self,
        library_manager,
        mock_services,
        sample_installed_library
    ):
        """Test retrieval with context filter"""
        # Setup mocks
        mock_services['library_repository'].get_libraries_by_project.return_value = [
            sample_installed_library
        ]
        
        # Execute
        libraries = await library_manager.get_installed_libraries(
            "test-project",
            context=ProjectContext.FRONTEND
        )
        
        # Verify
        assert len(libraries) == 1
        
        mock_services['library_repository'].get_libraries_by_project.assert_called_once_with(
            project_id="test-project",
            context=ProjectContext.FRONTEND
        )
    
    @pytest.mark.asyncio
    async def test_get_installed_libraries_database_error(self, library_manager, mock_services):
        """Test retrieval when database error occurs"""
        # Setup mocks
        mock_services['library_repository'].get_libraries_by_project.side_effect = Exception(
            "Database connection failed"
        )
        
        # Execute and verify exception
        with pytest.raises(LibraryManagerError) as exc_info:
            await library_manager.get_installed_libraries("test-project")
        
        assert "Failed to retrieve libraries" in str(exc_info.value)


class TestGetLibraryDetails(TestLibraryManager):
    """Test cases for get_library_details method"""
    
    @pytest.mark.asyncio
    async def test_get_library_details_success(
        self,
        library_manager,
        mock_services,
        sample_installed_library
    ):
        """Test successful retrieval of library details"""
        # Setup mocks
        mock_services['library_repository'].get_library_by_name.return_value = sample_installed_library
        
        # Execute
        library = await library_manager.get_library_details(
            project_id="test-project",
            library_name="react",
            context=ProjectContext.FRONTEND
        )
        
        # Verify
        assert library is not None
        assert library.name == "react"
        
        mock_services['library_repository'].get_library_by_name.assert_called_once_with(
            project_id="test-project",
            name="react",
            context=ProjectContext.FRONTEND
        )
    
    @pytest.mark.asyncio
    async def test_get_library_details_not_found(self, library_manager, mock_services):
        """Test retrieval when library is not found"""
        # Setup mocks
        mock_services['library_repository'].get_library_by_name.return_value = None
        
        # Execute
        library = await library_manager.get_library_details(
            project_id="test-project",
            library_name="nonexistent",
            context=ProjectContext.FRONTEND
        )
        
        # Verify
        assert library is None


class TestUpdateLibraryVersion(TestLibraryManager):
    """Test cases for update_library_version method"""
    
    @pytest.mark.asyncio
    async def test_update_library_version_success(
        self,
        library_manager,
        mock_services,
        sample_installed_library
    ):
        """Test successful library version update"""
        # Setup mocks
        mock_services['library_repository'].get_library_by_name.return_value = sample_installed_library
        
        # Mock the install_library method
        installation_result = InstallationResult(
            success=True,
            installed_library=sample_installed_library,
            errors=[]
        )
        library_manager.install_library = AsyncMock(return_value=installation_result)
        mock_services['library_repository'].update_library_version.return_value = None
        
        # Execute
        result = await library_manager.update_library_version(
            project_id="test-project",
            library_name="react",
            context=ProjectContext.FRONTEND,
            new_version="18.1.0",
            user_id="test-user"
        )
        
        # Verify
        assert result.success is True
        
        # Verify service calls
        library_manager.install_library.assert_called_once()
        mock_services['library_repository'].update_library_version.assert_called_once_with(
            library_id=1,
            new_version="18.1.0"
        )
    
    @pytest.mark.asyncio
    async def test_update_library_version_not_found(self, library_manager, mock_services):
        """Test update when library is not found"""
        # Setup mocks
        mock_services['library_repository'].get_library_by_name.return_value = None
        
        # Execute
        result = await library_manager.update_library_version(
            project_id="test-project",
            library_name="nonexistent",
            context=ProjectContext.FRONTEND,
            new_version="1.0.0"
        )
        
        # Verify
        assert result.success is False
        assert "not found" in result.errors[0]


class TestLibraryManagerInitialization(TestLibraryManager):
    """Test cases for LibraryManager initialization"""
    
    def test_initialization_without_repository_raises_error(self):
        """Test that initialization without repository raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LibraryManager()
        
        assert "LibraryRepository is required" in str(exc_info.value)
    
    def test_initialization_with_all_services(self, mock_services):
        """Test successful initialization with all services"""
        manager = LibraryManager(**mock_services)
        
        assert manager.uri_parser is mock_services['uri_parser']
        assert manager.metadata_fetcher is mock_services['metadata_fetcher']
        assert manager.context_detector is mock_services['context_detector']
        assert manager.dependency_resolver is mock_services['dependency_resolver']
        assert manager.package_installer is mock_services['package_installer']
        assert manager.library_repository is mock_services['library_repository']
    
    def test_initialization_with_defaults(self, mock_services):
        """Test initialization with default services (only repository provided)"""
        manager = LibraryManager(library_repository=mock_services['library_repository'])
        
        # Verify that default services are created
        assert manager.uri_parser is not None
        assert manager.metadata_fetcher is not None
        assert manager.context_detector is not None
        assert manager.dependency_resolver is not None
        assert manager.package_installer is not None
        assert manager.library_repository is mock_services['library_repository']


class TestLibraryManagerCleanup(TestLibraryManager):
    """Test cases for LibraryManager resource cleanup"""
    
    @pytest.mark.asyncio
    async def test_close_resources(self, library_manager, mock_services):
        """Test resource cleanup"""
        # Execute
        await library_manager.close()
        
        # Verify metadata fetcher close was called
        mock_services['metadata_fetcher'].close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_services):
        """Test async context manager usage"""
        async with LibraryManager(**mock_services) as manager:
            assert manager is not None
        
        # Verify close was called
        mock_services['metadata_fetcher'].close.assert_called_once()