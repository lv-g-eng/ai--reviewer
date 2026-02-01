# Migration 002: Library Management Tables

## Overview

This migration adds database tables to support the Library Management feature, which enables developers to add external libraries to the AI Code Review Platform by entering a library URI.

## Migration Details

- **Revision ID**: `002_add_library_management_tables`
- **Revises**: `001_initial_schema`
- **Created**: 2026-01-14 12:00:00

## Tables Created

### 1. libraries

Stores metadata about installed libraries for each project.

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Auto-incrementing unique identifier
- `project_id` (VARCHAR(255), NOT NULL): ID of the project this library belongs to
- `name` (VARCHAR(255), NOT NULL): Name of the library package
- `version` (VARCHAR(50), NOT NULL): Version of the installed library
- `registry_type` (ENUM, NOT NULL): Type of package registry ('npm', 'pypi', 'maven')
- `project_context` (ENUM, NOT NULL): Project context where library is installed ('backend', 'frontend', 'services')
- `description` (TEXT, NULLABLE): Library description from registry
- `license` (VARCHAR(100), NULLABLE): Library license information
- `installed_at` (TIMESTAMP WITH TIMEZONE, NOT NULL): Timestamp when library was installed (default: now())
- `installed_by` (VARCHAR(255), NOT NULL): User who installed the library
- `uri` (TEXT, NOT NULL): Original URI used to install the library
- `metadata` (JSONB, NULLABLE): Additional metadata stored as JSON

**Constraints:**
- PRIMARY KEY on `id`
- UNIQUE constraint on (`project_id`, `name`, `project_context`) - prevents duplicate libraries in same context

**Indexes:**
- `idx_libraries_project_id` on `project_id` - for querying libraries by project
- `idx_libraries_project_context` on `project_context` - for filtering by context
- `idx_libraries_installed_at` on `installed_at DESC` - for sorting by installation date
- `idx_libraries_project_context_composite` on (`project_id`, `project_context`) - for combined queries
- `idx_libraries_metadata` GIN index on `metadata` - for efficient JSONB queries

### 2. library_dependencies

Tracks dependencies for each installed library.

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Auto-incrementing unique identifier
- `library_id` (INTEGER, NOT NULL, FOREIGN KEY): References `libraries.id`
- `dependency_name` (VARCHAR(255), NOT NULL): Name of the dependency
- `dependency_version` (VARCHAR(50), NOT NULL): Version of the dependency
- `is_direct` (BOOLEAN, NOT NULL, DEFAULT true): Whether this is a direct dependency

**Constraints:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `library_id` REFERENCES `libraries(id)` ON DELETE CASCADE

**Indexes:**
- `idx_library_dependencies_library_id` on `library_id` - for querying dependencies by library
- `idx_library_dependencies_name` on `dependency_name` - for searching dependencies by name

## ENUM Types Created

### registry_type
Values: 'npm', 'pypi', 'maven'

### project_context
Values: 'backend', 'frontend', 'services'

## Requirements Satisfied

This migration satisfies the following requirements from the Library Management specification:

- **Requirement 6.1**: Store library metadata in PostgreSQL database
- **Requirement 6.2**: Store library name, version, installation date, and target project context
- **Requirement 6.3**: Store the user who added the library for audit purposes
- **Requirement 6.4**: Associate library metadata with the current project
- **Requirement 6.5**: Support querying installed libraries by project, date, or user

## Usage

### Apply Migration

```bash
cd backend
alembic upgrade head
```

### Rollback Migration

```bash
cd backend
alembic downgrade -1
```

### Verify Migration

```bash
cd backend
alembic current
```

## Example Queries

### Query all libraries for a project

```sql
SELECT * FROM libraries 
WHERE project_id = 'project-123' 
ORDER BY installed_at DESC;
```

### Query libraries by context

```sql
SELECT * FROM libraries 
WHERE project_id = 'project-123' 
  AND project_context = 'frontend';
```

### Query library with dependencies

```sql
SELECT l.*, 
       json_agg(json_build_object(
         'name', ld.dependency_name,
         'version', ld.dependency_version,
         'is_direct', ld.is_direct
       )) as dependencies
FROM libraries l
LEFT JOIN library_dependencies ld ON l.id = ld.library_id
WHERE l.project_id = 'project-123'
GROUP BY l.id;
```

### Query libraries installed by user

```sql
SELECT * FROM libraries 
WHERE installed_by = 'user@example.com' 
ORDER BY installed_at DESC;
```

### Search libraries by name

```sql
SELECT * FROM libraries 
WHERE name ILIKE '%react%';
```

### Query metadata using JSONB

```sql
SELECT * FROM libraries 
WHERE metadata @> '{"homepage": "https://reactjs.org"}';
```

## Testing

A test suite has been created at `backend/tests/test_library_migration.py` to verify:
- Migration file exists
- Migration can be imported without errors
- Migration has correct structure (upgrade/downgrade functions)
- All required columns are defined
- All required indexes are created

Run tests with:
```bash
cd backend
python -m pytest tests/test_library_migration.py -v
```

## Notes

1. The `metadata` column uses JSONB for flexible storage of additional library information
2. The GIN index on `metadata` enables efficient querying of JSON data
3. The CASCADE delete on foreign keys ensures dependencies are automatically removed when a library is deleted
4. The unique constraint prevents duplicate library installations in the same project context
5. Timestamps use timezone-aware TIMESTAMP type for accurate time tracking across timezones

## Related Files

- Migration: `backend/alembic/versions/002_add_library_management_tables.py`
- Tests: `backend/tests/test_library_migration.py`
- Design Document: `.kiro/specs/library-management/design.md`
- Requirements: `.kiro/specs/library-management/requirements.md`
- Tasks: `.kiro/specs/library-management/tasks.md`
