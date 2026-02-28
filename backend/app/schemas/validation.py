"""
Enhanced Pydantic validation models with comprehensive input sanitization

This module provides validated schemas for all API request/response models
with built-in sanitization to prevent SQL injection, XSS, and other attacks.

Requirements:
- 2.9: Validate all input data using Pydantic schemas
- 2.10: Sanitize all user input to prevent SQL injection and XSS attacks
- 8.7: Validate and sanitize all user input to prevent injection attacks
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import datetime
from app.utils.validators import (
    sanitize_html,
    sanitize_string,
    validate_url,
    validate_github_url,
    validate_file_path,
    validate_integer_range,
    validate_string_length,
    sanitize_filename
)


class SanitizedStringField(BaseModel):
    """Base model with sanitized string field"""
    
    @field_validator('*', mode='before')
    @classmethod
    def sanitize_strings(cls, v):
        """Automatically sanitize all string fields"""
        if isinstance(v, str):
            return sanitize_string(v)
        return v


class ProjectCreateRequest(SanitizedStringField):
    """
    Validated request for creating a new project
    
    Requirements:
        - 2.9: Validate all input data
        - 2.10: Sanitize user input
    """
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate and sanitize project name"""
        is_valid, error = validate_string_length(v, min_length=1, max_length=200)
        if not is_valid:
            raise ValueError(error)
        return sanitize_string(v, max_length=200)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate and sanitize description"""
        if v:
            is_valid, error = validate_string_length(v, max_length=1000)
            if not is_valid:
                raise ValueError(error)
            # Allow safe HTML in descriptions
            return sanitize_html(v)
        return v
    
    @field_validator('repository_url')
    @classmethod
    def validate_repo_url(cls, v):
        """Validate repository URL"""
        if v:
            is_valid, error = validate_github_url(v)
            if not is_valid:
                raise ValueError(error)
        return v


class CommentCreateRequest(SanitizedStringField):
    """
    Validated request for creating a comment
    
    Requirements:
        - 2.9: Validate all input data
        - 2.10: Sanitize user input to prevent XSS
    """
    content: str = Field(..., min_length=1, max_length=5000, description="Comment content")
    file_path: Optional[str] = Field(None, max_length=500, description="File path")
    line_number: Optional[int] = Field(None, ge=1, description="Line number")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate and sanitize comment content"""
        is_valid, error = validate_string_length(v, min_length=1, max_length=5000)
        if not is_valid:
            raise ValueError(error)
        # Sanitize HTML to prevent XSS
        return sanitize_html(v)
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v):
        """Validate file path to prevent directory traversal"""
        if v:
            is_valid, error = validate_file_path(v, allow_absolute=False)
            if not is_valid:
                raise ValueError(error)
            return sanitize_string(v, max_length=500)
        return v
    
    @field_validator('line_number')
    @classmethod
    def validate_line_number(cls, v):
        """Validate line number range"""
        if v is not None:
            is_valid, error = validate_integer_range(v, min_value=1, max_value=1000000)
            if not is_valid:
                raise ValueError(error)
        return v


