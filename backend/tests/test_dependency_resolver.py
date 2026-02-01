"""
Unit tests for Dependency Resolver Service
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.library_management.dependency_resolver import (
    DependencyResolver,
    DependencyResolverError,
    FileParsingError,
    VersionConflictError,
    CircularDependencyError
)
from app.schemas.library import LibraryMetadata, Dependency, ConflictAnalysis, ConflictInfo
from app.models.library import RegistryType, ProjectContext


class TestDependencyResolver:
    """Test cases for DependencyResolver class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.resolver = DependencyResolver(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_file(self, relative_path: str, content: str):
        """Helper method to create files"""
        full_path = Path(self.temp_dir) / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        return full_path
    
    def create_package_json(self, path: str = "frontend/package.json", dependencies: dict = None):
        """Helper to create package.json files"""
        package_data = {
            "name": "test-package",
            "version": "1.0.0",
            "dependencies": dependencies or {}
        }
        self.create_file(path, json.dumps(package_data, indent=2))
    
    def create_requirements_txt(self, path: str = "backend/requirements.txt", requirements: list = None):
        """Helper to create requirements.txt files"""
        content = "\n".join(requirements or [])
        self.create_file(path, content)
    
    # ========================================================================
    # Test _parse_package_json method
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_parse_package_json_with_dependencies(self):
        """Test parsing package.json with dependencies"""
        dependencies = {
            "react": "^18.0.0",
            "lodash": "~4.17.0",
            "axios": ">=0.27.0"
        }
        self.create_package_json(dependencies=dependencies)
        
        result = await self.resolver._parse_package_json()
        
        assert result == dependencies
    
    @pytest.mark.asyncio
    async def test_parse_package_json_with_dev_dependencies(self):
        """Test parsing package.json with devDependencies"""
        package_data = {
            "name": "test-package",
            "version": "1.0.0",
            "dependencies": {"react": "^18.0.0"},
            "devDependencies": {"jest": "^29.0.0", "typescript": "^4.9.0"},
            "peerDependencies": {"react-dom": "^18.0.0"}
        }
        self.create_file("frontend/package.json", json.dumps(package_data, indent=2))
        
        result = await self.resolver._parse_package_json()
        
        expected = {
            "react": "^18.0.0",
            "jest": "^29.0.0",
            "typescript": "^4.9.0",
            "react-dom": "^18.0.0"
        }
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_parse_package_json_missing_file(self):
        """Test parsing non-existent package.json"""
        result = await self.resolver._parse_package_json()
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_parse_package_json_invalid_json(self):
        """Test parsing invalid JSON in package.json"""
        self.create_file("frontend/package.json", "invalid json content")
        
        with pytest.raises(FileParsingError, match="Invalid JSON"):
            await self.resolver._parse_package_json()
    
    @pytest.mark.asyncio
    async def test_parse_package_json_custom_path(self):
        """Test parsing package.json from custom path"""
        dependencies = {"express": "^4.18.0"}
        self.create_package_json("services/package.json", dependencies)
        
        result = await self.resolver._parse_package_json("services/package.json")
        
        assert result == dependencies
    
    # ========================================================================
    # Test _parse_requirements_txt method
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_parse_requirements_txt_with_dependencies(self):
        """Test parsing requirements.txt with dependencies"""
        requirements = [
            "django==4.2.0",
            "psycopg2>=2.9.0",
            "celery~=5.3.0",
            "redis!=4.0.0"
        ]
        self.create_requirements_txt(requirements=requirements)
        
        result = await self.resolver._parse_requirements_txt()
        
        expected = {
            "django": "==4.2.0",
            "psycopg2": ">=2.9.0",
            "celery": "~=5.3.0",
            "redis": "!=4.0.0"
        }
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_parse_requirements_txt_with_comments_and_empty_lines(self):
        """Test parsing requirements.txt with comments and empty lines"""
        content = """
# Web framework
django==4.2.0

# Database
psycopg2>=2.9.0

# Task queue
celery~=5.3.0
        """.strip()
        self.create_file("backend/requirements.txt", content)
        
        result = await self.resolver._parse_requirements_txt()
        
        expected = {
            "django": "==4.2.0",
            "psycopg2": ">=2.9.0",
            "celery": "~=5.3.0"
        }
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_parse_requirements_txt_with_pip_options(self):
        """Test parsing requirements.txt with pip options (should be skipped)"""
        requirements = [
            "-e git+https://github.com/user/repo.git#egg=package",
            "--index-url https://pypi.org/simple/",
            "django==4.2.0",
            "-r other-requirements.txt"
        ]
        self.create_requirements_txt(requirements=requirements)
        
        result = await self.resolver._parse_requirements_txt()
        
        expected = {"django": "==4.2.0"}
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_parse_requirements_txt_missing_file(self):
        """Test parsing non-existent requirements.txt"""
        result = await self.resolver._parse_requirements_txt()
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_parse_requirements_txt_package_without_version(self):
        """Test parsing requirements.txt with package without version specifier"""
        requirements = ["django", "psycopg2==2.9.0"]
        self.create_requirements_txt(requirements=requirements)
        
        result = await self.resolver._parse_requirements_txt()
        
        expected = {
            "django": "",
            "psycopg2": "==2.9.0"
        }
        assert result == expected
    
    # ========================================================================
    # Test _parse_existing_dependencies method
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_parse_existing_dependencies_frontend(self):
        """Test parsing dependencies for frontend context"""
        dependencies = {"react": "^18.0.0", "lodash": "~4.17.0"}
        self.create_package_json(dependencies=dependencies)
        
        result = await self.resolver._parse_existing_dependencies(ProjectContext.FRONTEND)
        
        assert result == dependencies
    
    @pytest.mark.asyncio
    async def test_parse_existing_dependencies_backend(self):
        """Test parsing dependencies for backend context"""
        requirements = ["django==4.2.0", "psycopg2>=2.9.0"]
        self.create_requirements_txt(requirements=requirements)
        
        result = await self.resolver._parse_existing_dependencies(ProjectContext.BACKEND)
        
        expected = {
            "django": "==4.2.0",
            "psycopg2": ">=2.9.0"
        }
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_parse_existing_dependencies_services(self):
        """Test parsing dependencies for services context"""
        dependencies = {"express": "^4.18.0"}
        self.create_package_json("services/package.json", dependencies)
        
        result = await self.resolver._parse_existing_dependencies(ProjectContext.SERVICES)
        
        assert result == dependencies
    
    @pytest.mark.asyncio
    async def test_parse_existing_dependencies_unsupported_context(self):
        """Test parsing dependencies for unsupported context"""
        with pytest.raises(FileParsingError, match="Failed to parse dependency file"):
            await self.resolver._parse_existing_dependencies("UNSUPPORTED")
    
    # ========================================================================
    # Test _are_npm_versions_compatible method
    # ========================================================================
    
    def test_npm_versions_compatible_exact_match(self):
        """Test npm version compatibility with exact versions"""
        assert self.resolver._are_npm_versions_compatible("1.2.3", "1.2.3") is True
        assert self.resolver._are_npm_versions_compatible("1.2.3", "1.2.4") is False
    
    def test_npm_versions_compatible_caret_ranges(self):
        """Test npm version compatibility with caret ranges"""
        assert self.resolver._are_npm_versions_compatible("^1.2.3", "^1.3.0") is True
        assert self.resolver._are_npm_versions_compatible("^1.2.3", "^2.0.0") is False
        assert self.resolver._are_npm_versions_compatible("^1.2.3", "1.5.0") is True
    
    def test_npm_versions_compatible_tilde_ranges(self):
        """Test npm version compatibility with tilde ranges"""
        assert self.resolver._are_npm_versions_compatible("~1.2.3", "~1.2.5") is True
        assert self.resolver._are_npm_versions_compatible("~1.2.3", "~1.3.0") is False
        assert self.resolver._are_npm_versions_compatible("~1.2.3", "1.2.5") is True
    
    def test_npm_versions_compatible_mixed_specifiers(self):
        """Test npm version compatibility with mixed specifiers"""
        assert self.resolver._are_npm_versions_compatible("^1.2.3", "~1.2.5") is True
        assert self.resolver._are_npm_versions_compatible("^1.2.3", "~2.0.0") is False
    
    def test_npm_versions_compatible_malformed_versions(self):
        """Test npm version compatibility with malformed versions"""
        assert self.resolver._are_npm_versions_compatible("", "1.2.3") is False
        assert self.resolver._are_npm_versions_compatible("invalid", "1.2.3") is False
    
    # ========================================================================
    # Test _are_python_versions_compatible method
    # ========================================================================
    
    def test_python_versions_compatible_exact_match(self):
        """Test Python version compatibility with exact versions"""
        assert self.resolver._are_python_versions_compatible("==1.2.3", "==1.2.3") is True
        assert self.resolver._are_python_versions_compatible("==1.2.3", "==1.2.4") is False
        assert self.resolver._are_python_versions_compatible("1.2.3", "1.2.3") is True
    
    def test_python_versions_compatible_range_specifiers(self):
        """Test Python version compatibility with range specifiers"""
        assert self.resolver._are_python_versions_compatible(">=1.2.0", ">=1.2.3") is True
        assert self.resolver._are_python_versions_compatible(">=1.2.0", "==1.2.5") is True
        assert self.resolver._are_python_versions_compatible(">=2.0.0", "==1.9.0") is False
    
    def test_python_versions_compatible_compatible_release(self):
        """Test Python version compatibility with compatible release (~=)"""
        assert self.resolver._are_python_versions_compatible("~=1.2.0", "==1.2.5") is True
        assert self.resolver._are_python_versions_compatible("~=1.2.0", "==1.3.0") is False
    
    def test_python_versions_compatible_invalid_specifiers(self):
        """Test Python version compatibility with invalid specifiers"""
        assert self.resolver._are_python_versions_compatible("invalid", "==1.2.3") is False
        assert self.resolver._are_python_versions_compatible(">=1.2.0", "invalid") is False
    
    # ========================================================================
    # Test _detect_version_conflicts method
    # ========================================================================
    
    def test_detect_version_conflicts_no_conflicts(self):
        """Test conflict detection with no conflicts"""
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="lodash", version="^4.17.0"),
                Dependency(name="axios", version="^0.27.0")
            ]
        )
        
        existing_deps = {
            "react": "^18.0.0",
            "typescript": "^4.9.0"
        }
        
        conflicts = self.resolver._detect_version_conflicts(library, existing_deps)
        
        assert len(conflicts) == 0
    
    def test_detect_version_conflicts_with_conflicts(self):
        """Test conflict detection with version conflicts"""
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="react", version="^17.0.0"),  # Conflicts with existing ^18.0.0
                Dependency(name="lodash", version="^4.17.0")   # No conflict
            ]
        )
        
        existing_deps = {
            "react": "^18.0.0",
            "typescript": "^4.9.0"
        }
        
        conflicts = self.resolver._detect_version_conflicts(library, existing_deps)
        
        assert len(conflicts) == 1
        assert conflicts[0].package == "react"
        assert conflicts[0].existing_version == "^18.0.0"
        assert conflicts[0].required_version == "^17.0.0"
    
    def test_detect_version_conflicts_multiple_conflicts(self):
        """Test conflict detection with multiple conflicts"""
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.PYPI,
            dependencies=[
                Dependency(name="django", version="==3.2.0"),    # Conflicts with existing ==4.2.0
                Dependency(name="psycopg2", version="==2.8.0")   # Conflicts with existing >=2.9.0
            ]
        )
        
        existing_deps = {
            "django": "==4.2.0",
            "psycopg2": ">=2.9.0"
        }
        
        conflicts = self.resolver._detect_version_conflicts(library, existing_deps)
        
        assert len(conflicts) == 2
        conflict_packages = [c.package for c in conflicts]
        assert "django" in conflict_packages
        assert "psycopg2" in conflict_packages
    
    # ========================================================================
    # Test detect_circular_dependencies method
    # ========================================================================
    
    def test_detect_circular_dependencies_no_cycles(self):
        """Test circular dependency detection with no cycles"""
        library = LibraryMetadata(
            name="A",
            version="1.0.0",
            description="Library A",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="B", version="1.0.0"),
                Dependency(name="C", version="1.0.0")
            ]
        )
        
        existing_deps = [
            Dependency(name="B", version="1.0.0"),
            Dependency(name="C", version="1.0.0"),
            Dependency(name="D", version="1.0.0")
        ]
        
        result = self.resolver.detect_circular_dependencies(library, existing_deps)
        
        assert result is None
    
    def test_detect_circular_dependencies_with_cycle(self):
        """Test circular dependency detection with a cycle"""
        # This is a simplified test - in reality, we'd need to mock
        # the dependency information for existing packages
        library = LibraryMetadata(
            name="A",
            version="1.0.0",
            description="Library A",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="B", version="1.0.0")
            ]
        )
        
        existing_deps = [
            Dependency(name="B", version="1.0.0")
        ]
        
        # Mock the dependency graph to create a cycle
        with patch.object(self.resolver, '_build_dependency_graph') as mock_build:
            mock_build.return_value = {
                "A": ["B"],
                "B": ["A"]  # B depends on A, creating a cycle
            }
            
            result = self.resolver.detect_circular_dependencies(library, existing_deps)
            
            assert result is not None
            assert "A" in result
            assert "B" in result
    
    # ========================================================================
    # Test suggest_compatible_version method
    # ========================================================================
    
    def test_suggest_compatible_version_npm_exact(self):
        """Test version suggestion for npm with exact versions"""
        constraints = ["1.2.3", "1.2.3"]
        
        result = self.resolver.suggest_compatible_version("react", constraints)
        
        assert result == "1.2.3"
    
    def test_suggest_compatible_version_npm_conflicting_exact(self):
        """Test version suggestion for npm with conflicting exact versions"""
        constraints = ["1.2.3", "1.2.4"]
        
        result = self.resolver.suggest_compatible_version("react", constraints)
        
        assert result is None
    
    def test_suggest_compatible_version_npm_ranges(self):
        """Test version suggestion for npm with version ranges"""
        constraints = ["^1.2.0", "~1.2.3"]
        
        result = self.resolver.suggest_compatible_version("react", constraints)
        
        assert result is not None
        assert result.startswith("1.2")
    
    def test_suggest_compatible_version_python(self):
        """Test version suggestion for Python packages"""
        constraints = [">=1.2.0", "==1.2.5"]
        
        result = self.resolver.suggest_compatible_version("django", constraints)
        
        assert result == "1.2.5"
    
    def test_suggest_compatible_version_no_constraints(self):
        """Test version suggestion with no constraints"""
        result = self.resolver.suggest_compatible_version("react", [])
        
        assert result is None
    
    def test_suggest_compatible_version_invalid_constraints(self):
        """Test version suggestion with invalid constraints"""
        constraints = ["invalid", "also-invalid"]
        
        result = self.resolver.suggest_compatible_version("react", constraints)
        
        assert result is None
    
    # ========================================================================
    # Test _generate_conflict_suggestions method
    # ========================================================================
    
    def test_generate_conflict_suggestions_no_conflicts(self):
        """Test suggestion generation with no conflicts"""
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[]
        )
        
        suggestions = self.resolver._generate_conflict_suggestions([], library)
        
        assert len(suggestions) == 0
    
    def test_generate_conflict_suggestions_single_conflict(self):
        """Test suggestion generation with single conflict"""
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[]
        )
        
        conflicts = [
            ConflictInfo(
                package="react",
                existing_version="^17.0.0",
                required_version="^18.0.0"
            )
        ]
        
        suggestions = self.resolver._generate_conflict_suggestions(conflicts, library)
        
        assert len(suggestions) > 0
        assert any("Upgrade react" in s for s in suggestions)
        assert any("Find a version of test-lib" in s for s in suggestions)
    
    def test_generate_conflict_suggestions_multiple_conflicts(self):
        """Test suggestion generation with multiple conflicts"""
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[]
        )
        
        conflicts = [
            ConflictInfo(
                package="react",
                existing_version="^17.0.0",
                required_version="^18.0.0"
            ),
            ConflictInfo(
                package="lodash",
                existing_version="^3.0.0",
                required_version="^4.0.0"
            )
        ]
        
        suggestions = self.resolver._generate_conflict_suggestions(conflicts, library)
        
        assert len(suggestions) > 0
        assert any("updating multiple dependencies" in s for s in suggestions)
    
    # ========================================================================
    # Test check_conflicts method (integration)
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_check_conflicts_no_conflicts_frontend(self):
        """Test complete conflict checking with no conflicts for frontend"""
        # Create package.json with existing dependencies
        dependencies = {
            "react": "^18.0.0",
            "typescript": "^4.9.0"
        }
        self.create_package_json(dependencies=dependencies)
        
        # Library with non-conflicting dependencies
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="lodash", version="^4.17.0"),
                Dependency(name="axios", version="^0.27.0")
            ]
        )
        
        result = await self.resolver.check_conflicts(library, ProjectContext.FRONTEND)
        
        assert isinstance(result, ConflictAnalysis)
        assert result.has_conflicts is False
        assert len(result.conflicts) == 0
        assert len(result.suggestions) == 0
        assert result.circular_dependencies is None
    
    @pytest.mark.asyncio
    async def test_check_conflicts_with_conflicts_backend(self):
        """Test complete conflict checking with conflicts for backend"""
        # Create requirements.txt with existing dependencies
        requirements = [
            "django==4.2.0",
            "psycopg2>=2.9.0"
        ]
        self.create_requirements_txt(requirements=requirements)
        
        # Library with conflicting dependencies
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.PYPI,
            dependencies=[
                Dependency(name="django", version="==3.2.0"),  # Conflicts with existing
                Dependency(name="requests", version=">=2.28.0")  # No conflict
            ]
        )
        
        result = await self.resolver.check_conflicts(library, ProjectContext.BACKEND)
        
        assert isinstance(result, ConflictAnalysis)
        assert result.has_conflicts is True
        assert len(result.conflicts) == 1
        assert result.conflicts[0].package == "django"
        assert len(result.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_check_conflicts_missing_dependency_file(self):
        """Test conflict checking when dependency file doesn't exist"""
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="react", version="^18.0.0")
            ]
        )
        
        result = await self.resolver.check_conflicts(library, ProjectContext.FRONTEND)
        
        # Should succeed with no conflicts when no existing dependencies
        assert isinstance(result, ConflictAnalysis)
        assert result.has_conflicts is False
        assert len(result.conflicts) == 0
    
    # ========================================================================
    # Test error handling and edge cases
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_check_conflicts_file_parsing_error(self):
        """Test error handling when dependency file parsing fails"""
        # Create invalid package.json
        self.create_file("frontend/package.json", "invalid json")
        
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[]
        )
        
        with pytest.raises(DependencyResolverError, match="Failed to analyze dependencies"):
            await self.resolver.check_conflicts(library, ProjectContext.FRONTEND)
    
    def test_initialization_with_custom_project_root(self):
        """Test initialization with custom project root"""
        custom_root = "/custom/path"
        resolver = DependencyResolver(project_root=custom_root)
        assert resolver.project_root == Path(custom_root)
    
    def test_initialization_with_default_project_root(self):
        """Test initialization with default project root"""
        resolver = DependencyResolver()
        assert resolver.project_root == Path(".")
    
    # ========================================================================
    # Test logging and debugging
    # ========================================================================
    
    @patch('app.services.library_management.dependency_resolver.logger')
    def test_logging_on_conflict_detection(self, mock_logger):
        """Test that conflicts are logged appropriately"""
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="react", version="^17.0.0")
            ]
        )
        
        existing_deps = {"react": "^18.0.0"}
        
        self.resolver._detect_version_conflicts(library, existing_deps)
        
        # Check that warning was logged for conflict
        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Version conflict detected" in call_args
        assert "react" in call_args
    
    @patch('app.services.library_management.dependency_resolver.logger')
    @pytest.mark.asyncio
    async def test_logging_on_successful_analysis(self, mock_logger):
        """Test that successful analysis is logged"""
        self.create_package_json(dependencies={"react": "^18.0.0"})
        
        library = LibraryMetadata(
            name="test-lib",
            version="1.0.0",
            description="Test library",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[]
        )
        
        await self.resolver.check_conflicts(library, ProjectContext.FRONTEND)
        
        # Check that info logs were called
        mock_logger.info.assert_called()


