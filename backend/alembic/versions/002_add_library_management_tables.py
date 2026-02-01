"""Add library management tables

Revision ID: 002_add_library_management_tables
Revises: 001_initial_schema
Create Date: 2026-01-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_library_management_tables'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None

# Constants for repeated literals
TIMESTAMP_NOW_FUNCTION = 'now()'
CREATED_AT_DESC = 'created_at DESC'
INSTALLED_AT_DESC = 'installed_at DESC'


def upgrade() -> None:
    # Create custom ENUM types for library management
    registry_type_enum = postgresql.ENUM(
        'npm', 'pypi', 'maven',
        name='registry_type',
        create_type=False
    )
    registry_type_enum.create(op.get_bind(), checkfirst=True)
    
    project_context_enum = postgresql.ENUM(
        'backend', 'frontend', 'services',
        name='project_context',
        create_type=False
    )
    project_context_enum.create(op.get_bind(), checkfirst=True)
    
    # Create libraries table
    op.create_table(
        'libraries',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('project_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('registry_type', registry_type_enum, nullable=False),
        sa.Column('project_context', project_context_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('installed_at', sa.TIMESTAMP(timezone=True), server_default=sa.text(TIMESTAMP_NOW_FUNCTION), nullable=False),
        sa.Column('installed_by', sa.String(length=255), nullable=False),
        sa.Column('uri', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'name', 'project_context', name='uq_libraries_project_name_context')
    )
    
    # Create indexes on libraries table
    op.create_index('idx_libraries_project_id', 'libraries', ['project_id'])
    op.create_index('idx_libraries_project_context', 'libraries', ['project_context'])
    op.create_index('idx_libraries_installed_at', 'libraries', [sa.text(INSTALLED_AT_DESC)])
    op.create_index('idx_libraries_project_context_composite', 'libraries', ['project_id', 'project_context'])
    op.create_index('idx_libraries_metadata', 'libraries', ['metadata'], postgresql_using='gin')
    
    # Create library_dependencies table
    op.create_table(
        'library_dependencies',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('library_id', sa.Integer(), nullable=False),
        sa.Column('dependency_name', sa.String(length=255), nullable=False),
        sa.Column('dependency_version', sa.String(length=50), nullable=False),
        sa.Column('is_direct', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.ForeignKeyConstraint(['library_id'], ['libraries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on library_dependencies table
    op.create_index('idx_library_dependencies_library_id', 'library_dependencies', ['library_id'])
    op.create_index('idx_library_dependencies_name', 'library_dependencies', ['dependency_name'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('library_dependencies')
    op.drop_table('libraries')
    
    # Drop ENUM types
    sa.Enum(name='project_context').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='registry_type').drop(op.get_bind(), checkfirst=True)
