"""
Property-based tests for Library Repository Service
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.library_management.library_repository import LibraryRepository
from app.models.library import RegistryType, ProjectContext
from app.schemas.library import InstalledLibrary, Dependency


# Hypothesis strategies for generating test data
registry_types = st.sampled_from([RegistryType.NPM, RegistryType.PYPI, RegistryType.MAVEN])
project_contexts = st.sampled_from([ProjectContext.BACKEND, ProjectContext.FRONTEND, ProjectContext.SERVICES])

# Generate valid library names based on registry type
def library_name_strategy(registry_type):
    """Generate valid library names based on registry type"""
    if registry_type == RegistryType.NPM:
        # npm allows scoped packages like @types/node
        return st.one_of(
            st.from_regex(r'^[a-z0-9][a-z0-9\-]{0,50}$'),  # regular packages
            st.from_regex(r'^@[a-z0-9\-]+/[a-z0-9][a-z0-9\-]{0,50}$')  # scoped packages
        )
    elif registry_type == RegistryType.PYPI:
        # PyPI allows letters, numbers, hyphens, underscores, periods
        return st.from_regex(r'^[a-zA-Z0-9][a-zA-Z0-9\-_.]{0,50}$')
    else:  # MAVEN
        # Maven uses group:artifact format, but we store just artifact name
        return st.from_regex(r'^[a-z0-9][a-z0-9\-]{0,50}$')

# Generate semantic versions
version_strategy = st.from_regex(r'^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9\-]+)?$')

# Generate project IDs
project_id_strategy = st.from_regex(r'^[a-zA-Z0-9\-]{1,100}$')

# Generate user IDs
user_id_strategy = st.from_regex(r'^[a-zA-Z0-9\-]{1,50}$')

# Generate URIs based on registry type
def uri_strategy(registry_type, name, version):
    """Generate valid URIs based on registry type"""
    if registry_type == RegistryType.NPM:
        return f"npm:{name}@{version}"
    elif registry_type == RegistryType.PYPI:
        return f"pypi:{name}=={version}"
    else:  # MAVEN
        return f"maven:com.example:{name}:{version}"

# Generate dependencies
dependency_strategy = st.builds(
    Dependency,
    name=st.from_regex(r'^[a-zA-Z0-9][a-zA-Z0-9\-_.]{0,30}$'),
    version=version_strategy,
    is_direct=st.booleans()
)

# Generate installed libraries
@st.composite
def installed_library_strategy(draw):
    """Generate InstalledLibrary instances"""
    registry_type = draw(registry_types)
    project_context = draw(project_contexts)
    name = draw(library_name_strategy(registry_type))
    version = draw(version_strategy)
    project_id = draw(project_id_strategy)
    user_id = draw(user_id_strategy)
    
    return InstalledLibrary(
        project_id=project_id,
        name=name,
        version=version,
        registry_type=registry_type,
        project_context=project_context,
        description=draw(st.text(min_size=0, max_size=500)),
        license=draw(st.text(min_size=1, max_size=50)),
        installed_at=draw(st.datetimes(
            min_value=datetime(2020, 1, 1),  # Remove timezone info
            max_value=datetime(2024, 12, 31)  # Remove timezone info
        ).map(lambda dt: dt.replace(tzinfo=timezone.utc))),  # Add timezone after generation
        installed_by=user_id,
        uri=uri_strategy(registry_type, name, version),
        metadata=draw(st.one_of(
            st.none(),
            st.dictionaries(
                st.text(min_size=1, max_size=20),
                st.one_of(st.text(max_size=100), st.integers(), st.booleans()),
                max_size=5
            )
        ))
    )


@pytest.mark.asyncio
class TestLibraryRepositoryProperties:
    """Property-based tests for LibraryRepository"""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_db_session):
        """Create LibraryRepository instance with mock session"""
        return LibraryRepository(mock_db_session)

    # Feature: library-management, Property 11: Database Storage Completeness
    @given(installed_library_strategy())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_database_storage_completeness(self, repository, mock_db_session, library):
        """
        Property 11: For any successfully installed library, the database should contain 
        a record with all required fields: name, version, installation date, project context, 
        installed_by user, and project association.
        """
        # Mock successful database operations
        mock_library = MagicMock()
        mock_library.id = 42
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        
        with patch('app.services.library_management.library_repository.Library') as mock_library_class:
            mock_library_class.return_value = mock_library
            
            # Execute save operation
            result = await repository.save_library(library)
            
            # Verify all required fields are stored
            call_args = mock_library_class.call_args[1]
            
            # Check all required fields are present and not None/empty
            assert call_args['project_id'] == library.project_id
            assert call_args['name'] == library.name
            assert call_args['version'] == library.version
            assert call_args['registry_type'] == library.registry_type
            assert call_args['project_context'] == library.project_context
            assert call_args['installed_at'] == library.installed_at
            assert call_args['installed_by'] == library.installed_by
            assert call_args['uri'] == library.uri
            
            # Verify description and license are handled (can be empty but not None)
            assert call_args['description'] is not None
            assert call_args['license'] is not None
            
            # Verify metadata is handled (None becomes empty dict)
            assert call_args['library_metadata'] is not None
            if library.metadata is None:
                assert call_args['library_metadata'] == {}
            else:
                assert call_args['library_metadata'] == library.metadata
            
            # Verify database operations were called
            mock_db_session.add.assert_called_once()
            mock_db_session.flush.assert_called_once()
            
            # Verify return value is the library ID
            assert result == 42

    # Feature: library-management, Property 12: Library Query Correctness
    @given(
        project_id=project_id_strategy,
        context=st.one_of(st.none(), project_contexts),
        libraries=st.lists(installed_library_strategy(), min_size=0, max_size=10)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_library_query_correctness(self, repository, mock_db_session, project_id, context, libraries):
        """
        Property 12: For any query filter (project, date, or user), the repository should 
        return only libraries that match the filter criteria and should return all libraries that match.
        """
        # Filter libraries that should match the query
        expected_libraries = []
        for lib in libraries:
            # Set project_id to match for some libraries
            if len(expected_libraries) < len(libraries) // 2:
                lib.project_id = project_id
                if context is None or lib.project_context == context:
                    expected_libraries.append(lib)
        
        # Mock database result
        mock_db_libraries = []
        for lib in expected_libraries:
            mock_db_lib = MagicMock()
            mock_db_lib.id = len(mock_db_libraries) + 1
            mock_db_lib.project_id = lib.project_id
            mock_db_lib.name = lib.name
            mock_db_lib.version = lib.version
            mock_db_lib.registry_type = lib.registry_type
            mock_db_lib.project_context = lib.project_context
            mock_db_lib.description = lib.description
            mock_db_lib.license = lib.license
            mock_db_lib.installed_at = lib.installed_at
            mock_db_lib.installed_by = lib.installed_by
            mock_db_lib.uri = lib.uri
            mock_db_lib.library_metadata = lib.metadata or {}
            mock_db_libraries.append(mock_db_lib)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_db_libraries
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute query
        result_libraries = await repository.get_libraries_by_project(project_id, context)
        
        # Verify query correctness
        assert len(result_libraries) == len(expected_libraries)
        
        for i, result_lib in enumerate(result_libraries):
            expected_lib = expected_libraries[i]
            
            # Verify all returned libraries match the filter criteria
            assert result_lib.project_id == project_id
            if context is not None:
                assert result_lib.project_context == context
            
            # Verify all expected data is returned
            assert result_lib.name == expected_lib.name
            assert result_lib.version == expected_lib.version
            assert result_lib.registry_type == expected_lib.registry_type
            assert result_lib.project_context == expected_lib.project_context

    # Feature: library-management, Property: Dependency Storage Consistency
    @given(
        library_id=st.integers(min_value=1, max_value=1000),
        dependencies=st.lists(dependency_strategy, min_size=0, max_size=20)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_dependency_storage_consistency(self, repository, mock_db_session, library_id, dependencies):
        """
        Property: For any library and its dependencies, saving and retrieving dependencies 
        should return the exact same dependency list with all fields preserved.
        """
        # Mock library exists
        mock_library = MagicMock()
        mock_library.name = "test-lib"
        mock_library_result = MagicMock()
        mock_library_result.scalar_one_or_none.return_value = mock_library
        
        # Mock dependency retrieval
        mock_db_dependencies = []
        for dep in dependencies:
            mock_db_dep = MagicMock()
            mock_db_dep.dependency_name = dep.name
            mock_db_dep.dependency_version = dep.version
            mock_db_dep.is_direct = dep.is_direct
            mock_db_dependencies.append(mock_db_dep)
        
        mock_deps_result = MagicMock()
        mock_deps_result.scalars.return_value.all.return_value = mock_db_dependencies
        
        # Setup mock to return library for save, then library + deps for retrieve
        mock_db_session.execute = AsyncMock(side_effect=[
            mock_library_result,  # save_dependencies library check
            mock_library_result,  # get_library_dependencies library check  
            mock_deps_result      # get_library_dependencies deps query
        ])
        mock_db_session.add = MagicMock()
        
        # Save dependencies
        await repository.save_dependencies(library_id, dependencies)
        
        # Retrieve dependencies
        retrieved_dependencies = await repository.get_library_dependencies(library_id)
        
        # Verify consistency
        assert len(retrieved_dependencies) == len(dependencies)
        
        # Sort both lists by name for comparison
        original_sorted = sorted(dependencies, key=lambda d: d.name)
        retrieved_sorted = sorted(retrieved_dependencies, key=lambda d: d.name)
        
        for orig, retr in zip(original_sorted, retrieved_sorted):
            assert retr.name == orig.name
            assert retr.version == orig.version
            assert retr.is_direct == orig.is_direct

    # Feature: library-management, Property: Version Update Consistency
    @given(
        library_id=st.integers(min_value=1, max_value=1000),
        old_version=version_strategy,
        new_version=version_strategy
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_version_update_consistency(self, repository, mock_db_session, library_id, old_version, new_version):
        """
        Property: For any library version update, the operation should either succeed completely 
        or fail without partial updates.
        """
        assume(old_version != new_version)  # Only test actual version changes
        
        # Mock library exists with old version
        mock_library = MagicMock()
        mock_library.name = "test-lib"
        mock_library.version = old_version
        mock_library_result = MagicMock()
        mock_library_result.scalar_one_or_none.return_value = mock_library
        
        mock_db_session.execute = AsyncMock(return_value=mock_library_result)
        
        # Execute version update
        await repository.update_library_version(library_id, new_version)
        
        # Verify update operation was attempted
        assert mock_db_session.execute.call_count == 2  # select + update
        
        # Verify no rollback was called (indicating success)
        mock_db_session.rollback.assert_not_called()

    # Feature: library-management, Property: User Query Isolation
    @given(
        user1=user_id_strategy,
        user2=user_id_strategy,
        project_id=project_id_strategy,
        libraries_user1=st.lists(installed_library_strategy(), min_size=0, max_size=5),
        libraries_user2=st.lists(installed_library_strategy(), min_size=0, max_size=5)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_user_query_isolation(self, repository, mock_db_session, user1, user2, project_id, libraries_user1, libraries_user2):
        """
        Property: For any user query, only libraries installed by that specific user should be returned,
        ensuring proper user isolation.
        """
        assume(user1 != user2)  # Ensure different users
        
        # Set up libraries for user1
        for lib in libraries_user1:
            lib.installed_by = user1
            lib.project_id = project_id
        
        # Mock database result for user1 query
        mock_db_libraries_user1 = []
        for lib in libraries_user1:
            mock_db_lib = MagicMock()
            mock_db_lib.id = len(mock_db_libraries_user1) + 1
            mock_db_lib.project_id = lib.project_id
            mock_db_lib.name = lib.name
            mock_db_lib.version = lib.version
            mock_db_lib.registry_type = lib.registry_type
            mock_db_lib.project_context = lib.project_context
            mock_db_lib.description = lib.description
            mock_db_lib.license = lib.license
            mock_db_lib.installed_at = lib.installed_at
            mock_db_lib.installed_by = lib.installed_by
            mock_db_lib.uri = lib.uri
            mock_db_lib.library_metadata = lib.metadata or {}
            mock_db_libraries_user1.append(mock_db_lib)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_db_libraries_user1
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Query libraries for user1
        result_libraries = await repository.get_libraries_by_user(user1, project_id)
        
        # Verify user isolation
        assert len(result_libraries) == len(libraries_user1)
        
        for result_lib in result_libraries:
            # All returned libraries should belong to user1
            assert result_lib.installed_by == user1
            assert result_lib.project_id == project_id

    # Feature: library-management, Property: Date Range Query Accuracy
    @given(
        project_id=project_id_strategy,
        start_date=st.datetimes(
            min_value=datetime(2020, 1, 1, tzinfo=timezone.utc),
            max_value=datetime(2023, 12, 31, tzinfo=timezone.utc)
        ),
        libraries=st.lists(installed_library_strategy(), min_size=0, max_size=10)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_date_range_query_accuracy(self, repository, mock_db_session, project_id, start_date, libraries):
        """
        Property: For any date range query, only libraries installed within that date range 
        should be returned, with accurate date filtering.
        """
        end_date = start_date + timedelta(days=30)  # 30-day range
        
        # Filter libraries that should be in the date range
        expected_libraries = []
        for lib in libraries:
            lib.project_id = project_id
            # Set some libraries to be in range, others out of range
            if len(expected_libraries) < len(libraries) // 2:
                # Set installation date within range
                lib.installed_at = start_date + timedelta(
                    days=len(expected_libraries),
                    hours=len(expected_libraries)
                )
                if start_date <= lib.installed_at <= end_date:
                    expected_libraries.append(lib)
        
        # Mock database result
        mock_db_libraries = []
        for lib in expected_libraries:
            mock_db_lib = MagicMock()
            mock_db_lib.id = len(mock_db_libraries) + 1
            mock_db_lib.project_id = lib.project_id
            mock_db_lib.name = lib.name
            mock_db_lib.version = lib.version
            mock_db_lib.registry_type = lib.registry_type
            mock_db_lib.project_context = lib.project_context
            mock_db_lib.description = lib.description
            mock_db_lib.license = lib.license
            mock_db_lib.installed_at = lib.installed_at
            mock_db_lib.installed_by = lib.installed_by
            mock_db_lib.uri = lib.uri
            mock_db_lib.library_metadata = lib.metadata or {}
            mock_db_libraries.append(mock_db_lib)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_db_libraries
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute date range query
        result_libraries = await repository.get_libraries_by_date_range(
            project_id, start_date, end_date
        )
        
        # Verify date range accuracy
        assert len(result_libraries) == len(expected_libraries)
        
        for result_lib in result_libraries:
            # All returned libraries should be within the date range
            assert start_date <= result_lib.installed_at <= end_date
            assert result_lib.project_id == project_id

    # Feature: library-management, Property: Library Deletion Completeness
    @given(library_id=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_library_deletion_completeness(self, repository, mock_db_session, library_id):
        """
        Property: For any library deletion operation, the operation should either 
        completely remove the library and all its dependencies, or fail without partial deletion.
        """
        # Mock library exists
        mock_library = MagicMock()
        mock_library.name = "test-lib"
        mock_library.version = "1.0.0"
        mock_library_result = MagicMock()
        mock_library_result.scalar_one_or_none.return_value = mock_library
        
        mock_db_session.execute = AsyncMock(return_value=mock_library_result)
        
        # Execute deletion
        result = await repository.delete_library(library_id)
        
        # Verify deletion was attempted
        assert result is True
        assert mock_db_session.execute.call_count == 2  # select + delete
        
        # Verify no rollback was called (indicating success)
        mock_db_session.rollback.assert_not_called()

    # Feature: library-management, Property: Unique Constraint Handling
    @given(installed_library_strategy())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_unique_constraint_handling(self, repository, mock_db_session, library):
        """
        Property: For any library that violates unique constraints (same name, project, context),
        the repository should handle the constraint violation gracefully with a descriptive error.
        """
        from sqlalchemy.exc import IntegrityError
        
        # Mock unique constraint violation
        error = IntegrityError("statement", "params", "duplicate key value violates unique constraint")
        error.orig = Exception("unique constraint")
        
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock(side_effect=error)
        mock_db_session.rollback = AsyncMock()
        
        # Execute and verify graceful handling
        with pytest.raises(ValueError) as exc_info:
            await repository.save_library(library)
        
        # Verify error message is descriptive and mentions the constraint violation
        error_message = str(exc_info.value)
        assert "already installed" in error_message
        assert library.name in error_message
        assert library.project_context.value in error_message
        assert library.project_id in error_message
        
        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()