class FileUploadRequest(SanitizedStringField):
    """
    Validated request for file upload
    
    Requirements:
        - 2.9: Validate all input data
        - 8.7: Prevent injection attacks
    """
    filename: str = Field(..., min_length=1, max_length=255, description="Filename")
    content_type: str = Field(..., max_length=100, description="Content type")
    size_bytes: int = Field(..., ge=0, le=100_000_000, description="File size in bytes")
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate and sanitize filename"""
        return sanitize_filename(v)
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        """Validate content type"""
        allowed_types = [
            'text/plain', 'text/markdown', 'text/html',
            'application/json', 'application/xml',
            'application/pdf', 'application/zip',
            'image/png', 'image/jpeg', 'image/gif'
        ]
        if v not in allowed_types:
            raise ValueError(f"Content type not allowed: {v}")
        return v


class SearchRequest(SanitizedStringField):
    """
    Validated request for search operations
    
    Requirements:
        - 2.9: Validate all input data
        - 2.10: Sanitize user input
    """
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    page: int = Field(1, ge=1, le=1000, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Page size")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate and sanitize search query"""
        is_valid, error = validate_string_length(v, min_length=1, max_length=500)
        if not is_valid:
            raise ValueError(error)
        # Escape special characters to prevent injection
        return sanitize_string(v, max_length=500)
    
    @field_validator('filters')
    @classmethod
    def validate_filters(cls, v):
        """Validate search filters"""
        if v:
            # Limit filter complexity
            if len(v) > 10:
                raise ValueError("Too many filters (maximum 10)")
            
            # Sanitize filter values
            sanitized = {}
            for key, value in v.items():
                if isinstance(value, str):
                    sanitized[sanitize_string(key)] = sanitize_string(value)
                else:
                    sanitized[sanitize_string(key)] = value
            return sanitized
        return v


class WebhookPayload(SanitizedStringField):
    """
    Validated webhook payload
    
    Requirements:
        - 2.9: Validate all input data
        - 2.10: Sanitize user input
    """
    event_type: str = Field(..., max_length=100, description="Event type")
    payload: Dict[str, Any] = Field(..., description="Event payload")
    signature: Optional[str] = Field(None, max_length=500, description="Webhook signature")
    
    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v):
        """Validate event type"""
        allowed_events = [
            'pull_request', 'push', 'issue', 'comment',
            'review', 'status', 'deployment'
        ]
        sanitized = sanitize_string(v, max_length=100)
        if sanitized not in allowed_events:
            raise ValueError(f"Unknown event type: {sanitized}")
        return sanitized
    
    @field_validator('payload')
    @classmethod
    def validate_payload(cls, v):
        """Validate and sanitize payload"""
        if not isinstance(v, dict):
            raise ValueError("Payload must be a dictionary")
        
        # Limit payload size
        if len(str(v)) > 1_000_000:  # 1MB limit
            raise ValueError("Payload too large")
        
        return v


class ConfigurationUpdate(SanitizedStringField):
    """
    Validated configuration update request
    
    Requirements:
        - 2.9: Validate all input data
        - 8.7: Prevent injection attacks
    """
    key: str = Field(..., min_length=1, max_length=100, description="Configuration key")
    value: str = Field(..., max_length=1000, description="Configuration value")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    
    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        """Validate configuration key"""
        # Only allow alphanumeric, underscore, and dot
        import re
        if not re.match(r'^[a-zA-Z0-9_\.]+$', v):
            raise ValueError("Key can only contain alphanumeric characters, underscore, and dot")
        return sanitize_string(v, max_length=100)
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        """Validate and sanitize configuration value"""
        return sanitize_string(v, max_length=1000)


class UserProfileUpdate(SanitizedStringField):
    """
    Validated user profile update request
    
    Requirements:
        - 2.9: Validate all input data
        - 2.10: Sanitize user input to prevent XSS
    """
    full_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Full name")
    bio: Optional[str] = Field(None, max_length=1000, description="User bio")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        """Validate and sanitize full name"""
        if v:
            is_valid, error = validate_string_length(v, min_length=1, max_length=200)
            if not is_valid:
                raise ValueError(error)
            return sanitize_string(v, max_length=200)
        return v
    
    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v):
        """Validate and sanitize bio"""
        if v:
            is_valid, error = validate_string_length(v, max_length=1000)
            if not is_valid:
                raise ValueError(error)
            # Allow safe HTML in bio
            return sanitize_html(v)
        return v
    
    @field_validator('avatar_url')
    @classmethod
    def validate_avatar_url(cls, v):
        """Validate avatar URL"""
        if v:
            if not validate_url(v, allowed_schemes=['http', 'https']):
                raise ValueError("Invalid avatar URL")
            return sanitize_string(v, max_length=500)
        return v


