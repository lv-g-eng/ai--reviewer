"""
Test for library management database migration.

This test verifies that the migration file is correctly structured
and can be imported without errors.
"""
import pytest
import sys
from pathlib import Path


def test_migration_file_exists():
    """Test that the migration file exists."""
    migration_file = Path(__file__).parent.parent / "alembic" / "versions" / "002_add_library_management_tables.py"
    assert migration_file.exists(), "Migration file should exist"


def test_migration_imports():
    """Test that the migration file can be imported."""
    # Add the alembic versions directory to the path
    versions_dir = Path(__file__).parent.parent / "alembic" / "versions"
    sys.path.insert(0, str(versions_dir))
    
    try:
        # Import the migration module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "migration_002",
            versions_dir / "002_add_library_management_tables.py"
        )
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)
        
        # Verify the migration has required attributes
        assert hasattr(migration_module, 'revision'), "Migration should have revision"
        assert hasattr(migration_module, 'down_revision'), "Migration should have down_revision"
        assert hasattr(migration_module, 'upgrade'), "Migration should have upgrade function"
        assert hasattr(migration_module, 'downgrade'), "Migration should have downgrade function"
        
        # Verify revision IDs
        assert migration_module.revision == '002_add_library_management_tables'
        assert migration_module.down_revision == '001_initial_schema'
        
    finally:
        sys.path.pop(0)


def test_migration_structure():
    """Test that the migration has the correct structure."""
    versions_dir = Path(__file__).parent.parent / "alembic" / "versions"
    migration_file = versions_dir / "002_add_library_management_tables.py"
    
    # Read the migration file content
    content = migration_file.read_text()
    
    # Verify key elements are present
    assert "CREATE TABLE libraries" in content or "create_table" in content, "Should create libraries table"
    assert "CREATE TABLE library_dependencies" in content or "library_dependencies" in content, "Should create library_dependencies table"
    assert "registry_type" in content, "Should define registry_type enum"
    assert "project_context" in content, "Should define project_context enum"
    assert "idx_libraries_project_id" in content, "Should create index on project_id"
    assert "idx_libraries_installed_at" in content, "Should create index on installed_at"
    assert "idx_library_dependencies_library_id" in content, "Should create index on library_id"
    assert "UNIQUE" in content or "UniqueConstraint" in content, "Should have unique constraint"
    assert "def upgrade" in content, "Should have upgrade function"
    assert "def downgrade" in content, "Should have downgrade function"


def test_migration_columns():
    """Test that all required columns are defined in the migration."""
    versions_dir = Path(__file__).parent.parent / "alembic" / "versions"
    migration_file = versions_dir / "002_add_library_management_tables.py"
    
    content = migration_file.read_text()
    
    # Verify libraries table columns
    required_columns = [
        'id', 'project_id', 'name', 'version', 'registry_type',
        'project_context', 'description', 'license', 'installed_at',
        'installed_by', 'uri', 'metadata'
    ]
    
    for column in required_columns:
        assert column in content, f"Migration should define column: {column}"
    
    # Verify library_dependencies table columns
    dependency_columns = [
        'id', 'library_id', 'dependency_name', 'dependency_version', 'is_direct'
    ]
    
    for column in dependency_columns:
        assert column in content, f"Migration should define dependency column: {column}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
