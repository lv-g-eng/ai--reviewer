"""Add RBAC authentication tables

Revision ID: 003_rbac_auth
Revises: 002_add_library_management_tables
Create Date: 2026-02-19

This migration adds tables for the Enterprise RBAC Authentication System:
- rbac_users: User accounts with roles
- rbac_sessions: User sessions with JWT tokens
- rbac_projects: Projects owned by users
- rbac_project_accesses: Project access grants
- rbac_audit_logs: Audit trail for compliance

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_rbac_auth'
down_revision = '002_add_library_management_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Create RBAC authentication tables."""
    
    # Create rbac_users table
    op.create_table(
        'rbac_users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    
    # Create index on username for faster lookups
    op.create_index('ix_rbac_users_username', 'rbac_users', ['username'])
    
    # Create rbac_sessions table
    op.create_table(
        'rbac_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('device_info', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['rbac_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes on sessions for faster queries
    op.create_index('ix_rbac_sessions_user_id', 'rbac_sessions', ['user_id'])
    op.create_index('ix_rbac_sessions_token', 'rbac_sessions', ['token'])
    op.create_index('ix_rbac_sessions_expires_at', 'rbac_sessions', ['expires_at'])
    
    # Create rbac_projects table
    op.create_table(
        'rbac_projects',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['rbac_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on owner_id for faster queries
    op.create_index('ix_rbac_projects_owner_id', 'rbac_projects', ['owner_id'])
    
    # Create rbac_project_accesses table
    op.create_table(
        'rbac_project_accesses',
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('granted_by', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['rbac_projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['rbac_users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['granted_by'], ['rbac_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'user_id')
    )
    
    # Create indexes for faster access grant queries
    op.create_index('ix_rbac_project_accesses_user_id', 'rbac_project_accesses', ['user_id'])
    op.create_index('ix_rbac_project_accesses_project_id', 'rbac_project_accesses', ['project_id'])
    
    # Create rbac_audit_logs table
    op.create_table(
        'rbac_audit_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_id', sa.String(length=36), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['rbac_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for faster audit log queries
    op.create_index('ix_rbac_audit_logs_user_id', 'rbac_audit_logs', ['user_id'])
    op.create_index('ix_rbac_audit_logs_timestamp', 'rbac_audit_logs', ['timestamp'])
    op.create_index('ix_rbac_audit_logs_action', 'rbac_audit_logs', ['action'])
    op.create_index('ix_rbac_audit_logs_success', 'rbac_audit_logs', ['success'])
    
    # Insert default admin user
    # IMPORTANT: This is a placeholder hash. In production, create admin user through 
    # secure registration or use environment variables for initial setup.
    # The password hash below is a random string and will not work for login.
    op.execute("""
        INSERT INTO rbac_users (id, username, password_hash, role, created_at, updated_at, is_active)
        VALUES (
            'admin-default-id',
            'admin',
            '$2b$12$PLACEHOLDERHASHREQUIRESREPLACEMENT',
            'ADMIN',
            NOW(),
            NOW(),
            false
        )
    """)


def downgrade():
    """Drop RBAC authentication tables."""
    
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_index('ix_rbac_audit_logs_success', table_name='rbac_audit_logs')
    op.drop_index('ix_rbac_audit_logs_action', table_name='rbac_audit_logs')
    op.drop_index('ix_rbac_audit_logs_timestamp', table_name='rbac_audit_logs')
    op.drop_index('ix_rbac_audit_logs_user_id', table_name='rbac_audit_logs')
    op.drop_table('rbac_audit_logs')
    
    op.drop_index('ix_rbac_project_accesses_project_id', table_name='rbac_project_accesses')
    op.drop_index('ix_rbac_project_accesses_user_id', table_name='rbac_project_accesses')
    op.drop_table('rbac_project_accesses')
    
    op.drop_index('ix_rbac_projects_owner_id', table_name='rbac_projects')
    op.drop_table('rbac_projects')
    
    op.drop_index('ix_rbac_sessions_expires_at', table_name='rbac_sessions')
    op.drop_index('ix_rbac_sessions_token', table_name='rbac_sessions')
    op.drop_index('ix_rbac_sessions_user_id', table_name='rbac_sessions')
    op.drop_table('rbac_sessions')
    
    op.drop_index('ix_rbac_users_username', table_name='rbac_users')
    op.drop_table('rbac_users')
