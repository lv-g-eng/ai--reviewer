"""
Unit tests for library management SQLAlchemy models
"""
import pytest
from datetime import datetime

from app.models.library import Library, LibraryDependency, RegistryType, ProjectContext


def test_library_enum_values():
    """Test that enum values are correctly defined"""
    # Test RegistryType enum
    assert RegistryType.NPM.value == "npm"
    assert RegistryType.PYPI.value == "pypi"
    assert RegistryType.MAVEN.value == "maven"
    
    # Test ProjectContext enum
    assert ProjectContext.BACKEND.value == "backend"
    assert ProjectContext.FRONTEND.value == "frontend"
    assert ProjectContext.SERVICES.value == "services"


def test_library_model_attributes():
    """Test that Library model has all required attributes"""
    library = Library(
        project_id="test-project-123",
        name="react",
        version="18.0.0",
        registry_type=RegistryType.NPM,
        project_context=ProjectContext.FRONTEND,
        description="A JavaScript library for building user interfaces",
        license="MIT",
        installed_by="user@example.com",
        uri="npm:react@18.0.0",
        library_metadata={"homepage": "https://reactjs.org"}
    )
    
    # Verify attributes are set correctly
    assert library.project_id == "test-project-123"
    assert library.name == "react"
    assert library.version == "18.0.0"
    assert library.registry_type == RegistryType.NPM
    assert library.project_context == ProjectContext.FRONTEND
    assert library.description == "A JavaScript library for building user interfaces"
    assert library.license == "MIT"
    assert library.installed_by == "user@example.com"
    assert library.uri == "npm:react@18.0.0"
    assert library.library_metadata == {"homepage": "https://reactjs.org"}


def test_library_dependency_model_attributes():
    """Test that LibraryDependency model has all required attributes"""
    dep = LibraryDependency(
        library_id=1,
        dependency_name="body-parser",
        dependency_version="1.20.0",
        is_direct=True
    )
    
    # Verify attributes are set correctly
    assert dep.library_id == 1
    assert dep.dependency_name == "body-parser"
    assert dep.dependency_version == "1.20.0"
    assert dep.is_direct is True


def test_library_repr():
    """Test the string representation of Library model"""
    library = Library(
        project_id="test-project-123",
        name="django",
        version="4.2.0",
        registry_type=RegistryType.PYPI,
        project_context=ProjectContext.BACKEND,
        installed_by="user@example.com",
        uri="pypi:django==4.2.0"
    )
    
    assert repr(library) == "<Library django@4.2.0 (pypi)>"


def test_library_dependency_repr():
    """Test the string representation of LibraryDependency model"""
    dep = LibraryDependency(
        library_id=1,
        dependency_name="pytest",
        dependency_version="7.4.0",
        is_direct=True
    )
    
    assert repr(dep) == "<LibraryDependency pytest@7.4.0>"


def test_library_table_name():
    """Test that table names are correctly set"""
    assert Library.__tablename__ == "libraries"
    assert LibraryDependency.__tablename__ == "library_dependencies"


def test_library_model_has_relationship():
    """Test that Library model has dependencies relationship"""
    assert hasattr(Library, 'dependencies')


def test_library_dependency_model_has_relationship():
    """Test that LibraryDependency model has library relationship"""
    assert hasattr(LibraryDependency, 'library')