class AnalysisRequest(SanitizedStringField):
    """
    Validated code analysis request
    
    Requirements:
        - 2.9: Validate all input data
        - 2.10: Sanitize user input
    """
    project_id: str = Field(..., description="Project ID")
    commit_sha: Optional[str] = Field(None, max_length=40, description="Commit SHA")
    branch: Optional[str] = Field(None, max_length=200, description="Branch name")
    files: Optional[List[str]] = Field(None, max_items=1000, description="Files to analyze")
    
    @field_validator('commit_sha')
    @classmethod
    def validate_commit_sha(cls, v):
        """Validate commit SHA format"""
        if v:
            import re
            if not re.match(r'^[a-f0-9]{40}$', v):
                raise ValueError("Invalid commit SHA format")
        return v
    
    @field_validator('branch')
    @classmethod
    def validate_branch(cls, v):
        """Validate branch name"""
        if v:
            import re
            if not re.match(r'^[\w\-\.\/]+$', v):
                raise ValueError("Invalid branch name format")
            return sanitize_string(v, max_length=200)
        return v
    
    @field_validator('files')
    @classmethod
    def validate_files(cls, v):
        """Validate file paths"""
        if v:
            if len(v) > 1000:
                raise ValueError("Too many files (maximum 1000)")
            
            sanitized = []
            for file_path in v:
                is_valid, error = validate_file_path(file_path, allow_absolute=False)
                if not is_valid:
                    raise ValueError(f"Invalid file path: {file_path} - {error}")
                sanitized.append(sanitize_string(file_path, max_length=500))
            return sanitized
        return v


class BulkOperationRequest(SanitizedStringField):
    """
    Validated bulk operation request
    
    Requirements:
        - 2.9: Validate all input data
    """
    operation: str = Field(..., max_length=50, description="Operation type")
    entity_ids: List[str] = Field(..., min_items=1, max_items=100, description="Entity IDs")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v):
        """Validate operation type"""
        allowed_operations = [
            'delete', 'archive', 'restore', 'update',
            'export', 'analyze', 'scan'
        ]
        sanitized = sanitize_string(v, max_length=50)
        if sanitized not in allowed_operations:
            raise ValueError(f"Unknown operation: {sanitized}")
        return sanitized
    
    @field_validator('entity_ids')
    @classmethod
    def validate_entity_ids(cls, v):
        """Validate entity IDs"""
        if len(v) > 100:
            raise ValueError("Too many entities (maximum 100)")
        
        # Sanitize each ID
        return [sanitize_string(id_val, max_length=100) for id_val in v]


class NotificationPreferences(SanitizedStringField):
    """
    Validated notification preferences
    
    Requirements:
        - 2.9: Validate all input data
    """
    email_enabled: bool = Field(True, description="Enable email notifications")
    slack_enabled: bool = Field(False, description="Enable Slack notifications")
    slack_webhook_url: Optional[str] = Field(None, max_length=500, description="Slack webhook URL")
    notification_types: List[str] = Field(default_factory=list, description="Notification types")
    
    @field_validator('slack_webhook_url')
    @classmethod
    def validate_slack_webhook(cls, v):
        """Validate Slack webhook URL"""
        if v:
            if not validate_url(v, allowed_schemes=['https']):
                raise ValueError("Invalid Slack webhook URL")
            if not v.startswith('https://hooks.slack.com/'):
                raise ValueError("Invalid Slack webhook URL format")
            return sanitize_string(v, max_length=500)
        return v
    
    @field_validator('notification_types')
    @classmethod
    def validate_notification_types(cls, v):
        """Validate notification types"""
        allowed_types = [
            'security_alert', 'analysis_complete', 'pr_review',
            'deployment', 'error', 'warning'
        ]
        for notification_type in v:
            if notification_type not in allowed_types:
                raise ValueError(f"Unknown notification type: {notification_type}")
        return v
