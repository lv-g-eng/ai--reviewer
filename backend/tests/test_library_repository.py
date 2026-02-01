"""
Unit tests for Library Repository Service
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.services.library_management.library_repository import LibraryRepository
from app.models.library import Library, LibraryDependency, RegistryType, ProjectContext
from app.schemas.library import InstalledLibrary, Dependency


@pytest.mark.asyncio
class TestLibraryRepository:
    """Test cases for LibraryRepository"""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session"""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def repository(self, mock_db_session):
        """Create LibraryRepository instance with mock session"""
        return LibraryRepository(mock_db_session)

    @pytest.fixture
    def sample_installed_library(self):
        """Create sample InstalledLibrary for testing"""
        return InstalledLibrary(
            project_id="test-project-123",
            name="react",
            version="18.2.0",
            registry_type=RegistryType.NPM,
            project_context=ProjectContext.FRONTEND,
            description="A JavaScript library for building user interfaces",
            license="MIT",
            installed_at=datetime.now(timezone.utc),
            installed_by="user-123",
            uri="npm:react@18.2.0",
            metadata={"homepage": "https://reactjs.org"}
        )

    @pytest.fixture
    def sample_db_library(self):
        """Create sample Library model for testing"""
        library = Library(
            id=1,
            project_id="test-project-123",
            name="react",
            version="18.2.0",
            registry_type=RegistryType.NPM,
            project_context=ProjectContext.FRONTEND,
            description="A JavaScript library for building user interfaces",
            license="MIT",
            installed_at=datetime.now(timezone.utc),
            installed_by="user-123",
            uri="npm:react@18.2.0",
            library_metadata={"homepage": "https://reactjs.org"}
        )
        return library

    @pytest.fixture
    def sample_dependencies(self):
        """Create sample dependencies for testing"""
        return [
            Dependency(name="prop-types", version="15.8.1", is_direct=True),
            Dependency(name="scheduler", version="0.23.0", is_direct=False)
        ]

    async def test_save_library_success(self, repository, mock_db_session, sample_installed_library):
        """Test successful library save operation"""
        # Mock database operations
        mock_library = MagicMock()
        mock_library.id = 42
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        
        # Mock the library creation to return our mock
        with patch('app.services.library_management.library_repository.Library') as mock_library_class:
            mock_library_class.return_value = mock_library
            
            # Execute
            result = await repository.save_library(sample_installed_library)
            
            # Verify
            assert result == 42
            mock_db_session.add.assert_called_once_with(mock_library)
            mock_db_session.flush.assert_called_once()
            
            # Verify library was created with correct data
            mock_library_class.assert_called_once_with(
                project_id=sample_installed_library.project_id,
                name=sample_installed_library.name,
                version=sample_installed_library.version,
                registry_type=sample_installed_library.registry_type,
                project_context=sample_installed_library.project_context,
                description=sample_installed_library.description,
                license=sample_installed_library.license,
                installed_at=sample_installed_library.installed_at,
                installed_by=sample_installed_library.installed_by,
                uri=sample_installed_library.uri,
                library_metadata=sample_installed_library.metadata
            )

    async def test_save_library_unique_constraint_violation(self, repository, mock_db_session, sample_installed_library):
        """Test handling of unique constraint violation"""
        # Mock IntegrityError with unique constraint message
        error = IntegrityError("statement", "params", "duplicate key value violates unique constraint")
        error.orig = Exception("unique constraint")
        
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock(side_effect=error)
        mock_db_session.rollback = AsyncMock()
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            await repository.save_library(sample_installed_library)
        
        assert "already installed" in str(exc_info.value)
        mock_db_session.rollback.assert_called_once()

    async def test_save_library_database_error(self, repository, mock_db_session, sample_installed_library):
        """Test handling of general database error"""
        # Mock general database error
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock(side_effect=Exception("Database connection failed"))
        mock_db_session.rollback = AsyncMock()
        
        # Execute and verify exception
        with pytest.raises(RuntimeError) as exc_info:
            await repository.save_library(sample_installed_library)
        
        assert "Failed to save library" in str(exc_info.value)
        mock_db_session.rollback.assert_called_once()

    async def test_get_libraries_by_project_success(self, repository, mock_db_session, sample_db_library):
        """Test successful retrieval of libraries by project"""
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_db_library]
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        libraries = await repository.get_libraries_by_project("test-project-123")
        
        # Verify
        assert len(libraries) == 1
        library = libraries[0]
        assert library.name == "react"
        assert library.version == "18.2.0"
        assert library.project_id == "test-project-123"
        assert library.registry_type == RegistryType.NPM
        assert library.project_context == ProjectContext.FRONTEND

    async def test_get_libraries_by_project_with_context_filter(self, repository, mock_db_session):
        """Test retrieval of libraries with context filter"""
        # Mock empty result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        libraries = await repository.get_libraries_by_project(
            "test-project-123", 
            ProjectContext.BACKEND
        )
        
        # Verify
        assert len(libraries) == 0
        mock_db_session.execute.assert_called_once()

    async def test_get_libraries_by_project_database_error(self, repository, mock_db_session):
        """Test handling of database error in get_libraries_by_project"""
        # Mock database error
        mock_db_session.execute = AsyncMock(side_effect=Exception("Query failed"))
        
        # Execute and verify exception
        with pytest.raises(RuntimeError) as exc_info:
            await repository.get_libraries_by_project("test-project-123")
        
        assert "Failed to retrieve libraries" in str(exc_info.value)

    async def test_get_library_by_name_found(self, repository, mock_db_session, sample_db_library):
        """Test successful retrieval of library by name"""
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_db_library
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        library = await repository.get_library_by_name(
            "test-project-123", 
            "react", 
            ProjectContext.FRONTEND
        )
        
        # Verify
        assert library is not None
        assert library.name == "react"
        assert library.version == "18.2.0"
        assert library.id == 1

    async def test_get_library_by_name_not_found(self, repository, mock_db_session):
        """Test retrieval of non-existent library by name"""
        # Mock empty result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        library = await repository.get_library_by_name(
            "test-project-123", 
            "nonexistent", 
            ProjectContext.FRONTEND
        )
        
        # Verify
        assert library is None

    async def test_get_library_by_name_database_error(self, repository, mock_db_session):
        """Test handling of database error in get_library_by_name"""
        # Mock database error
        mock_db_session.execute = AsyncMock(side_effect=Exception("Query failed"))
        
        # Execute and verify exception
        with pytest.raises(RuntimeError) as exc_info:
            await repository.get_library_by_name(
                "test-project-123", 
                "react", 
                ProjectContext.FRONTEND
            )
        
        assert "Failed to retrieve library" in str(exc_info.value)

    async def test_update_library_version_success(self, repository, mock_db_session, sample_db_library):
        """Test successful library version update"""
        # Mock library exists check
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_db_library
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        await repository.update_library_version(1, "18.3.0")
        
        # Verify execute was called twice (select + update)
        assert mock_db_session.execute.call_count == 2

    async def test_update_library_version_not_found(self, repository, mock_db_session):
        """Test update of non-existent library version"""
        # Mock library not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            await repository.update_library_version(999, "18.3.0")
        
        assert "Library with ID 999 not found" in str(exc_info.value)

    async def test_update_library_version_database_error(self, repository, mock_db_session, sample_db_library):
        """Test handling of database error in update_library_version"""
        # Mock library exists but update fails
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_db_library
        mock_db_session.execute = AsyncMock(side_effect=[mock_result, Exception("Update failed")])
        mock_db_session.rollback = AsyncMock()
        
        # Execute and verify exception
        with pytest.raises(RuntimeError) as exc_info:
            await repository.update_library_version(1, "18.3.0")
        
        assert "Failed to update library version" in str(exc_info.value)
        mock_db_session.rollback.assert_called_once()

    async def test_save_dependencies_success(self, repository, mock_db_session, sample_db_library, sample_dependencies):
        """Test successful saving of dependencies"""
        # Mock library exists check
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_db_library
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.add = MagicMock()
        
        # Execute
        await repository.save_dependencies(1, sample_dependencies)
        
        # Verify delete and add operations
        assert mock_db_session.execute.call_count == 2  # select + delete
        assert mock_db_session.add.call_count == 2  # two dependencies

    async def test_save_dependencies_library_not_found(self, repository, mock_db_session, sample_dependencies):
        """Test saving dependencies for non-existent library"""
        # Mock library not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            await repository.save_dependencies(999, sample_dependencies)
        
        assert "Library with ID 999 not found" in str(exc_info.value)

    async def test_save_dependencies_database_error(self, repository, mock_db_session, sample_db_library, sample_dependencies):
        """Test handling of database error in save_dependencies"""
        # Mock library exists but save fails
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_db_library
        mock_db_session.execute = AsyncMock(side_effect=[mock_result, Exception("Save failed")])
        mock_db_session.rollback = AsyncMock()
        
        # Execute and verify exception
        with pytest.raises(RuntimeError) as exc_info:
            await repository.save_dependencies(1, sample_dependencies)
        
        assert "Failed to save dependencies" in str(exc_info.value)
        mock_db_session.rollback.assert_called_once()

    async def test_get_library_dependencies_success(self, repository, mock_db_session, sample_db_library):
        """Test successful retrieval of library dependencies"""
        # Mock library exists
        mock_library_result = MagicMock()
        mock_library_result.scalar_one_or_none.return_value = sample_db_library
        
        # Mock dependencies
        mock_dep1 = MagicMock()
        mock_dep1.dependency_name = "prop-types"
        mock_dep1.dependency_version = "15.8.1"
        mock_dep1.is_direct = True
        
        mock_dep2 = MagicMock()
        mock_dep2.dependency_name = "scheduler"
        mock_dep2.dependency_version = "0.23.0"
        mock_dep2.is_direct = False
        
        mock_deps_result = MagicMock()
        mock_deps_result.scalars.return_value.all.return_value = [mock_dep1, mock_dep2]
        
        mock_db_session.execute = AsyncMock(side_effect=[mock_library_result, mock_deps_result])
        
        # Execute
        dependencies = await repository.get_library_dependencies(1)
        
        # Verify
        assert len(dependencies) == 2
        assert dependencies[0].name == "prop-types"
        assert dependencies[0].version == "15.8.1"
        assert dependencies[0].is_direct is True
        assert dependencies[1].name == "scheduler"
        assert dependencies[1].version == "0.23.0"
        assert dependencies[1].is_direct is False

    async def test_get_library_dependencies_library_not_found(self, repository, mock_db_session):
        """Test getting dependencies for non-existent library"""
        # Mock library not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            await repository.get_library_dependencies(999)
        
        assert "Library with ID 999 not found" in str(exc_info.value)

    async def test_delete_library_success(self, repository, mock_db_session, sample_db_library):
        """Test successful library deletion"""
        # Mock library exists
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_db_library
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await repository.delete_library(1)
        
        # Verify
        assert result is True
        assert mock_db_session.execute.call_count == 2  # select + delete

    async def test_delete_library_not_found(self, repository, mock_db_session):
        """Test deletion of non-existent library"""
        # Mock library not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await repository.delete_library(999)
        
        # Verify
        assert result is False

    async def test_delete_library_database_error(self, repository, mock_db_session, sample_db_library):
        """Test handling of database error in delete_library"""
        # Mock library exists but delete fails
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_db_library
        mock_db_session.execute = AsyncMock(side_effect=[mock_result, Exception("Delete failed")])
        mock_db_session.rollback = AsyncMock()
        
        # Execute and verify exception
        with pytest.raises(RuntimeError) as exc_info:
            await repository.delete_library(1)
        
        assert "Failed to delete library" in str(exc_info.value)
        mock_db_session.rollback.assert_called_once()

    async def test_get_libraries_by_user_success(self, repository, mock_db_session, sample_db_library):
        """Test successful retrieval of libraries by user"""
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_db_library]
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        libraries = await repository.get_libraries_by_user("user-123")
        
        # Verify
        assert len(libraries) == 1
        assert libraries[0].installed_by == "user-123"

    async def test_get_libraries_by_user_with_project_filter(self, repository, mock_db_session):
        """Test retrieval of libraries by user with project filter"""
        # Mock empty result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        libraries = await repository.get_libraries_by_user("user-123", "test-project-123")
        
        # Verify
        assert len(libraries) == 0
        mock_db_session.execute.assert_called_once()

    async def test_get_libraries_by_date_range_success(self, repository, mock_db_session, sample_db_library):
        """Test successful retrieval of libraries by date range"""
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_db_library]
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
        
        # Execute
        libraries = await repository.get_libraries_by_date_range(
            "test-project-123", 
            start_date, 
            end_date
        )
        
        # Verify
        assert len(libraries) == 1
        assert libraries[0].project_id == "test-project-123"

    async def test_get_libraries_by_date_range_with_context_filter(self, repository, mock_db_session):
        """Test retrieval of libraries by date range with context filter"""
        # Mock empty result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
        
        # Execute
        libraries = await repository.get_libraries_by_date_range(
            "test-project-123", 
            start_date, 
            end_date,
            ProjectContext.BACKEND
        )
        
        # Verify
        assert len(libraries) == 0
        mock_db_session.execute.assert_called_once()

    async def test_get_libraries_by_date_range_database_error(self, repository, mock_db_session):
        """Test handling of database error in get_libraries_by_date_range"""
        # Mock database error
        mock_db_session.execute = AsyncMock(side_effect=Exception("Query failed"))
        
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
        
        # Execute and verify exception
        with pytest.raises(RuntimeError) as exc_info:
            await repository.get_libraries_by_date_range(
                "test-project-123", 
                start_date, 
                end_date
            )
        
        assert "Failed to retrieve libraries" in str(exc_info.value)


