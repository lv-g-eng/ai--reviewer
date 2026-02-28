"""Add audit_log_entries table with immutability features

Revision ID: 007
Revises: 006
Create Date: 2024-01-15 10:00:00.000000

This migration creates the audit_log_entries table with:
- Append-only design (no UPDATE or DELETE permissions)
- Hash chain for tamper detection
- Comprehensive indexing for efficient queries
- 7-year default retention period

Validates Requirements: 15.5
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create audit_log_entries table with immutability constraints"""
    
    # Create audit_log_entries table
    op.create_table(
        'audit_log_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('previous_hash', sa.String(length=64), nullable=True),
        sa.Column('current_hash', sa.String(length=64), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_category', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='info'),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('resource_name', sa.String(length=500), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('user_role', sa.String(length=50), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_path', sa.String(length=1000), nullable=True),
        sa.Column('action', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('previous_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_frameworks', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('retention_until', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('current_hash', name='uq_audit_log_current_hash')
    )
    
    # Create indexes for efficient querying
    op.create_index('idx_audit_timestamp', 'audit_log_entries', ['timestamp'], unique=False)
    op.create_index('idx_audit_timestamp_desc', 'audit_log_entries', [sa.text('timestamp DESC')], unique=False)
    op.create_index('idx_audit_user_timestamp', 'audit_log_entries', ['user_id', sa.text('timestamp DESC')], unique=False)
    op.create_index('idx_audit_event_timestamp', 'audit_log_entries', ['event_type', sa.text('timestamp DESC')], unique=False)
    op.create_index('idx_audit_resource', 'audit_log_entries', ['resource_type', 'resource_id'], unique=False)
    op.create_index('idx_audit_category_timestamp', 'audit_log_entries', ['event_category', sa.text('timestamp DESC')], unique=False)
    op.create_index('idx_audit_ip_timestamp', 'audit_log_entries', ['ip_address', sa.text('timestamp DESC')], unique=False)
    op.create_index('idx_audit_previous_hash', 'audit_log_entries', ['previous_hash'], unique=False)
    op.create_index('idx_audit_event_type', 'audit_log_entries', ['event_type'], unique=False)
    op.create_index('idx_audit_user_id', 'audit_log_entries', ['user_id'], unique=False)
    op.create_index('idx_audit_user_email', 'audit_log_entries', ['user_email'], unique=False)
    op.create_index('idx_audit_resource_type', 'audit_log_entries', ['resource_type'], unique=False)
    op.create_index('idx_audit_resource_id', 'audit_log_entries', ['resource_id'], unique=False)
    op.create_index('idx_audit_action', 'audit_log_entries', ['action'], unique=False)
    op.create_index('idx_audit_success', 'audit_log_entries', ['success'], unique=False)
    op.create_index('idx_audit_retention_until', 'audit_log_entries', ['retention_until'], unique=False)
    op.create_index('idx_audit_request_id', 'audit_log_entries', ['request_id'], unique=False)
    
    # Create function to prevent updates and deletes (immutability)
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'UPDATE' THEN
                RAISE EXCEPTION 'Audit log entries are immutable and cannot be updated';
            END IF;
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'Audit log entries are immutable and cannot be deleted';
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger to enforce immutability
    op.execute("""
        CREATE TRIGGER prevent_audit_log_modification_trigger
        BEFORE UPDATE OR DELETE ON audit_log_entries
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_log_modification();
    """)
    
    # Revoke UPDATE and DELETE permissions from all roles
    op.execute("""
        REVOKE UPDATE, DELETE ON audit_log_entries FROM PUBLIC;
    """)
    
    # Add comment to table
    op.execute("""
        COMMENT ON TABLE audit_log_entries IS 
        'Immutable audit log table with hash chain for tamper detection. 
        Entries cannot be modified or deleted after creation.';
    """)


def downgrade() -> None:
    """Remove audit_log_entries table and related objects"""
    
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS prevent_audit_log_modification_trigger ON audit_log_entries;")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_log_modification();")
    
    # Drop indexes (will be dropped automatically with table, but explicit for clarity)
    op.drop_index('idx_audit_request_id', table_name='audit_log_entries')
    op.drop_index('idx_audit_retention_until', table_name='audit_log_entries')
    op.drop_index('idx_audit_success', table_name='audit_log_entries')
    op.drop_index('idx_audit_action', table_name='audit_log_entries')
    op.drop_index('idx_audit_resource_id', table_name='audit_log_entries')
    op.drop_index('idx_audit_resource_type', table_name='audit_log_entries')
    op.drop_index('idx_audit_user_email', table_name='audit_log_entries')
    op.drop_index('idx_audit_user_id', table_name='audit_log_entries')
    op.drop_index('idx_audit_event_type', table_name='audit_log_entries')
    op.drop_index('idx_audit_previous_hash', table_name='audit_log_entries')
    op.drop_index('idx_audit_ip_timestamp', table_name='audit_log_entries')
    op.drop_index('idx_audit_category_timestamp', table_name='audit_log_entries')
    op.drop_index('idx_audit_resource', table_name='audit_log_entries')
    op.drop_index('idx_audit_event_timestamp', table_name='audit_log_entries')
    op.drop_index('idx_audit_user_timestamp', table_name='audit_log_entries')
    op.drop_index('idx_audit_timestamp_desc', table_name='audit_log_entries')
    op.drop_index('idx_audit_timestamp', table_name='audit_log_entries')
    
    # Drop table
    op.drop_table('audit_log_entries')
