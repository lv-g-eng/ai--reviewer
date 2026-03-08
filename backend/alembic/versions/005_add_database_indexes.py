"""Add database indexes for optimization

Revision ID: 005
Revises: 004
Create Date: 2024-01-15 10:00:00.000000

This migration adds indexes on all foreign keys and composite indexes
for common query patterns to optimize database performance.

Requirements: 10.5 - Database query optimization with proper indexes on all foreign keys
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004_project_access_session_code_entity'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes for database optimization"""
    
    # Foreign key indexes for pull_requests table
    op.create_index('idx_pull_requests_project_id', 'pull_requests', ['project_id'])
    op.create_index('idx_pull_requests_author_id', 'pull_requests', ['author_id'])
    
    # Foreign key indexes for code_reviews table
    op.create_index('idx_code_reviews_pull_request_id', 'code_reviews', ['pull_request_id'])
    
    # Foreign key indexes for review_comments table
    op.create_index('idx_review_comments_review_id', 'review_comments', ['review_id'])
    
    # Foreign key indexes for architecture_analyses table
    op.create_index('idx_architecture_analyses_pull_request_id', 'architecture_analyses', ['pull_request_id'])
    
    # Foreign key indexes for architecture_violations table
    op.create_index('idx_architecture_violations_analysis_id', 'architecture_violations', ['analysis_id'])
    
    # Foreign key indexes for review_results table
    op.create_index('idx_review_results_pull_request_id', 'review_results', ['pull_request_id'])
    
    # Foreign key indexes for projects table
    op.create_index('idx_projects_owner_id', 'projects', ['owner_id'])
    
    # Foreign key indexes for audit_logs table
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    
    # Foreign key indexes for architectural_baselines table
    op.create_index('idx_architectural_baselines_project_id', 'architectural_baselines', ['project_id'])
    
    # Foreign key indexes for token_blacklist table
    op.create_index('idx_token_blacklist_user_id', 'token_blacklist', ['user_id'])
    
    # Foreign key indexes for library_dependencies table (already has index, but ensuring)
    # op.create_index('idx_library_dependencies_library_id', 'library_dependencies', ['library_id'])
    
    # Composite indexes for common query patterns
    
    # Query PRs by project and status
    op.create_index('idx_pull_requests_project_status', 'pull_requests', ['project_id', 'status'])
    
    # Query PRs by project and creation date (for recent PRs)
    op.create_index('idx_pull_requests_project_created', 'pull_requests', ['project_id', 'created_at'])
    
    # Query reviews by PR and status
    op.create_index('idx_code_reviews_pr_status', 'code_reviews', ['pull_request_id', 'status'])
    
    # Query comments by review and severity
    op.create_index('idx_review_comments_review_severity', 'review_comments', ['review_id', 'severity'])
    
    # Query comments by file path (for file-specific queries)
    op.create_index('idx_review_comments_file_path', 'review_comments', ['file_path'])
    
    # Query architecture analyses by PR and status
    op.create_index('idx_architecture_analyses_pr_status', 'architecture_analyses', ['pull_request_id', 'status'])
    
    # Query violations by analysis and severity
    op.create_index('idx_architecture_violations_analysis_severity', 'architecture_violations', ['analysis_id', 'severity'])
    
    # Query violations by type (for filtering by violation type)
    op.create_index('idx_architecture_violations_type', 'architecture_violations', ['type'])
    
    # Query projects by owner and active status
    op.create_index('idx_projects_owner_active', 'projects', ['owner_id', 'is_active'])
    
    # Query audit logs by user and timestamp (for audit trails)
    op.create_index('idx_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    
    # Query audit logs by entity (for entity-specific audit trails)
    op.create_index('idx_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    
    # Query audit logs by action and timestamp (for action-specific queries)
    op.create_index('idx_audit_logs_action_timestamp', 'audit_logs', ['action', 'timestamp'])
    
    # Query baselines by project and current status
    op.create_index('idx_architectural_baselines_project_current', 'architectural_baselines', ['project_id', 'is_current'])
    
    # Query sessions by user and active status
    op.create_index('idx_sessions_user_active', 'sessions', ['user_id', 'is_active'])
    
    # Query sessions by expiration (for cleanup)
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])
    
    # Query code entities by project and type
    op.create_index('idx_code_entities_project_type', 'code_entities', ['project_id', 'entity_type'])
    
    # Query code entities by PR (for PR-specific entities)
    op.create_index('idx_code_entities_pull_request', 'code_entities', ['pull_request_id'])
    
    # Query code entities by file path (for file-specific queries)
    op.create_index('idx_code_entities_file_path', 'code_entities', ['file_path'])
    
    # Query libraries by project context (for frontend/backend separation)
    op.create_index('idx_libraries_project_context', 'libraries', ['project_id', 'project_context'])
    
    # Query libraries by registry type
    op.create_index('idx_libraries_registry_type', 'libraries', ['registry_type'])


def downgrade() -> None:
    """Remove indexes"""
    
    # Drop foreign key indexes
    op.drop_index('idx_pull_requests_project_id', table_name='pull_requests')
    op.drop_index('idx_pull_requests_author_id', table_name='pull_requests')
    op.drop_index('idx_code_reviews_pull_request_id', table_name='code_reviews')
    op.drop_index('idx_review_comments_review_id', table_name='review_comments')
    op.drop_index('idx_architecture_analyses_pull_request_id', table_name='architecture_analyses')
    op.drop_index('idx_architecture_violations_analysis_id', table_name='architecture_violations')
    op.drop_index('idx_review_results_pull_request_id', table_name='review_results')
    op.drop_index('idx_projects_owner_id', table_name='projects')
    op.drop_index('idx_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('idx_architectural_baselines_project_id', table_name='architectural_baselines')
    op.drop_index('idx_token_blacklist_user_id', table_name='token_blacklist')
    
    # Drop composite indexes
    op.drop_index('idx_pull_requests_project_status', table_name='pull_requests')
    op.drop_index('idx_pull_requests_project_created', table_name='pull_requests')
    op.drop_index('idx_code_reviews_pr_status', table_name='code_reviews')
    op.drop_index('idx_review_comments_review_severity', table_name='review_comments')
    op.drop_index('idx_review_comments_file_path', table_name='review_comments')
    op.drop_index('idx_architecture_analyses_pr_status', table_name='architecture_analyses')
    op.drop_index('idx_architecture_violations_analysis_severity', table_name='architecture_violations')
    op.drop_index('idx_architecture_violations_type', table_name='architecture_violations')
    op.drop_index('idx_projects_owner_active', table_name='projects')
    op.drop_index('idx_audit_logs_user_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_logs_entity', table_name='audit_logs')
    op.drop_index('idx_audit_logs_action_timestamp', table_name='audit_logs')
    op.drop_index('idx_architectural_baselines_project_current', table_name='architectural_baselines')
    op.drop_index('idx_sessions_user_active', table_name='sessions')
    op.drop_index('idx_sessions_expires_at', table_name='sessions')
    op.drop_index('idx_code_entities_project_type', table_name='code_entities')
    op.drop_index('idx_code_entities_pull_request', table_name='code_entities')
    op.drop_index('idx_code_entities_file_path', table_name='code_entities')
    op.drop_index('idx_libraries_project_context', table_name='libraries')
    op.drop_index('idx_libraries_registry_type', table_name='libraries')
