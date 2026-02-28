"""Add project_accesses, sessions, and code_entities tables

Revision ID: 004_project_access_session_code_entity
Revises: 003_rbac_auth
Create Date: 2026-02-20

This migration adds tables for:
- project_accesses: Project-level access control
- sessions: User session tracking
- code_entities: Parsed code elements storage

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_project_access_session_code_entity'
down_revision = '003_rbac_auth'
branch_labels = None
depends_on = None


def upgrade():
    """Create project_accesses, sessions, and code_entities tables."""
    
    # Create project_accesses table
    op.create_table(
        'project_accesses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('access_level', sa.String(length=50), nullable=False, server_default='read'),
        sa.Column('granted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_user_access')
    )
    
    # Create indexes on project_accesses
    op.create_index('ix_project_accesses_project_id', 'project_accesses', ['project_id'])
    op.create_index('ix_project_accesses_user_id', 'project_accesses', ['user_id'])
    op.create_index('ix_project_accesses_access_level', 'project_accesses', ['access_level'])
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_jti', sa.String(length=255), nullable=False),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_jti')
    )
    
    # Create indexes on sessions
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_sessions_token_jti', 'sessions', ['token_jti'])
    op.create_index('ix_sessions_expires_at', 'sessions', ['expires_at'])
    op.create_index('ix_sessions_is_active', 'sessions', ['is_active'])
    op.create_index('ix_sessions_user_active', 'sessions', ['user_id', 'is_active'])
    
    # Create code_entities table
    op.create_table(
        'code_entities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pull_request_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('qualified_name', sa.String(length=1000), nullable=False),
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('start_line', sa.Integer(), nullable=False),
        sa.Column('end_line', sa.Integer(), nullable=False),
        sa.Column('complexity', sa.Integer(), nullable=True),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('return_type', sa.String(length=255), nullable=True),
        sa.Column('docstring', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pull_request_id'], ['pull_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes on code_entities
    op.create_index('ix_code_entities_project_id', 'code_entities', ['project_id'])
    op.create_index('ix_code_entities_pull_request_id', 'code_entities', ['pull_request_id'])
    op.create_index('ix_code_entities_entity_type', 'code_entities', ['entity_type'])
    op.create_index('ix_code_entities_name', 'code_entities', ['name'])
    op.create_index('ix_code_entities_file_path', 'code_entities', ['file_path'])
    op.create_index('idx_code_entity_project_type', 'code_entities', ['project_id', 'entity_type'])
    op.create_index('idx_code_entity_file_name', 'code_entities', ['file_path', 'name'])
    
    # Create GIN indexes for JSONB columns
    op.create_index('ix_code_entities_parameters', 'code_entities', ['parameters'], postgresql_using='gin')
    op.create_index('ix_code_entities_metadata', 'code_entities', ['metadata'], postgresql_using='gin')


def downgrade():
    """Drop project_accesses, sessions, and code_entities tables."""
    
    # Drop code_entities table and indexes
    op.drop_index('ix_code_entities_metadata', table_name='code_entities')
    op.drop_index('ix_code_entities_parameters', table_name='code_entities')
    op.drop_index('idx_code_entity_file_name', table_name='code_entities')
    op.drop_index('idx_code_entity_project_type', table_name='code_entities')
    op.drop_index('ix_code_entities_file_path', table_name='code_entities')
    op.drop_index('ix_code_entities_name', table_name='code_entities')
    op.drop_index('ix_code_entities_entity_type', table_name='code_entities')
    op.drop_index('ix_code_entities_pull_request_id', table_name='code_entities')
    op.drop_index('ix_code_entities_project_id', table_name='code_entities')
    op.drop_table('code_entities')
    
    # Drop sessions table and indexes
    op.drop_index('ix_sessions_user_active', table_name='sessions')
    op.drop_index('ix_sessions_is_active', table_name='sessions')
    op.drop_index('ix_sessions_expires_at', table_name='sessions')
    op.drop_index('ix_sessions_token_jti', table_name='sessions')
    op.drop_index('ix_sessions_user_id', table_name='sessions')
    op.drop_table('sessions')
    
    # Drop project_accesses table and indexes
    op.drop_index('ix_project_accesses_access_level', table_name='project_accesses')
    op.drop_index('ix_project_accesses_user_id', table_name='project_accesses')
    op.drop_index('ix_project_accesses_project_id', table_name='project_accesses')
    op.drop_table('project_accesses')
