"""
Unit tests for library management Pydantic schemas
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.library import (
    ParsedURI,
    Dependency,
    LibraryMetadata,
    InstalledLibrary,
    ValidationResult,
    ConflictInfo,
    ConflictAnalysis,
    InstallationResult,
    ValidateLibraryRequest,
    InstallLibraryRequest,
    ValidationResponse,
    InstallationResponse,
    LibrarySearchResult,
    SearchResponse,
    LibraryListResponse,
)
from app.models.library import RegistryType, ProjectContext


class TestParsedURI:
    """Tests for ParsedURI schema"""

    def test_valid_parsed_uri(self):
        """Test creating a valid ParsedURI"""
        uri = ParsedURI(
            registry_type=RegistryType.NPM,
            package_name="react",
            version="18.0.0",
            raw_uri="npm:react@18.0.0"
        )
        assert uri.registry_type == RegistryType.NPM
        assert uri.package_name == "react"
        assert uri.version == "18.0.0"
        assert uri.raw_uri == "npm:react@18.0.0"

    def test_parsed_uri_without_version(self):
        """Test ParsedURI without version"""
        uri = ParsedURI(
            registry_type=RegistryType.PYPI,
            package_name="django",
            raw_uri="pypi:django"
        )
        assert uri.version is None


class TestDependency:
    """Tests for Dependency schema"""

    def test_valid_dependency(self):
        """Test creating a valid Dependency"""
        dep = Dependency(name="lodash", version="4.17.21", is_direct=True)
        assert dep.name == "lodash"
        assert dep.version == "4.17.21"
        assert dep.is_direct is True

    def test_dependency_default_is_direct(self):
        """Test Dependency with default is_direct"""
        dep = Dependency(name="axios", version="1.0.0")
        assert dep.is_direct is True


class TestLibraryMetadata:
    """Tests for LibraryMetadata schema"""

    def test_valid_library_metadata(self):
        """Test creating valid LibraryMetadata"""
        metadata = LibraryMetadata(
            name="react",
            version="18.0.0",
            description="A JavaScript library for building user interfaces",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="loose-envify", version="^1.1.0")
            ],
            homepage="https://reactjs.org",
            repository="https://github.com/facebook/react"
        )
        assert metadata.name == "react"
        assert metadata.version == "18.0.0"
        assert len(metadata.dependencies) == 1
        assert metadata.homepage == "https://reactjs.org"

    def test_library_metadata_minimal(self):
        """Test LibraryMetadata with minimal required fields"""
        metadata = LibraryMetadata(
            name="django",
            version="4.2.0",
            description="A high-level Python web framework",
            license="BSD",
            registry_type=RegistryType.PYPI
        )
        assert metadata.dependencies == []
        assert metadata.homepage is None
        assert metadata.repository is None


class TestInstalledLibrary:
    """Tests for InstalledLibrary schema"""

    def test_valid_installed_library(self):
        """Test creating a valid InstalledLibrary"""
        library = InstalledLibrary(
            id=1,
            project_id="proj-123",
            name="react",
            version="18.0.0",
            registry_type=RegistryType.NPM,
            project_context=ProjectContext.FRONTEND,
            description="A JavaScript library",
            license="MIT",
            installed_at=datetime.now(),
            installed_by="user@example.com",
            uri="npm:react@18.0.0",
            metadata={"downloads": 1000000}
        )
        assert library.name == "react"
        assert library.project_context == ProjectContext.FRONTEND


class TestValidationResult:
    """Tests for ValidationResult schema"""

    def test_valid_validation_result(self):
        """Test creating a valid ValidationResult"""
        result = ValidationResult(
            valid=True,
            library=LibraryMetadata(
                name="react",
                version="18.0.0",
                description="A JavaScript library",
                license="MIT",
                registry_type=RegistryType.NPM
            ),
            suggested_context=ProjectContext.FRONTEND,
            errors=[]
        )
        assert result.valid is True
        assert result.library is not None
        assert result.suggested_context == ProjectContext.FRONTEND

    def test_invalid_validation_result(self):
        """Test ValidationResult for invalid URI"""
        result = ValidationResult(
            valid=False,
            errors=["Invalid URI format"]
        )
        assert result.valid is False
        assert result.library is None
        assert len(result.errors) == 1


class TestConflictAnalysis:
    """Tests for ConflictAnalysis schema"""

    def test_conflict_analysis_with_conflicts(self):
        """Test ConflictAnalysis with conflicts"""
        analysis = ConflictAnalysis(
            has_conflicts=True,
            conflicts=[
                ConflictInfo(
                    package="react",
                    existing_version="17.0.2",
                    required_version="^18.0.0"
                )
            ],
            suggestions=["Upgrade react to ^18.0.0"],
            circular_dependencies=None
        )
        assert analysis.has_conflicts is True
        assert len(analysis.conflicts) == 1
        assert analysis.conflicts[0].package == "react"

    def test_conflict_analysis_no_conflicts(self):
        """Test ConflictAnalysis without conflicts"""
        analysis = ConflictAnalysis(has_conflicts=False)
        assert analysis.has_conflicts is False
        assert analysis.conflicts == []
        assert analysis.suggestions == []


class TestRequestSchemas:
    """Tests for request schemas"""

    def test_validate_library_request(self):
        """Test ValidateLibraryRequest"""
        request = ValidateLibraryRequest(
            uri="npm:react@18.0.0",
            project_context=ProjectContext.FRONTEND
        )
        assert request.uri == "npm:react@18.0.0"
        assert request.project_context == ProjectContext.FRONTEND

    def test_validate_library_request_strips_whitespace(self):
        """Test ValidateLibraryRequest strips whitespace from URI"""
        request = ValidateLibraryRequest(uri="  npm:react@18.0.0  ")
        assert request.uri == "npm:react@18.0.0"

    def test_validate_library_request_empty_uri(self):
        """Test ValidateLibraryRequest rejects empty URI"""
        with pytest.raises(ValidationError) as exc_info:
            ValidateLibraryRequest(uri="")
        # Pydantic's min_length validation triggers before custom validator
        assert "at least 1 character" in str(exc_info.value)

    def test_validate_library_request_whitespace_only_uri(self):
        """Test ValidateLibraryRequest rejects whitespace-only URI"""
        with pytest.raises(ValidationError) as exc_info:
            ValidateLibraryRequest(uri="   ")
        assert "URI cannot be empty" in str(exc_info.value)

    def test_install_library_request(self):
        """Test InstallLibraryRequest"""
        request = InstallLibraryRequest(
            uri="npm:react@18.0.0",
            project_context=ProjectContext.FRONTEND,
            version="18.2.0"
        )
        assert request.uri == "npm:react@18.0.0"
        assert request.project_context == ProjectContext.FRONTEND
        assert request.version == "18.2.0"

    def test_install_library_request_without_version(self):
        """Test InstallLibraryRequest without version override"""
        request = InstallLibraryRequest(
            uri="pypi:django",
            project_context=ProjectContext.BACKEND
        )
        assert request.version is None


class TestResponseSchemas:
    """Tests for response schemas"""

    def test_validation_response(self):
        """Test ValidationResponse"""
        response = ValidationResponse(
            valid=True,
            library=LibraryMetadata(
                name="react",
                version="18.0.0",
                description="A JavaScript library",
                license="MIT",
                registry_type=RegistryType.NPM
            ),
            suggested_context=ProjectContext.FRONTEND
        )
        assert response.valid is True
        assert response.library is not None

    def test_installation_response_success(self):
        """Test InstallationResponse for success"""
        response = InstallationResponse(
            success=True,
            installed_library=InstalledLibrary(
                project_id="proj-123",
                name="react",
                version="18.0.0",
                registry_type=RegistryType.NPM,
                project_context=ProjectContext.FRONTEND,
                description="A JavaScript library",
                license="MIT",
                installed_at=datetime.now(),
                installed_by="user@example.com",
                uri="npm:react@18.0.0"
            )
        )
        assert response.success is True
        assert response.installed_library is not None

    def test_installation_response_failure(self):
        """Test InstallationResponse for failure"""
        response = InstallationResponse(
            success=False,
            errors=["Installation failed: npm install returned exit code 1"]
        )
        assert response.success is False
        assert response.installed_library is None
        assert len(response.errors) == 1

    def test_search_response(self):
        """Test SearchResponse"""
        response = SearchResponse(
            results=[
                LibrarySearchResult(
                    name="react",
                    description="A JavaScript library",
                    version="18.0.0",
                    downloads=1000000,
                    uri="npm:react",
                    registry_type=RegistryType.NPM
                )
            ],
            total=1
        )
        assert len(response.results) == 1
        assert response.total == 1

    def test_library_list_response(self):
        """Test LibraryListResponse"""
        response = LibraryListResponse(
            libraries=[
                InstalledLibrary(
                    project_id="proj-123",
                    name="react",
                    version="18.0.0",
                    registry_type=RegistryType.NPM,
                    project_context=ProjectContext.FRONTEND,
                    description="A JavaScript library",
                    license="MIT",
                    installed_at=datetime.now(),
                    installed_by="user@example.com",
                    uri="npm:react@18.0.0"
                )
            ],
            total=1
        )
        assert len(response.libraries) == 1
        assert response.total == 1

    def test_library_list_response_empty(self):
        """Test LibraryListResponse with no libraries"""
        response = LibraryListResponse()
        assert response.libraries == []
        assert response.total == 0