# ============================================================================
# Integration-style tests
# ============================================================================

class TestDependencyResolverIntegration:
    """Integration tests for DependencyResolver with realistic scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.resolver = DependencyResolver(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_realistic_frontend_project(self):
        """Create a realistic frontend project structure"""
        package_data = {
            "name": "ai-code-review-frontend",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "next": "^14.0.0",
                "typescript": "^5.0.0",
                "tailwindcss": "^3.3.0"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "@types/react": "^18.2.0",
                "eslint": "^8.50.0"
            }
        }
        
        full_path = Path(self.temp_dir) / "frontend" / "package.json"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(package_data, indent=2))
    
    def create_realistic_backend_project(self):
        """Create a realistic backend project structure"""
        requirements = [
            "django==4.2.7",
            "djangorestframework==3.14.0",
            "psycopg2-binary==2.9.7",
            "celery==5.3.4",
            "redis==5.0.1",
            "gunicorn==21.2.0",
            "python-dotenv==1.0.0"
        ]
        
        full_path = Path(self.temp_dir) / "backend" / "requirements.txt"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("\n".join(requirements))
    
    @pytest.mark.asyncio
    async def test_realistic_frontend_library_addition_no_conflicts(self):
        """Test adding a frontend library with no conflicts"""
        self.create_realistic_frontend_project()
        
        # Add a library that doesn't conflict
        library = LibraryMetadata(
            name="axios",
            version="1.6.0",
            description="Promise based HTTP client",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="follow-redirects", version="^1.15.0"),
                Dependency(name="form-data", version="^4.0.0")
            ]
        )
        
        result = await self.resolver.check_conflicts(library, ProjectContext.FRONTEND)
        
        assert result.has_conflicts is False
        assert len(result.conflicts) == 0
        assert result.circular_dependencies is None
    
    @pytest.mark.asyncio
    async def test_realistic_frontend_library_addition_with_conflicts(self):
        """Test adding a frontend library with version conflicts"""
        self.create_realistic_frontend_project()
        
        # Add a library that requires an older version of React
        library = LibraryMetadata(
            name="old-react-component",
            version="1.0.0",
            description="Component requiring old React",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="react", version="^17.0.0"),  # Conflicts with existing ^18.2.0
                Dependency(name="prop-types", version="^15.8.0")
            ]
        )
        
        result = await self.resolver.check_conflicts(library, ProjectContext.FRONTEND)
        
        assert result.has_conflicts is True
        assert len(result.conflicts) == 1
        assert result.conflicts[0].package == "react"
        assert result.conflicts[0].existing_version == "^18.2.0"
        assert result.conflicts[0].required_version == "^17.0.0"
        assert len(result.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_realistic_backend_library_addition_no_conflicts(self):
        """Test adding a backend library with no conflicts"""
        self.create_realistic_backend_project()
        
        # Add a library that doesn't conflict
        library = LibraryMetadata(
            name="requests",
            version="2.31.0",
            description="HTTP library for Python",
            license="Apache 2.0",
            registry_type=RegistryType.PYPI,
            dependencies=[
                Dependency(name="urllib3", version=">=1.21.1,<3"),
                Dependency(name="certifi", version=">=2017.4.17")
            ]
        )
        
        result = await self.resolver.check_conflicts(library, ProjectContext.BACKEND)
        
        assert result.has_conflicts is False
        assert len(result.conflicts) == 0
        assert result.circular_dependencies is None
    
    @pytest.mark.asyncio
    async def test_realistic_backend_library_addition_with_conflicts(self):
        """Test adding a backend library with version conflicts"""
        self.create_realistic_backend_project()
        
        # Add a library that requires an incompatible Django version
        library = LibraryMetadata(
            name="old-django-package",
            version="1.0.0",
            description="Package requiring old Django",
            license="MIT",
            registry_type=RegistryType.PYPI,
            dependencies=[
                Dependency(name="django", version="==3.2.0"),  # Conflicts with existing ==4.2.7
                Dependency(name="six", version=">=1.16.0")
            ]
        )
        
        result = await self.resolver.check_conflicts(library, ProjectContext.BACKEND)
        
        assert result.has_conflicts is True
        assert len(result.conflicts) == 1
        assert result.conflicts[0].package == "django"
        assert result.conflicts[0].existing_version == "==4.2.7"
        assert result.conflicts[0].required_version == "==3.2.0"
        assert len(result.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_complex_dependency_scenario(self):
        """Test complex scenario with multiple conflicts and suggestions"""
        self.create_realistic_frontend_project()
        
        # Add a library with multiple conflicting dependencies
        library = LibraryMetadata(
            name="complex-lib",
            version="2.0.0",
            description="Library with complex dependencies",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[
                Dependency(name="react", version="^17.0.0"),      # Conflicts
                Dependency(name="typescript", version="^4.0.0"),  # Conflicts
                Dependency(name="lodash", version="^4.17.0"),     # No conflict
                Dependency(name="moment", version="^2.29.0")      # No conflict
            ]
        )
        
        result = await self.resolver.check_conflicts(library, ProjectContext.FRONTEND)
        
        assert result.has_conflicts is True
        assert len(result.conflicts) == 2  # react and typescript conflicts
        
        conflict_packages = [c.package for c in result.conflicts]
        assert "react" in conflict_packages
        assert "typescript" in conflict_packages
        
        assert len(result.suggestions) > 0
        assert any("updating multiple dependencies" in s for s in result.suggestions)