"""add github fields to user

Revision ID: 008
Revises: 007
Create Date: 2026-02-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add GitHub token and username fields to users table
    op.add_column('users', sa.Column('github_token', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('github_username', sa.String(length=255), nullable=True))
    
    # Add index on github_username for faster lookups
    op.create_index(op.f('ix_users_github_username'), 'users', ['github_username'], unique=False)


def downgrade() -> None:
    # Remove index
    op.drop_index(op.f('ix_users_github_username'), table_name='users')
    
    # Remove columns
    op.drop_column('users', 'github_username')
    op.drop_column('users', 'github_token')
