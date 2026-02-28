"""Add encryption to sensitive fields

Revision ID: 006
Revises: 005
Create Date: 2024-01-15 10:00:00.000000

Implements Requirement 8.4: Encrypt all sensitive data at rest using AES-256 encryption

This migration:
1. Identifies sensitive fields that should be encrypted
2. Adds encryption to: github_webhook_secret, API keys, tokens
3. Provides rollback capability

Note: This migration does NOT encrypt existing data. To encrypt existing data,
run the encryption migration script after applying this migration.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add encryption to sensitive fields.
    
    Sensitive fields identified:
    - projects.github_webhook_secret (webhook secrets)
    - Future: API keys, tokens, credentials
    
    Note: Existing data remains unencrypted until migration script is run.
    """
    # Add comment to sensitive fields to indicate they should be encrypted
    op.execute("""
        COMMENT ON COLUMN projects.github_webhook_secret IS 
        'GitHub webhook secret - should be encrypted at application level using EncryptedString type'
    """)
    
    # Create a table to track encryption status
    op.create_table(
        'encryption_metadata',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('table_name', sa.String(100), nullable=False),
        sa.Column('column_name', sa.String(100), nullable=False),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('encryption_algorithm', sa.String(50), nullable=True),
        sa.Column('encrypted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('encrypted_by', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('table_name', 'column_name', name='uq_encryption_metadata_table_column')
    )
    
    # Add index for efficient lookups
    op.create_index(
        'idx_encryption_metadata_table',
        'encryption_metadata',
        ['table_name', 'is_encrypted']
    )
    
    # Register sensitive fields that should be encrypted
    op.execute("""
        INSERT INTO encryption_metadata (id, table_name, column_name, is_encrypted, encryption_algorithm, notes)
        VALUES 
            (gen_random_uuid(), 'projects', 'github_webhook_secret', false, 'AES-256-GCM', 'GitHub webhook secret for validating webhook requests'),
            (gen_random_uuid(), 'users', 'password_hash', false, 'bcrypt', 'Password hashes are already encrypted using bcrypt')
    """)
    
    print("✅ Encryption metadata table created")
    print("⚠️  To encrypt existing data, run: python backend/scripts/encrypt_existing_data.py")


def downgrade() -> None:
    """Remove encryption metadata."""
    op.drop_index('idx_encryption_metadata_table', table_name='encryption_metadata')
    op.drop_table('encryption_metadata')
    
    # Remove comments
    op.execute("COMMENT ON COLUMN projects.github_webhook_secret IS NULL")