@pytest.mark.asyncio
class TestLibraryRepositoryEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_db_session):
        """Create LibraryRepository instance with mock session"""
        return LibraryRepository(mock_db_session)

    async def test_save_library_with_empty_metadata(self, repository, mock_db_session):
        """Test saving library with None metadata"""
        library = InstalledLibrary(
            project_id="test-project",
            name="test-lib",
            version="1.0.0",
            registry_type=RegistryType.NPM,
            project_context=ProjectContext.FRONTEND,
            description="Test library",
            license="MIT",
            installed_at=datetime.now(timezone.utc),
            installed_by="user-123",
            uri="npm:test-lib@1.0.0",
            metadata=None  # None metadata
        )
        
        # Mock successful save
        mock_library = MagicMock()
        mock_library.id = 1
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        
        with patch('app.services.library_management.library_repository.Library') as mock_library_class:
            mock_library_class.return_value = mock_library
            
            result = await repository.save_library(library)
            
            # Verify metadata was converted to empty dict
            call_args = mock_library_class.call_args[1]
            assert call_args['library_metadata'] == {}

    async def test_save_dependencies_empty_list(self, repository, mock_db_session):
        """Test saving empty dependencies list"""
        # Mock library exists
        mock_library = MagicMock()
        mock_library.name = "test-lib"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_library
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.add = MagicMock()
        
        # Execute with empty dependencies
        await repository.save_dependencies(1, [])
        
        # Verify delete was called but no add operations
        assert mock_db_session.execute.call_count == 2  # select + delete
        mock_db_session.add.assert_not_called()

    async def test_get_libraries_by_project_empty_project_id(self, repository, mock_db_session):
        """Test querying with empty project ID"""
        # Mock empty result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute with empty project ID
        libraries = await repository.get_libraries_by_project("")
        
        # Should still work but return empty list
        assert len(libraries) == 0

    async def test_library_with_special_characters_in_name(self, repository, mock_db_session):
        """Test handling library names with special characters"""
        library = InstalledLibrary(
            project_id="test-project",
            name="@types/node",  # npm scoped package
            version="18.0.0",
            registry_type=RegistryType.NPM,
            project_context=ProjectContext.BACKEND,
            description="TypeScript definitions for Node.js",
            license="MIT",
            installed_at=datetime.now(timezone.utc),
            installed_by="user-123",
            uri="npm:@types/node@18.0.0"
        )
        
        # Mock successful save
        mock_library = MagicMock()
        mock_library.id = 1
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        
        with patch('app.services.library_management.library_repository.Library') as mock_library_class:
            mock_library_class.return_value = mock_library
            
            result = await repository.save_library(library)
            
            # Verify special characters are handled correctly
            call_args = mock_library_class.call_args[1]
            assert call_args['name'] == "@types/node"

    async def test_library_with_very_long_description(self, repository, mock_db_session):
        """Test handling library with very long description"""
        long_description = "A" * 10000  # Very long description
        
        library = InstalledLibrary(
            project_id="test-project",
            name="test-lib",
            version="1.0.0",
            registry_type=RegistryType.PYPI,
            project_context=ProjectContext.BACKEND,
            description=long_description,
            license="MIT",
            installed_at=datetime.now(timezone.utc),
            installed_by="user-123",
            uri="pypi:test-lib==1.0.0"
        )
        
        # Mock successful save
        mock_library = MagicMock()
        mock_library.id = 1
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        
        with patch('app.services.library_management.library_repository.Library') as mock_library_class:
            mock_library_class.return_value = mock_library
            
            result = await repository.save_library(library)
            
            # Verify long description is handled
            call_args = mock_library_class.call_args[1]
            assert call_args['description'] == long_description